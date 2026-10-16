"""Source-reviewed B46 Whole-plant navigation and evidence release review packages (Pass A). Never replay acceptance."""
import argparse
import json
from pathlib import Path

SCOPES = ["route_walk", "release_audit"]
DOCS = {"route_walk": "doc_9c169bf7536b4ebca236", "release_audit": "doc_b5fdd81fad264a448d33"}

def main():
    ap = argparse.ArgumentParser(description="B46: Whole-plant navigation and evidence release review")
    ap.add_argument("scope", choices=SCOPES)
    args = ap.parse_args()
    pkg = Path(__file__).resolve().parents[1] / "output/plant-enrichment/B46" / args.scope / "package.json"
    print(f"Loaded {args.scope} package ({DOCS[args.scope]}):", pkg)

if __name__ == "__main__":
    main()
