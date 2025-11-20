"""Tests for Shoring component."""

import pytest
from cross_section.core.domain.components import Shoring
from cross_section.core.domain.section import ControlPoint


class TestShoring:
    """Tests for Shoring component."""

    def test_create_shoring_defaults(self):
        """Test creating a shoring wall with defaults."""
        shoring = Shoring()
        assert shoring.height == 1.219  # 4 feet in meters
        assert shoring.thickness == 0.203  # 8 inches in meters
        assert shoring.mode == 'fill'

    def test_create_shoring_custom(self):
        """Test creating shoring with custom parameters."""
        shoring = Shoring(
            height=3.05,  # 10 feet
            thickness=0.25,  # ~10 inches
            mode='cut'
        )
        assert shoring.height == 3.05
        assert shoring.thickness == 0.25
        assert shoring.mode == 'cut'

    def test_insertion_point_right(self):
        """Test that shoring snaps to previous attachment point (right side)."""
        shoring = Shoring()
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = shoring.get_insertion_point(cp, 'right')
        assert insertion.x == 0.0
        assert insertion.y == 100.0

    def test_insertion_point_left(self):
        """Test that shoring snaps to previous attachment point (left side)."""
        shoring = Shoring()
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = shoring.get_insertion_point(cp, 'left')
        assert insertion.x == 0.0
        assert insertion.y == 100.0

    def test_attachment_point_fill_right(self):
        """Test attachment point for fill mode (right side)."""
        shoring = Shoring(height=3.0, thickness=0.2, mode='fill')
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = shoring.get_insertion_point(cp, 'right')
        attachment = shoring.get_attachment_point(insertion, 'right')

        # Should be offset in positive X direction by thickness
        assert attachment.x == 0.2
        # Should drop by height (fill mode goes down)
        assert attachment.y == pytest.approx(100.0 - 3.0)

    def test_attachment_point_fill_left(self):
        """Test attachment point for fill mode (left side)."""
        shoring = Shoring(height=3.0, thickness=0.2, mode='fill')
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = shoring.get_insertion_point(cp, 'left')
        attachment = shoring.get_attachment_point(insertion, 'left')

        # Should be offset in negative X direction by thickness
        assert attachment.x == -0.2
        # Should drop by height (fill mode goes down)
        assert attachment.y == pytest.approx(100.0 - 3.0)

    def test_attachment_point_cut_right(self):
        """Test attachment point for cut mode (right side)."""
        shoring = Shoring(height=3.0, thickness=0.2, mode='cut')
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = shoring.get_insertion_point(cp, 'right')
        attachment = shoring.get_attachment_point(insertion, 'right')

        # Should be offset in positive X direction by thickness
        assert attachment.x == 0.2
        # Should rise by height (cut mode goes up)
        assert attachment.y == pytest.approx(100.0 + 3.0)

    def test_attachment_point_cut_left(self):
        """Test attachment point for cut mode (left side)."""
        shoring = Shoring(height=3.0, thickness=0.2, mode='cut')
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = shoring.get_insertion_point(cp, 'left')
        attachment = shoring.get_attachment_point(insertion, 'left')

        # Should be offset in negative X direction by thickness
        assert attachment.x == -0.2
        # Should rise by height (cut mode goes up)
        assert attachment.y == pytest.approx(100.0 + 3.0)

    def test_to_geometry_fill_right(self):
        """Test geometry generation for fill mode (right side)."""
        shoring = Shoring(height=3.0, thickness=0.2, mode='fill')
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = shoring.get_insertion_point(cp, 'right')
        geometry = shoring.to_geometry(insertion, 'right')

        # Should have one rectangular polygon
        assert len(geometry.polygons) == 1
        assert len(geometry.polygons[0].exterior) == 4

        # Check vertices for fill mode right side
        vertices = geometry.polygons[0].exterior
        # Top inside
        assert vertices[0].x == 0.0
        assert vertices[0].y == 100.0
        # Top outside
        assert vertices[1].x == 0.2
        assert vertices[1].y == 100.0
        # Bottom outside
        assert vertices[2].x == 0.2
        assert vertices[2].y == 97.0  # 100 - 3
        # Bottom inside
        assert vertices[3].x == 0.0
        assert vertices[3].y == 97.0

        # Check metadata
        assert geometry.metadata['component_type'] == 'Shoring'
        assert geometry.metadata['height'] == 3.0
        assert geometry.metadata['thickness'] == 0.2
        assert geometry.metadata['mode'] == 'fill'
        assert geometry.metadata['assembly_direction'] == 'right'
        assert geometry.metadata['material'] == 'corrugated_steel'

    def test_to_geometry_fill_left(self):
        """Test geometry generation for fill mode (left side)."""
        shoring = Shoring(height=3.0, thickness=0.2, mode='fill')
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = shoring.get_insertion_point(cp, 'left')
        geometry = shoring.to_geometry(insertion, 'left')

        # Should have one rectangular polygon
        assert len(geometry.polygons) == 1
        assert len(geometry.polygons[0].exterior) == 4

        # Check vertices for fill mode left side
        vertices = geometry.polygons[0].exterior
        # Top inside
        assert vertices[0].x == 0.0
        assert vertices[0].y == 100.0
        # Bottom inside
        assert vertices[1].x == 0.0
        assert vertices[1].y == 97.0
        # Bottom outside
        assert vertices[2].x == -0.2
        assert vertices[2].y == 97.0
        # Top outside
        assert vertices[3].x == -0.2
        assert vertices[3].y == 100.0

        # Check metadata
        assert geometry.metadata['component_type'] == 'Shoring'
        assert geometry.metadata['mode'] == 'fill'
        assert geometry.metadata['assembly_direction'] == 'left'

    def test_to_geometry_cut_right(self):
        """Test geometry generation for cut mode (right side)."""
        shoring = Shoring(height=3.0, thickness=0.2, mode='cut')
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = shoring.get_insertion_point(cp, 'right')
        geometry = shoring.to_geometry(insertion, 'right')

        # Should have one rectangular polygon
        assert len(geometry.polygons) == 1
        assert len(geometry.polygons[0].exterior) == 4

        # Check vertices for cut mode right side
        vertices = geometry.polygons[0].exterior
        # Bottom inside
        assert vertices[0].x == 0.0
        assert vertices[0].y == 100.0
        # Bottom outside
        assert vertices[1].x == 0.2
        assert vertices[1].y == 100.0
        # Top outside
        assert vertices[2].x == 0.2
        assert vertices[2].y == 103.0  # 100 + 3
        # Top inside
        assert vertices[3].x == 0.0
        assert vertices[3].y == 103.0

        # Check metadata
        assert geometry.metadata['component_type'] == 'Shoring'
        assert geometry.metadata['mode'] == 'cut'
        assert geometry.metadata['assembly_direction'] == 'right'

    def test_to_geometry_cut_left(self):
        """Test geometry generation for cut mode (left side)."""
        shoring = Shoring(height=3.0, thickness=0.2, mode='cut')
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = shoring.get_insertion_point(cp, 'left')
        geometry = shoring.to_geometry(insertion, 'left')

        # Should have one rectangular polygon
        assert len(geometry.polygons) == 1
        assert len(geometry.polygons[0].exterior) == 4

        # Check vertices for cut mode left side
        vertices = geometry.polygons[0].exterior
        # Bottom inside
        assert vertices[0].x == 0.0
        assert vertices[0].y == 100.0
        # Top inside
        assert vertices[1].x == 0.0
        assert vertices[1].y == 103.0
        # Top outside
        assert vertices[2].x == -0.2
        assert vertices[2].y == 103.0
        # Bottom outside
        assert vertices[3].x == -0.2
        assert vertices[3].y == 100.0

        # Check metadata
        assert geometry.metadata['component_type'] == 'Shoring'
        assert geometry.metadata['mode'] == 'cut'
        assert geometry.metadata['assembly_direction'] == 'left'

    def test_validate_valid_fill(self):
        """Test validation of valid fill shoring."""
        shoring = Shoring(height=3.0, thickness=0.2, mode='fill')
        errors = shoring.validate()
        assert errors == []

    def test_validate_valid_cut(self):
        """Test validation of valid cut shoring."""
        shoring = Shoring(height=3.0, thickness=0.2, mode='cut')
        errors = shoring.validate()
        assert errors == []

    def test_validate_negative_height(self):
        """Test validation catches negative height."""
        shoring = Shoring(height=-1.0)
        errors = shoring.validate()
        assert len(errors) > 0
        assert any('positive' in error.lower() for error in errors)

    def test_validate_zero_height(self):
        """Test validation catches zero height."""
        shoring = Shoring(height=0.0)
        errors = shoring.validate()
        assert len(errors) > 0
        assert any('positive' in error.lower() for error in errors)

    def test_validate_very_short_height(self):
        """Test validation warns about very short shoring."""
        shoring = Shoring(height=0.2)
        errors = shoring.validate()
        assert len(errors) > 0
        assert any('very short' in error.lower() for error in errors)

    def test_validate_excessive_height(self):
        """Test validation warns about excessive height."""
        shoring = Shoring(height=20.0)
        errors = shoring.validate()
        assert len(errors) > 0
        assert any('exceeds' in error.lower() for error in errors)

    def test_validate_negative_thickness(self):
        """Test validation catches negative thickness."""
        shoring = Shoring(thickness=-0.1)
        errors = shoring.validate()
        assert len(errors) > 0
        assert any('positive' in error.lower() for error in errors)

    def test_validate_zero_thickness(self):
        """Test validation catches zero thickness."""
        shoring = Shoring(thickness=0.0)
        errors = shoring.validate()
        assert len(errors) > 0
        assert any('positive' in error.lower() for error in errors)

    def test_validate_very_thin_thickness(self):
        """Test validation warns about very thin shoring."""
        shoring = Shoring(thickness=0.01)
        errors = shoring.validate()
        assert len(errors) > 0
        assert any('very thin' in error.lower() for error in errors)

    def test_validate_excessive_thickness(self):
        """Test validation warns about excessive thickness."""
        shoring = Shoring(thickness=1.0)
        errors = shoring.validate()
        assert len(errors) > 0
        assert any('very large' in error.lower() for error in errors)

    def test_validate_invalid_mode(self):
        """Test validation catches invalid mode."""
        shoring = Shoring(mode='invalid')
        errors = shoring.validate()
        assert len(errors) > 0
        assert any("must be 'fill' or 'cut'" in error.lower() for error in errors)
