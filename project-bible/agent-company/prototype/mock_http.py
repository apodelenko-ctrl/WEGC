"""Loopback-only ACI simulator. No real KYC, providers, documents or payments."""
import argparse
import copy
import hashlib
import json
import os
import re
import secrets
import threading
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from lifecycle import Actor, Lifecycle

MAX_BODY = 16384  # Technical test limit, not a commercial entitlement.


class APIError(Exception):
    def __init__(self, status, code):
        self.status, self.code = status, code
        super().__init__(code)


def require(condition, code="invalid_payload", status=422):
    if not condition:
        raise APIError(status, code)


def decode_body(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate_json_key", 400)
            result[key] = value
        return result
    try:
        value = json.loads(raw, object_pairs_hook=unique,
                           parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
    except (ValueError, UnicodeError, RecursionError):
        raise APIError(400, "invalid_json") from None
    require(isinstance(value, dict), "object_required")
    return value


class MockAPI:
    def __init__(self, tokens):
        require(bool(tokens), "tokens_required")
        self.tokens = dict(tokens)
        require(all(a.role in {"agent", "operator"} for a in tokens.values()), "invalid_role")
        self.flow, self.cache, self.audit = Lifecycle(), {}, []
        self.lock = threading.RLock()

    def call(self, method, path, authorization="", key="", payload=None):
        try:
            with self.lock:
                data = self._call(method, path, authorization, key, payload)
            return 200, {"simulation": True, "external_side_effect": False, "data": data}
        except APIError as exc:
            return exc.status, {"simulation": True, "error": {"code": exc.code}}
        except KeyError:
            return 404, {"simulation": True, "error": {"code": "not_found"}}
        except PermissionError as exc:
            code = str(exc)
            return (404 if code == "tenant_or_principal_scope" else 403), {
                "simulation": True, "error": {"code": "not_found" if code == "tenant_or_principal_scope" else code}}
        except ValueError as exc:
            return 409, {"simulation": True, "error": {"code": str(exc)}}

    def _call(self, method, path, authorization, key, payload):
        if method == "GET" and path == "/v1/capabilities":
            return {"mode": "local_mock", "production": False,
                    "implemented": ["applications", "operator_approvals", "simulation_events", "mandates", "operations"],
                    "not_implemented": ["KYC", "EIN", "payments", "document_storage", "persistence", "agent_runner"]}
        token = authorization.removeprefix("Bearer ") if authorization.startswith("Bearer ") else ""
        actor = self.tokens.get(token)
        require(actor is not None, "unauthorized", 401)
        match = re.fullmatch(r"/v1/applications/([a-f0-9-]+)(?:/([a-z-]+))?", path)
        rid, action = match.groups() if match else (None, None)
        if rid:
            self.flow.get(actor, rid)  # Scope check happens before cache access.
        if method == "GET" and rid and not action:
            return asdict(self.flow.get(actor, rid))
        require(method == "POST", "route_not_found", 404)
        require(path == "/v1/applications" or (rid and action), "route_not_found", 404)
        schemas = {None: {"name", "principal_ref"}, "approvals": set(), "submission": set(),
                   "simulate-formation": set(), "payment-submission": set(), "simulate-payment-approval": set(),
                   "mandates": {"agent_id", "scopes"}, "revocation": set(), "operations": {"action"}}
        require(action in schemas, "route_not_found", 404)
        require(isinstance(payload, dict) and set(payload) == schemas[action])
        require(isinstance(key, str) and re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", key), "idempotency_key_required", 400)
        if action in {"approvals", "simulate-formation", "payment-submission", "simulate-payment-approval", "mandates", "revocation"}:
            require(actor.role == "operator", "operator_required", 403)
        if action == "operations":
            require(isinstance(payload["action"], str))
            self.flow.operate(actor, rid, payload["action"])  # Revalidate even an idempotent replay after revocation.
        if action is None:
            require(payload["principal_ref"] == actor.principal_ref, "principal_mismatch", 403)
            require(isinstance(payload["name"], str) and 0 < len(payload["name"].strip()) <= 200)
        if action == "mandates":
            require(isinstance(payload["agent_id"], str) and bool(payload["agent_id"].strip()))
            require(isinstance(payload["scopes"], list) and all(isinstance(s, str) for s in payload["scopes"]))
        fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, allow_nan=False).encode()).hexdigest()
        index = (actor.tenant_id, actor.principal_ref, actor.role, actor.agent_id, path, key)
        if index in self.cache:
            previous, response = self.cache[index]
            require(previous == fingerprint, "idempotency_conflict", 409)
            return copy.deepcopy(response)
        if action is None:
            # Separate the underlying model's keys by actor, like the HTTP cache.
            model_key = hashlib.sha256(repr(index).encode()).hexdigest()
            result = asdict(self.flow.create(actor, payload["name"], model_key))
        elif action == "mandates":
            result = asdict(self.flow.grant(actor, rid, payload["agent_id"], tuple(payload["scopes"])))
        elif action == "revocation":
            result = asdict(self.flow.revoke(actor, rid))
        elif action == "operations":
            result = self.flow.operate(actor, rid, payload["action"])
        else:
            events = {"approvals": "approve_submission", "submission": "submit_formation",
                      "simulate-formation": "formation_confirmed", "payment-submission": "submit_payments",
                      "simulate-payment-approval": "payments_approved"}
            event_actor = Actor(actor.tenant_id, actor.principal_ref, "provider_fixture") if action.startswith("simulate-") else actor
            result = asdict(self.flow.transition(event_actor, rid, events[action], "sim:local_fixture"))
        self.cache[index] = (fingerprint, copy.deepcopy(result))
        self.audit.append({"method": method, "path": path, "tenant_id": actor.tenant_id,
                           "role": actor.role, "simulation": True})
        return result


def make_server(api, port=0, host="127.0.0.1"):
    require(host == "127.0.0.1", "loopback_only")

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass  # Do not log bearer headers or request payloads.

        def do_GET(self):
            self.handle_api()

        def do_POST(self):
            self.handle_api()

        def handle_api(self):
            self.connection.settimeout(3)
            try:
                hosts = self.headers.get_all("Host", [])
                require(len(hosts) == 1 and hosts[0] == f"127.0.0.1:{self.server.server_port}", "invalid_host", 400)
                require(not self.headers.get("Origin"), "browser_origin_denied", 403)
                require(not self.headers.get("Transfer-Encoding"), "transfer_encoding_denied", 400)
                for name in ("Authorization", "Content-Length", "Idempotency-Key", "Content-Type"):
                    require(len(self.headers.get_all(name, [])) <= 1, "duplicate_header", 400)
                payload = None
                if self.command == "POST":
                    require(self.headers.get("Content-Type", "").split(";")[0].strip() == "application/json", "json_required", 415)
                    length = self.headers.get("Content-Length", "")
                    require(length.isdigit(), "content_length_required", 411)
                    require(0 < int(length) <= MAX_BODY, "body_too_large", 413)
                    raw = self.rfile.read(int(length))
                    require(len(raw) == int(length), "incomplete_body", 400)
                    payload = decode_body(raw)
                code, body = api.call(self.command, self.path, self.headers.get("Authorization", ""),
                                      self.headers.get("Idempotency-Key", ""), payload)
            except APIError as exc:
                code, body = exc.status, {"simulation": True, "error": {"code": exc.code}}
            except TimeoutError:
                code, body = 408, {"simulation": True, "error": {"code": "request_timeout"}}
            except Exception:
                code, body = 500, {"simulation": True, "error": {"code": "internal_error"}}
            encoded = json.dumps(body, ensure_ascii=False).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(encoded)

    return ThreadingHTTPServer((host, port), Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--credentials-file", required=True, help="New local file OUTSIDE the repository; synthetic credentials only")
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()
    path = Path(args.credentials_file).resolve()
    require(not path.is_relative_to(Path(__file__).resolve().parents[3]), "credentials_outside_repo_required")
    fixtures = {role: secrets.token_urlsafe(32) for role in ("agent", "operator")}
    tokens = {token: Actor("simulation_tenant", "simulation_principal", role, "simulation_agent" if role == "agent" else "")
              for role, token in fixtures.items()}
    server = make_server(MockAPI(tokens), args.port)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as output:
            json.dump({"simulation": True, "base_url": f"http://127.0.0.1:{server.server_port}",
                       "principal_ref": "simulation_principal", "agent_id": "simulation_agent", "tokens": fixtures}, output)
        print(f"LOCAL SIMULATION ONLY: http://127.0.0.1:{server.server_port}; credentials written to requested private file")
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
