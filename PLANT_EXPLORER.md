# Visual plant explorer

The app opens on `#overview` as an interactive plant drawing. Open a process
area, select equipment, and use **Open assembly** to descend into its parts.
The drawing stays visible when a selected component's details open beside it.
The operations dashboard remains at `#desk`.

## Daily use

- **Understand the plant:** follow the illustrated coal journey, or choose one of
  the five documented route guides. Open a stage to see actual equipment links.
- **Explore a machine:** select a component in its assembly, then open it. The
  drive view follows documented motor → coupling → gearbox → head-pulley links;
  scoop coupling views expose the oil circulation system and its instruments.
- **Explore a place:** TP views combine owned equipment and equipment explicitly
  located there. Yard views show the shed, pile, stacker, reclaimer, conveyors,
  dust suppression and runoff collection. A stockpile can show the machines and
  services connected to it even when it has no owned components.
- **Keep your bearings:** the plant strip, assembly breadcrumbs, and upstream /
  downstream links remain available. Global search finds tags and aliases; the
  component navigator searches the current assembly and associated equipment.
- **Trace connections:** open **View connections**, select a network layer, and
  click an arrow to inspect its individual source conditions. **Explain flow**
  animates documented directions only; it is an illustration, not live operation.
- **Inspect evidence:** select equipment to open its inspector. Ratings and counts
  retain individual source buttons. Expand all facts, applicable engineering
  references, relationships, or qualifications only when needed. Original PDF
  pages and enlarged cited regions open in the existing source dialog.
- **See smaller parts:** pan the drawing, use + / −, or choose **All parts**.
  **Fit** restores the opening composition. Conveyor and yard scenes also offer
  **Spread parts / Assembled**. Reduced-motion preferences are respected.
- **Search requirements and history:** the inspector links to the retained
  assembly-fact and maintenance-record workspace (`view=records`). Return to
  **Plant overview** to resume visual exploration.

The same visual navigation applies throughout the model. Generic symbols and
assembly layouts handle equipment without a specialized scene; the detailed
pilots remain EAC-1A, EAC-1B, UEF-1 and Coal Yard 1. More complete drawings require
further source extraction. Illustrative geometry never establishes surveyed
placement, dimensions, installed configuration, or an operating state.

## Evidence and scope

The initial nine browse groups and five path guides follow the accepted
`Control Write up for Coal Handling System.pdf` (model versions 462–466):
write-up Rev04, coal-flow drawing Rev8 on page 55, and layout Rev0 on page 56.
The source is a design document, approved on condition; it is not live telemetry
or a certification of the current installed plant.

Grouping is a read-only navigation projection. It does not commit assertions,
merge identities, or establish physical location. Exact tag families place the
main-route equipment; recorded location/component relationships place associated
items. Unplaced equipment, other systems, and references remain searchable.

Arrows use current, documented, non-inferred material connection assertions.
Directions, parallel source records, conditions, and silo crossovers are retained.
Inferred, unverified, retired, suppressed, dangling, and out-of-validity links
are not promoted to the diagram. Other connection records remain inspectable.
Area diagrams show in-area links; equipment scenes offer a separate connection view.
The graph preserves loops and routes bypass links around intermediate nodes.

Path selection highlights process stages only. It does not select compatible
gate positions, simulate a running route, infer isolation boundaries, or certify
startup permissives. The connection inspector and retained reference workspace also expose the individual links without relying on SVG.

Direct equipment claims and explicitly applicable reference claims are distinct.
Same-classification design dossiers are navigation suggestions only; their
ratings and components are not inherited by numbered equipment. Missing location,
hierarchy, or protection data stays visibly missing. Source-level qualifications
are retained; their UI detection is a wording aid, not a complete conflict audit.

## Implementation

- `dist/plant-model.js`: pure projection, placement, claim grouping, graph layout.
- `dist/plant-scene-model.js`: read-only scene scopes, ownership/location distinctions, nearest-parent navigation, and evidence-preserving edge groups.
- `dist/plant-scene.js`, `dist/plant-scene.css`: illustrated equipment scenes, selection inspector, route/assembly navigation, pan/zoom, and optional flow illustration.
- `dist/plant-explorer.js`: integration, retained reference workspace, and evidence actions.
- `dist/plant-explorer.css`: responsive diagrams, equipment panels, focus mode.
- `dist/app.js`, `dist/index.html`, `dist/operations-ui.js`: navigation integration.
- `chp/service.py`: workspace-scoped evidence index with page/locator metadata.
- `chp/server.py`: serves the new local browser assets.

The browser files in `dist` are application source served directly by Python;
there is no frontend build. `.gitignore` now permits the browser source files
while continuing to ignore other generated distribution content.

## Validation

Run `node --test tests/test_plant_explorer.cjs tests/test_plant_scene.cjs` and
`python -m unittest discover -s tests -v` using the project's Python environment.
Projection tests exercise documented direction, validity, exact silo crossover,
conditional branches, shared/cyclic hierarchy, applicability boundaries, graph
loops, and parallel yard lanes. HTTP coverage checks static assets and evidence
index workspace isolation. `python -m chp.verify --data data/plant` verifies
source originals, evidence, and the model version chain without writing it.

## Next model improvements

The interface exposes where further source review will have the greatest value:
confirm installed-tag applicability for machine dossiers; connect those units to
their auxiliaries; record exact physical locations; distinguish approved field
setpoints from design ranges; and accumulate equipment-bound inspection and repair
history. These require source-backed model updates rather than UI assumptions.

## Detailed equipment pilot

EAC-1A, EAC-1B and UEF-1 now have source-backed component dossiers. See
[the pilot report](EQUIPMENT_PILOT_REPORT.md) for scope and known gaps, and
[the reusable extraction prompt](EQUIPMENT_ENRICHMENT_AGENT_PROMPT.md) to extend the model.
The **Assembly facts** tab searches an equipment's containment tree without inheriting
unrelated shared-service facts. Physical-location links are browsable separately.
Fact sources can render a bounded, enlarged region directly from the immutable original PDF.
