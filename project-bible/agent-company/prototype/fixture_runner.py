"""Bounded local fixture runner. No LLM, shell, external tools or production work."""
from dataclasses import dataclass
import json
import math
from pathlib import Path
import re
import tempfile
import time
from uuid import uuid4
from sqlite_store import Store, canonical, digest


class RunnerError(Exception):
    pass


def ensure(condition, code):
    if not condition:
        raise RunnerError(code)


def positive(value):
    return type(value) in (int, float) and math.isfinite(value) and value > 0


def identifier(value):
    return isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", value)


@dataclass(frozen=True)
class Lease:
    task_id: str
    attempt_id: str
    worker_id: str
    fencing_token: int
    input_revision: str
    kind: str
    payload: dict


def fixture_result(kind, payload):
    """Allowlist of deterministic test functions, not a plugin/command executor."""
    ensure(kind in {"fixture.echo", "fixture.count"}, "unsupported_fixture")
    ensure(isinstance(payload, dict) and len(canonical(payload)) <= 16384, "invalid_fixture_payload")
    if kind == "fixture.echo":
        ensure(set(payload) == {"text"} and isinstance(payload["text"], str), "invalid_fixture_payload")
        data = {"text": payload["text"]}
    else:
        ensure(set(payload) == {"items"} and isinstance(payload["items"], list)
               and all(isinstance(x, str) for x in payload["items"]), "invalid_fixture_payload")
        data = {"item_count": len(payload["items"])}
    return {"fixture": True, "simulation": True, "external_actions": [], "data": data}


