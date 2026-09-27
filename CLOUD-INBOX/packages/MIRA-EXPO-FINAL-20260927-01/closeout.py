#!/usr/bin/env python3
"""Compute a fail-closed MIRA exhibition closeout from public evidence only."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ACCEPTED = {"passed_live", "accepted_receipt", "passed_artifact", "accepted_live"}
PUBLIC_REQUIRED = {"EXPO-01", "EXPO-03", "EXPO-04", "EXPO-11"}
AUTONOMY_REQUIRED = {"EXPO-05", "EXPO-06", "EXPO-07", "EXPO-08", "EXPO-09", "EXPO-10", "EXPO-12"}
COMMERCIAL_REQUIRED = {"EXPO-08", "EXPO-09", "EXPO-12"}


def evaluate(data: dict) -> dict:
    gates = data.get("gates")
    if not isinstance(gates, list):
        raise ValueError("gates must be a list")

    status_by_id: dict[str, str] = {}
    for gate in gates:
        gate_id = gate.get("id")
        status = gate.get("status")
        if not isinstance(gate_id, str) or not isinstance(status, str):
            raise ValueError("every gate requires string id and status")
        if gate_id in status_by_id:
            raise ValueError(f"duplicate gate: {gate_id}")
        status_by_id[gate_id] = status

    expected = {f"EXPO-{number:02d}" for number in range(1, 13)}
    missing_ids = sorted(expected - status_by_id.keys())
    unknown_ids = sorted(status_by_id.keys() - expected)
    if missing_ids or unknown_ids:
        raise ValueError(f"gate set mismatch: missing={missing_ids}, unknown={unknown_ids}")

    accepted_ids = sorted(gate_id for gate_id, status in status_by_id.items() if status in ACCEPTED)
    open_ids = sorted(expected - set(accepted_ids))
    route = data.get("route_check", {})
    route_safe = (
        route.get("status") == "PASS"
        and route.get("passed") == route.get("total")
        and route.get("total") == 9
        and route.get("new_requests_created") == 0
        and route.get("emails_sent") == 0
    )

    def all_accepted(required: set[str]) -> bool:
        return required.issubset(accepted_ids)

    public_go = route_safe and all_accepted(PUBLIC_REQUIRED)
    commercial_go = all_accepted(COMMERCIAL_REQUIRED)
    autonomy_go = all_accepted(AUTONOMY_REQUIRED)
    full_go = len(accepted_ids) == 12 and route_safe

    return {
        "assessed_at": data.get("assessed_at"),
        "source_main_sha": data.get("source_main_sha"),
        "source_research_sha": data.get("source_research_sha"),
        "accepted_gates": len(accepted_ids),
        "total_gates": 12,
        "accepted_gate_ids": accepted_ids,
        "open_gate_ids": open_ids,
        "verdicts": {
            "public_discovery_and_intake": "GO" if public_go else "NO_GO",
            "commercial_transaction": "GO" if commercial_go else "NO_GO",
            "autonomous_operation": "GO" if autonomy_go else "NO_GO",
            "full_exhibition_launch": "GO" if full_go else "NO_GO",
        },
        "route_check": {
            "status": route.get("status"),
            "passed": route.get("passed"),
            "total": route.get("total"),
            "safe_get_only": route_safe,
        },
        "counts": data.get("counts", {}),
        "limitations": data.get("limitations", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    result = evaluate(json.loads(args.input.read_text(encoding="utf-8")))
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
