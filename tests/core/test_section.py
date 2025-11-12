"""Tests for RoadSection coordinator."""

import pytest
from cross_section.core.domain.section import RoadSection, ControlPoint, SectionGeometry
from cross_section.core.domain.components import TravelLane


class TestControlPoint:
    """Tests for ControlPoint class."""

    def test_create_control_point(self):
        """Test creating a control point."""
        cp = ControlPoint(x=0.0, elevation=100.0, description="Crown")
        assert cp.x == 0.0
        assert cp.elevation == 100.0
        assert cp.description == "Crown"

    def test_to_connection_point(self):
        """Test converting to ConnectionPoint."""
        cp = ControlPoint(x=5.0, elevation=100.0, description="Test")
        conn = cp.to_connection_point()

        assert conn.x == 5.0
        assert conn.y == 100.0
        assert conn.description == "Test"


class TestSectionGeometry:
    """Tests for SectionGeometry class."""

    def test_create_section_geometry(self):
        """Test creating section geometry."""
        geom = SectionGeometry()
        assert geom.components == []
        assert geom.metadata == {}

    def test_bounds_empty(self):
        """Test bounds of empty section."""
        geom = SectionGeometry()
        bounds = geom.bounds()
        assert bounds == (0.0, 0.0, 0.0, 0.0)


class TestRoadSection:
    """Tests for RoadSection coordinator."""

    def test_create_section(self):
        """Test creating a road section."""
        cp = ControlPoint(x=0.0, elevation=100.0)
        section = RoadSection(name="Test Section", control_point=cp)

        assert section.name == "Test Section"
        assert section.control_point.x == 0.0
        assert section.left_components == []
        assert section.right_components == []

    def test_add_component_right(self):
        """Test adding components to right side."""
        cp = ControlPoint(x=0.0, elevation=100.0)
        section = RoadSection(name="Test", control_point=cp)

        lane1 = TravelLane(width=3.6)
        lane2 = TravelLane(width=3.6)

        section.add_component_right(lane1)
        section.add_component_right(lane2)

        assert len(section.right_components) == 2
        assert len(section.left_components) == 0

    def test_add_component_left(self):
        """Test adding components to left side."""
        cp = ControlPoint(x=0.0, elevation=100.0)
        section = RoadSection(name="Test", control_point=cp)

        lane1 = TravelLane(width=3.6)
        lane2 = TravelLane(width=3.6)

        section.add_component_left(lane1)
        section.add_component_left(lane2)

        assert len(section.left_components) == 2
        assert len(section.right_components) == 0

    def test_add_component_with_direction(self):
        """Test adding components using direction parameter."""
        cp = ControlPoint(x=0.0, elevation=100.0)
        section = RoadSection(name="Test", control_point=cp)

        section.add_component(TravelLane(width=3.6), 'right')
        section.add_component(TravelLane(width=3.6), 'left')

        assert len(section.right_components) == 1
        assert len(section.left_components) == 1

    def test_validate_empty_section(self):
        """Test validation catches empty section."""
        cp = ControlPoint(x=0.0, elevation=100.0)
        section = RoadSection(name="Test", control_point=cp)

        errors = section.validate()
        assert len(errors) > 0
        assert any('at least one component' in error.lower() for error in errors)

    def test_validate_with_components(self):
        """Test validation with valid components."""
        from cross_section.core.domain.pavement import AsphaltLayer

        cp = ControlPoint(x=0.0, elevation=100.0)
        section = RoadSection(name="Test", control_point=cp)

        # Use thicker pavement to avoid validation warnings
        layers = [
            AsphaltLayer(thickness=0.10, aggregate_size=12.5, binder_type='PG 64-22',
                        binder_percentage=5.5, density=2400),
            AsphaltLayer(thickness=0.10, aggregate_size=19.0, binder_type='PG 64-22',
                        binder_percentage=5.0, density=2380),
        ]

        section.add_component_right(TravelLane(width=3.6, pavement_layers=layers))
        section.add_component_right(TravelLane(width=3.6, pavement_layers=layers))

        errors = section.validate()
        assert errors == []

    def test_validate_invalid_component(self):
        """Test validation catches invalid component."""
        cp = ControlPoint(x=0.0, elevation=100.0)
        section = RoadSection(name="Test", control_point=cp)

        section.add_component_right(TravelLane(width=-1.0))  # Invalid width

        errors = section.validate()
        assert len(errors) > 0
        assert any('right component 0' in error.lower() for error in errors)

    def test_to_geometry_single_lane_right(self):
        """Test geometry generation with single right lane."""
        cp = ControlPoint(x=0.0, elevation=100.0)
        section = RoadSection(name="Test", control_point=cp)

        section.add_component_right(TravelLane(width=3.6))

        geometry = section.to_geometry()

        assert len(geometry.components) == 1
        assert geometry.metadata['name'] == "Test"
        assert geometry.metadata['right_component_count'] == 1
        assert geometry.metadata['left_component_count'] == 0

    def test_to_geometry_symmetric_section(self):
        """Test geometry generation with symmetric left and right lanes."""
        cp = ControlPoint(x=0.0, elevation=100.0)
        section = RoadSection(name="Symmetric Road", control_point=cp)

        section.add_component_left(TravelLane(width=3.6, cross_slope=0.02))
        section.add_component_right(TravelLane(width=3.6, cross_slope=0.02))

        geometry = section.to_geometry()

        assert len(geometry.components) == 2
        assert geometry.metadata['left_component_count'] == 1
        assert geometry.metadata['right_component_count'] == 1

        # Left lane should extend in negative X direction
        left_lane_geom = geometry.components[0]
        assert left_lane_geom.polygons[0].exterior[0].x == 0.0  # Starts at control point
        assert any(p.x < 0 for p in left_lane_geom.polygons[0].exterior)  # Has negative X vertices

        # Right lane should extend in positive X direction
        right_lane_geom = geometry.components[1]
        assert right_lane_geom.polygons[0].exterior[0].x == 0.0  # Starts at control point
        assert any(p.x > 0 for p in right_lane_geom.polygons[0].exterior)  # Has positive X vertices

    def test_to_geometry_multiple_lanes_chaining(self):
        """Test geometry generation with multiple lanes snapping together."""
        cp = ControlPoint(x=0.0, elevation=100.0)
        section = RoadSection(name="Multi-Lane Road", control_point=cp)

        section.add_component_right(TravelLane(width=3.6, cross_slope=0.02))
        section.add_component_right(TravelLane(width=3.6, cross_slope=0.02))

        geometry = section.to_geometry()

        assert len(geometry.components) == 2

        # First lane starts at control point (x=0)
        first_lane_geom = geometry.components[0]
        assert first_lane_geom.polygons[0].exterior[0].x == 0.0

        # Second lane should start where first lane ended (at x=3.6)
        second_lane_geom = geometry.components[1]
        assert second_lane_geom.polygons[0].exterior[0].x == pytest.approx(3.6)

    def test_section_repr(self):
        """Test string representation."""
        cp = ControlPoint(x=0.0, elevation=100.0)
        section = RoadSection(name="Test Section", control_point=cp)
        section.add_component_right(TravelLane(width=3.6))
        section.add_component_left(TravelLane(width=3.6))

        repr_str = repr(section)
        assert "Test Section" in repr_str
        assert "2 components" in repr_str
        assert "1 left" in repr_str
        assert "1 right" in repr_str
