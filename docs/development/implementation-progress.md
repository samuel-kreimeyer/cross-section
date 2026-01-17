## Implementation Progress (2026-01-16)

### Summary
- Introduced guide-based annotation planning with profiles and a component registry.
- Anchored leader annotations now keep arrow tips fixed and clamp elbow extensions.
- Added crown-dimension enforcement and cross-slope warning logic.
- Expanded annotation tests for crown dimensions and cross-slope symbols.

### Details
- New modules: `src/cross_section/core/domain/annotations/guides.py`, `src/cross_section/core/domain/annotations/profile.py`, `src/cross_section/core/domain/annotations/planner.py`.
- `AnnotationGenerator` now delegates to `AnnotationPlanner`, mapping options to an `AnnotationProfile`.
- `LeaderAnnotation.reposition` preserves anchor points and shortens elbow segments to avoid long underlines.
- `RoadSection.validate` emits warnings when left/right cross slopes oppose.
- Tests updated: `tests/core/test_annotation_generation.py`, `tests/core/test_annotations.py`, `tests/core/test_section.py`.

---

## Implementation Progress (2026-01-14)

### Summary
- Added core missing components for surface-only geometry and urban features.
- Enforced shapely validation in tests and fixed scenario/test import paths.
- Refactored remaining manual scenarios to use the domain API.
- Exposed a stable public API surface and documented migration notes.
- Added geometry invariants documentation and updated the component spec status table.

### Details
- New components: `SurfaceProfile`, `Buffer`, `Gutter`, `Sidewalk`, `TurnLane`, `TraveledWay`.
- `RoadSection` now accepts `TraveledWay` for left/right assembly.
- Added unit tests for new components and traveled way helpers.
- Scenario updates: `tests/scenarios/crowned_road.py`, `tests/scenarios/three_lane_urban.py`.
- Test enforcement: `tests/conftest.py` requires shapely; scenario validation always runs shapely checks.
- Stable API: `src/cross_section/api.py` with re-exports via `src/cross_section/__init__.py`.
- Documentation updates: `docs/reference/geometry_invariants.md`, `docs/reference/component_spec.md`, `docs/development/migration_notes.md`.
