# Implementation Plan: Spec-Aligned Domain Model and Geometry Soundness

## Goal
Deliver a core library with a simple, domain-aligned API for roadway cross sections. Tests must enforce geometry soundness during development, while shapely remains optional at runtime.

## Recent Changes Incorporated
- Shapely-backed validation now exists, including clipping and gap checks, with dedicated tests.
- Rehabilitation components exist (`ExistingPavement`, `MillAndOverlay`, `NotchAndWidening`) and are used in the ARDOT notch/widen scenario.
- Barrier and retaining wall components are implemented.
- Annotations and annotated SVG export infrastructure landed with test coverage.
- Scenario and generator structure has been formalized under `tests/scenarios` and `tests/generators`.

## Status by Component
| Component | Spec Status | Implementation Status | Notes / Next Step |
| --- | --- | --- | --- |
| RoadSection / ControlPoint | Core | Implemented | Central assembly API is present. |
| TravelLane | Core | Implemented | Uses layered pavement and validation. |
| Shoulder | Core | Implemented | Supports fully paved + slumped; partial paving still needed for spec parity. |
| Slope | Core | Implemented | Surface-only slopes now render as polylines; material slopes remain polygons. |
| Ditch | Core | Implemented | Void line + optional lining in place. |
| Curb | Core | Implemented | Gutter integrated; standalone Gutter not yet present. |
| Barrier (concrete/guardrail/cable) | Extended | Implemented | Spec alignment needed in documentation. |
| RetainingWall / MSEWall | Extended | Implemented | Spec alignment needed in documentation. |
| Shoring | Extended | Implemented | Spec alignment needed in documentation. |
| Rehabilitation (ExistingPavement / MillAndOverlay / NotchAndWidening) | Extended | Implemented | ARDOT notch/widen uses these. |
| TraveledWay / LaneGroup | Core | Missing | Needed for multi-lane grouping and shared pavement structure. |
| TurnLane | Core | Missing | Needed for urban scenario. |
| Buffer | Core | Missing | Needed for urban scenario. |
| Sidewalk / PedestrianFacility | Core | Missing | Needed for urban scenario. |
| Gutter (standalone) | Core | Missing | Currently folded into Curb. |
| SurfaceProfile / PolylineComponent | Core | Implemented | Use for surface-only elements without artificial thickness. |

## Plan (Revised)

### 1) Spec alignment and refinement (docs first)
- Update `docs/reference/component_spec.md` to explicitly define:
  - Core vs extended components (including barriers, retaining walls, shoring, rehab)
  - Required behaviors and validation rules
  - Component metadata contracts
- Add a concise geometry invariant document (new file or section):
  - Coordinate conventions and sign rules
  - Crown/grade point behavior
  - Overlap/gap tolerance rules
  - Polygon winding requirements
  - Surface-only element representation (no artificial thickness)

Deliverables:
- Updated spec with explicit scope and priorities.
- Geometry invariants documented.

### 2) Core API surface cleanup
- Define a stable import surface (e.g., `cross_section.api` or re-exports in `cross_section/__init__.py`).
- Add aliases/deprecations only after the API is stable.

Deliverables:
- Single stable API module exporting domain objects.

### 3) Domain gaps still blocking spec alignment
Prioritize components that eliminate remaining manual geometry in scenarios.

3.1 TraveledWay / LaneGroup
- Represent ordered lanes with shared pavement structure and crown logic.
- Support a `TurnLane` subtype.
- Integrate cleanly with `RoadSection`.

3.2 TurnLane
- Add lane subtype with validation rules and metadata.

3.3 Shoulder enhancements (if still needed beyond current slumped support)
- Support partial paving and aggregate flats/slumps:
  - `paved_width`, `aggregate_flat_width`, `slumped_width`
  - `surface_slope` vs `fill_slope`
- Add surface-only geometry representation.

3.4 Sidewalk, Buffer, Gutter
- Implement components aligned to the spec.
- Compose curb+gutter as a convenience component.

Deliverables:
- Components sufficient to re-implement the remaining manual scenarios via API.

### 4) Geometry representation updates
- Expand use of `SurfaceProfile`/polyline-based geometry for surface-only elements.
- Keep validation focused on area overlap for solids while still checking polyline crossings.

Deliverables:
- Surface-only elements are represented without artificial thickness.

### 5) Validation + test enforcement
- Shapely validation exists; now enforce it in tests:
  - Add a test fixture that fails if shapely is missing for geometry tests.
  - Ensure CI installs `cross-section[validation]` (or equivalent).
- Expand unit tests for new components and invariants:
  - Attachment continuity
  - Overlap/gap rules within sequence groups
  - Bounds and metadata correctness

Deliverables:
- Tests fail without shapely in dev/CI.
- Geometry soundness is enforced by the test suite.

### 6) Scenario refactors to API usage (remaining work)
- `tests/scenarios/crowned_road.py`: migrate to `RoadSection`, `TravelLane`, `Shoulder`, `Ditch`.
- `tests/scenarios/three_lane_urban.py`: migrate to `TraveledWay`, `TurnLane`, `Curb+Gutter`, `Buffer`, `Sidewalk`, `Slope`.
- Preserve annotations, but drive dimensions from API outputs.

Deliverables:
- All scenarios use the domain API (no manual `ComponentGeometry` construction).

### 7) Deprecation and migration (after API stabilizes)
- Add deprecation notices for old names/parameters.
- Provide a migration guide in `docs/development`.

Deliverables:
- Clear migration path for user code and examples.

## Definition of Done
- All scenarios use the domain API (no manual `ComponentGeometry` construction).
- Shapely is required for tests and CI geometry validation.
- Spec and implementation match for core components.
- A stable API surface exists for users.
