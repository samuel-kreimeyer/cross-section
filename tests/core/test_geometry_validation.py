"""Tests for Shapely-based geometry validation."""

import pytest

from cross_section.core.geometry.primitives import ComponentGeometry, Point2D, Polygon
from cross_section.core.geometry.validate import (
    clip_hatched_polylines,
    clip_overlap_allowed_polygons,
    validate_section_geometry,
)

pytest.importorskip("shapely")


def _square(x0: float, y0: float, size: float) -> Polygon:
    return Polygon(
        exterior=[
            Point2D(x0, y0),
            Point2D(x0 + size, y0),
            Point2D(x0 + size, y0 + size),
            Point2D(x0, y0 + size),
        ]
    )


class TestGeometryValidation:
    """Tests for overlap validation behavior."""

    def test_overlap_within_component_allowed(self):
        """Overlapping polygons inside a single component are allowed."""
        poly_a = _square(0.0, 0.0, 1.0)
        poly_b = _square(0.5, 0.5, 1.0)
        component = ComponentGeometry(polygons=[poly_a, poly_b])

        errors = validate_section_geometry([component])
        assert errors == []

    def test_overlap_between_components_rejected(self):
        """Overlaps between separate components are flagged."""
        comp_a = ComponentGeometry(polygons=[_square(0.0, 0.0, 1.0)], metadata={"component_type": "A"})
        comp_b = ComponentGeometry(polygons=[_square(0.5, 0.5, 1.0)], metadata={"component_type": "B"})

        errors = validate_section_geometry([comp_a, comp_b])
        assert any("overlaps" in error for error in errors)

    def test_overlap_allowed_polygons_excluded(self):
        """Polygons flagged as overlap-allowed are excluded from overlap checks."""
        backfill = ComponentGeometry(
            polygons=[_square(0.0, 0.0, 1.0)],
            metadata={"component_type": "Backfill", "overlap_allow_polygons": [0]},
        )
        wall = ComponentGeometry(
            polygons=[_square(0.5, 0.5, 1.0)],
            metadata={"component_type": "Wall"},
        )

        errors = validate_section_geometry([backfill, wall])
        assert errors == []

    def test_clip_overlap_allowed_polygons(self):
        """Overlap-allowed polygons can be clipped to other component solids."""
        backfill = ComponentGeometry(
            polygons=[_square(0.0, 0.0, 1.0)],
            metadata={"component_type": "Backfill", "overlap_allow_polygons": [0]},
        )
        wall = ComponentGeometry(
            polygons=[_square(0.5, 0.5, 1.0)],
            metadata={"component_type": "Wall"},
        )

        clipped = clip_overlap_allowed_polygons([backfill, wall])
        errors = validate_section_geometry(clipped)
        assert errors == []

        original_area = backfill.polygons[0].area()
        clipped_area = sum(poly.area() for poly in clipped[0].polygons)
        assert clipped_area < original_area

    def test_clip_hatched_polylines(self):
        """Hatchet polylines are clipped against other component solids."""
        boundary = [
            Point2D(0.0, 0.0),
            Point2D(2.0, 0.0),
            Point2D(2.0, 2.0),
            Point2D(0.0, 2.0),
            Point2D(0.0, 0.0),
        ]
        hatch_component = ComponentGeometry(
            polygons=[],
            polylines=[boundary],
            metadata={
                "component_type": "Hatch",
                "hatch_boundary_index": 0,
                "hatch_spacing": 0.5,
                "hatch_orientation": "horizontal",
            },
        )
        blocker = ComponentGeometry(
            polygons=[_square(1.0, 1.0, 1.0)],
            metadata={"component_type": "Blocker"},
        )

        clipped = clip_hatched_polylines([hatch_component, blocker])
        clipped_boundary = clipped[0].polylines[0]

        assert any(point.x < 1.0 for point in clipped_boundary)

    def test_gap_between_components_detected(self):
        """Adjacent components with a gap are flagged."""
        left = ComponentGeometry(
            polygons=[_square(0.0, 0.0, 1.0)],
            metadata={"component_type": "Left", "sequence_group": "right"},
        )
        right = ComponentGeometry(
            polygons=[_square(2.0, 0.0, 1.0)],
            metadata={"component_type": "Right", "sequence_group": "right"},
        )

        errors = validate_section_geometry([left, right])
        assert any("gap" in error for error in errors)

    def test_gap_skipped_between_groups(self):
        """Gaps between different assembly groups are ignored."""
        left = ComponentGeometry(
            polygons=[_square(0.0, 0.0, 1.0)],
            metadata={"component_type": "Left", "sequence_group": "left"},
        )
        right = ComponentGeometry(
            polygons=[_square(2.0, 0.0, 1.0)],
            metadata={"component_type": "Right", "sequence_group": "right"},
        )

        errors = validate_section_geometry([left, right])
        assert errors == []

    def test_polyline_crossing_detected(self):
        """Crossing polylines are flagged."""
        line_a = [Point2D(0.0, 0.0), Point2D(1.0, 1.0)]
        line_b = [Point2D(0.0, 1.0), Point2D(1.0, 0.0)]
        comp_a = ComponentGeometry(polylines=[line_a], metadata={"component_type": "A"})
        comp_b = ComponentGeometry(polylines=[line_b], metadata={"component_type": "B"})

        errors = validate_section_geometry([comp_a, comp_b])
        assert any("polyline" in error.lower() for error in errors)
