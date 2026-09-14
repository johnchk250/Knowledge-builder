"""Build existing knowledge into an auditable spatial draft, optionally save it."""
import argparse
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from .store import Store, dumps
from . import spatial, spatial_knowledge


class ReadOnlyStore(Store):
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.path = self.root / 'plant.sqlite3'

    def connect(self):
        connection = sqlite3.connect(self.path.as_uri() + '?mode=ro', uri=True)
        connection.row_factory = sqlite3.Row
        return connection


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', default='data/plant')
    parser.add_argument('--output', required=True, help='Directory for scene, mapping/gap report and glTF')
    parser.add_argument('--entity', action='append', help='Optional canonical identity scope')
    parser.add_argument('--save', action='store_true', help='Save validated representations; preserves reviewed parameters')
    args = parser.parse_args()
    source = ReadOnlyStore(args.data)
    draft = spatial_knowledge.build(source, args.entity)
    rendered = spatial.rendered(source, scene_override=draft)
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / 'spatial-draft.json').write_text(json.dumps(draft, ensure_ascii=False, indent=2), encoding='utf-8')
    summary = {**draft['build_summary'], 'plant_version': draft['model_version'], 'triangles': rendered['triangle_count'],
               'spatial_revision_before': draft['revision'], 'saved': False}
    if args.save and draft['scene'] != spatial.current(source)['scene']:
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        backup = out / ('plant-before-spatial-' + stamp + '.sqlite3')
        with source.connect() as src, sqlite3.connect(backup) as dst:
            src.backup(dst)
        store = Store(args.data)
        saved = spatial.save(store, draft['scene'], draft['revision'], draft['model_version'],
                             'Build equipment representations from accepted knowledge; exact rule mappings retain source evidence; unknown geometry and placement remain schematic.')
        summary.update(saved=True, spatial_revision=saved['revision'], database_backup=str(backup))
        (out / 'plant-scene.gltf').write_text(dumps(spatial.export_gltf(source)), encoding='utf-8')
    (out / 'summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
