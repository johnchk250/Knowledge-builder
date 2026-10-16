# B21 breadth complete at v675

B21 Tier1 accepted v674-v675: 12 new major components, 65 assertions, 0 retirements (1 existing weigher reused). Yard3 stacker EAD-3 and portal reclaimer EAF-3 motion assemblies from unit-specific family sources against the B15 applicability matrix; no Yard1/2 motor/lube/DSS counts inherited.

Two source-scoped proposals (one document each): stacker prop_1b704e98a21c43f8901d (v674, BOD 175249 Rev2 doc_78bebe6773984d59b013 pp1-3: type Four(4), 3400/3740 t/h, travel/slew/luff/boom/tripper/cabin/weigher notes with crushed-coal conflict preserved); reclaimer prop_6c238f41d90b47e2a514 (v675, GA 175127 Rev2 doc_3e81ea1c32df4215968d p3 spec table + pp4-6 replies: EAF-1..4 family scope, 1250/1375 t/h, main/aux booms, hoist 3/34 m/min, travel 55.8 m span, power/control reels, wind-unit conflict and 179103 safety-instrument gap preserved). EAD-3 weigher ent_2335d2395f6049908706 reused (was thin 2-fact placeholder); all other labels new with part_of owner.

Verification: fresh integrity/FK pass (266 documents, 5196 evidence blocks, v675); 52/52 Node scene tests; both pilot audits pass (silo v527, crusher v558 shapes unchanged); Yard1 breadth audit passes with zero Yard1 changes (413 records, 1959 claims); rehearsal preservation checks pass on both proposals (32+33 added, 0 retired, prior aliases/merges/conflicts preserved; only 4 pre-existing B01 pump/head conflicts retained as warnings). Route checks: EAC-11->EAD-3->EAE-3->EAF-3->EBA-12 intact, no coal flow into UAX-3, Yard3 membership intact, headline ratings with units, rail/span notes present.

Limitation: none outstanding for Tier 1. Visual pass: 12/12 PNG + 2/2 source journeys, 0 console errors (desktop-1440 + mobile-480); EAD-3 Page 2 and EAF-3 Page 3-text-block-1 journeys open correct document/page and return to inspector. All BOD pp1-6 and GA pp1-6 (incl. review replies) visually reviewed via originals.

Tool: tools/build_b21_machines.py (stacker/reclaimer scopes, tmp IDs, empty-quote visual regions, full-doc reviewed_evidence_ids); acceptance via tools/accept_b02_scoped.py rehearsal then guarded --apply, sequential baselines v673->v674->v675. Nothing replayed.

Vendor drive internals, brake/protection numeric settings, chain/blade take-up detail, lube/DSS/fire, safety-instrument loops and commissioned settings remain in the depth queue (DQ-B21-001/002). Local services B22 follows.

Next: B22 PassA: Yard3 local SPDS sector/AP/SV map, onboard DSS refill boundaries, drainage/fire gaps and TP4/9 interfaces from Yard3 source branches; do not copy Yard1/2 SP-8 or AP/SV mapping.
