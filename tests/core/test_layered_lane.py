"""Tests for layered lane geometry with SVG visualization."""

import pytest
import os
from cross_section.core.domain import (
    RoadSection, ControlPoint, TravelLane,
    AsphaltLayer, ConcreteLayer, CrushedRockLayer
)
from cross_section.export.svg import SimpleSVGExporter


class TestLayeredLane:
    """Tests for TravelLane with layered pavement structure."""

    def test_default_single_layer(self):
        """Test lane with default single asphalt layer."""
        lane = TravelLane(width=3.6)

        assert len(lane.pavement_layers) == 1
        assert isinstance(lane.pavement_layers[0], AsphaltLayer)
        assert lane.pavement_layers[0].thickness == 0.05

    def test_custom_layers(self):
        """Test lane with custom layer configuration."""
        layers = [
            AsphaltLayer(thickness=0.05, aggregate_size=12.5, binder_type='PG 64-22',
                        binder_percentage=5.5, density=2400),
            CrushedRockLayer(thickness=0.20, aggregate_size=37.5, density=2200),
        ]

        lane = TravelLane(width=3.6, pavement_layers=layers)

        assert len(lane.pavement_layers) == 2
        assert isinstance(lane.pavement_layers[0], AsphaltLayer)
        assert isinstance(lane.pavement_layers[1], CrushedRockLayer)

    def test_geometry_has_one_polygon_per_layer(self):
        """Test that geometry contains one polygon per pavement layer."""
        layers = [
            AsphaltLayer(thickness=0.05, aggregate_size=12.5, binder_type='PG 64-22',
                        binder_percentage=5.5, density=2400),
            AsphaltLayer(thickness=0.075, aggregate_size=19.0, binder_type='PG 64-22',
                        binder_percentage=5.0, density=2380),
            CrushedRockLayer(thickness=0.20, aggregate_size=37.5, density=2200),
        ]

        lane = TravelLane(width=3.6, pavement_layers=layers)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = lane.get_insertion_point(cp, 'right')
        geometry = lane.to_geometry(insertion, 'right')

        # Should have 3 polygons (one per layer)
        assert len(geometry.polygons) == 3

        # Check metadata
        assert geometry.metadata['layer_count'] == 3
        assert geometry.metadata['total_depth'] == pytest.approx(0.325)  # 0.05 + 0.075 + 0.20

    def test_layers_are_stacked_vertically(self):
        """Test that layers are stacked from top to bottom."""
        layers = [
            AsphaltLayer(thickness=0.10, aggregate_size=12.5, binder_type='PG 64-22',
                        binder_percentage=5.5, density=2400),
            CrushedRockLayer(thickness=0.20, aggregate_size=37.5, density=2200),
        ]

        lane = TravelLane(width=3.6, pavement_layers=layers)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = lane.get_insertion_point(cp, 'right')
        geometry = lane.to_geometry(insertion, 'right')

        # First polygon (surface layer) should have top at insertion.y
        surface_poly = geometry.polygons[0]
        assert any(p.y == pytest.approx(100.0) for p in surface_poly.exterior)

        # Verify layers are stacked by checking inside edge vertices (x=insertion.x)
        # At inside edge, cross slope doesn't affect the Y coordinates
        surface_inside_y_values = [p.y for p in surface_poly.exterior if p.x == pytest.approx(insertion.x)]
        base_inside_y_values = [p.y for p in geometry.polygons[1].exterior if p.x == pytest.approx(insertion.x)]

        # Surface should have top and bottom at inside edge
        assert max(surface_inside_y_values) == pytest.approx(100.0)  # Top
        assert min(surface_inside_y_values) == pytest.approx(99.9)   # Bottom (100 - 0.10)

        # Base should have top matching surface bottom
        assert max(base_inside_y_values) == pytest.approx(99.9)  # Top of base = bottom of surface
        assert min(base_inside_y_values) == pytest.approx(99.7)  # Bottom (99.9 - 0.20)

    def test_validate_layers(self):
        """Test that lane validation includes layer validation."""
        # Create lane with invalid layer (negative thickness)
        layers = [
            AsphaltLayer(thickness=-0.05, aggregate_size=12.5, binder_type='PG 64-22',
                        binder_percentage=5.5, density=2400),
        ]

        lane = TravelLane(width=3.6, pavement_layers=layers)
        errors = lane.validate()

        assert len(errors) > 0
        assert any('layer' in error.lower() for error in errors)
        assert any('positive' in error.lower() for error in errors)

    def test_svg_export_multilayer_section(self):
        """Test SVG export of a multi-layer pavement section.

        This test creates an SVG file for visual verification of the layered geometry.
        """
        # Create section with different pavement structures
        control_point = ControlPoint(x=0.0, elevation=100.0)
        section = RoadSection(name="Test Layered Section", control_point=control_point)

        # Flexible pavement (asphalt layers)
        flexible_layers = [
            AsphaltLayer(thickness=0.05, aggregate_size=12.5, binder_type='PG 64-22',
                        binder_percentage=5.5, density=2400),
            AsphaltLayer(thickness=0.075, aggregate_size=19.0, binder_type='PG 64-22',
                        binder_percentage=5.0, density=2380),
            CrushedRockLayer(thickness=0.20, aggregate_size=37.5, density=2200),
        ]

        # Rigid pavement (concrete)
        rigid_layers = [
            ConcreteLayer(thickness=0.25, compressive_strength=35.0,
                         reinforced=True, steel_per_cy=40.0),
            CrushedRockLayer(thickness=0.15, aggregate_size=50.0, density=2100),
        ]

        section.add_component_left(TravelLane(width=3.6, pavement_layers=rigid_layers))
        section.add_component_right(TravelLane(width=3.6, pavement_layers=flexible_layers))
        section.add_component_right(TravelLane(width=3.6, pavement_layers=flexible_layers))

        # Validate
        errors = section.validate()
        assert errors == []

        # Generate geometry
        geometry = section.to_geometry()

        # Verify layer counts
        left_comp = geometry.components[0]
        assert len(left_comp.polygons) == 2  # Concrete + base

        right_comp_1 = geometry.components[1]
        assert len(right_comp_1.polygons) == 3  # 2 asphalt + base

        right_comp_2 = geometry.components[2]
        assert len(right_comp_2.polygons) == 3  # 2 asphalt + base

        # Export to SVG for visual verification
        output_dir = "tests/output"
        os.makedirs(output_dir, exist_ok=True)
        svg_path = f"{output_dir}/test_layered_section.svg"

        exporter = SimpleSVGExporter(scale=100.0, vertical_exaggeration=5.0)
        with open(svg_path, 'w') as f:
            exporter.export(geometry, f)

        # Verify SVG file was created
        assert os.path.exists(svg_path)
        assert os.path.getsize(svg_path) > 100  # SVG should have some content

        print(f"\n  ✓ SVG exported to {svg_path} for visual verification")
