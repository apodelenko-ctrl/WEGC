#!/usr/bin/env python3
"""Summarize evidence-backed expo gates; no service calls or production writes."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

REQUIRED = {f'EXPO-{i:02d}' for i in range(1, 13)}
ACCEPTED = {'passed_live', 'accepted_receipt', 'passed_artifact'}
ALLOWED = ACCEPTED | {'partial', 'blocked', 'not_run', 'prepared', 'deferred'}

def date(value):
    result = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if result.tzinfo is None:
        raise ValueError('Evidence time must include timezone')
    return result

def assess(document, now):
    gates = document['gates']
    ids = [g['id'] for g in gates]
    if len(ids) != len(set(ids)) or set(ids) != REQUIRED:
        raise ValueError('All twelve unique expo gates are required')
    if now.tzinfo is None:
        raise ValueError('Assessment time must include timezone')
    results = []
    for gate in gates:
        state = gate['status']
        if state not in ALLOWED:
            raise ValueError('Unknown status for ' + gate['id'])
        accepted = state in ACCEPTED
        reason = ''
        if accepted:
            if not gate.get('evidence') or not gate.get('checked_at'):
                raise ValueError('Accepted gate requires evidence and checked_at: ' + gate['id'])
            checked = date(gate['checked_at'])
            if checked > now:
                raise ValueError('Future evidence: ' + gate['id'])
            if gate.get('valid_until') and date(gate['valid_until']) < now:
                accepted, reason = False, 'evidence_expired'
        results.append({'id': gate['id'], 'accepted': accepted, 'status': state,
                        'reason': reason, 'owner': gate['owner'], 'next_action': gate['next_action']})
    missing = [r['id'] for r in results if not r['accepted']]
    return {'assessed_at': now.isoformat(), 'ready': not missing,
            'accepted_gates': len(results) - len(missing), 'total_gates': len(results),
            'open_gates': missing, 'gates': results}

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('evidence', type=Path)
    p.add_argument('--at', help='ISO timestamp with timezone; defaults to now')
    p.add_argument('--out', type=Path)
    a = p.parse_args()
    result = assess(json.loads(a.evidence.read_text()), date(a.at) if a.at else datetime.now(timezone.utc))
    body = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if a.out:
        a.out.write_text(body)
    print(body)
