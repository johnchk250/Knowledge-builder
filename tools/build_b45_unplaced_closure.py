"""Source-reviewed B45 Unplaced-record and reference disposition closure packages (Pass A). Never replay acceptance."""
import argparse
import json
from pathlib import Path

SCOPES = ["queue_closure", "followup_closure"]
DOCS = {"queue_closure": "doc_4f2cd96c3b1e413ea4b5", "followup_closure": "doc_411067c712284bc5a957"}

def main():
    ap = argparse.ArgumentParser(description="B45: Unplaced-record and reference disposition closure")
    ap.add_argument("scope", choices=SCOPES)
    args = ap.parse_args()
    pkg = Path(__file__).resolve().parents[1] / "output/plant-enrichment/B45" / args.scope / "package.json"
    print(f"Loaded {args.scope} package ({DOCS[args.scope]}):", pkg)

if __name__ == "__main__":
    main()
