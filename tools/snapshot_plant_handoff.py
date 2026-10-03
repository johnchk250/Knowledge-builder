"""Export a consistent, read-only planning snapshot; never initializes the store."""
import argparse
import datetime as dt
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from chp.store import Store


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    with sqlite3.connect((ROOT / 'data/plant/plant.sqlite3').as_uri() + '?mode=ro', uri=True) as db:
        db.row_factory = sqlite3.Row
        db.execute('PRAGMA query_only=ON')
        db.execute('BEGIN')
        result = {
            'captured_at': dt.datetime.now(dt.timezone.utc).isoformat(),
            'model': Store.__new__(Store).model(db=db),
            'documents': [dict(row) for row in db.execute('SELECT * FROM documents ORDER BY name')],
            'evidence': [dict(row) for row in db.execute('SELECT * FROM evidence ORDER BY document_id,page,id')],
            'integrity': [row[0] for row in db.execute('PRAGMA integrity_check')],
            'foreign_key_errors': [list(row) for row in db.execute('PRAGMA foreign_key_check')],
        }
    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({'snapshot': str(output), 'version': result['model']['version'],
                      'documents': len(result['documents']), 'evidence': len(result['evidence']),
                      'integrity': result['integrity'], 'foreign_key_errors': result['foreign_key_errors']}))


if __name__ == '__main__':
    main()
