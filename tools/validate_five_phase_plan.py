"""Read-only handoff checks; writes a report, never canonical plant data."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/plant-handoff"


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    state = read(BASE / "phase-progress.json")
    batches = {b["id"]: b for b in read(BASE / "batches.json")["batches"]}
    targets = read(BASE / "inventory/targets.json")
    current = read(BASE / "current/target-status.json")
    reused = set(state["accepted_reuse_batches"])
    ordered = [b for phase in state["phases"] for b in phase["batches"]]
    assert len(state["phases"]) == 5
    assert len(ordered) == len(set(ordered)), "Batch appears in two phases"
    assert not reused.intersection(ordered), "Accepted reuse is scheduled for replay"
    assert set(batches) == reused.union(ordered), "Missing or unknown batch"
    ready = set(reused)
    for bid in ordered:
        assert set(batches[bid]["depends_on"]).issubset(ready), bid
        ready.add(bid)
    assert {(t["id"], t["label"]) for t in targets} == {(t["id"], t["label"]) for t in current}
    assert len(current) == len({t["card"] for t in current})
    # Planned yard cards deliberately have no canonical identity yet.
    identified = [t["id"] for t in current if t["id"] is not None]
    assert len(identified) == len(set(identified))
    for t in current:
        assert t["primary_batch"] in batches, t["label"]
        assert (BASE / "current" / t["card"]).is_file(), t["card"]
    active = next(p for p in state["phases"] if p["id"] == state["active_phase"])
    if state["status"] != "complete":
        assert state["next_batch"] in active["batches"]
    for rel in (state["plan"], state["current_inventory"],
                state["last_completed_work"]["checkpoint"],
                state["accepted_followup_queue"]):
        assert (ROOT / rel).is_file(), rel
    files = [BASE / "FIVE_PHASE_PLAN.md", BASE / "current/CURRENT_STATUS.md",
             ROOT / "output/plant-enrichment/B36-corrections/checkpoint.md",
             ROOT / "output/plant-enrichment/B36-corrections/verification.md"]
    checked_links = 0
    for file in files:
        for link in re.findall(r"\]\(([^)]+)\)", file.read_text(encoding="utf-8")):
            if "://" in link or link.startswith("#"):
                continue
            target = link.split("#")[0]
            assert (file.parent / target).exists(), f"{file}: {link}"
            checked_links += 1
    result = {"ok": True, "inventory_version": read(BASE / "current/summary.json")["version"],
              "phases": len(state["phases"]), "batches": len(batches),
              "reused_batches": len(reused), "scheduled_batches": len(ordered),
              "targets": len(current), "checked_local_links": checked_links,
              "dependency_order_valid": True, "next_phase": active["id"],
              "next_batch": state["next_batch"],
              "scope": "Handoff coverage and references, not engineering acceptance"}
    (BASE / "current/plan-validation.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
