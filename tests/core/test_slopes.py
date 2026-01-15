"""Tests for Slope component."""

import pytest

from cross_section.core.domain.components.slopes import Slope
from cross_section.core.domain.section import ControlPoint


class TestSlope:
    """Tests for Slope component."""

    def test_create_slope_with_dimensions(self):
        """Test creating a slope with horizontal run and vertical drop."""
        slope = Slope(horizontal_run=4.0, vertical_drop=1.0)
        assert slope.horizontal_run == 4.0
        assert slope.vertical_drop == 1.0
        assert slope.surface_type == 'grass'
        assert slope.thickness == 0.0

    def test_create_slope_with_ratio_and_drop(self):
        """Test creating a slope with slope ratio and vertical drop."""
        slope = Slope(slope_ratio=4.0, vertical_drop=1.0)
        assert slope.slope_ratio == 4.0
        assert slope.vertical_drop == 1.0
        # horizontal_run should be calculated: 4.0 * 1.0 = 4.0
        assert slope.horizontal_run == pytest.approx(4.0)

    def test_create_slope_with_ratio_and_run(self):
        """Test creating a slope with slope ratio and horizontal run."""
        slope = Slope(slope_ratio=4.0, horizontal_run=8.0)
        assert slope.slope_ratio == 4.0
        assert slope.horizontal_run == 8.0
        # vertical_drop should be calculated: 8.0 / 4.0 = 2.0
        assert slope.vertical_drop == pytest.approx(2.0)

    def test_create_slope_custom_surface(self):
        """Test creating a slope with custom surface type and thickness."""
        slope = Slope(
            horizontal_run=4.0,
            vertical_drop=1.0,
            surface_type='crushed_rock',
            thickness=0.15,
        )
        assert slope.surface_type == 'crushed_rock'
        assert slope.thickness == 0.15

    def test_post_init_raises_without_dimensions(self):
        """Test that __post_init__ raises error without required dimensions."""
        with pytest.raises(ValueError, match='Must specify'):
            Slope(slope_ratio=4.0)  # Missing either horizontal_run or vertical_drop

    def test_post_init_raises_without_any_parameters(self):
        """Test that __post_init__ raises error without any dimensions."""
        with pytest.raises(ValueError, match='Must specify'):
            Slope()

    def test_insertion_point_right(self):
        """Test that slope snaps to previous attachment point (right side)."""
        slope = Slope(horizontal_run=4.0, vertical_drop=1.0)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = slope.get_insertion_point(cp, 'right')
        assert insertion.x == 0.0
        assert insertion.y == 100.0

    def test_insertion_point_left(self):
        """Test that slope snaps to previous attachment point (left side)."""
        slope = Slope(horizontal_run=4.0, vertical_drop=1.0)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = slope.get_insertion_point(cp, 'left')
        assert insertion.x == 0.0
        assert insertion.y == 100.0

    def test_attachment_point_right_downslope(self):
        """Test attachment point for right side downslope (foreslope)."""
        slope = Slope(horizontal_run=4.0, vertical_drop=1.0)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = slope.get_insertion_point(cp, 'right')
        attachment = slope.get_attachment_point(insertion, 'right')

        # Attachment should be 4.0 to the right, 1.0 down
        assert attachment.x == pytest.approx(4.0)
        assert attachment.y == pytest.approx(99.0)

    def test_attachment_point_left_downslope(self):
        """Test attachment point for left side downslope."""
        slope = Slope(horizontal_run=4.0, vertical_drop=1.0)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = slope.get_insertion_point(cp, 'left')
        attachment = slope.get_attachment_point(insertion, 'left')

        # Attachment should be 4.0 to the left, 1.0 down
        assert attachment.x == pytest.approx(-4.0)
        assert attachment.y == pytest.approx(99.0)

    def test_attachment_point_upslope(self):
        """Test attachment point for upslope (backslope - negative drop)."""
        slope = Slope(horizontal_run=2.0, vertical_drop=-1.0)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = slope.get_insertion_point(cp, 'right')
        attachment = slope.get_attachment_point(insertion, 'right')

        # Negative drop means going up
        assert attachment.x == pytest.approx(2.0)
        assert attachment.y == pytest.approx(101.0)  # Goes up by 1.0

    def test_to_geometry_right_surface_only(self):
        """Test geometry for right side slope with zero thickness."""
        slope = Slope(horizontal_run=4.0, vertical_drop=1.0, thickness=0.0)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        geometry = slope.to_geometry(cp, 'right')

        # Should have one polygon (very thin trapezoid)
        assert len(geometry.polygons) == 1
        polygon = geometry.polygons[0]
        assert len(polygon.exterior) == 4

        # Check metadata
        assert geometry.metadata['component_type'] == 'Slope'
        assert geometry.metadata['horizontal_run'] == 4.0
        assert geometry.metadata['vertical_drop'] == 1.0
        assert geometry.metadata['slope_ratio'] == pytest.approx(4.0)
        assert geometry.metadata['surface_type'] == 'grass'
        assert geometry.metadata['thickness'] == 0.0
        assert geometry.metadata['assembly_direction'] == 'right'

    def test_to_geometry_left_surface_only(self):
        """Test geometry for left side slope with zero thickness."""
        slope = Slope(horizontal_run=4.0, vertical_drop=1.0, thickness=0.0)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        geometry = slope.to_geometry(cp, 'left')

        assert len(geometry.polygons) == 1
        polygon = geometry.polygons[0]

        # Vertices should be on left side (negative X)
        for point in polygon.exterior:
            assert point.x <= 0.0

        assert geometry.metadata['assembly_direction'] == 'left'

    def test_to_geometry_right_with_thickness(self):
        """Test geometry for slope with material thickness."""
        slope = Slope(horizontal_run=4.0, vertical_drop=1.0, thickness=0.3)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        geometry = slope.to_geometry(cp, 'right')

        # Should create trapezoid with thickness
        assert len(geometry.polygons) == 1
        polygon = geometry.polygons[0]
        assert len(polygon.exterior) == 4

        # Verify thickness is applied
        assert geometry.metadata['thickness'] == 0.3

    def test_to_geometry_left_with_thickness(self):
        """Test geometry for left side slope with thickness."""
        slope = Slope(horizontal_run=4.0, vertical_drop=1.0, thickness=0.3)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        geometry = slope.to_geometry(cp, 'left')

        assert len(geometry.polygons) == 1
        polygon = geometry.polygons[0]
        assert len(polygon.exterior) == 4

    def test_geometry_upslope(self):
        """Test geometry for upslope (backslope)."""
        slope = Slope(horizontal_run=2.0, vertical_drop=-1.0)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        geometry = slope.to_geometry(cp, 'right')
        assert len(geometry.polygons) == 1
        assert geometry.metadata['vertical_drop'] == -1.0

    def test_validate_valid_slope(self):
        """Test validation passes for valid 4:1 slope."""
        slope = Slope(horizontal_run=4.0, vertical_drop=1.0)
        errors = slope.validate()
        assert errors == []

    def test_validate_valid_2_to_1_slope(self):
        """Test validation passes for valid 2:1 slope."""
        slope = Slope(horizontal_run=2.0, vertical_drop=1.0)
        errors = slope.validate()
        assert errors == []

    def test_validate_steep_slope_warning(self):
        """Test validation warns about steep slope (steeper than 1:1)."""
        slope = Slope(horizontal_run=0.5, vertical_drop=1.0)  # 0.5:1 ratio
        errors = slope.validate()
        assert any('steeper than 1:1' in error.lower() for error in errors)

    def test_validate_flat_slope_warning(self):
        """Test validation warns about very flat slope."""
        slope = Slope(horizontal_run=25.0, vertical_drop=1.0)  # 25:1 ratio
        errors = slope.validate()
        assert any('very flat' in error.lower() for error in errors)

    def test_validate_negative_horizontal_run(self):
        """Test validation catches negative horizontal run."""
        slope = Slope(horizontal_run=-4.0, vertical_drop=1.0)
        errors = slope.validate()
        assert any('horizontal run' in error.lower() and 'positive' in error.lower() for error in errors)

    def test_validate_zero_vertical_drop(self):
        """Test validation catches zero vertical drop."""
        slope = Slope(horizontal_run=4.0, vertical_drop=0.0)
        errors = slope.validate()
        assert any('vertical drop' in error.lower() and 'non-zero' in error.lower() for error in errors)

    def test_validate_negative_thickness(self):
        """Test validation catches negative thickness."""
        slope = Slope(horizontal_run=4.0, vertical_drop=1.0, thickness=-0.1)
        errors = slope.validate()
        assert any('thickness' in error.lower() and 'negative' in error.lower() for error in errors)

    def test_validate_excessive_thickness(self):
        """Test validation warns about excessive thickness."""
        slope = Slope(horizontal_run=4.0, vertical_drop=1.0, thickness=1.5)
        errors = slope.validate()
        assert any('thickness' in error.lower() and 'large' in error.lower() for error in errors)

    def test_foreslope_4_to_1(self):
        """Test typical 4:1 foreslope configuration."""
        slope = Slope(slope_ratio=4.0, vertical_drop=1.5, surface_type='grass')
        assert slope.horizontal_run == pytest.approx(6.0)
        assert slope.vertical_drop == 1.5
        errors = slope.validate()
        assert errors == []

    def test_backslope_2_to_1(self):
        """Test typical 2:1 backslope configuration."""
        slope = Slope(slope_ratio=2.0, vertical_drop=-3.0)  # Going up
        assert slope.horizontal_run == pytest.approx(6.0)
        assert slope.vertical_drop == -3.0
        errors = slope.validate()
        assert errors == []

    def test_slope_with_crushed_rock_base(self):
        """Test slope with crushed rock surface and thickness."""
        slope = Slope(
            slope_ratio=3.0,
            vertical_drop=1.0,
            surface_type='crushed_rock',
            thickness=0.15,
        )
        assert slope.surface_type == 'crushed_rock'
        assert slope.thickness == 0.15
        errors = slope.validate()
        assert errors == []

    def test_metadata_includes_calculated_ratio(self):
        """Test that metadata includes slope ratio even when specified differently."""
        slope = Slope(horizontal_run=6.0, vertical_drop=2.0)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        geometry = slope.to_geometry(cp, 'right')
        # Should calculate ratio as 6.0 / 2.0 = 3.0
        assert geometry.metadata['slope_ratio'] == pytest.approx(3.0)
