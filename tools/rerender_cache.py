"""Repopulate data/plant/renders from immutable originals.

Render math mirrors chp/ingest.py exactly (same scale formula, same
PyMuPDF call), so regenerated files are byte-identical and keep the
same sha256 filenames the evidence table references.

Read-only with respect to the database: only SELECT queries, never
writes canonical tables. Safe to re-run; existing files are skipped.

Usage:
    python tools/rerender_cache.py --data data/plant          # fill gaps
    python tools/rerender_cache.py --data data/plant --check  # report only
    python tools/rerender_cache.py --data data/plant --doc <sha256>
"""
import argparse
import hashlib
import sqlite3
import sys
from pathlib import Path

try:
    import fitz
except ImportError:
    sys.exit('PyMuPDF is required: python -m pip install -r requirements.txt')


def render_page(page):
    # Must stay identical to chp/ingest.py or filenames will not match.
    scale = min(2.0, 1600 / max(page.rect.width, page.rect.height))
    pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
    return pix.tobytes('png')


def main():
    parser = argparse.ArgumentParser(description='Repopulate renders/ from originals/')
    parser.add_argument('--data', required=True, help='Workspace folder containing plant.sqlite3')
    parser.add_argument('--check', action='store_true', help='Report missing renders without writing')
    parser.add_argument('--doc', default=None, help='Only process one document (sha256)')
    args = parser.parse_args()

    root = Path(args.data)
    db_path = root / 'plant.sqlite3'
    renders = root / 'renders'
    if not db_path.exists():
        sys.exit(f'No database at {db_path}')

    db = sqlite3.connect(f'file:{db_path}?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    docs = db.execute(
        "SELECT id, sha256, name, media_type FROM documents WHERE media_type IN "
        "('application/pdf','image/png','image/jpeg')").fetchall()
    if args.doc:
        docs = [d for d in docs if d['sha256'] == args.doc]
        if not docs:
            sys.exit(f'Document {args.doc} not found')
    images = {row['image'] for row in db.execute(
        'SELECT DISTINCT image FROM evidence WHERE image IS NOT NULL')}
    db.close()

    if args.check:
        missing = sorted(name for name in images if not (renders / name).exists())
        print(f'evidence images referenced: {len(images)}, missing files: {len(missing)}')
        for name in missing[:20]:
            print(f'  MISSING {name}')
        if len(missing) > 20:
            print(f'  ... and {len(missing) - 20} more')
        sys.exit(1 if missing else 0)

    renders.mkdir(exist_ok=True)
    written = skipped = 0
    for doc in docs:
        original = root / 'originals' / doc['sha256']
        if not original.exists():
            print(f'SKIP {doc["name"]}: original {doc["sha256"]} absent')
            continue
        try:
            with fitz.open(original) as document:
                if document.needs_pass:
                    print(f'SKIP {doc["name"]}: encrypted')
                    continue
                for page in document:
                    png = render_page(page)
                    target = renders / (hashlib.sha256(png).hexdigest() + '.png')
                    if target.exists():
                        skipped += 1
                    else:
                        target.write_bytes(png)
                        written += 1
        except Exception as exc:
            print(f'SKIP {doc["name"]}: {type(exc).__name__}: {exc}')
    print(f'documents: {len(docs)}, pages written: {written}, pages already cached: {skipped}')

    missing = sorted(name for name in images if not (renders / name).exists())
    if missing:
        print(f'STILL MISSING {len(missing)} referenced renders (first 20):')
        for name in missing[:20]:
            print(f'  {name}')
        sys.exit(1)
    print(f'all {len(images)} referenced renders present')


if __name__ == '__main__':
    main()
