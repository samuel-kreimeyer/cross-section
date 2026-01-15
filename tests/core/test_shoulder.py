"""Tests for Shoulder component."""

import pytest
from cross_section.core.domain import Shoulder, ControlPoint
from cross_section.core.domain.pavement import AsphaltLayer, CrushedRockLayer


class TestShoulder:
    """Tests for Shoulder component."""

    def test_create_shoulder(self):
        """Test creating a shoulder with defaults."""
        shoulder = Shoulder(width=2.4)
        assert shoulder.width == 2.4
        assert shoulder.cross_slope == 0.02
        assert shoulder.foreslope_ratio == 6.0
        assert shoulder.paved is True
        assert len(shoulder.pavement_layers) == 1

    def test_create_custom_shoulder(self):
        """Test creating shoulder with custom parameters."""
        layers = [
            AsphaltLayer(thickness=0.04, aggregate_size=12.5, binder_type='PG 64-22',
                        binder_percentage=5.5, density=2400),
            CrushedRockLayer(thickness=0.15, aggregate_size=37.5, density=2200),
        ]

        shoulder = Shoulder(
            width=3.0,
            cross_slope=0.025,
            foreslope_ratio=4.0,
            paved=True,
            pavement_layers=layers
        )

        assert shoulder.width == 3.0
        assert shoulder.cross_slope == 0.025
        assert shoulder.foreslope_ratio == 4.0
        assert len(shoulder.pavement_layers) == 2

    def test_insertion_point(self):
        """Test that shoulder snaps to previous attachment point."""
        shoulder = Shoulder(width=2.4)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = shoulder.get_insertion_point(cp, 'right')
        assert insertion.x == 0.0
        assert insertion.y == 100.0

    def test_attachment_point_right(self):
        """Test attachment point at outermost bottom corner (right side)."""
        shoulder = Shoulder(width=2.4, cross_slope=0.02)
        cp = ControlPoint(x=3.6, elevation=99.928).to_connection_point()

        insertion = shoulder.get_insertion_point(cp, 'right')
        attachment = shoulder.get_attachment_point(insertion, 'right')

        total_depth = sum(layer.thickness for layer in shoulder.pavement_layers)
        expected_extension = total_depth * shoulder.foreslope_ratio

        # Should be at outermost extent of the bottom of pavement
        assert attachment.x == pytest.approx(3.6 + 2.4 + expected_extension)
        # Should drop by cross slope plus total pavement depth
        expected_drop = (2.4 * 0.02) + total_depth
        assert attachment.y == pytest.approx(99.928 - expected_drop)

    def test_attachment_point_left(self):
        """Test attachment point at outermost bottom corner (left side)."""
        shoulder = Shoulder(width=2.4, cross_slope=0.02)
        cp = ControlPoint(x=-3.6, elevation=99.928).to_connection_point()

        insertion = shoulder.get_insertion_point(cp, 'left')
        attachment = shoulder.get_attachment_point(insertion, 'left')

        total_depth = sum(layer.thickness for layer in shoulder.pavement_layers)
        expected_extension = total_depth * shoulder.foreslope_ratio

        # Should extend in negative X to outermost extent of the bottom of pavement
        assert attachment.x == pytest.approx(-3.6 - 2.4 - expected_extension)
        expected_drop = (2.4 * 0.02) + total_depth
        assert attachment.y == pytest.approx(99.928 - expected_drop)

    def test_trapezoid_geometry(self):
        """Test that shoulder creates trapezoid-shaped layers."""
        layers = [
            AsphaltLayer(thickness=0.04, aggregate_size=12.5, binder_type='PG 64-22',
                        binder_percentage=5.5, density=2400),
            CrushedRockLayer(thickness=0.15, aggregate_size=37.5, density=2200),
        ]

        shoulder = Shoulder(
            width=2.4,
            cross_slope=0.02,
            foreslope_ratio=6.0,
            paved=True,
            pavement_layers=layers
        )

        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()
        insertion = shoulder.get_insertion_point(cp, 'right')
        geometry = shoulder.to_geometry(insertion, 'right')

        # Should have 2 polygons (one per layer)
        assert len(geometry.polygons) == 2

        # Check trapezoid dimensions
        # Layer 0: surface, depth 0 to 0.04m
        # - Top extends: 2.4 + 0*6 = 2.4m
        # - Bottom extends: 2.4 + 0.04*6 = 2.64m
        layer0_poly = geometry.polygons[0]
        layer0_x_coords = [p.x for p in layer0_poly.exterior]
        layer0_width = max(layer0_x_coords) - min(layer0_x_coords)
        assert layer0_width == pytest.approx(2.64, abs=0.01)

        # Layer 1: base, depth 0.04 to 0.19m
        # - Top extends: 2.4 + 0.04*6 = 2.64m
        # - Bottom extends: 2.4 + 0.19*6 = 3.54m
        layer1_poly = geometry.polygons[1]
        layer1_x_coords = [p.x for p in layer1_poly.exterior]
        layer1_width = max(layer1_x_coords) - min(layer1_x_coords)
        assert layer1_width == pytest.approx(3.54, abs=0.01)

        # Bottom layer should be wider than top layer
        assert layer1_width > layer0_width

    def test_foreslope_extension_calculation(self):
        """Test that foreslope extension is calculated correctly."""
        # Example from user: 2ft wide, 1ft deep pavement should extend to 8ft at bottom
        # In meters: 0.61m wide, 0.305m deep should extend to 2.44m at bottom
        shoulder = Shoulder(
            width=0.61,  # ~2ft
            foreslope_ratio=6.0,
            pavement_layers=[
                AsphaltLayer(thickness=0.305, aggregate_size=12.5, binder_type='PG 64-22',
                            binder_percentage=5.5, density=2400)
            ]
        )

        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()
        insertion = shoulder.get_insertion_point(cp, 'right')
        geometry = shoulder.to_geometry(insertion, 'right')

        # Single polygon
        poly = geometry.polygons[0]
        x_coords = [p.x for p in poly.exterior]

        # Top should be at paved width: 0.61m
        # Bottom should extend: 0.61 + 0.305*6 = 0.61 + 1.83 = 2.44m (~8ft)
        width = max(x_coords) - min(x_coords)
        assert width == pytest.approx(2.44, abs=0.01)

    def test_validate_valid_shoulder(self):
        """Test validation of valid shoulder."""
        shoulder = Shoulder(
            width=2.4,
            cross_slope=0.02,
            foreslope_ratio=6.0,
            pavement_layers=[
                AsphaltLayer(thickness=0.04, aggregate_size=12.5, binder_type='PG 64-22',
                            binder_percentage=5.5, density=2400),
                CrushedRockLayer(thickness=0.10, aggregate_size=37.5, density=2200),
            ]
        )
        errors = shoulder.validate()
        assert errors == []

    def test_validate_steep_foreslope(self):
        """Test validation warns about steep foreslopes."""
        shoulder = Shoulder(width=2.4, foreslope_ratio=3.0)  # 3:1 is steep
        errors = shoulder.validate()
        assert len(errors) > 0
        assert any('barrier' in error.lower() or 'steep' in error.lower() for error in errors)

    def test_validate_very_steep_foreslope(self):
        """Test validation catches very steep (unsafe) foreslopes."""
        shoulder = Shoulder(width=2.4, foreslope_ratio=1.5)  # 1.5:1 is very steep
        errors = shoulder.validate()
        assert len(errors) > 0
        assert any('too steep' in error.lower() for error in errors)

    def test_metadata_includes_foreslope(self):
        """Test that geometry metadata includes foreslope information."""
        shoulder = Shoulder(width=2.4, foreslope_ratio=6.0)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = shoulder.get_insertion_point(cp, 'right')
        geometry = shoulder.to_geometry(insertion, 'right')

        assert geometry.metadata['component_type'] == 'Shoulder'
        assert geometry.metadata['width'] == 2.4
        assert geometry.metadata['foreslope_ratio'] == 6.0
        assert geometry.metadata['paved'] is True

    def test_fully_paved_mode_single_asphalt_layer(self):
        """Test fully_paved mode with single asphalt layer creates slumped geometry."""
        shoulder = Shoulder(
            width=2.4,
            cross_slope=0.02,
            foreslope_ratio=6.0,
            paved=True,
            pavement_layers=[
                AsphaltLayer(thickness=0.10, aggregate_size=12.5, binder_type='PG 64-22',
                            binder_percentage=5.5, density=2400),
            ],
            shoulder_type="paved_top_slumped",
        )

        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()
        insertion = shoulder.get_insertion_point(cp, 'right')
        geometry = shoulder.to_geometry(insertion, 'right')

        # Should have 1 polygon for the asphalt layer
        assert len(geometry.polygons) == 1

        # Asphalt layer with 1:1 slump: bottom width = top width + thickness
        # Top width: 2.4m, bottom width: 2.4 + 0.10 = 2.5m
        poly = geometry.polygons[0]
        assert len(poly.exterior) == 4  # Trapezoid

        x_coords = [p.x for p in poly.exterior]
        width = max(x_coords) - min(x_coords)
        assert width == pytest.approx(2.5, abs=0.01)

    def test_fully_paved_mode_multiple_asphalt_layers(self):
        """Test fully_paved mode with multiple asphalt layers creates stacked slumped geometry."""
        shoulder = Shoulder(
            width=2.4,
            cross_slope=0.02,
            foreslope_ratio=6.0,
            paved=True,
            pavement_layers=[
                AsphaltLayer(thickness=0.05, aggregate_size=9.5, binder_type='PG 64-22',
                            binder_percentage=5.5, density=2400),
                AsphaltLayer(thickness=0.08, aggregate_size=19.0, binder_type='PG 64-22',
                            binder_percentage=5.0, density=2400),
            ],
            shoulder_type="paved_top_slumped",
        )

        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()
        insertion = shoulder.get_insertion_point(cp, 'right')
        geometry = shoulder.to_geometry(insertion, 'right')

        # Should have 2 polygons (one per asphalt layer)
        assert len(geometry.polygons) == 2

        # First layer (top): width 2.4 at top, 2.4 + 0.05 = 2.45 at bottom
        poly0 = geometry.polygons[0]
        x_coords0 = [p.x for p in poly0.exterior]
        width0 = max(x_coords0) - min(x_coords0)
        assert width0 == pytest.approx(2.45, abs=0.01)

        # Second layer: width 2.45 at top, 2.45 + 0.08 = 2.53 at bottom
        poly1 = geometry.polygons[1]
        x_coords1 = [p.x for p in poly1.exterior]
        width1 = max(x_coords1) - min(x_coords1)
        assert width1 == pytest.approx(2.53, abs=0.01)

    def test_fully_paved_mode_with_base_layer(self):
        """Test fully_paved mode with asphalt and base creates 5-vertex base polygon."""
        shoulder = Shoulder(
            width=2.4,
            cross_slope=0.02,
            foreslope_ratio=6.0,
            paved=True,
            pavement_layers=[
                AsphaltLayer(thickness=0.10, aggregate_size=12.5, binder_type='PG 64-22',
                            binder_percentage=5.5, density=2400),
                CrushedRockLayer(thickness=0.20, aggregate_size=37.5, density=2200),
            ],
            shoulder_type="paved_top_slumped",
        )

        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()
        insertion = shoulder.get_insertion_point(cp, 'right')
        geometry = shoulder.to_geometry(insertion, 'right')

        # Should have 2 polygons: asphalt + base
        assert len(geometry.polygons) == 2

        # Asphalt layer: 4 vertices (trapezoid)
        asphalt_poly = geometry.polygons[0]
        assert len(asphalt_poly.exterior) == 4

        # Base layer: 5 vertices (irregular polygon extending to foreslope)
        base_poly = geometry.polygons[1]
        assert len(base_poly.exterior) == 5

    def test_fully_paved_mode_left_direction(self):
        """Test fully_paved mode creates correct geometry for left side."""
        shoulder = Shoulder(
            width=2.4,
            cross_slope=0.02,
            foreslope_ratio=6.0,
            paved=True,
            pavement_layers=[
                AsphaltLayer(thickness=0.10, aggregate_size=12.5, binder_type='PG 64-22',
                            binder_percentage=5.5, density=2400),
            ],
            shoulder_type="paved_top_slumped",
        )

        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()
        insertion = shoulder.get_insertion_point(cp, 'left')
        geometry = shoulder.to_geometry(insertion, 'left')

        # Should have 1 polygon
        assert len(geometry.polygons) == 1

        poly = geometry.polygons[0]
        x_coords = [p.x for p in poly.exterior]

        # All X coordinates should be negative or zero (left side)
        assert all(x <= 0 for x in x_coords)

        # Width should still be 2.4 + 0.10 = 2.5m
        width = max(x_coords) - min(x_coords)
        assert width == pytest.approx(2.5, abs=0.01)

    def test_fully_paved_mode_attachment_point_right(self):
        """Test fully_paved mode attachment point extends to foreslope intercept."""
        shoulder = Shoulder(
            width=2.4,
            cross_slope=0.02,
            foreslope_ratio=6.0,
            paved=True,
            pavement_layers=[
                AsphaltLayer(thickness=0.10, aggregate_size=12.5, binder_type='PG 64-22',
                            binder_percentage=5.5, density=2400),
                CrushedRockLayer(thickness=0.20, aggregate_size=37.5, density=2200),
            ],
            shoulder_type="paved_top_slumped",
        )

        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()
        insertion = shoulder.get_insertion_point(cp, 'right')
        attachment = shoulder.get_attachment_point(insertion, 'right')

        # Total depth = 0.10 + 0.20 = 0.30m
        # Extension from paved edge = 0.30 * 6.0 = 1.8m
        # Attachment X = 0 + 2.4 (width) + 1.8 (extension) = 4.2m
        expected_x = 2.4 + 1.8
        assert attachment.x == pytest.approx(expected_x, abs=0.01)

        # Attachment Y = surface - cross_slope_drop - total_depth
        # = 100.0 - (2.4 * 0.02) - 0.30 = 100.0 - 0.048 - 0.30 = 99.652
        expected_y = 100.0 - (2.4 * 0.02) - 0.30
        assert attachment.y == pytest.approx(expected_y, abs=0.01)

    def test_fully_paved_mode_attachment_point_left(self):
        """Test fully_paved mode attachment point for left side."""
        shoulder = Shoulder(
            width=2.4,
            cross_slope=0.02,
            foreslope_ratio=6.0,
            paved=True,
            pavement_layers=[
                AsphaltLayer(thickness=0.10, aggregate_size=12.5, binder_type='PG 64-22',
                            binder_percentage=5.5, density=2400),
            ],
            shoulder_type="paved_top_slumped",
        )

        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()
        insertion = shoulder.get_insertion_point(cp, 'left')
        attachment = shoulder.get_attachment_point(insertion, 'left')

        # Extension = 0.10 * 6.0 = 0.6m
        # Attachment X = 0 - 2.4 - 0.6 = -3.0m
        expected_x = -(2.4 + 0.6)
        assert attachment.x == pytest.approx(expected_x, abs=0.01)

    def test_fully_paved_mode_only_base_layers(self):
        """Test fully_paved mode with only crushed rock base (no asphalt)."""
        shoulder = Shoulder(
            width=2.4,
            cross_slope=0.02,
            foreslope_ratio=6.0,
            paved=True,
            pavement_layers=[
                CrushedRockLayer(thickness=0.20, aggregate_size=37.5, density=2200),
            ],
            shoulder_type="paved_top_slumped",
        )

        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()
        insertion = shoulder.get_insertion_point(cp, 'right')
        geometry = shoulder.to_geometry(insertion, 'right')

        # Should have 1 polygon for the base layer
        assert len(geometry.polygons) == 1

        # Base layer should be 5-vertex polygon
        poly = geometry.polygons[0]
        assert len(poly.exterior) == 5

    def test_fully_paved_mode_asphalt_slump_accumulation(self):
        """Test that asphalt slump accumulates correctly across layers."""
        shoulder = Shoulder(
            width=2.4,
            cross_slope=0.02,
            foreslope_ratio=6.0,
            paved=True,
            pavement_layers=[
                AsphaltLayer(thickness=0.05, aggregate_size=9.5, binder_type='PG 64-22',
                            binder_percentage=5.5, density=2400),
                AsphaltLayer(thickness=0.05, aggregate_size=12.5, binder_type='PG 64-22',
                            binder_percentage=5.5, density=2400),
                AsphaltLayer(thickness=0.05, aggregate_size=19.0, binder_type='PG 64-22',
                            binder_percentage=5.0, density=2400),
            ],
            shoulder_type="paved_top_slumped",
        )

        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()
        insertion = shoulder.get_insertion_point(cp, 'right')
        geometry = shoulder.to_geometry(insertion, 'right')

        # Should have 3 asphalt polygons
        assert len(geometry.polygons) == 3

        # Each layer adds 0.05m to the width due to 1:1 slump
        # Layer 0: 2.4 -> 2.45
        # Layer 1: 2.45 -> 2.50
        # Layer 2: 2.50 -> 2.55
        poly2 = geometry.polygons[2]
        x_coords = [p.x for p in poly2.exterior]
        final_width = max(x_coords) - min(x_coords)
        expected_width = 2.4 + (3 * 0.05)  # 2.55m
        assert final_width == pytest.approx(expected_width, abs=0.01)
