"""Tests for Ditch component."""

import pytest

from cross_section.core.domain.components import Ditch
from cross_section.core.domain.pavement import CrushedRockLayer
from cross_section.core.domain.section import ControlPoint


class TestDitch:
    """Tests for Ditch component."""

    def test_ditch_type_selection(self):
        """Test ditch type determined by bottom width."""
        v_ditch = Ditch(depth=1.0, bottom_width=0.0)
        assert v_ditch.ditch_type == 'v_ditch'

        trapezoid = Ditch(depth=1.0, bottom_width=1.0)
        assert trapezoid.ditch_type == 'trapezoid'

    def test_attachment_point_right(self):
        """Test attachment point at top of backslope (right side)."""
        ditch = Ditch(depth=1.0, foreslope_ratio=4.0, backslope_ratio=3.0, bottom_width=2.0)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = ditch.get_insertion_point(cp, 'right')
        attachment = ditch.get_attachment_point(insertion, 'right')

        total_width = (1.0 * 4.0) + 2.0 + (1.0 * 3.0)
        assert attachment.x == pytest.approx(0.0 + total_width)
        assert attachment.y == pytest.approx(100.0)

    def test_geometry_v_ditch(self):
        """Test v-ditch geometry produces a simple polyline."""
        ditch = Ditch(depth=1.0, bottom_width=0.0)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        geometry = ditch.to_geometry(cp, 'right')
        assert len(geometry.polygons) == 0
        assert len(geometry.polylines) == 1
        assert len(geometry.polylines[0]) == 3

    def test_geometry_with_lining(self):
        """Test lining creates a polygon."""
        lining = CrushedRockLayer(thickness=0.15, aggregate_size=37.5, density=2200)
        ditch = Ditch(depth=1.0, bottom_width=1.0, lining=lining)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        geometry = ditch.to_geometry(cp, 'right')
        assert len(geometry.polygons) == 1
        assert geometry.metadata['has_lining'] is True
        assert geometry.metadata['layers'][0]['type'] == 'CrushedRockLayer'

    def test_validate_invalid_depth(self):
        """Test validation catches shallow depth."""
        ditch = Ditch(depth=0.1, bottom_width=1.0)
        errors = ditch.validate()
        assert any('shallow' in error.lower() for error in errors)
