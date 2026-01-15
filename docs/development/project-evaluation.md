# Project Evaluation: Domain Alignment and Geometry Soundness

## Goals
- Core library should expose a simple API that matches the roadway cross section domain model.
- Tests should be comprehensive with strong guarantees of geometric soundness.
- Examples and scenarios should use the API; manual geometry should drive API improvements.
- Runtime may keep shapely optional, but tests should catch geometry issues during development.
- Codebase should align with the specification, with spec updates where needed.

## Findings
### API drift and usage gaps
- README quick start references `Section` and `Lane`, which do not exist; current API uses `RoadSection` and `TravelLane`. `README.md:25`
- Examples pass `surface_type` to `TravelLane`, which is not a parameter. `examples/basic_section.py:24`, `examples/symmetric_section.py:25`
- Scenario builders often bypass the domain API and construct `SectionGeometry` and `ComponentGeometry` directly, which avoids exercising domain rules and validation. `tests/scenarios/crowned_road.py:34`, `tests/scenarios/three_lane_urban.py:25`, `tests/scenarios/ardot_undivided_notch_and_widen.py:25`

### Geometry soundness and validation
- Shapely-backed validation is optional and integration tests do not fail when it is missing; this weakens guarantees during development. `tests/integration/test_scenario_validation.py:26`, `src/cross_section/core/domain/section.py:175`
- Surface-only slopes are represented as thin polygons, which can introduce artificial overlaps/gaps in validation and exports. `src/cross_section/core/domain/components/slopes.py:120`

### Spec alignment
- The current implementation lacks several components and abstractions described in `component_spec.md` (TraveledWay, TurnLane, Buffer, PedestrianFacility, etc.), which contributes to manual geometry in scenarios. `docs/reference/component_spec.md:12`
- The top-level package does not expose a stable, simple API surface for the domain model. `src/cross_section/__init__.py:1`

## Manual Geometry That Signals Missing API
- ARDOT notch/widen scenario models overlay, notch, and widening as raw polygons rather than a domain component. `tests/scenarios/ardot_undivided_notch_and_widen.py:131`
- 3-lane urban scenario models turn lane, gutter/curb, buffer, sidewalk, and fill slopes manually. `tests/scenarios/three_lane_urban.py:136`
- Crowned road scenario models ditches manually rather than using `Ditch`. `tests/scenarios/crowned_road.py:34`

## Alignment Actions (Specification + API)
### Specification updates needed
- Clarify and prioritize which abstractions are core (TraveledWay/LaneGroup, TurnLane, Shoulder variants, Barrier/Buffer, Pedestrian/Bike facilities).
- Define how existing pavement, overlays, and widening transitions should be represented.
- Add explicit guidance for surface-only elements (cross slopes, aggregate flats, slumped shoulders) to avoid representing them as artificial solids.

### API additions implied by scenarios
- TraveledWay/LaneGroup that includes multiple lanes with shared pavement structure and crown logic.
- TurnLane component aligned with the spec and with traveled way membership.
- Shoulder variants: paved/aggregate split, slumped aggregate, and surface-only extensions.
- Overlay/Notch/Widening components for rehabilitation work.
- Buffer and Sidewalk/PedestrianFacility components with standard slopes/materials.
- SurfaceProfile or PolylineComponent for surface-only geometry without fabricated thickness.

## Test Strategy (Shapely optional at runtime)
- Make shapely a required dependency for the test environment (CI and local test extras), while keeping runtime optional.
- Fail tests explicitly if shapely is missing when geometry validation is expected.
- Add API-first scenario tests that build sections using the domain objects rather than raw `SectionGeometry`.

## Decisions Recorded
- Shapely remains an optional runtime dependency, but geometry validation must be enforced in tests.
- Codebase should align with the component specification; the spec may need refinement to reflect the desired domain model and priorities.
