"""Isolated browser QA against a temporary database snapshot."""
import sqlite3
import sys
import tempfile
import shutil
from pathlib import Path
from http.server import ThreadingHTTPServer
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from chp.service import Service
from chp.server import make_handler


def main():
    source = Path(__file__).resolve().parents[1] / 'data' / 'plant'
    with tempfile.TemporaryDirectory(prefix='chp-spatial-browser-') as directory:
        target = Path(directory) / 'plant'
        target.mkdir()
        with sqlite3.connect((source / 'plant.sqlite3').as_uri() + '?mode=ro', uri=True) as src, sqlite3.connect(target / 'plant.sqlite3') as dst:
            src.backup(dst)
        # Copy the pulley drawing sources used by the browser QA source-reference check.
        with sqlite3.connect(target / 'plant.sqlite3') as db:
            images = db.execute("SELECT image FROM evidence e JOIN documents d ON d.id=e.document_id WHERE d.name='016535_04.PDF' AND image IS NOT NULL").fetchall()
        (target / 'renders').mkdir()
        for (name,) in images:
            shutil.copyfile(source / 'renders' / name, target / 'renders' / name)
        service = Service(directory)
        server = ThreadingHTTPServer(('127.0.0.1', 8766), make_handler(service, 'spatial-browser-test', 8766))
        print('Isolated browser QA ready at http://127.0.0.1:8766/#spatial', flush=True)
        try:
            server.serve_forever()
        finally:
            server.server_close()


if __name__ == '__main__':
    main()
