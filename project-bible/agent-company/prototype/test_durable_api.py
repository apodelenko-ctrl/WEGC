"""Persistence, restart, expiry, isolation and rollback tests. Synthetic data only."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
import http.client
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from durable_api import DurableAPI
from lifecycle import Actor
from mock_http import APIError, make_server
from sqlite_store import Store, VersionConflict


class DurableTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = str(Path(self.temp.name) / "fixture.sqlite")
        self.now = 1000.0  # Injected test clock, not a real business timestamp.
        self.api = DurableAPI(self.db, lambda: self.now)
        self.agent = Actor("fixture", "principal", "agent", "bot")
        self.owner = Actor("fixture", "principal", "operator")
        self.agent_id = self.api.register_identity("fixture-agent", self.agent, 5000)
        self.owner_id = self.api.register_identity("fixture-operator", self.owner, 5000)
        code, body = self.request("POST", "/v1/applications", {"name": "SIM ONLY", "principal_ref": "principal"})
        self.assertEqual(code, 200)
        self.rid = body["data"]["id"]
        self.base = "/v1/applications/" + self.rid

    def request(self, method, path, payload=None, role="agent", key="fixture-key", api=None):
        return (api or self.api).call(method, path, "Bearer fixture-" + role, key, payload)

    def step(self, action, payload=None, role="operator", key="step"):
        return self.request("POST", self.base + "/" + action, payload if payload is not None else {}, role, key)

    def formed(self):
        for action in ("approvals", "submission", "simulate-formation"):
            self.assertEqual(self.step(action)[0], 200)

    def grant(self, expiry=2000):
        self.formed()
        body = {"agent_id": "bot", "scopes": ["read_documents"], "expires_at": expiry}
        self.assertEqual(self.step("mandates", body)[0], 200)
        return body

    def op(self, key="op"):
        return self.step("operations", {"action": "read_documents"}, "agent", key)

    def test_replay_survives_new_instance(self):
        other = DurableAPI(self.db, lambda: self.now)
        code, body = self.request("POST", "/v1/applications", {"name": "SIM ONLY", "principal_ref": "principal"}, api=other)
        self.assertEqual(code, 200)
        self.assertEqual(body["data"]["id"], self.rid)
        self.assertTrue(body["receipt"]["replayed"])
        with other.store.transaction() as tx:
            self.assertEqual(len(tx.scan("applications")), 1)

    def test_replay_from_separate_process(self):
        code = """import json,sys
from durable_api import DurableAPI
api=DurableAPI(sys.argv[1],lambda:1000)
print(json.dumps(api.call('POST','/v1/applications','Bearer fixture-agent','fixture-key',{'name':'SIM ONLY','principal_ref':'principal'})))
"""
        run = subprocess.run([sys.executable, "-c", code, self.db], cwd=Path(__file__).parent,
                             capture_output=True, text=True, timeout=10)
        self.assertEqual(run.returncode, 0, run.stderr)
        status, response = json.loads(run.stdout)
        self.assertEqual(status, 200)
        self.assertEqual(response["data"]["id"], self.rid)
        self.assertTrue(response["receipt"]["replayed"])

    def test_simultaneous_independent_instances(self):
        apis = [DurableAPI(self.db, lambda: self.now) for _ in range(4)]
        def send(i):
            return self.request("POST", "/v1/applications", {"name": "CONCURRENT", "principal_ref": "principal"}, key="parallel", api=apis[i % 4])
        with ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(send, range(16)))
        self.assertEqual({r[0] for r in results}, {200})
        self.assertEqual(len({r[1]["data"]["id"] for r in results}), 1)
        self.assertEqual(sum(not r[1]["receipt"]["replayed"] for r in results), 1)

    def test_changed_payload_same_key_conflicts_after_restart(self):
        other = DurableAPI(self.db, lambda: self.now)
        self.assertEqual(self.request("POST", "/v1/applications", {"name": "CHANGED", "principal_ref": "principal"}, api=other)[0], 409)

    def test_versions_reject_stale_write(self):
        version = self.request("GET", self.base)[1]["data"]["record_version"]
        first = self.step("approvals", {"expected_version": version})
        self.assertEqual(first[0], 200)
        self.assertEqual(first[1]["data"]["record_version"], version + 1)
        self.assertEqual(self.step("submission", {"expected_version": version}, "agent")[0], 409)

    def test_replay_does_not_increment_version(self):
        first = self.step("approvals")
        second = self.step("approvals")
        self.assertEqual(first[1]["data"]["record_version"], second[1]["data"]["record_version"])
        self.assertEqual(first[1]["receipt"]["id"], second[1]["receipt"]["id"])
        self.assertTrue(second[1]["receipt"]["result_is_historical"])

    def test_failure_before_commit_rolls_back_state_receipt_and_audit(self):
        with self.api.store.transaction() as tx:
            events = tx.connection.execute("SELECT count(*) FROM events").fetchone()[0]
        def fail():
            raise RuntimeError("injected_local_crash")
        self.api.store.before_commit = fail
        with self.assertRaises(RuntimeError):
            self.step("approvals")
        self.api.store.before_commit = None
        self.assertEqual(self.request("GET", self.base)[1]["data"]["state"], "review_required")
        with self.api.store.transaction() as tx:
            self.assertEqual(tx.connection.execute("SELECT count(*) FROM events").fetchone()[0], events)
        retry = self.step("approvals")
        self.assertEqual(retry[0], 200)
        self.assertFalse(retry[1]["receipt"]["replayed"])

    def test_process_exit_before_commit_is_recoverable(self):
        code = """import os,sys
