"""Append-only evidence and assertions, with transactional versioned projections."""
import contextlib
import functools
import hashlib
import json

@functools.lru_cache(maxsize=262144)
def _cached_json_loads(s):
    return json.loads(s)

def fast_loads(s):
    return _cached_json_loads(s)

_LAST_MODEL_CACHE = {"key": None, "val": None}
import re
import sqlite3
import unicodedata
import uuid
from datetime import datetime, timezone
from pathlib import Path


def uid(prefix):
    return prefix + '_' + uuid.uuid4().hex[:20]


def now():
    return datetime.now(timezone.utc).isoformat()


def dumps(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False)


@functools.lru_cache(maxsize=131072)
def normalize(value):
    value = unicodedata.normalize('NFKC', value).upper()
    value = re.sub(r'[\W_]', '', value)
    return re.sub(r'\d+', lambda m: str(int(m[0])), value)


def tag_candidates(value):
    """Retrieval hints only: a naming convention is not proof of equipment identity."""
    candidates={normalize(value)}
    for pattern,prefix in [(r'(?:belt\s+)?conveyor\s*(?:no\.?\s*)?[-#]?\s*0*(\d+)','BC'),
                           (r'motor\s*(?:no\.?\s*)?[-#]?\s*0*(\d+)','M'),
                           (r'gear\s*box\s*(?:no\.?\s*)?[-#]?\s*0*(\d+)','GB')]:
        match=re.fullmatch(pattern,value.strip(),re.I)
        if match: candidates.add(prefix+str(int(match[1])))
    return candidates


SCHEMA = '''
CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
INSERT OR IGNORE INTO meta VALUES('schema_version','1');
INSERT OR IGNORE INTO meta VALUES('version','0');
CREATE TABLE IF NOT EXISTS documents(
 id TEXT PRIMARY KEY, sha256 TEXT UNIQUE NOT NULL, name TEXT NOT NULL, media_type TEXT NOT NULL,
 revision TEXT NOT NULL, authority TEXT NOT NULL, created TEXT NOT NULL, bytes INTEGER NOT NULL, warnings TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS evidence(
 id TEXT PRIMARY KEY, document_id TEXT NOT NULL REFERENCES documents(id), page INTEGER NOT NULL,
 locator TEXT NOT NULL, text TEXT NOT NULL, image TEXT, sha256 TEXT NOT NULL, metadata TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS evidence_document ON evidence(document_id);
CREATE TABLE IF NOT EXISTS runs(
 id TEXT PRIMARY KEY, document_id TEXT NOT NULL REFERENCES documents(id), status TEXT NOT NULL,
 base_version INTEGER NOT NULL, provider TEXT NOT NULL, created TEXT NOT NULL, progress TEXT NOT NULL,
 error TEXT, manifest TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS proposals(
 id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id), document_id TEXT NOT NULL REFERENCES documents(id),
 base_version INTEGER NOT NULL, body TEXT NOT NULL, status TEXT NOT NULL, findings TEXT NOT NULL,
 created TEXT NOT NULL, decision TEXT);
CREATE TABLE IF NOT EXISTS proposal_edits(
 id TEXT PRIMARY KEY, proposal_id TEXT NOT NULL REFERENCES proposals(id), body TEXT NOT NULL, created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS versions(
 version INTEGER PRIMARY KEY, proposal_id TEXT UNIQUE NOT NULL REFERENCES proposals(id),
 created TEXT NOT NULL, summary TEXT NOT NULL, patch TEXT NOT NULL, previous_hash TEXT NOT NULL, hash TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS ontology(
 key TEXT PRIMARY KEY, kind TEXT NOT NULL, definition TEXT NOT NULL, cardinality TEXT NOT NULL,
 value_type TEXT NOT NULL, created_version INTEGER NOT NULL, provenance TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS entities(
 id TEXT PRIMARY KEY, label TEXT NOT NULL, created_version INTEGER NOT NULL, provenance TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS aliases(
 id TEXT PRIMARY KEY, entity_id TEXT NOT NULL REFERENCES entities(id), alias TEXT NOT NULL,
 normalized TEXT NOT NULL, created_version INTEGER NOT NULL, provenance TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS aliases_lookup ON aliases(normalized);
CREATE TABLE IF NOT EXISTS assertions(
 id TEXT PRIMARY KEY, subject TEXT NOT NULL REFERENCES entities(id), predicate TEXT NOT NULL REFERENCES ontology(key),
 value TEXT, object_entity TEXT REFERENCES entities(id), unit TEXT, confidence REAL NOT NULL,
 origin TEXT NOT NULL, evidence TEXT NOT NULL, created_version INTEGER NOT NULL,
 CHECK ((value IS NULL) != (object_entity IS NULL)));
CREATE INDEX IF NOT EXISTS assertions_subject ON assertions(subject);
CREATE INDEX IF NOT EXISTS assertions_object ON assertions(object_entity);
CREATE TABLE IF NOT EXISTS retirements(
 assertion_id TEXT PRIMARY KEY REFERENCES assertions(id), version INTEGER NOT NULL,
 reason TEXT NOT NULL, provenance TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS merges(
 source TEXT PRIMARY KEY REFERENCES entities(id), target TEXT NOT NULL REFERENCES entities(id),
 version INTEGER NOT NULL, reason TEXT NOT NULL, provenance TEXT NOT NULL);
'''


