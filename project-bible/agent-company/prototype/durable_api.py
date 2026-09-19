"""Durable loopback simulator: fixture identities, no KYC, providers or money."""
import argparse
from dataclasses import asdict
import json
import math
import os
from pathlib import Path
import re
import secrets
import sqlite3
import time
from uuid import uuid4
from lifecycle import Actor, Application, Lifecycle
from mock_http import APIError, make_server, require
from sqlite_store import Store, VersionConflict, digest

AGENT_SCOPES = {"create_application", "read_application", "submit_formation", "read_documents", "prepare_invoice"}
SCHEMAS = {"create": {"name", "principal_ref"}, "approvals": set(), "submission": set(),
           "simulate-formation": set(), "payment-submission": set(), "simulate-payment-approval": set(),
           "mandates": {"agent_id", "scopes", "expires_at"}, "revocation": set(),
           "operations": {"action"}, "identity-revocation": set(), "agent-revocation": set()}
OPERATOR_ACTIONS = set(SCHEMAS) - {"create", "submission", "operations"}


def finite_number(value):
    return type(value) in (int, float) and math.isfinite(value)


def text(value, maximum=200):
    return isinstance(value, str) and 0 < len(value.strip()) <= maximum


class DurableAPI:
    def __init__(self, database, clock=time.time):
        self.store, self.clock = Store(database), clock

    def register_identity(self, token, actor, expires_at, applications=None, scopes=None):
        """Trusted LOCAL provisioning only; deliberately NOT an HTTP route or KYC."""
        require(text(token, 512) and actor.role in {"operator", "agent"}, "invalid_identity")
        require(text(actor.tenant_id) and text(actor.principal_ref), "invalid_identity")
        require(actor.role != "agent" or text(actor.agent_id), "agent_id_required")
        require(finite_number(expires_at) and expires_at > self.clock(), "invalid_expiry")
        require(applications is None or isinstance(applications, list) and all(text(a) for a in applications), "invalid_applications")
        selected = sorted(AGENT_SCOPES if scopes is None else scopes)
        require(set(selected).issubset(AGENT_SCOPES), "invalid_scopes")
        token_key = digest(token)
        profile = {"tenant_id": actor.tenant_id, "principal_ref": actor.principal_ref, "role": actor.role,
                   "agent_id": actor.agent_id, "expires_at": expires_at,
                   "applications": sorted(set(applications)) if applications is not None else None,
                   "scopes": selected}
        with self.store.transaction() as tx:
            disabled, _ = tx.get("disabled_agents", digest([actor.tenant_id, actor.principal_ref, actor.agent_id]))
            require(actor.role != "agent" or disabled is None, "agent_revoked", 401)
            mapping, _ = tx.get("tokens", token_key)
            if mapping:
                old, _ = tx.get("identities", mapping["id"])
                require(all(old[k] == v for k, v in profile.items()), "identity_already_provisioned", 409)
                require(not old["revoked"], "identity_revoked", 401)
                return old["id"]
            identity_id = str(uuid4())
            tx.put("identities", identity_id, {**profile, "id": identity_id, "revoked": False}, 0)
            tx.put("tokens", token_key, {"id": identity_id}, 0)
            tx.event(self.clock(), "identity_provisioned", {"id": identity_id, "simulation": True})
            return identity_id

    def _identity(self, tx, authorization, now):
        token = authorization[7:] if isinstance(authorization, str) and authorization.startswith("Bearer ") else ""
        mapping, _ = tx.get("tokens", digest(token))
        require(bool(token) and mapping is not None, "unauthorized", 401)
        identity, _ = tx.get("identities", mapping["id"])
        require(identity is not None and not identity["revoked"] and now < identity["expires_at"], "identity_inactive", 401)
        disabled, _ = tx.get("disabled_agents", digest([identity["tenant_id"], identity["principal_ref"], identity["agent_id"]]))
        require(identity["role"] != "agent" or disabled is None, "agent_revoked", 401)
        return identity, Actor(identity["tenant_id"], identity["principal_ref"], identity["role"], identity["agent_id"])

    def call(self, method, path, authorization="", key="", payload=None):
        try:
            with self.store.transaction() as tx:
                data, receipt = self._call(tx, method, path, authorization, key, payload)
            result = {"simulation": True, "external_side_effect": False, "data": data}
            if receipt is not None:
                result["receipt"] = receipt
            return 200, result
        except APIError as exc:
            status, code = exc.status, exc.code
        except (KeyError, PermissionError) as exc:
            status, code = (404, "not_found") if isinstance(exc, KeyError) or str(exc) == "tenant_or_principal_scope" else (403, str(exc))
        except (ValueError, VersionConflict) as exc:
            status, code = 409, str(exc)
        except sqlite3.OperationalError:
            status, code = 503, "store_unavailable"
        return status, {"simulation": True, "error": {"code": code}}

    def _call(self, tx, method, path, authorization, key, payload):
        now = self.clock()
        if method == "GET" and path == "/v1/capabilities":
            return {"mode": "durable_local_mock", "production": False,
                    "implemented": ["sqlite_state", "idempotency", "record_versions", "identity_expiry",
                                    "identity_revocation", "application_scopes", "mandate_expiry", "historical_receipts"],
                    "not_implemented": ["KYC", "EIN", "real_payments", "provider_webhooks", "production_auth"]}, None
        identity, actor = self._identity(tx, authorization, now)
        match = re.fullmatch(r"/v1/applications/([a-f0-9-]+)(?:/([a-z-]+))?", path)
        rid, action = match.groups() if match else (None, None)
        revoke_match = re.fullmatch(r"/v1/identities/([a-f0-9-]+)/revocation", path)
        target_id = revoke_match.group(1) if revoke_match else None
        agent_match = re.fullmatch(r"/v1/agents/([A-Za-z0-9_.:-]{1,128})/revocation", path)
        target_agent = agent_match.group(1) if agent_match else None
        flow, stored, version, expiry = Lifecycle(), None, 0, None
        if rid:
            stored, version = tx.get("applications", rid)
            require(stored is not None, "not_found", 404)
            require(identity["applications"] is None or rid in identity["applications"], "not_found", 404)
            expiry = stored["mandate_expires_at"]
            fields = dict(stored["record"])
            fields["scopes"] = tuple(fields["scopes"])
            flow._records[rid] = Application(**fields)  # Adapter to the preserved baseline model.
            flow.get(actor, rid)
        if method == "GET" and rid and not action:
            self._scope(identity, "read_application")
            result = {**asdict(flow.get(actor, rid)), "record_version": version, "mandate_expires_at": expiry}
            disabled, _ = tx.get("disabled_agents", digest([actor.tenant_id, actor.principal_ref, result["agent_id"]]))
            result["mandate_effective"] = result["mandate"] == "active" and expiry is not None and now < expiry and disabled is None
            return result, None
        if path == "/v1/applications":
            action = "create"
        if target_id:
            action = "identity-revocation"
        if target_agent:
            action = "agent-revocation"
        require(method == "POST" and action in SCHEMAS and (rid or target_id or target_agent or action == "create"), "route_not_found", 404)
        require(isinstance(payload, dict), "invalid_payload")
        fields = set(payload) - {"expected_version"}
        require(fields == SCHEMAS[action], "invalid_payload")
        require(isinstance(key, str) and re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", key), "idempotency_key_required", 400)
        if "expected_version" in payload:
            require(rid is not None and type(payload["expected_version"]) is int and payload["expected_version"] > 0, "invalid_version")
        if action in OPERATOR_ACTIONS:
            require(actor.role == "operator", "operator_required", 403)
        if action == "create":
            self._scope(identity, "create_application")
            require(identity["applications"] is None, "application_scope_denied", 403)
            require(payload["principal_ref"] == actor.principal_ref, "principal_mismatch", 403)
            require(text(payload["name"]), "invalid_name")
        if action == "submission":
            self._scope(identity, "submit_formation")
        if action == "operations":
            require(isinstance(payload["action"], str), "invalid_action")
            self._scope(identity, payload["action"])
            require(expiry is not None and now < expiry, "mandate_expired", 403)
            flow.operate(actor, rid, payload["action"])  # Authorization is checked BEFORE historical replay.
        if action == "mandates":
            require(text(payload["agent_id"]), "invalid_agent")
            require(isinstance(payload["scopes"], list) and all(isinstance(s, str) for s in payload["scopes"]), "invalid_scopes")
            require(finite_number(payload["expires_at"]), "invalid_expiry")
        if target_id or target_agent:
            require(identity["applications"] is None, "unrestricted_operator_required", 403)
        if target_id:
            target, target_version = tx.get("identities", target_id)
            require(target is not None and (target["tenant_id"], target["principal_ref"]) == (actor.tenant_id, actor.principal_ref), "not_found", 404)
            require(target["role"] == "agent", "agent_identity_required", 403)
        request_key = digest([identity["id"], method, path, key])
        fingerprint = digest(payload)
        previous, _ = tx.get("requests", request_key)
        if previous:
            require(previous["fingerprint"] == fingerprint, "idempotency_conflict", 409)
            return previous["data"], {**previous["receipt"], "replayed": True,
                   "result_is_historical": True, "current_authorization_checked": True}
        if "expected_version" in payload:
            require(version == payload["expected_version"], "version_conflict", 409)
        if action == "create":
            record = flow.create(actor, payload["name"], request_key)
            rid = record.id
            data = asdict(record)
        elif action == "mandates":
            require(payload["expires_at"] > now, "invalid_expiry")
            expiry = payload["expires_at"]
            data = asdict(flow.grant(actor, rid, payload["agent_id"], tuple(payload["scopes"])))
        elif action == "revocation":
            data = asdict(flow.revoke(actor, rid))
        elif action == "operations":
            data = flow.operate(actor, rid, payload["action"])
        elif target_agent:
            disabled_key = digest([actor.tenant_id, actor.principal_ref, target_agent])
            _, disabled_version = tx.get("disabled_agents", disabled_key)
            tx.put("disabled_agents", disabled_key, {"revoked": True, "simulation": True}, disabled_version)
            data = {"agent_id": target_agent, "revoked": True, "simulation": True}
        elif target_id:
            target["revoked"] = True
            tx.put("identities", target_id, target, target_version)
            data = {"identity_id": target_id, "revoked": True, "simulation": True}
        else:
            events = {"approvals": "approve_submission", "submission": "submit_formation",
                      "simulate-formation": "formation_confirmed", "payment-submission": "submit_payments",
                      "simulate-payment-approval": "payments_approved"}
            event_actor = Actor(actor.tenant_id, actor.principal_ref, "provider_fixture") if action.startswith("simulate-") else actor
            data = asdict(flow.transition(event_actor, rid, events[action], "sim:local_fixture"))
        if rid:
            value = {"record": asdict(flow.get(actor, rid)), "mandate_expires_at": expiry}
            version = tx.put("applications", rid, value, version)
            data["record_version"] = version
        receipt = {"id": str(uuid4()), "replayed": False, "result_is_historical": False,
                   "current_authorization_checked": True, "simulation": True}
        tx.put("requests", request_key, {"fingerprint": fingerprint, "data": data, "receipt": receipt}, 0)
        tx.event(now, "api_mutation", {"identity_id": identity["id"], "method": method, "path": path,
                                      "receipt_id": receipt["id"], "record_version": version, "simulation": True})
        return data, receipt

    @staticmethod
    def _scope(identity, scope):
        require(identity["role"] == "operator" or scope in identity["scopes"], "identity_scope_denied", 403)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-db", required=True)
    parser.add_argument("--credentials-file", required=True)
    parser.add_argument("--initialize", action="store_true", help="Create a new fixture store and credential file")
    parser.add_argument("--identity-ttl", type=int, default=3600, help="Fixture credential lifetime in seconds")
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()
    database, credentials = Path(args.state_db).resolve(), Path(args.credentials_file).resolve()
    repo = Path(__file__).resolve().parents[3]
    require(all(not p.is_relative_to(repo) for p in (database, credentials)), "private_files_outside_repo_required")
    if args.initialize:
        require(not database.exists() and not credentials.exists(), "refuse_overwrite", 409)
        require(args.identity_ttl > 0, "invalid_ttl")
    else:
        require(database.is_file() and credentials.is_file(), "initialize_required")
    api = DurableAPI(database)
    if args.initialize:
        tokens = {role: secrets.token_urlsafe(32) for role in ("agent", "operator")}
        expiry = time.time() + args.identity_ttl
        identities = {role: api.register_identity(token, Actor("simulation_tenant", "simulation_principal", role,
                      "simulation_agent" if role == "agent" else ""), expiry) for role, token in tokens.items()}
        fd = os.open(credentials, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as output:
            json.dump({"simulation": True, "tokens": tokens, "identities": identities,
                       "expires_at": expiry, "principal_ref": "simulation_principal", "agent_id": "simulation_agent"}, output)
    server = make_server(api, args.port)
    try:
        print(f"LOCAL SIMULATION ONLY http://127.0.0.1:{server.server_port}; no real providers", flush=True)
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
