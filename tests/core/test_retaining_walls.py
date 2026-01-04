"""Tests for retaining wall components."""

import pytest

from cross_section.core.domain.components import MSEWall, RetainingWall
from cross_section.core.domain.components.retaining_walls import feet
from cross_section.core.domain.section import ControlPoint


class TestRetainingWall:
    """Tests for RetainingWall component."""

    def test_fill_attachment_right(self):
        """Test fill wall attaches at front/grade (right side)."""
        wall = RetainingWall(height=feet(4), thickness=feet(1), mode='fill')
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = wall.get_insertion_point(cp, 'right')
        attachment = wall.get_attachment_point(insertion, 'right')

        assert attachment.x == pytest.approx(0.0 + wall.thickness)
        assert attachment.y == pytest.approx(100.0 - wall.height)

    def test_cut_attachment_left(self):
        """Test cut wall attaches at top/back (left side)."""
        wall = RetainingWall(height=feet(4), thickness=feet(1), mode='cut')
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = wall.get_insertion_point(cp, 'left')
        attachment = wall.get_attachment_point(insertion, 'left')

        assert attachment.x == pytest.approx(0.0 - wall.thickness)
        assert attachment.y == pytest.approx(100.0 + wall.height)

    def test_geometry_backfill_toggle(self):
        """Test backfill polygon is optional."""
        wall = RetainingWall(mode='fill', show_backfill=True)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        geometry = wall.to_geometry(cp, 'right')
        assert len(geometry.polygons) == 3

        wall_no_fill = RetainingWall(mode='fill', show_backfill=False)
        geometry_no_fill = wall_no_fill.to_geometry(cp, 'right')
        assert len(geometry_no_fill.polygons) == 2

    def test_validate_invalid_mode(self):
        """Test validation catches invalid mode."""
        wall = RetainingWall(mode='invalid')
        errors = wall.validate()
        assert any('mode' in error.lower() for error in errors)


class TestMSEWall:
    """Tests for MSEWall component."""

    def test_fill_insertion_offset(self):
        """Test insertion offset for fill mode uses coping width."""
        wall = MSEWall(mode='fill', coping_width=feet(2))
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion_right = wall.get_insertion_point(cp, 'right')
        insertion_left = wall.get_insertion_point(cp, 'left')

        assert insertion_right.x == pytest.approx(0.0 - wall.coping_width)
        assert insertion_left.x == pytest.approx(0.0 + wall.coping_width)

    def test_geometry_includes_backfill_hatch(self):
        """Test MSE wall adds hatch polylines and styles."""
        wall = MSEWall(mode='fill', show_backfill=True)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        geometry = wall.to_geometry(cp, 'right')
        assert len(geometry.polygons) == 3
        assert len(geometry.polylines) >= 2

        styles = geometry.metadata.get('polyline_styles', [])
        assert len(styles) == len(geometry.polylines)
        assert styles[0].get('stroke_dasharray') == '6,4'

        boundary = geometry.polylines[0]
        assert boundary[0].x == pytest.approx(boundary[-1].x)
        assert boundary[0].y == pytest.approx(boundary[-1].y)
