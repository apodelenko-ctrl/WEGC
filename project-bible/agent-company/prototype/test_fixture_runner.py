"""Local queue tests, never claims independently reviewed or real LLM work."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from fixture_runner import FixtureRunner, RunnerError, fixture_result

BASE_REVISION = "6f5740942a9aa65395930989967baf392d85385b"


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "runner.sqlite"
        self.now = 1000.0
        self.runner = FixtureRunner(self.path, lambda: self.now)

    def enqueue(self, name="fixture-task", dependencies=(), max_attempts=3):
        return self.runner.enqueue(name, "fixture.count", {"items": ["a", "b"]}, BASE_REVISION, dependencies, max_attempts)

    def test_fixture_worker_finishes_and_receipt_survives_restart(self):
        self.enqueue()
        receipts = self.runner.run_bounded("fixture-worker", 1)
        self.assertEqual(len(receipts), 1)
        self.assertFalse(receipts[0]["independent_review"])
        other = FixtureRunner(self.path, lambda: self.now)
        self.assertEqual(other.get("fixture-task")["receipt"], receipts[0])
        self.assertEqual(other.get("fixture-task")["status"], "done")

    def test_enqueue_is_idempotent_and_rejects_changed_spec(self):
        self.assertEqual(self.enqueue(), self.enqueue())
        with self.assertRaisesRegex(RunnerError, "task_spec_conflict"):
            self.runner.enqueue("fixture-task", "fixture.echo", {"text": "changed"}, BASE_REVISION)

    def test_dependency_runs_first(self):
        self.enqueue("z-parent")
        self.enqueue("a-child", ["z-parent"])
        receipts = self.runner.run_bounded("fixture-worker", 3)
        self.assertEqual([r["task_id"] for r in receipts], ["z-parent", "a-child"])

    def test_unknown_and_self_dependency_rejected(self):
        with self.assertRaisesRegex(RunnerError, "unknown_dependency"):
            self.enqueue(dependencies=["unknown"])
        with self.assertRaisesRegex(RunnerError, "self_dependency"):
            self.enqueue(dependencies=["fixture-task"])

    def test_parallel_claim_only_one_owner(self):
        self.enqueue()
        runners = [FixtureRunner(self.path, lambda: self.now) for _ in range(4)]
        with ThreadPoolExecutor(max_workers=4) as pool:
            leases = list(pool.map(lambda i: runners[i].claim(f"worker-{i}", 10), range(4)))
        self.assertEqual(sum(lease is not None for lease in leases), 1)

    def test_expired_lease_reclaims_with_new_fence(self):
        self.enqueue()
        first = self.runner.claim("old", 10)
        self.now = 1010
        other = FixtureRunner(self.path, lambda: self.now)
        second = other.claim("new", 10)
        self.assertGreater(second.fencing_token, first.fencing_token)
        self.assertNotEqual(second.attempt_id, first.attempt_id)
        with self.assertRaisesRegex(RunnerError, "stale_attempt"):
            self.runner.complete(first, fixture_result(first.kind, first.payload))
        self.assertTrue(other.complete(second, fixture_result(second.kind, second.payload))["fixture_only"])

    def test_expired_lease_rejects_completion_before_reclaim(self):
        self.enqueue()
        lease = self.runner.claim("worker", 10)
        self.now = 1010
        with self.assertRaisesRegex(RunnerError, "lease_inactive"):
            self.runner.complete(lease, fixture_result(lease.kind, lease.payload))

    def test_heartbeat_extends_lease(self):
        self.enqueue()
        lease = self.runner.claim("worker", 10)
        self.now = 1009
        self.runner.heartbeat(lease, 10)
        self.now = 1011
        self.assertIsNone(self.runner.claim("other", 10))
        self.runner.complete(lease, fixture_result(lease.kind, lease.payload))

    def test_late_heartbeat_cannot_revive_lease(self):
        self.enqueue()
        lease = self.runner.claim("worker", 10)
        self.now = 1010
        with self.assertRaises(RunnerError):
            self.runner.heartbeat(lease, 10)

    def test_worker_and_input_revision_cannot_be_replaced(self):
        self.enqueue()
        lease = self.runner.claim("worker", 10)
        for bad in (replace(lease, worker_id="other"), replace(lease, input_revision="f" * 40), replace(lease, fencing_token=99)):
            with self.assertRaisesRegex(RunnerError, "stale_attempt"):
                self.runner.complete(bad, fixture_result(lease.kind, lease.payload))

    def test_result_requires_fixture_validation(self):
        self.enqueue()
        lease = self.runner.claim("worker", 10)
        with self.assertRaisesRegex(RunnerError, "fixture_result_not_validated"):
            self.runner.complete(lease, {"done": True})
        self.assertEqual(self.runner.get("fixture-task")["status"], "leased")

    def test_completion_replay_returns_same_receipt(self):
        self.enqueue()
        lease = self.runner.claim("worker", 10)
        result = fixture_result(lease.kind, lease.payload)
        receipt = self.runner.complete(lease, result)
        self.now = 9999
        self.assertEqual(receipt, self.runner.complete(lease, result))
        with self.assertRaisesRegex(RunnerError, "result_conflict"):
            self.runner.complete(lease, {"changed": True})

    def test_fail_retries_then_stops(self):
        self.enqueue(max_attempts=2)
        first = self.runner.claim("worker", 10)
        self.runner.fail(first, "fixture_failure")
        second = self.runner.claim("worker", 10)
        self.runner.fail(second, "fixture_failure")
        self.assertEqual(self.runner.get("fixture-task")["status"], "failed")
        self.assertIsNone(self.runner.claim("worker", 10))

    def test_expired_last_attempt_stops(self):
        self.enqueue(max_attempts=1)
        self.runner.claim("worker", 10)
        self.now = 1010
        self.assertIsNone(self.runner.claim("other", 10))
        self.assertEqual(self.runner.get("fixture-task")["status"], "failed")

    def test_failed_dependency_does_not_run_child(self):
        self.enqueue("parent", max_attempts=1)
        self.enqueue("child", ["parent"])
        lease = self.runner.claim("worker", 10)
        self.runner.fail(lease, "fixture_failure")
        self.assertIsNone(self.runner.claim("other", 10))
        self.assertEqual(self.runner.get("child")["status"], "ready")

    def test_bounded_execution_stops_at_requested_count(self):
        for i in range(3):
            self.enqueue(f"task-{i}")
        self.assertEqual(len(self.runner.run_bounded("worker", 2)), 2)
        self.assertEqual(len(self.runner.run_bounded("worker", 2)), 1)

    def test_arbitrary_shell_and_unbounded_runs_rejected(self):
        with self.assertRaisesRegex(RunnerError, "unsupported_fixture"):
            self.runner.enqueue("evil", "shell", {"text": "not executed"}, BASE_REVISION)
        for n in (0, -1, True):
            with self.assertRaises(RunnerError):
                self.runner.run_bounded("worker", n)

    def test_attempt_history_keeps_expired_and_successful_attempts(self):
        self.enqueue()
        first = self.runner.claim("worker-1", 10)
        self.now = 1010
        second = self.runner.claim("worker-2", 10)
        self.runner.complete(second, fixture_result(second.kind, second.payload))
        with self.runner.store.transaction() as tx:
            self.assertEqual(tx.get("runner_attempts", first.attempt_id)[0]["status"], "expired")
            self.assertEqual(tx.get("runner_attempts", second.attempt_id)[0]["status"], "done")

    def test_failed_completion_transaction_can_be_retried(self):
        self.enqueue()
        lease = self.runner.claim("worker", 10)
        def fail():
            raise RuntimeError("injected_fixture_crash")
        self.runner.store.before_commit = fail
        with self.assertRaises(RuntimeError):
            self.runner.complete(lease, fixture_result(lease.kind, lease.payload))
        self.runner.store.before_commit = None
        self.assertEqual(self.runner.get("fixture-task")["status"], "leased")
        receipt = self.runner.complete(lease, fixture_result(lease.kind, lease.payload))
        self.assertTrue(receipt["fixture_only"])


if __name__ == "__main__":
    unittest.main()
