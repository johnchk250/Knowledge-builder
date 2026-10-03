# Visual plant model — September 2026

The default plant experience is now an illustrated, navigable assembly model.
This is a presentation change over accepted model version 510, not a new data
extraction or a claim that every installed component has been documented.

## What changed

- Whole-plant coal journey with nine process areas and five documented route guides.
- Equipment scenes and a selection inspector throughout the model. Facts and
  original sources open on demand; the existing reference and maintenance
  workspace remains available through the inspector.
- Conveyor compositions, motor / coupling / gearbox / head-pulley drive chains,
  scoop oil-system diagrams, transfer-house cutaways, yard assemblies, and generic
  component scenes for the remaining equipment classes.
- Source-backed ownership, location and connection relationships remain distinct.
  TP-1 exposes the conveyor drives located there without adopting them as children.
  Stockpiles expose their connected machines, shed and dust systems even without
  owned components. Shared utility supplies remain separate equipment.
- Plant context, assembly breadcrumbs, tag search, component navigator, network
  layers, pan / zoom, assembled / spread views for conveyor and yard scenes,
  keyboard selection and optional flow illustration.
- The reusable enrichment prompt now requires visual integration and component-level
  provenance instead of a primary interface of isolated fact cards.

## Verification

- 76 Python tests passed, including new scene static-asset coverage through the
  existing HTTP test and original-page evidence rendering.
- 27 JavaScript tests passed: 18 existing projection checks and 9 scene checks.
- An accepted-model render sweep exercised 1,461 non-reference equipment records
  and all nine process areas without exceptions or invalid numeric output.
- Browser checks covered Conveyor 1A → drive → scoop coupling → oil pump → its
  cited PDF page and enlarged region; both images loaded successfully.
- Conveyor 1B protection navigation worked by keyboard. PCS displayed its original
  14-pair quantity and separate derived 28-switch count with source buttons; BSS
  retained 11 pairs / 22 switches. Values came from the model, not UI constants.
- Checked TP-1 A/B chute and drive composition, stockyard → Coal Yard 1 → EAD-1,
  stockpile context, route-source dialog, 1440 px and 480 px layouts, and browser
  console errors (none observed). Compact inspector had no page-width overflow.
- Read-only integrity verification: 266 documents, 5,196 evidence blocks, 510
  versions, no errors. Canonical model version remains 510.

## Limits and continued work

Illustrations are schematic, not surveyed coordinates, certified as-built geometry,
or live operating status. Flow illustration does not select a valid simultaneous
operating route. Source qualifications remain attached to their facts.

Detailed engineering coverage still varies across the plant. Generic symbols and
layouts provide navigation for records without a specialized scene. Future work
should improve source-backed relationships and reusable scene templates together;
it must not copy pilot ratings or invent component locations to fill a drawing.

See `PLANT_EXPLORER.md` for use and implementation, and
`EQUIPMENT_ENRICHMENT_AGENT_PROMPT.md` for the continuation prompt.
