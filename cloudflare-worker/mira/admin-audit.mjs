import {ApiError} from './auth.mjs';
import {string} from './rules.mjs';
/**
 * Commit an administrative mutation and its immutable audit event together.
 * D1 batch is transactional; audit failure must never leave an unlogged grant.
 * No personal names, email addresses, documents or secrets go into the reason.
 * See https://developers.cloudflare.com/d1/worker-api/d1-database/#batch
 */
export async function auditedMutation(env, identity, mutation, {
  entityType, entityId, agencyId = null, status, evidenceRef = null
}) {
  const event = crypto.randomUUID();
  const timestamp = new Date().toISOString();
  // Both the sequence and changes() are evaluated inside the same serialized batch.
  // A denied operator overwrite or duplicate assignment changes no row => no event.
  const audit = env.MIRA_DB.prepare(`
    INSERT INTO mira_events
      (id,entity_type,entity_id,agency_id,actor,status,version,evidence_ref,reason,created_at)
    SELECT ?,?,?,?,?,?,
      (SELECT COALESCE(MAX(version),-1)+1 FROM mira_events WHERE entity_type=? AND entity_id=?),
      ?,?,?
    WHERE changes()>0
  `).bind(event, entityType, entityId, agencyId, identity.subject, status,
    entityType, entityId, evidenceRef, 'Operator configuration change; not commercial activation', timestamp);
  const results = await env.MIRA_DB.batch([mutation, audit]);
  return results[0];
}

/** Operator authorization is enforced by the Worker before this read is called. */
export async function administrativeHistory(env, url) {
  const keys = ['entity_type', 'entity_id', 'after_version', 'limit'];
  if ([...url.searchParams.keys()].some(k => !keys.includes(k)) ||
      keys.some(k => url.searchParams.getAll(k).length > 1)) throw new ApiError(400, 'invalid_audit_query');
  const type = url.searchParams.get('entity_type');
  if (!['agency', 'membership', 'project', 'agency_project'].includes(type)) throw new ApiError(400, 'invalid_audit_entity');
  const id = string(url.searchParams.get('entity_id'), 1, 401);
  const rawAfter = url.searchParams.get('after_version') ?? '-1';
  const rawLimit = url.searchParams.get('limit') ?? '50';
  if (!/^(?:-1|0|[1-9]\d*)$/.test(rawAfter) || !/^[1-9]\d*$/.test(rawLimit)) throw new ApiError(400, 'invalid_audit_page');
  const after = Number(rawAfter), limit = Number(rawLimit);
  if (!Number.isSafeInteger(after) || !Number.isSafeInteger(limit) || limit > 100) throw new ApiError(400, 'invalid_audit_page');
  const rows = (await env.MIRA_DB.prepare(`SELECT id,entity_type,entity_id,agency_id,actor,status,version,evidence_ref,reason,created_at
    FROM mira_events WHERE entity_type=? AND entity_id=? AND version>? ORDER BY version LIMIT ?`
  ).bind(type, id, after, limit + 1).all()).results || [];
  const records = rows.slice(0, limit);
  return {records, next_after_version: rows.length > limit ? records.at(-1).version : null,
    meaning: 'Recorded administrative changes only. No historical changes or commercial activation inferred.'};
}
