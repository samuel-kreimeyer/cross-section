"""Tests for Barrier component."""

import pytest

from cross_section.core.domain.components import (
    Barrier,
    CABLE_3_STRAND,
    JERSEY_32,
    W_BEAM_BLOCKOUT,
)
from cross_section.core.domain.section import ControlPoint


class TestBarrier:
    """Tests for Barrier component."""

    def test_insertion_point(self):
        """Test that barrier snaps to previous attachment point."""
        barrier = Barrier(spec=JERSEY_32, front_prepared_width=0.6, back_prepared_width=0.4)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = barrier.get_insertion_point(cp, 'right')
        assert insertion.x == 0.0
        assert insertion.y == 100.0

    def test_attachment_point_right(self):
        """Test attachment point uses prepared surface width (right side)."""
        barrier = Barrier(
            spec=JERSEY_32,
            front_prepared_width=0.6,
            back_prepared_width=0.4,
            back_surface_delta=0.1,
        )
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = barrier.get_insertion_point(cp, 'right')
        attachment = barrier.get_attachment_point(insertion, 'right')

        expected_x = 0.0 + 0.6 + JERSEY_32.footprint_width + 0.4
        expected_y = 100.0 + 0.1
        assert attachment.x == pytest.approx(expected_x)
        assert attachment.y == pytest.approx(expected_y)

    def test_concrete_barrier_geometry(self):
        """Test concrete barrier creates a single polygon profile."""
        barrier = Barrier(spec=JERSEY_32, front_prepared_width=0.6, back_prepared_width=0.4)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        geometry = barrier.to_geometry(cp, 'right')
        assert len(geometry.polygons) == 1
        assert len(geometry.polylines) == 0
        assert len(geometry.polygons[0].exterior) == len(JERSEY_32.profile_points)

    def test_guardrail_geometry_w_beam_direction(self):
        """Test guardrail has block/post polygons and W-beam polyline."""
        barrier = Barrier(spec=W_BEAM_BLOCKOUT, front_prepared_width=0.6)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        geometry = barrier.to_geometry(cp, 'right')
        assert len(geometry.polygons) == 2
        assert len(geometry.polylines) == 1

        rail = geometry.polylines[0]
        assert len(rail) == 5
        x_face = rail[0].x
        assert min(p.x for p in rail) < x_face

    def test_cable_barrier_holes(self):
        """Test cable barrier creates hole polylines and polygon holes."""
        barrier = Barrier(spec=CABLE_3_STRAND, front_prepared_width=0.6)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        geometry = barrier.to_geometry(cp, 'right')
        assert len(geometry.polygons) == 1
        assert len(geometry.polylines) == CABLE_3_STRAND.hole_count

        post_poly = geometry.polygons[0]
        assert post_poly.holes is not None
        assert len(post_poly.holes) == CABLE_3_STRAND.hole_count

        for polyline in geometry.polylines:
            assert polyline[0].x == pytest.approx(polyline[-1].x)
            assert polyline[0].y == pytest.approx(polyline[-1].y)

    def test_validate_negative_prepared_width(self):
        """Test validation catches negative prepared width."""
        barrier = Barrier(spec=JERSEY_32, front_prepared_width=-0.1)
        errors = barrier.validate()
        assert any('prepared' in error.lower() for error in errors)
