# B24 breadth complete at v684

B24 Tier1 accepted v683-v684: 12 new major components, 65 assertions, 0 retirements (1 existing weigher reused). Yard4 stacker EAD-4 and portal reclaimer EAF-4 motion assemblies from unit-specific family sources against the B15 applicability matrix; no Yard1/2/3 motor/lube/DSS counts inherited.

Two source-scoped proposals: stacker prop_c0812e94a50146e2978a (v683, BOD 175249 Rev2 doc_78bebe6773984d59b013 pp1-3: type Four(4), 3400/3740 t/h, travel/slew/luff/boom/tripper/cabin/weigher notes with crushed-coal conflict preserved); reclaimer prop_d7193b2a8e4142f9b8c0 (v684, GA 175127 Rev2 doc_3e81ea1c32df4215968d p3 spec table + pp4-6 replies: EAF-1..4 family scope, 1250/1375 t/h, main/aux booms, hoist 3/34 m/min, travel 55.8 m span, power/control reels, wind-unit conflict and 179103 safety-instrument gap preserved). EAD-4 weigher ent_9ed0efef76a94da08af4 reused (was thin 2-fact placeholder); all other labels new with part_of owner.

Verification: fresh integrity/FK pass (266 documents, 5196 evidence blocks, v684); 52/52 Node scene tests; both pilot audits pass; Yard1 breadth audit passes with zero Yard1 changes (413 records, 1959 claims); rehearsal preservation checks pass on both proposals. Route checks: EAC-13->EAD-4->EAE-4->EAF-4->EBA-14 intact, no coal flow into UAX-4, Yard4 membership intact, headline ratings with units, rail/span notes present.

Tool: tools/build_b24_yard4_machines.py (stacker/reclaimer scopes, tmp IDs, empty-quote visual regions, full-doc reviewed_evidence_ids).
