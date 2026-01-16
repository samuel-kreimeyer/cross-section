# Geometry Invariants

This document defines geometry rules and invariants used by the core domain model, validation, and exporters.

## Coordinate System
- X axis: horizontal, positive to the right of the control point.
- Y axis: vertical, positive upward.
- ControlPoint: canonical origin for section assembly.

## Assembly Direction
- `right`: components extend in positive X from the current attachment point.
- `left`: components extend in negative X from the current attachment point.
- Components must keep insertion/attachment continuity along their assembly direction.

## Units and Tolerance
- Geometry is expressed in meters (float).
- Validation uses a small tolerance (default 1e-6) for overlap/gap checks.

## Polygons and Winding
- Polygons must be valid, non-self-intersecting.
- Winding is expected to be consistent for components; exporters should not rely on mixed winding.
- Holes are optional and must be fully contained within the exterior.

## Overlap and Gap Rules
- Overlaps between different components are errors unless explicitly allowed via metadata (e.g., `overlap_allow_polygons`).
- Gaps between sequential components in the same assembly group are errors.
- Gaps between left and right assembly groups are allowed.

## Surface-Only Geometry
- Surface-only elements (e.g., aggregate flats, crowned slopes) should be represented as polylines, not thin polygons.
- Validation should exclude surface-only polylines from area overlap checks but still detect polyline intersections.

## Metadata Contract (Minimum)
Each `ComponentGeometry` should include:
- `component_type`: stable identifier for validation/export.
- `assembly_direction`: `left` or `right` when produced via section assembly.
- `sequence_group`: group identifier (`left` or `right`) when assembled.
- Component-specific fields (width, slope, layer metadata) as needed.
