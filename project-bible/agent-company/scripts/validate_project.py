"""Validate this project library and its task queue. No network or credentials."""
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]


def run() -> dict:
    errors = []
    queue = json.loads((ROOT / "agents/QUEUE.json").read_text(encoding="utf-8"))
    roles = json.loads((ROOT / "agents/ROLES.json").read_text(encoding="utf-8"))["roles"]
    tasks = queue["tasks"]
    by_id = {t["id"]: t for t in tasks}
    if len(by_id) != len(tasks):
        errors.append("duplicate task IDs")
    role_ids = {r["id"] for r in roles}

    def exists(path):
        target = (ROOT / path).resolve()
        return target.is_relative_to(ROOT) and target.is_file()

    for role in roles:
        if not exists(role["prompt"]):
            errors.append(f"missing role prompt: {role['id']}")
    for task in tasks:
        tid = task["id"]
        if task["assigned_role"] not in role_ids:
            errors.append(f"unknown role: {tid}")
        if task["status"] not in {"ready", "blocked", "in_progress", "done"}:
            errors.append(f"unknown status: {tid}")
        if not task.get("acceptance"):
            errors.append(f"missing acceptance criteria: {tid}")
        for dep in task["depends_on"]:
            if dep not in by_id:
                errors.append(f"unknown dependency: {tid}/{dep}")
            elif task["status"] in {"ready", "done"} and by_id[dep]["status"] != "done":
                errors.append(f"incomplete dependency: {tid}/{dep}")
        if task["status"] == "done":
            if not task.get("completed_by") or not task.get("evidence_paths"):
                errors.append(f"missing completion evidence: {tid}")
            for path in task.get("evidence_paths", []):
                if not exists(path):
                    errors.append(f"missing evidence: {tid}/{path}")
        if task["status"] == "blocked" and not task.get("blocker"):
            errors.append(f"missing blocker: {tid}")

    visited, stack = set(), set()

    def visit(tid):
        if tid in stack:
            errors.append(f"dependency cycle: {tid}")
            return
        if tid in visited or tid not in by_id:
            return
        stack.add(tid)
        for dep in by_id[tid]["depends_on"]:
            visit(dep)
        stack.remove(tid)
        visited.add(tid)

    for tid in by_id:
        visit(tid)
    source_text = (ROOT / "SOURCES.md").read_text(encoding="utf-8")
    sources = set(re.findall(r"^## (S\d+)$", source_text, re.MULTILINE))
    for path in ROOT.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for ref in re.findall(r"\[(S\d+)\]", text):
            if ref not in sources:
                errors.append(f"unknown source: {path.relative_to(ROOT)}/{ref}")
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
            if "://" in link or link.startswith(("#", "mailto:")):
                continue
            target = (path.parent / unquote(link.split("#", 1)[0])).resolve()
            if not target.is_relative_to(ROOT) or not target.is_file():
                errors.append(f"broken local link: {path.relative_to(ROOT)}/{link}")
    counts = {state: sum(t["status"] == state for t in tasks)
              for state in ("done", "ready", "blocked", "in_progress")}
    return {"result": "passed" if not errors else "failed",
            "tasks": len(tasks), "task_counts": counts, "roles": len(roles),
            "sources": len(sources), "errors": errors,
            "scope": "library structure only; not legal or production approval"}


if __name__ == "__main__":
    result = run()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["result"] == "passed" else 1)