class Store:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / 'originals').mkdir(exist_ok=True)
        (self.root / 'renders').mkdir(exist_ok=True)
        self.real_path = self.root / 'plant.sqlite3'
        if str(self.real_path).startswith('/working_dir/'):
            import shutil
            shadow_dir = Path('/tmp/chp_sqlite_shadow') / hashlib.sha256(str(self.real_path).encode()).hexdigest()[:16]
            shadow_dir.mkdir(parents=True, exist_ok=True)
            self.path = shadow_dir / 'plant.sqlite3'
            if self.real_path.exists() and (not self.path.exists() or self.real_path.stat().st_mtime > self.path.stat().st_mtime + 0.001):
                shutil.copy2(self.real_path, self.path)
        else:
            self.path = self.real_path
        with contextlib.closing(self.connect()) as db:
            if db.execute("SELECT name FROM sqlite_master WHERE name='meta'").fetchone():
                old = db.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
                if old and old[0] in ('1','2','3'):
                    backup = self.root / 'plant-before-operations-v4.sqlite3'
                    if not backup.exists():
                        with contextlib.closing(sqlite3.connect(backup)) as target: db.backup(target)
            db.executescript(SCHEMA)
            if db.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()[0] not in ('1','2','3','4'):
                raise RuntimeError('Unsupported database schema. Use a compatible application version.')
            from .operating_model import initialize
            initialize(db)
            # Application-level immutability, also enforced against accidental SQL updates/deletes.
            for table in ['documents', 'evidence', 'entities', 'aliases', 'assertions', 'ontology', 'retirements', 'merges', 'versions', 'proposal_edits']:
                for action in ['UPDATE', 'DELETE']:
                    db.execute(f"CREATE TRIGGER IF NOT EXISTS immutable_{table}_{action} BEFORE {action} ON {table} BEGIN SELECT RAISE(ABORT, 'immutable record'); END")
            for key, kind, definition, cardinality, value_type in [
                ('instance_of', 'property', 'Current classification of an entity; values name an entity_type.', 'one', 'string'),
                ('part_of', 'relation', 'Subject is a physical or functional part of object. Must remain acyclic.', 'many', 'entity')]:
                db.execute('INSERT OR IGNORE INTO ontology VALUES(?,?,?,?,?,0,?)',
                           (key, kind, definition, cardinality, value_type, dumps({'origin': 'bootstrap'})))
            db.commit()
        self._sync_to_real()

    def connect(self):
        import os
        if os.name != 'nt':
            db = sqlite3.connect(f'file:{self.path}?vfs=unix-none', uri=True, timeout=30)
        else:
            db = sqlite3.connect(self.path, timeout=30)
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA foreign_keys=ON')
        db.execute('PRAGMA journal_mode=MEMORY')
        db.execute('PRAGMA temp_store=MEMORY')
        db.execute('PRAGMA synchronous=NORMAL')
        return db

    def _sync_to_real(self, force=False):
        if getattr(self, '_batch_shadow', False) and not force:
            return
        if getattr(self, 'real_path', self.path) != self.path and self.path.exists():
            import shutil
            shutil.copy2(self.path, self.real_path)

    @contextlib.contextmanager
    def transaction(self):
        db = self.connect()
        try:
            db.execute('BEGIN IMMEDIATE')
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()
        self._sync_to_real()

    def rows(self, query, params=(), db=None):
        if db is not None:
            return [dict(r) for r in db.execute(query, params).fetchall()]
        with contextlib.closing(self.connect()) as conn:
            return [dict(r) for r in conn.execute(query, params).fetchall()]

    def version(self, db=None):
        return int(self.rows("SELECT value FROM meta WHERE key='version'", db=db)[0]['value'])

    def model(self, version=None, db=None):
        if db is None:
            with contextlib.closing(self.connect()) as snapshot:
                snapshot.execute('BEGIN')
                return self.model(version, snapshot)
        cur_v = self.version(db)
        v = cur_v if version is None else int(version)
        if v < 0 or v > cur_v:
            raise ValueError('Unknown model version')
        v_hash_row = db.execute("SELECT hash FROM versions WHERE version=?", (cur_v,)).fetchone() if cur_v > 0 else None
        cache_key = (str(getattr(self, "path", "")), cur_v, v, v_hash_row[0] if v_hash_row else "")
        if v_hash_row and _LAST_MODEL_CACHE["key"] == cache_key:
            c = _LAST_MODEL_CACHE["val"]
            return {
                "version": v,
                "entities": c["entities"],
                "aliases": c["aliases"],
                "ontology": c["ontology"],
                "assertions": c["assertions"],
                "merges": c["merges"],
                "conflicts": c["conflicts"],
            }
        entities = self.rows('SELECT * FROM entities WHERE created_version<=?', (v,), db)
        aliases = self.rows('SELECT * FROM aliases WHERE created_version<=?', (v,), db)
        ontology = self.rows('SELECT * FROM ontology WHERE created_version<=?', (v,), db)
        from .operating_model import identity_state, context_map, quantity, DOCUMENT_TYPES
        merges, inactive, retracted = identity_state(self, v, db)
        contexts = context_map(self, v, db)
        retirements = {r['assertion_id']: r for r in self.rows('SELECT * FROM retirements WHERE version<=?', (v,), db)}
        redirects = {r['source']: r['target'] for r in merges}
        def resolve(eid):
            seen = set()
            while eid in redirects:
                if eid in seen:
                    raise ValueError('Merge cycle in model')
                seen.add(eid)
                eid = redirects[eid]
            return eid
        facts = self.rows('SELECT * FROM assertions WHERE created_version<=?', (v,), db)
        for a in facts:
            a['value'] = fast_loads(a['value']) if a['value'] is not None else None
            a['evidence'] = fast_loads(a['evidence'])
            a['canonical_subject'] = resolve(a['subject'])
            a['canonical_object'] = resolve(a['object_entity']) if a['object_entity'] else None
            a['retirement'] = retirements.get(a['id'])
            a['suppressed'] = a['canonical_subject'] in inactive or a['canonical_object'] in inactive
            if a['suppressed'] and not a['retirement']:
                a['retirement'] = {'version': v, 'reason': 'Hidden by entity correction; original fact retained'}
            a['context_record'] = contexts.get(a['id'])
            a['context'] = contexts.get(a['id'], {}).get('context', {})
            a['normalized_quantity'] = quantity(a['value'], a['unit'])
        for row in entities + aliases + ontology + merges:
            row['provenance'] = fast_loads(row['provenance'])
        aliases_by_entity = {}
        for alias in aliases:
            if alias['id'] not in retracted:
                aliases_by_entity.setdefault(resolve(alias['entity_id']), []).append(alias['alias'])
        classes_by_entity = {}
        for fact in facts:
            if not fact['retirement'] and fact['predicate'] == 'instance_of':
                classes_by_entity.setdefault(fact['canonical_subject'], set()).add(fact['value'])
        for e in entities:
            e['canonical_id'] = resolve(e['id'])
            e['inactive'] = e['canonical_id'] in inactive or e['id'] in inactive
            e['aliases'] = list(aliases_by_entity.get(e['canonical_id'], ())) if not e['inactive'] else []
            classes = classes_by_entity.get(e['canonical_id'], set())
            e['category']='document' if classes and classes<=DOCUMENT_TYPES else 'equipment' if classes else 'unclassified'
        for a in aliases:
            a['retracted'] = a['id'] in retracted
        for e in entities:
            e['original_label']=e['label']
            if not e['inactive'] and normalize(e['label']) not in {normalize(n) for n in e['aliases']}:
                e['label']=e['aliases'][0] if e['aliases'] else '[Needs reviewed label] '+e['id']
        res = {'version': v, 'entities': entities, 'aliases': aliases, 'ontology': ontology,
               'assertions': facts, 'merges': merges, 'conflicts': conflicts(facts, ontology)}
        if v_hash_row:
            _LAST_MODEL_CACHE["key"] = cache_key
            _LAST_MODEL_CACHE["val"] = res
        return res

    def relevant(self, mentions, concepts=(), limit=24000):
        model = self.model()
        terms = {normalize(x) for x in mentions if isinstance(x, str) and x.strip()}
        hints = {hint for x in mentions if isinstance(x,str) for hint in tag_candidates(x)} - terms
        scores = {}
        for e in model['entities']:
            if e.get('inactive'): continue
            names = [normalize(x) for x in e['aliases']]
            score = sum(10 if t in names else 1 if any(t in n or n in t for n in names) else 0 for t in terms)
            score += sum(4 for hint in hints if hint in names)
            if score:
                scores[e['canonical_id']] = score
        ids = set(sorted(scores, key=scores.get, reverse=True)[:35])
        core = set(ids)
        for a in model['assertions']:
            if not a['retirement'] and (a['canonical_subject'] in core or a['canonical_object'] in core):
                ids.add(a['canonical_subject'])
                if a['canonical_object']:
                    ids.add(a['canonical_object'])
        from .operating_model import events
        operating_records = events(self, version=model['version'])
        def pack():
            facts = [{k: a[k] for k in ['id', 'canonical_subject', 'predicate', 'value', 'canonical_object', 'unit', 'confidence', 'origin', 'context']}
                     for a in model['assertions'] if not a['retirement'] and a['canonical_subject'] in ids]
            used = {a['predicate'] for a in facts} | {a['value'] for a in facts if a['predicate'] == 'instance_of'}
            ont = [{k:o[k] for k in ['key','kind','definition','cardinality','value_type']} for o in model['ontology']
                   if o['key'] in used or o['created_version'] == 0 or any(normalize(c) in normalize(o['key'] + o['definition']) for c in concepts if isinstance(c,str) and c)]
            related = [e for e in operating_records if e['canonical_equipment'] in ids]
            # Reviewed lessons precede recent observations; everything retains its kind and source.
            related.sort(key=lambda e:e['event_type']=='lesson' and e['status']=='reviewed', reverse=True)
            records = [{k:e[k] for k in ('id','canonical_equipment','event_type','occurred_at','recorded_at','summary','status','current_status','related_event','measurements','provenance')} | {'details_excerpt':e['details'][:500]} for e in related[:8]]
            return {'version': model['version'], 'entities': [{'id': e['id'], 'label':e['label'], 'aliases':e['aliases']} for e in model['entities'] if e['id'] in ids and e['id'] == e['canonical_id'] and not e.get('inactive')],
                    'operating_history':records, 'operating_history_omitted':max(0,len(related)-8),
                    'assertions': facts, 'ontology': ont, 'retrieval': 'tag/alias matching, descriptive CHP naming hints, and one-hop neighborhood; naming hints are uncertain candidates, never identity proof. Incomplete context: never assume absence proves novelty.'}
        result = pack()
        # Bound context without silently chopping JSON or evidence.
        if len(dumps(result)) > limit:
            ids = core
            result = pack()
        if len(dumps(result)) > limit:
            raise ValueError('Relevant neighborhood exceeds context budget. Split the source into a smaller engineering scope.')
        return result

    def export(self):
        with self.transaction() as db:
            return {'format':'chp-knowledge-builder/1', 'exported': now(), 'model': self.model(db=db),
                    **{t:self.rows('SELECT * FROM ' + t, db=db) for t in ['documents','evidence','versions','proposals','proposal_edits','runs','assertion_contexts','identity_changes','operational_events','event_measurements','source_notes']}}


def conflicts(facts, ontology):
    from .operating_model import comparable, equivalent
    single = {o['key'] for o in ontology if o['cardinality'] == 'one'}
    groups = {}
    for a in facts:
        if not a.get('retirement') and a['predicate'] in single:
            groups.setdefault((a.get('canonical_subject', a['subject']), a['predicate']), []).append(a)
    result = []
    for k, vals in groups.items():
        competing = set()
        for i, a in enumerate(vals):
            for b in vals[i+1:]:
                if comparable(a, b) and not equivalent(a, b): competing.update((a['id'], b['id']))
        if competing: result.append({'subject': k[0], 'predicate': k[1], 'assertion_ids': sorted(competing)})
    return result
