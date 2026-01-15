# Issue: Domain Model Misalignment and Geometry Soundness Gaps

**Type:** design
**Severity:** high
**Tool:** manual-review
**Detected:** 2026-01-14T14:31:58Z

## Summary
The current implementation and scenarios do not consistently use the domain API described in the component specification, and geometry soundness is not enforced by the test suite when shapely is missing.

## Evidence
- Scenario builders construct `SectionGeometry`/`ComponentGeometry` directly, bypassing `RoadSection` and component validation. `tests/scenarios/crowned_road.py:34`, `tests/scenarios/three_lane_urban.py:25`, `tests/scenarios/ardot_undivided_notch_and_widen.py:25`
- Shapely validation is optional and tests pass without it, reducing geometry guarantees. `tests/integration/test_scenario_validation.py:26`, `src/cross_section/core/domain/section.py:175`
- The spec lists components and abstractions not present in code (TraveledWay, TurnLane, Buffer, PedestrianFacility). `docs/reference/component_spec.md:12`
- Examples and README reference API names/parameters that do not exist. `README.md:25`, `examples/basic_section.py:24`

## Impact
- The core library is not validated by the most representative scenarios, masking API gaps.
- Geometry issues can slip through development and be discovered at runtime.
- Drift between spec and implementation undermines the goal of a domain-aligned API.

## Recommended Action
- Align implementation with the component specification, refining the spec where necessary.
- Require shapely in CI/test environments and fail tests when geometry validation is not available.
- Rebuild scenarios to use the domain API and use manual geometry only as a driver for API extensions.

## Automation
- Detectable: partially
- Auto-fixable: no
