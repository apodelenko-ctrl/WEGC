"""Contract and real loopback HTTP tests with synthetic credentials and data."""
import http.client
import json
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from lifecycle import Actor
from mock_http import APIError, MockAPI, decode_body, make_server

TOKENS = {
    "fixture-agent-token": Actor("a", "p", "agent", "bot"),
    "fixture-operator-token": Actor("a", "p", "operator"),
    "fixture-other-tenant": Actor("b", "p", "agent", "bot"),
    "fixture-other-principal": Actor("a", "q", "operator"),
    "fixture-other-agent": Actor("a", "p", "agent", "other-bot"),
}


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.api = MockAPI(TOKENS)
        _, result = self.request("POST", "/v1/applications", {"name": "SIMULATION", "principal_ref": "p"})
        self.rid = result["data"]["id"]
        self.base = "/v1/applications/" + self.rid

    def request(self, method, path, payload=None, role="agent", key="test-key"):
        token = "fixture-" + role + "-token"
        return self.api.call(method, path, "Bearer " + token, key, payload)

    def step(self, action, payload=None, role="operator", key="step-key"):
        return self.request("POST", self.base + "/" + action, payload or {}, role, key)

    def formed(self):
        for action in ("approvals", "submission", "simulate-formation"):
            self.assertEqual(self.step(action)[0], 200)

    def mandated(self):
        self.formed()
        self.assertEqual(self.step("mandates", {"agent_id": "bot", "scopes": ["read_documents"]})[0], 200)

    def test_capabilities_never_claim_production(self):
        self.assertFalse(self.api.call("GET", "/v1/capabilities")[1]["data"]["production"])

    def test_authentication_required(self):
        self.assertEqual(self.api.call("GET", self.base)[0], 401)

    def test_body_cannot_inject_role(self):
        self.assertEqual(self.step("approvals", {"role": "operator"}, "agent")[0], 422)

    def test_agent_cannot_self_approve(self):
        self.assertEqual(self.step("approvals", role="agent")[0], 403)

    def test_tenant_isolation(self):
        self.assertEqual(self.api.call("GET", self.base, "Bearer fixture-other-tenant")[0], 404)

    def test_principal_isolation(self):
        self.assertEqual(self.api.call("GET", self.base, "Bearer fixture-other-principal")[0], 404)

    def test_request_cannot_choose_another_principal(self):
        self.assertEqual(self.request("POST", "/v1/applications", {"name": "X", "principal_ref": "q"})[0], 403)

    def test_submitted_is_not_formed(self):
        self.step("approvals")
        _, result = self.step("submission", role="agent")
        self.assertEqual(result["data"]["formation"], "submitted")
        self.assertEqual(result["data"]["payments"], "not_requested")

    def test_agent_cannot_forge_provider_event(self):
        self.assertEqual(self.step("simulate-formation", role="agent")[0], 403)

    def test_separate_payment_approval(self):
        self.formed()
        self.assertEqual(self.step("simulate-payment-approval")[0], 409)
        self.assertEqual(self.step("payment-submission", role="agent")[0], 403)
        self.step("payment-submission")
        self.assertEqual(self.step("simulate-payment-approval")[1]["data"]["payments"], "approved")

    def test_idempotency_returns_same_application(self):
        result = self.request("POST", "/v1/applications", {"name": "SIMULATION", "principal_ref": "p"})
        self.assertEqual(result[1]["data"]["id"], self.rid)
        self.assertEqual(len(self.api.audit), 1)

    def test_idempotency_payload_conflict(self):
        self.assertEqual(self.request("POST", "/v1/applications", {"name": "OTHER", "principal_ref": "p"})[0], 409)

    def test_repeated_transition_is_idempotent(self):
        first = self.step("approvals")
        self.assertEqual(first, self.step("approvals"))

    def test_missing_idempotency_key(self):
        self.assertEqual(self.step("approvals", key="")[0], 400)

    def test_atomic_repeated_requests(self):
        def send(_):
            return self.request("POST", "/v1/applications", {"name": "CONCURRENT FIXTURE", "principal_ref": "p"}, key="parallel")
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(send, range(12)))
        self.assertEqual({r[0] for r in results}, {200})
        self.assertEqual(len({r[1]["data"]["id"] for r in results}), 1)

    def test_revocation_denies_even_cached_operation(self):
        self.mandated()
        self.assertEqual(self.step("operations", {"action": "read_documents"}, "agent")[0], 200)
        self.step("revocation")
        self.assertEqual(self.step("operations", {"action": "read_documents"}, "agent")[0], 403)

    def test_cached_grant_does_not_reactivate_mandate(self):
        self.mandated()
        self.step("revocation")
        self.step("mandates", {"agent_id": "bot", "scopes": ["read_documents"]})
        self.assertEqual(self.request("GET", self.base)[1]["data"]["mandate"], "revoked")

    def test_different_agent_cannot_use_mandate(self):
        self.mandated()
        self.assertEqual(self.api.call("POST", self.base + "/operations", "Bearer fixture-other-agent", "op", {"action": "read_documents"})[0], 403)

    def test_unknown_scope_denied(self):
        self.formed()
        self.assertEqual(self.step("mandates", {"agent_id": "bot", "scopes": ["move_money"]})[0], 409)

    def test_invalid_scope_shape_is_stable_error(self):
        self.formed()
        self.assertEqual(self.step("mandates", {"agent_id": "bot", "scopes": [["nested"]]})[0], 422)

    def test_route_and_object_not_found(self):
        self.assertEqual(self.request("GET", "/unknown")[0], 404)
        self.assertEqual(self.request("GET", "/v1/applications/deadbeef")[0], 404)

    def test_no_secrets_in_audit(self):
        self.step("approvals")
        text = json.dumps(self.api.audit)
        self.assertNotIn("token", text)
        self.assertNotIn("Authorization", text)

    def test_no_real_provider_role_over_http(self):
        with self.assertRaises(APIError):
            MockAPI({"fixture": Actor("a", "p", "provider_fixture")})

    def test_cannot_bind_public_address(self):
        with self.assertRaises(APIError):
            make_server(self.api, host="0.0.0.0")


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server(MockAPI(TOKENS))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def send(self, body, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        request_headers = {"Content-Type": "application/json", "Authorization": "Bearer fixture-agent-token", "Idempotency-Key": self.id()}
        request_headers.update(headers or {})
        try:
            connection.request("POST", "/v1/applications", body=body, headers=request_headers)
            response = connection.getresponse()
            return response.status, json.loads(response.read())
        finally:
            connection.close()

    def test_actual_http_request(self):
        status, body = self.send(json.dumps({"name": "HTTP FIXTURE", "principal_ref": "p"}))
        self.assertEqual(status, 200)
        self.assertTrue(body["simulation"])
        self.assertFalse(body["external_side_effect"])

    def test_invalid_json(self):
        self.assertEqual(self.send("{")[0], 400)

    def test_duplicate_json_keys(self):
        self.assertEqual(self.send('{"name":"a","name":"b","principal_ref":"p"}')[0], 400)

    def test_not_a_json_object(self):
        self.assertEqual(self.send("[]")[0], 422)

    def test_nan_not_permitted(self):
        self.assertEqual(self.send('{"name":NaN,"principal_ref":"p"}')[0], 400)

    def test_browser_origin_denied(self):
        self.assertEqual(self.send("{}", {"Origin": "https://untrusted.invalid"})[0], 403)

    def test_rebinding_host_denied(self):
        self.assertEqual(self.send("{}", {"Host": "untrusted.invalid"})[0], 400)

    def test_large_body_denied(self):
        self.assertEqual(self.send("x" * 16385)[0], 413)

    def test_wrong_content_type_denied(self):
        self.assertEqual(self.send("{}", {"Content-Type": "text/plain"})[0], 415)


if __name__ == "__main__":
    unittest.main()