from durable_api import DurableAPI
api=DurableAPI(sys.argv[1],lambda:1000)
api.store.before_commit=lambda:os._exit(7)
api.call('POST',sys.argv[2]+'/approvals','Bearer fixture-operator','crash',{})
"""
        run = subprocess.run([sys.executable, "-c", code, self.db, self.base], cwd=Path(__file__).parent,
                             capture_output=True, timeout=10)
        self.assertEqual(run.returncode, 7)
        self.assertEqual(self.request("GET", self.base)[1]["data"]["state"], "review_required")
        self.assertFalse(self.step("approvals", key="crash")[1]["receipt"]["replayed"])

    def test_backup_restores_snapshot(self):
        self.formed()
        backup = self.api.store.backup(Path(self.temp.name) / "backup.sqlite")
        restored = DurableAPI(backup, lambda: self.now)
        self.assertEqual(self.request("GET", self.base, api=restored)[1]["data"]["formation"], "formed")
        with self.assertRaises(FileExistsError):
            self.api.store.backup(backup)

    def test_identity_expiry_blocks_reads_writes_and_replays(self):
        self.now = 5000
        self.assertEqual(self.request("GET", self.base)[0], 401)
        self.assertEqual(self.request("POST", "/v1/applications", {"name": "SIM ONLY", "principal_ref": "principal"})[0], 401)
        self.assertEqual(self.step("approvals")[0], 401)

    def test_revoked_identity_blocks_all_its_routes_after_restart(self):
        result = self.request("POST", f"/v1/identities/{self.agent_id}/revocation", {}, "operator")
        self.assertEqual(result[0], 200)
        self.api = DurableAPI(self.db, lambda: self.now)
        self.assertEqual(self.request("GET", self.base)[0], 401)
        self.assertEqual(self.step("submission", role="agent")[0], 401)
        self.assertEqual(self.request("POST", "/v1/applications", {"name": "SIM ONLY", "principal_ref": "principal"})[0], 401)
        with self.assertRaises(APIError):
            self.api.register_identity("fixture-agent", self.agent, 5000)

    def test_global_agent_revoke_blocks_rotated_tokens(self):
        self.api.register_identity("fixture-rotated", self.agent, 5000)
        self.assertEqual(self.request("POST", "/v1/agents/bot/revocation", {}, "operator")[0], 200)
        for role in ("agent", "rotated"):
            self.assertEqual(self.request("GET", self.base, role=role)[0], 401)
        with self.assertRaises(APIError):
            self.api.register_identity("fixture-new", self.agent, 5000)
        self.assertEqual(self.request("GET", self.base, role="operator")[0], 200)

    def test_global_revoke_is_visible_in_mandate_status(self):
        self.grant()
        self.request("POST", "/v1/agents/bot/revocation", {}, "operator")
        self.assertFalse(self.request("GET", self.base, role="operator")[1]["data"]["mandate_effective"])

    def test_agent_cannot_revoke_identity(self):
        self.assertEqual(self.request("POST", f"/v1/identities/{self.owner_id}/revocation", {})[0], 403)

    def test_cross_tenant_reads_and_revoke_are_hidden(self):
        self.api.register_identity("fixture-other", Actor("other", "principal", "operator"), 5000)
        self.assertEqual(self.request("GET", self.base, role="other")[0], 404)
        self.assertEqual(self.request("POST", f"/v1/identities/{self.agent_id}/revocation", {}, "other")[0], 404)

    def test_application_scoped_identity_cannot_see_other_application(self):
        self.api.register_identity("fixture-scoped", self.agent, 5000, applications=[self.rid])
        other = self.request("POST", "/v1/applications", {"name": "SECOND", "principal_ref": "principal"}, key="other")[1]["data"]["id"]
        self.assertEqual(self.request("GET", self.base, role="scoped")[0], 200)
        self.assertEqual(self.request("GET", "/v1/applications/" + other, role="scoped")[0], 404)
        self.assertEqual(self.request("POST", "/v1/applications", {"name": "NEW", "principal_ref": "principal"}, role="scoped")[0], 403)

    def test_scoped_operator_cannot_revoke_tenant_wide_identity(self):
        self.api.register_identity("fixture-scoped-owner", self.owner, 5000, applications=[self.rid])
        self.assertEqual(self.request("POST", f"/v1/identities/{self.agent_id}/revocation", {}, "scoped-owner")[0], 403)

    def test_identity_action_scope_is_enforced(self):
        self.api.register_identity("fixture-readonly", self.agent, 5000, scopes=["read_application"])
        self.assertEqual(self.request("GET", self.base, role="readonly")[0], 200)
        self.assertEqual(self.step("submission", role="readonly")[0], 403)

    def test_mandate_expires_at_exact_boundary(self):
        self.grant(1100)
        self.assertEqual(self.op()[0], 200)
        self.now = 1100
        self.assertEqual(self.op()[0], 403)
        self.assertEqual(self.op("different-key")[0], 403)
        self.assertFalse(self.request("GET", self.base)[1]["data"]["mandate_effective"])

    def test_replay_grant_does_not_reactivate_revoked_mandate(self):
        payload = self.grant()
        self.step("revocation")
        repeated = self.step("mandates", payload)
        self.assertTrue(repeated[1]["receipt"]["result_is_historical"])
        self.assertEqual(self.op()[0], 403)
        self.assertEqual(self.request("GET", self.base)[1]["data"]["mandate"], "revoked")

    def test_mandate_expiry_is_in_idempotency_fingerprint(self):
        payload = self.grant()
        payload["expires_at"] = 2200
        self.assertEqual(self.step("mandates", payload)[0], 409)

    def test_revoked_operation_replay_does_not_return_success(self):
        self.grant()
        self.assertEqual(self.op()[0], 200)
        self.step("revocation")
        self.assertEqual(self.op()[0], 403)

    def test_no_mandate_cross_application(self):
        self.grant()
        other = self.request("POST", "/v1/applications", {"name": "SECOND", "principal_ref": "principal"}, key="second")[1]["data"]["id"]
        self.assertEqual(self.request("POST", "/v1/applications/" + other + "/operations", {"action": "read_documents"})[0], 403)

    def test_invalid_expiry_and_extra_roles_fail(self):
        self.formed()
        for value in (True, float("inf"), "tomorrow", 999):
            payload = {"agent_id": "bot", "scopes": ["read_documents"], "expires_at": value}
            self.assertEqual(self.step("mandates", payload)[0], 422)
        self.assertEqual(self.step("approvals", {"role": "operator"}, "agent")[0], 422)

    def test_unknown_monetary_scope_is_not_supported(self):
        self.formed()
        self.assertEqual(self.step("mandates", {"agent_id": "bot", "scopes": ["move_money"], "expires_at": 2000})[0], 409)

    def test_no_plaintext_credentials_in_store(self):
        with self.api.store.transaction() as tx:
            text = json.dumps(tx.connection.execute("SELECT namespace,key,body FROM objects").fetchall())
            text += json.dumps(tx.connection.execute("SELECT body FROM events").fetchall())
        self.assertNotIn("fixture-agent", text)
        self.assertNotIn("fixture-operator", text)
        self.assertNotIn("Bearer", text)

    def test_capabilities_do_not_claim_production(self):
        data = self.api.call("GET", "/v1/capabilities")[1]["data"]
        self.assertFalse(data["production"])
        self.assertIn("sqlite_state", data["implemented"])

    def test_store_version_compare_and_swap(self):
        with self.api.store.transaction() as tx:
            self.assertEqual(tx.put("fixture", "x", {"a": 1}, 0), 1)
            with self.assertRaises(VersionConflict):
                tx.put("fixture", "x", {"a": 2}, 0)

    def test_unknown_schema_is_refused(self):
        other = str(Path(self.temp.name) / "alien.sqlite")
        connection = sqlite3.connect(other)
        connection.execute("CREATE TABLE alien(x)")
        connection.close()
        with self.assertRaises(ValueError):
            Store(other)

    def test_loopback_transport_works_with_durable_adapter(self):
        server = make_server(self.api)
        thread = threading.Thread(target=server.serve_forever)
        thread.start()
        try:
            connection = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=3)
            connection.request("GET", self.base, headers={"Authorization": "Bearer fixture-agent"})
            response = connection.getresponse()
            self.assertEqual(response.status, 200)
            self.assertEqual(json.loads(response.read())["data"]["id"], self.rid)
            connection.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)
            self.assertFalse(thread.is_alive())


if __name__ == "__main__":
    unittest.main()
