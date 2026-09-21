#!/usr/bin/env python3
"""Prepare replayable D1 research snapshots. Never calls a network or writes production."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import sys

VERSION = 1
AGENCY_PATH = 'project-bible/mira/research/agency-expansion-2026-09-19/master-agencies.json'
DEVELOPER_PATH = 'project-bible/mira/research/developer-expansion-2026-09-19/developers.json'
LINK_PATH = 'project-bible/mira/research/developer-expansion-2026-09-19/project-links.json'
FIELD_KEYS = ('city','brand','legal_name','parent_brand','canonical_domain','segment',
 'company_phone','direct_business_phone','contact_first_name','contact_last_name','contact_role',
 'general_email','direct_public_work_email','whatsapp_url','telegram_url','telegram_kind',
 'vk_url','other_social_url','contact_page')
TABLES = {
 'entities': ('mira_research_entities', ('snapshot_id','kind','source_id')),
 'aliases': ('mira_research_aliases', ('snapshot_id','kind','alias_id','source_id')),
 'fields': ('mira_research_fields', ('snapshot_id','kind','source_id','field_key','occurrence')),
 'project_links': ('mira_research_project_links', ('snapshot_id','market','project_id')),
 'native_lineage': ('mira_native_lineage', ('snapshot_id','crm_account_id')),
}

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)

def digest(value):
    return hashlib.sha256(value.encode('utf-8')).hexdigest()

def required_string(value, label):
    if not isinstance(value, str) or not value.strip() or '\x00' in value:
        raise ValueError('Missing or invalid ' + label)
    return value

def sql_value(value):
    if value is None:
        return 'NULL'
    if isinstance(value, int):
        return str(value)
    if not isinstance(value, str) or '\x00' in value:
        raise ValueError('Invalid SQL value')
    return "'" + value.replace("'", "''") + "'"

def insert(table, row, keys):
    # Identifiers are internal constants. All source data are quoted literals.
    cols = tuple(row)
    updates = [k for k in cols if k not in keys]
    conflict = ('DO UPDATE SET ' + ','.join(k+'=excluded.'+k for k in updates)) if updates else 'DO NOTHING'
    statement = ('INSERT INTO '+table+' ('+','.join(cols)+') VALUES ('+
                 ','.join(sql_value(row[k]) for k in cols)+') ON CONFLICT ('+
                 ','.join(keys)+') '+conflict+';')
    if len(statement.encode('utf-8')) > 99000:
        raise ValueError('Row exceeds D1 statement budget; split source record explicitly')
    return statement

def unique_rows(rows, key, label):
    out = {}
    for row in rows:
        identity = required_string(row.get(key), label+' ID')
        if identity in out:
            raise ValueError('Duplicate '+label+' ID')
        out[identity] = row
    return out

def field_row(kind, identity, field, value, evidence, occurrence=0, scope='unknown'):
    statuses = [e.get('verification_status', e.get('status', 'not_checked')) for e in evidence]
    status = statuses[0] if statuses and len(set(statuses)) == 1 else ('multiple_evidence_statuses' if statuses else 'not_checked')
    return dict(kind=kind,source_id=identity,field_key=field,occurrence=occurrence,
                value_json=canonical(value),evidence_json=canonical(evidence),
                verification_status=status,conversation_scope=scope)

def build(agencies_document, developers, links, source_commit, native=None):
    if not re.fullmatch(r'[0-9a-f]{40}', source_commit):
        raise ValueError('Exact source commit required')
    agencies = agencies_document['records']
    agency_map = unique_rows(agencies,'agency_id','agency')
    developer_map = unique_rows(developers,'developer_id','developer')
    manifests = {'schema_version':VERSION,'source_commit':source_commit,
                 'agency_sha256':digest(canonical(agencies_document)),
                 'developer_sha256':digest(canonical(developers)),
                 'project_links_sha256':digest(canonical(links)),
                 'native_crosswalk_sha256':digest(canonical(native)) if native is not None else None}
    snapshot = 'MIRA-IMPORT-'+digest(canonical(manifests))
    data = {k:[] for k in TABLES}
    aliases = {}
    for kind, mapping in [('agency',agency_map),('developer',developer_map)]:
        for identity, row in sorted(mapping.items()):
            name = required_string(row.get('brand') if kind=='agency' else row.get('name'),kind+' name')
            data['entities'].append(dict(kind=kind,source_id=identity,name=name,city=row.get('city'),
                market=row.get('country') if kind=='agency' else row.get('market'),segment=row.get('segment'),
                row_json=canonical(row),row_sha256=digest(canonical(row))))
            for alias in sorted(set([identity]+(row.get('legacy_ids',[]) if kind=='agency' else []))):
                required_string(alias,'legacy alias')
                aliases.setdefault((kind,alias),set()).add(identity)
                data['aliases'].append(dict(kind=kind,alias_id=alias,source_id=identity))
            if kind=='agency':
                for field in FIELD_KEYS:
                    evidence=[e for e in row.get('field_evidence',[]) if e.get('field')==field]
                    scope='unknown'
                    if field=='telegram_url' and row.get('telegram_kind') in ('channel','public_channel'):
                        scope='public_channel'
                    elif field in ('direct_business_phone','direct_public_work_email') and row.get(field):
                        scope='published_work_contact_not_dialogue'
                    data['fields'].append(field_row(kind,identity,field,row.get(field),evidence,scope=scope))
            else:
                for index, contact in enumerate(row.get('contacts',[])):
                    key=required_string(contact.get('kind'),'contact kind')
                    scope='direct_dialogue_verified' if contact.get('direct_dialogue_verified') is True else 'public_contact_not_dialogue'
                    data['fields'].append(field_row(kind,identity,'contact:'+key,contact.get('value'),[contact],index,scope))
    seen_links=set()
    for row in links:
        project=required_string(row.get('project_id'),'project ID')
        market=required_string(row.get('market'),'project market')
        if (market,project) in seen_links:
            raise ValueError('Duplicate market/project ID')
        seen_links.add((market,project))
        developer=row.get('developer_id')
        if developer is not None and developer not in developer_map:
            raise ValueError('Unknown developer in project mapping')
        for candidate in row.get('candidate_developer_ids',[]):
            if candidate not in developer_map:
                raise ValueError('Unknown candidate developer')
        data['project_links'].append(dict(market=market,project_id=project,developer_kind='developer',
            developer_id=developer,mapping_status=required_string(row.get('mapping_status'),'mapping status'),
            row_json=canonical(row),row_sha256=digest(canonical(row))))
    resolved_agencies=0
    if native is not None:
        if native.get('private_only') is not True:
            raise ValueError('Native crosswalk must be explicitly private')
        nrows=native['rows']
        unique_rows(nrows,'crm_account_id','native account')
        unique_rows(nrows,'native_external_id','native external')
        for row in nrows:
            kind=row.get('entity_type')
            if kind not in ('agency','developer'):
                raise ValueError('Synthetic/non-research native entity not accepted')
            resolved=None
            if kind=='agency':
                candidates=set()
                source_ids=row.get('canonical_research_ids',[])
                if not source_ids:
                    raise ValueError('Agency native lineage has no canonical IDs')
                for source_id in source_ids:
                    matches=aliases.get((kind,source_id),set())
                    if len(matches)!=1:
                        raise ValueError('Missing or ambiguous native agency reference')
                    candidates.update(matches)
                if len(candidates)!=1:
                    raise ValueError('Native agency maps to multiple canonical groups')
                resolved=next(iter(candidates));resolved_agencies+=1
            # Developer domain candidates are observations only, never auto-resolved entities.
            data['native_lineage'].append(dict(crm_account_id=row['crm_account_id'],
                native_external_id=row['native_external_id'],kind=kind,
                mapping_status=required_string(row.get('status'),'native mapping status'),
                resolved_source_id=resolved,row_json=canonical(row),row_sha256=digest(canonical(row))))
    expected={key:len(value) for key,value in data.items()}
    header=dict(id=snapshot,source_commit=source_commit,source_manifest_json=canonical(manifests),
                expected_json=canonical(expected),contains_private=int(native is not None))
    statements=[insert('mira_import_snapshots',header,('id',))]
    for name,(table,keys) in TABLES.items():
        for row in data[name]:
            statements.append(insert(table,dict(snapshot_id=snapshot,**row),keys))
    statements.append(insert('mira_import_commits',dict(snapshot_id=snapshot),('snapshot_id',)))
    sql='\n'.join(statements)+'\n'
    summary=dict(snapshot_id=snapshot,source_commit=source_commit,expected=expected,
        agency_candidates=len(agency_map),developer_groups=len(developer_map),
        native_agency_links_resolved=resolved_agencies,
        native_developer_entity_links_resolved=0,
        native_developer_lineage_held=sum(r['kind']=='developer' for r in data['native_lineage']),
        contains_private=native is not None,sql_sha256=digest(sql),
        max_statement_bytes=max(len(s.encode()) for s in statements),
        commercial_activations=0,operational_table_writes=0,remote_imports=0,
        source_hash_semantics='SHA256 of canonical JSON, not original file byte hash')
    return sql,summary,data

def immutable_schema(base_sql):
    # A replay may issue identical no-op UPSERTs. Changed existing data fail loudly.
    schemas={
      'mira_import_snapshots':('id','source_commit','source_manifest_json','expected_json','contains_private'),
      'mira_research_entities':('snapshot_id','kind','source_id','name','city','market','segment','row_json','row_sha256'),
      'mira_research_aliases':('snapshot_id','kind','alias_id','source_id'),
      'mira_research_fields':('snapshot_id','kind','source_id','field_key','occurrence','value_json','evidence_json','verification_status','conversation_scope'),
      'mira_research_project_links':('snapshot_id','market','project_id','developer_kind','developer_id','mapping_status','row_json','row_sha256'),
      'mira_native_lineage':('snapshot_id','crm_account_id','native_external_id','kind','mapping_status','resolved_source_id','row_json','row_sha256'),
      'mira_import_commits':('snapshot_id',),
    }
    chunks=[base_sql]
    for table,columns in schemas.items():
        chunks.append('CREATE TRIGGER '+table+'_immutable BEFORE UPDATE ON '+table+' WHEN '+
           ' OR '.join('NEW.'+c+' IS NOT OLD.'+c for c in columns)+
           " BEGIN SELECT RAISE(ABORT,'import_snapshot_immutable'); END;")
        chunks.append('CREATE TRIGGER '+table+'_no_delete BEFORE DELETE ON '+table+
           " BEGIN SELECT RAISE(ABORT,'import_snapshot_immutable'); END;")
        if table!='mira_import_commits':
            idcol='id' if table=='mira_import_snapshots' else 'snapshot_id'
            # Replays hit existing keys; adding a new row to a published snapshot is blocked.
            keycols=('id',) if table=='mira_import_snapshots' else next(v[1] for v in TABLES.values() if v[0]==table)
            same=' AND '.join(c+'=NEW.'+c for c in keycols)
            chunks.append('CREATE TRIGGER '+table+'_sealed BEFORE INSERT ON '+table+
              ' WHEN EXISTS(SELECT 1 FROM mira_import_commits WHERE snapshot_id=NEW.'+idcol+')'+
              ' AND NOT EXISTS(SELECT 1 FROM '+table+' WHERE '+same+')'+
              " BEGIN SELECT RAISE(ABORT,'published_snapshot_sealed'); END;")
    return '\n'.join(chunks)+'\n'

def verify(database,snapshot):
    # mode=ro avoids accidentally creating a new database when the filename is wrong.
    with sqlite3.connect(Path(database).resolve().as_uri()+'?mode=ro',uri=True) as db:
        expected=db.execute('SELECT expected_json FROM mira_import_snapshots WHERE id=?',(snapshot,)).fetchone()
        if expected is None:
            raise ValueError('Snapshot absent')
        counts={k:db.execute('SELECT count(*) FROM '+v[0]+' WHERE snapshot_id=?',(snapshot,)).fetchone()[0] for k,v in TABLES.items()}
        committed=db.execute('SELECT count(*) FROM mira_import_commits WHERE snapshot_id=?',(snapshot,)).fetchone()[0]==1
        integrity=[]
        for table in ('mira_research_entities','mira_research_project_links','mira_native_lineage'):
            for raw,sha in db.execute('SELECT row_json,row_sha256 FROM '+table+' WHERE snapshot_id=?',(snapshot,)):
                if digest(raw)!=sha:integrity.append(table)
        fk=list(db.execute('PRAGMA foreign_key_check'))
        result=dict(snapshot_id=snapshot,counts=counts,committed=committed,counts_match=counts==json.loads(expected[0]),
                    payload_hash_mismatches=len(integrity),foreign_key_errors=len(fk),remote=False)
        result['passed']=committed and result['counts_match'] and not integrity and not fk
        return result

def private_write(path, text):
    # New output only; refuse symlinks, stale artifacts and accidental replacement.
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w',encoding='utf-8') as f:f.write(text)

def main():
    p=argparse.ArgumentParser(description=__doc__);subs=p.add_subparsers(dest='command',required=True)
    prep=subs.add_parser('prepare');prep.add_argument('--repo',type=Path,required=True)
    prep.add_argument('--source-commit',required=True);prep.add_argument('--out',type=Path,required=True)
    prep.add_argument('--native-crosswalk',type=Path);prep.add_argument('--private-output',action='store_true')
    check=subs.add_parser('verify');check.add_argument('--database',required=True);check.add_argument('--snapshot',required=True)
    args=p.parse_args()
    if args.command=='verify':
        report=verify(args.database,args.snapshot);print(canonical(report));return 0 if report['passed'] else 1
    if args.native_crosswalk and not args.private_output:
        raise ValueError('Native lineage requires --private-output; never publish output')
    read=lambda rel:json.loads((args.repo/rel).read_text())
    native=json.loads(args.native_crosswalk.read_text()) if args.native_crosswalk else None
    sql,summary,_=build(read(AGENCY_PATH),read(DEVELOPER_PATH),read(LINK_PATH),args.source_commit,native)
    if args.out.exists():raise ValueError('Output directory must be new')
    args.out.mkdir(mode=0o700,parents=True)
    base=Path(__file__).with_name('schema.base.sql').read_text()
    private_write(args.out/'0004_research_import.sql',immutable_schema(base))
    private_write(args.out/'import.sql',sql)
    private_write(args.out/'summary.json',json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    private_write(args.out/'.gitignore','*\n')
    print(canonical(summary));return 0

if __name__=='__main__':
    try:raise SystemExit(main())
    except (ValueError,KeyError,TypeError,sqlite3.Error,OSError) as exc:
        # No source row, credentials, SQL or private filesystem path is printed.
        print(canonical({'ok':False,'error_type':type(exc).__name__}),file=sys.stderr)
        raise SystemExit(1)