class FixtureRunner:
    def __init__(self, database, clock=time.time):
        self.store, self.clock = Store(database), clock

    def enqueue(self, task_id, kind, payload, input_revision, dependencies=(), max_attempts=3):
        ensure(identifier(task_id), "invalid_task_id")
        ensure(isinstance(input_revision, str) and re.fullmatch(r"[a-f0-9]{40}", input_revision), "input_commit_required")
        ensure(type(max_attempts) is int and max_attempts > 0, "invalid_attempt_limit")
        ensure(isinstance(dependencies, (list, tuple)) and all(identifier(d) for d in dependencies), "invalid_dependencies")
        ensure(task_id not in dependencies, "self_dependency")
        fixture_result(kind, payload)  # Validate and reject arbitrary executable work.
        specification = {"kind": kind, "payload": payload, "input_revision": input_revision,
                         "dependencies": sorted(set(dependencies)), "max_attempts": max_attempts}
        with self.store.transaction() as tx:
            old, _ = tx.get("runner_tasks", task_id)
            if old:
                ensure(old["spec_hash"] == digest(specification), "task_spec_conflict")
                return old
            for dependency in specification["dependencies"]:
                ensure(tx.get("runner_tasks", dependency)[0] is not None, "unknown_dependency")
            task = {"id": task_id, **specification, "spec_hash": digest(specification),
                    "status": "ready", "attempts": 0, "fencing_token": 0,
                    "attempt_id": None, "worker_id": None, "lease_expires_at": None,
                    "receipt": None, "simulation": True}
            tx.put("runner_tasks", task_id, task, 0)
            tx.event(self.clock(), "fixture_task_enqueued", {"task_id": task_id})
            return task

    def claim(self, worker_id, lease_seconds):
        ensure(identifier(worker_id) and positive(lease_seconds), "invalid_lease")
        now = self.clock()
        with self.store.transaction() as tx:
            for task_id, task, version in tx.scan("runner_tasks"):
                if task["status"] == "leased" and now >= task["lease_expires_at"]:
                    attempt, av = tx.get("runner_attempts", task["attempt_id"])
                    attempt.update(status="expired", ended_at=now)
                    tx.put("runner_attempts", task["attempt_id"], attempt, av)
                    task["status"] = "ready" if task["attempts"] < task["max_attempts"] else "failed"
                    version = tx.put("runner_tasks", task_id, task, version)
                    tx.event(now, "fixture_lease_expired", {"task_id": task_id, "attempt_id": task["attempt_id"]})
                if task["status"] != "ready":
                    continue
                if not all(tx.get("runner_tasks", dep)[0]["status"] == "done" for dep in task["dependencies"]):
                    continue
                attempt_id = str(uuid4())
                task.update(status="leased", attempts=task["attempts"] + 1,
                            fencing_token=task["fencing_token"] + 1, attempt_id=attempt_id,
                            worker_id=worker_id, lease_expires_at=now + lease_seconds)
                attempt = {"task_id": task_id, "attempt_id": attempt_id, "worker_id": worker_id,
                           "fencing_token": task["fencing_token"], "input_revision": task["input_revision"],
                           "status": "leased", "started_at": now, "heartbeat_at": now, "simulation": True}
                tx.put("runner_attempts", attempt_id, attempt, 0)
                tx.put("runner_tasks", task_id, task, version)
                tx.event(now, "fixture_task_claimed", attempt)
                return Lease(task_id, attempt_id, worker_id, task["fencing_token"],
                             task["input_revision"], task["kind"], task["payload"])
        return None

    @staticmethod
    def _check(task, lease, now):
        ensure(task is not None, "unknown_task")
        ensure((task["attempt_id"], task["worker_id"], task["fencing_token"], task["input_revision"])
               == (lease.attempt_id, lease.worker_id, lease.fencing_token, lease.input_revision), "stale_attempt")
        ensure(task["status"] == "leased" and now < task["lease_expires_at"], "lease_inactive")

    def heartbeat(self, lease, lease_seconds):
        ensure(positive(lease_seconds), "invalid_lease")
        now = self.clock()
        with self.store.transaction() as tx:
            task, version = tx.get("runner_tasks", lease.task_id)
            self._check(task, lease, now)
            task["lease_expires_at"] = max(task["lease_expires_at"], now + lease_seconds)
            attempt, av = tx.get("runner_attempts", lease.attempt_id)
            attempt["heartbeat_at"] = now
            tx.put("runner_attempts", lease.attempt_id, attempt, av)
            tx.put("runner_tasks", lease.task_id, task, version)
            tx.event(now, "fixture_heartbeat", {"attempt_id": lease.attempt_id})

    def complete(self, lease, result):
        now = self.clock()
        with self.store.transaction() as tx:
            task, version = tx.get("runner_tasks", lease.task_id)
            ensure(task is not None, "unknown_task")
            if task["status"] == "done" and task["receipt"]["attempt_id"] == lease.attempt_id:
                ensure(task["worker_id"] == lease.worker_id and task["fencing_token"] == lease.fencing_token
                       and task["input_revision"] == lease.input_revision, "stale_attempt")
                ensure(task["receipt"]["result_hash"] == digest(result), "result_conflict")
                return task["receipt"]
            self._check(task, lease, now)
            ensure(result == fixture_result(task["kind"], task["payload"]), "fixture_result_not_validated")
            receipt = {"id": str(uuid4()), "task_id": lease.task_id, "attempt_id": lease.attempt_id,
                       "worker_id": lease.worker_id, "fencing_token": lease.fencing_token,
                       "input_revision": task["input_revision"], "result_hash": digest(result),
                       "result": result, "completed_at": now, "fixture_only": True,
                       "validated_by": "deterministic_fixture_checker", "independent_review": False}
            task.update(status="done", receipt=receipt)
            attempt, av = tx.get("runner_attempts", lease.attempt_id)
            attempt.update(status="done", ended_at=now, receipt_id=receipt["id"])
            tx.put("runner_attempts", lease.attempt_id, attempt, av)
            tx.put("runner_tasks", lease.task_id, task, version)
            tx.event(now, "fixture_task_completed", {"task_id": lease.task_id, "receipt_id": receipt["id"]})
            return receipt

    def fail(self, lease, error_code):
        ensure(identifier(error_code), "invalid_error_code")
        now = self.clock()
        with self.store.transaction() as tx:
            task, version = tx.get("runner_tasks", lease.task_id)
            self._check(task, lease, now)
            attempt, av = tx.get("runner_attempts", lease.attempt_id)
            attempt.update(status="failed", ended_at=now, error_code=error_code)
            task["status"] = "ready" if task["attempts"] < task["max_attempts"] else "failed"
            tx.put("runner_attempts", lease.attempt_id, attempt, av)
            tx.put("runner_tasks", lease.task_id, task, version)
            tx.event(now, "fixture_task_failed", {"task_id": lease.task_id, "error_code": error_code})

    def get(self, task_id):
        with self.store.transaction() as tx:
            task, _ = tx.get("runner_tasks", task_id)
            ensure(task is not None, "unknown_task")
            return task

    def run_bounded(self, worker_id, max_tasks, lease_seconds=30):
        ensure(type(max_tasks) is int and max_tasks > 0, "invalid_run_bound")
        receipts = []
        for _ in range(max_tasks):
            lease = self.claim(worker_id, lease_seconds)
            if lease is None:
                break
            receipts.append(self.complete(lease, fixture_result(lease.kind, lease.payload)))
        return receipts


def demo():
    with tempfile.TemporaryDirectory(prefix="aci-fixture-runner-") as directory:
        runner = FixtureRunner(Path(directory) / "runner.sqlite")
        revision = "0" * 40  # Explicit fixture revision; NOT a real GitHub commit.
        runner.enqueue("fixture-first", "fixture.echo", {"text": "SIMULATION"}, revision)
        runner.enqueue("fixture-second", "fixture.count", {"items": ["fixture"]}, revision, ["fixture-first"])
        print(json.dumps({"simulation": True, "llm_workers_started": False,
                          "receipts": runner.run_bounded("fixture-worker", max_tasks=2)}, indent=2))


if __name__ == "__main__":
    demo()
