"""Evidence/render helper for Pass B depth work (read-only).

Bridges the canonical DB (documents/evidence) to the immutable page
renders under data/plant/renders so extraction work can locate pages,
search OCR text and produce crops for the top-model packages.

Subcommands:
    docs   <doc_id> [<doc_id> ...]          document info + per-page evidence
    pages  --doc <doc_id> [--page N]        page -> render image path(s)
    image  --doc <doc_id> --page N          print render path for a page
    text   --doc <doc_id> [--page N]        full OCR text blocks
    find   <regex> [--doc <doc_id>] [--limit N]   search OCR text
    crop   --doc <doc_id> --page N --region L,T,R,B --out PATH [--scale S]

Region is fractional (0-1) page coordinates, left,top,right,bottom.
No database writes; renders are read from data/plant/renders.
"""
import argparse
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / 'data/plant/plant.sqlite3'
RENDERS = ROOT / 'data/plant/renders'


def db():
    con = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
    con.row_factory = sqlite3.Row
    return con


def doc_rows(con, doc_ids):
    out = {}
    for doc in doc_ids:
        row = con.execute('SELECT * FROM documents WHERE id=?', (doc,)).fetchone()
        out[doc] = row
    return out


def cmd_docs(args):
    con = db()
    for doc in args.doc_id:
        row = con.execute('SELECT * FROM documents WHERE id=?', (doc,)).fetchone()
        if not row:
            print(f'{doc}: NOT FOUND')
            continue
        print(f'{doc}  {row["name"]}  rev={row["revision"]!r}  authority={row["authority"]!r}  bytes={row["bytes"]}')
        for ev in con.execute(
                'SELECT id, page, locator, image, length(text) tlen FROM evidence '
                'WHERE document_id=? ORDER BY page, id', (doc,)):
            print(f'   {ev["id"]}  p{ev["page"]}  {ev["locator"]}  img={ev["image"]}  textlen={ev["tlen"]}')


def cmd_pages(args):
    con = db()
    sql = 'SELECT DISTINCT page, image FROM evidence WHERE document_id=? AND image IS NOT NULL'
    params = [args.doc]
    if args.page:
        sql += ' AND page=?'
        params.append(args.page)
    for row in con.execute(sql + ' ORDER BY page', params):
        print(f'p{row["page"]}  {RENDERS / row["image"]}')


def cmd_image(args):
    con = db()
    rows = con.execute(
        'SELECT DISTINCT image FROM evidence WHERE document_id=? AND page=? AND image IS NOT NULL',
        (args.doc, args.page)).fetchall()
    if not rows:
        sys.exit('no evidence image for that doc/page')
    for row in rows:
        print(RENDERS / row['image'])


def cmd_text(args):
    con = db()
    sql = 'SELECT id, page, locator, text FROM evidence WHERE document_id=?'
    params = [args.doc]
    if args.page:
        sql += ' AND page=?'
        params.append(args.page)
    for row in con.execute(sql + ' ORDER BY page, id', params):
        print(f'--- {row["id"]} p{row["page"]} {row["locator"]} ---')
        print((row['text'] or '').strip())


def cmd_find(args):
    con = db()
    pattern = re.compile(args.regex, re.I)
    sql = 'SELECT e.id, e.page, e.locator, e.text, d.name, e.document_id FROM evidence e ' \
          'JOIN documents d ON d.id = e.document_id'
    params = []
    if args.doc:
        sql += ' WHERE e.document_id=?'
        params.append(args.doc)
    n = 0
    for row in con.execute(sql, params):
        text = row['text'] or ''
        m = pattern.search(text)
        if not m:
            continue
        n += 1
        start = max(0, m.start() - 70)
        end = min(len(text), m.end() + 110)
        snippet = text[start:end].replace('\n', ' ')
        print(f'{row["document_id"]} {row["name"][:55]} p{row["page"]} {row["id"]}: ...{snippet}...')
        if n >= args.limit:
            print(f'(stopped at --limit {args.limit})')
            break
    if n == 0:
        print('no matches')
    else:
        print(f'({n} match(es) shown)')


def cmd_crop(args):
    from PIL import Image
    con = db()
    rows = con.execute(
        'SELECT DISTINCT image FROM evidence WHERE document_id=? AND page=? AND image IS NOT NULL',
        (args.doc, args.page)).fetchall()
    if not rows:
        sys.exit('no evidence image for that doc/page')
    region = [float(v) for v in args.region.split(',')]
    if len(region) != 4 or not (region[0] < region[2] and region[1] < region[3]):
        sys.exit('region must be L,T,R,B with L<R and T<B')
    src = RENDERS / rows[0]['image']
    img = Image.open(src)
    w, h = img.size
    box = (int(region[0] * w), int(region[1] * h), int(region[2] * w), int(region[3] * h))
    crop = img.crop(box)
    if args.scale and args.scale != 1:
        crop = crop.resize((int(crop.width * args.scale), int(crop.height * args.scale)), Image.LANCZOS)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    crop.save(out)
    print(f'{out}  {crop.width}x{crop.height}  from {src.name} box={box}')


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest='cmd', required=True)

    p = sub.add_parser('docs')
    p.add_argument('doc_id', nargs='+')
    p.set_defaults(fn=cmd_docs)

    p = sub.add_parser('pages')
    p.add_argument('--doc', required=True)
    p.add_argument('--page', type=int)
    p.set_defaults(fn=cmd_pages)

    p = sub.add_parser('image')
    p.add_argument('--doc', required=True)
    p.add_argument('--page', type=int, required=True)
    p.set_defaults(fn=cmd_image)

    p = sub.add_parser('text')
    p.add_argument('--doc', required=True)
    p.add_argument('--page', type=int)
    p.set_defaults(fn=cmd_text)

    p = sub.add_parser('find')
    p.add_argument('regex')
    p.add_argument('--doc')
    p.add_argument('--limit', type=int, default=40)
    p.set_defaults(fn=cmd_find)

    p = sub.add_parser('crop')
    p.add_argument('--doc', required=True)
    p.add_argument('--page', type=int, required=True)
    p.add_argument('--region', required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--scale', type=float, default=1.0)
    p.set_defaults(fn=cmd_crop)

    args = ap.parse_args()
    args.fn(args)


if __name__ == '__main__':
    main()
