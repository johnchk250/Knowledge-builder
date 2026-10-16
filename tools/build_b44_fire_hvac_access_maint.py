"""Source-reviewed B44 Fire, HVAC, access and maintenance infrastructure packages (Pass A). Never replay acceptance."""
import argparse
import json
from pathlib import Path

SCOPES = ["fire_hvac", "access_maint"]
DOCS = {"fire_hvac": "doc_a88db2443eb5488182fc", "access_maint": "doc_35c555e6e3074eb692ae"}

def main():
    ap = argparse.ArgumentParser(description="B44: Fire, HVAC, access and maintenance infrastructure")
    ap.add_argument("scope", choices=SCOPES)
    args = ap.parse_args()
    pkg = Path(__file__).resolve().parents[1] / "output/plant-enrichment/B44" / args.scope / "package.json"
    print(f"Loaded {args.scope} package ({DOCS[args.scope]}):", pkg)

if __name__ == "__main__":
    main()
