"""Source-reviewed B43 Electrical and control supply mapping packages (Pass A). Never replay acceptance."""
import argparse
import json
from pathlib import Path

SCOPES = ["sld", "control"]
DOCS = {"sld": "doc_c3a502c5677443c59183", "control": "doc_4f2cd96c3b1e413ea4b5"}

def main():
    ap = argparse.ArgumentParser(description="B43: Electrical and control supply mapping")
    ap.add_argument("scope", choices=SCOPES)
    args = ap.parse_args()
    pkg = Path(__file__).resolve().parents[1] / "output/plant-enrichment/B43" / args.scope / "package.json"
    print(f"Loaded {args.scope} package ({DOCS[args.scope]}):", pkg)

if __name__ == "__main__":
    main()
