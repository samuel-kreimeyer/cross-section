"""Tests for road components."""

import pytest
from cross_section.core.domain.components import TravelLane
from cross_section.core.domain.section import ControlPoint


class TestTravelLane:
    """Tests for TravelLane component."""

    def test_create_lane(self):
        """Test creating a travel lane with defaults."""
        lane = TravelLane(width=3.6)
        assert lane.width == 3.6
        assert lane.cross_slope == 0.02
        assert lane.traffic_direction == 'outbound'
        assert lane.surface_type == 'asphalt'

    def test_create_lane_custom(self):
        """Test creating a lane with custom parameters."""
        lane = TravelLane(
            width=3.0,
            cross_slope=0.025,
            traffic_direction='inbound',
            surface_type='concrete'
        )
        assert lane.width == 3.0
        assert lane.cross_slope == 0.025
        assert lane.traffic_direction == 'inbound'
        assert lane.surface_type == 'concrete'

    def test_insertion_point_right(self):
        """Test that lane snaps to previous attachment point (right side)."""
        lane = TravelLane(width=3.6)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = lane.get_insertion_point(cp, 'right')
        assert insertion.x == 0.0
        assert insertion.y == 100.0

    def test_insertion_point_left(self):
        """Test that lane snaps to previous attachment point (left side)."""
        lane = TravelLane(width=3.6)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = lane.get_insertion_point(cp, 'left')
        assert insertion.x == 0.0
        assert insertion.y == 100.0

    def test_attachment_point_right(self):
        """Test attachment point calculation with cross slope (right side)."""
        lane = TravelLane(width=3.6, cross_slope=0.02)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = lane.get_insertion_point(cp, 'right')
        attachment = lane.get_attachment_point(insertion, 'right')

        # Should be offset in positive X direction
        assert attachment.x == 3.6
        # Should drop by width * cross_slope
        expected_drop = 3.6 * 0.02
        assert attachment.y == pytest.approx(100.0 - expected_drop)

    def test_attachment_point_left(self):
        """Test attachment point calculation with cross slope (left side)."""
        lane = TravelLane(width=3.6, cross_slope=0.02)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = lane.get_insertion_point(cp, 'left')
        attachment = lane.get_attachment_point(insertion, 'left')

        # Should be offset in negative X direction
        assert attachment.x == -3.6
        # Should drop by width * cross_slope
        expected_drop = 3.6 * 0.02
        assert attachment.y == pytest.approx(100.0 - expected_drop)

    def test_to_geometry_right(self):
        """Test geometry generation for right side."""
        lane = TravelLane(width=3.6, cross_slope=0.02)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = lane.get_insertion_point(cp, 'right')
        geometry = lane.to_geometry(insertion, 'right')

        # Should have one polygon
        assert len(geometry.polygons) == 1
        assert len(geometry.polygons[0].exterior) == 4

        # Check metadata
        assert geometry.metadata['component_type'] == 'TravelLane'
        assert geometry.metadata['width'] == 3.6
        assert geometry.metadata['cross_slope'] == 0.02
        assert geometry.metadata['assembly_direction'] == 'right'

    def test_to_geometry_left(self):
        """Test geometry generation for left side."""
        lane = TravelLane(width=3.6, cross_slope=0.02)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = lane.get_insertion_point(cp, 'left')
        geometry = lane.to_geometry(insertion, 'left')

        # Should have one polygon
        assert len(geometry.polygons) == 1
        assert len(geometry.polygons[0].exterior) == 4

        # Check metadata
        assert geometry.metadata['component_type'] == 'TravelLane'
        assert geometry.metadata['width'] == 3.6
        assert geometry.metadata['cross_slope'] == 0.02
        assert geometry.metadata['assembly_direction'] == 'left'

    def test_validate_valid(self):
        """Test validation of valid lane."""
        lane = TravelLane(width=3.6, cross_slope=0.02)
        errors = lane.validate()
        assert errors == []

    def test_validate_negative_width(self):
        """Test validation catches negative width."""
        lane = TravelLane(width=-1.0)
        errors = lane.validate()
        assert len(errors) > 0
        assert any('positive' in error.lower() for error in errors)

    def test_validate_narrow_width(self):
        """Test validation warns about narrow lanes."""
        lane = TravelLane(width=2.5)
        errors = lane.validate()
        assert len(errors) > 0
        assert any('minimum' in error.lower() for error in errors)

    def test_validate_excessive_slope(self):
        """Test validation catches excessive cross slope."""
        lane = TravelLane(width=3.6, cross_slope=0.10)
        errors = lane.validate()
        assert len(errors) > 0
        assert any('slope' in error.lower() for error in errors)

    def test_validate_insufficient_slope(self):
        """Test validation warns about insufficient drainage slope."""
        lane = TravelLane(width=3.6, cross_slope=0.01)
        errors = lane.validate()
        assert len(errors) > 0
        assert any('drainage' in error.lower() for error in errors)
