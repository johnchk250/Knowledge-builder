"""Preserve historical spatial storage for exports/backups; no modeling workflow."""
from .store import now

def initialize(store):
    (store.root/'meshes').mkdir(exist_ok=True)
    with store.transaction() as db:
        db.execute('CREATE TABLE IF NOT EXISTS spatial_revisions(revision INTEGER PRIMARY KEY,model_version INTEGER NOT NULL,scene TEXT NOT NULL,created TEXT NOT NULL,reason TEXT NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS spatial_suggestions(id TEXT PRIMARY KEY,run_id TEXT REFERENCES runs(id),proposal_id TEXT REFERENCES proposals(id),body TEXT NOT NULL,errors TEXT NOT NULL,created TEXT NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS spatial_decisions(suggestion_id TEXT PRIMARY KEY REFERENCES spatial_suggestions(id),decision TEXT NOT NULL,revision INTEGER,created TEXT NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS mesh_assets(sha256 TEXT PRIMARY KEY,name TEXT NOT NULL,vertices TEXT NOT NULL,bounds TEXT NOT NULL,created TEXT NOT NULL)')
        for table in ('spatial_revisions','spatial_suggestions','spatial_decisions','mesh_assets'):
            for action in ('UPDATE','DELETE'):
                db.execute(f"CREATE TRIGGER IF NOT EXISTS immutable_{table}_{action} BEFORE {action} ON {table} BEGIN SELECT RAISE(ABORT,'immutable record'); END")
        db.execute("INSERT OR IGNORE INTO spatial_revisions VALUES(0,0,'[]',?,'Empty spatial layer')",(now(),))
        db.execute("UPDATE meta SET value='3' WHERE key='schema_version' AND CAST(value AS INTEGER)<3")

