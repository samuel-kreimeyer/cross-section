#!/usr/bin/env python
"""Example demonstrating layered pavement structure with SVG export."""

from cross_section.core.domain import (
    RoadSection, ControlPoint, TravelLane,
    AsphaltLayer, ConcreteLayer, CrushedRockLayer
)
from cross_section.export.svg import SimpleSVGExporter


def main():
    """Create a road section with detailed pavement layers and export to SVG."""

    # Create a control point at the centerline crown
    control_point = ControlPoint(
        x=0.0,
        elevation=100.0,
        description="Centerline Crown"
    )

    # Create a road section
    section = RoadSection(
        name="Flexible Pavement Section",
        control_point=control_point
    )

    # Define a typical flexible pavement structure
    # (from top to bottom: surface, binder, base)
    flexible_pavement = [
        AsphaltLayer(
            thickness=0.05,  # 50mm surface course
            aggregate_size=12.5,  # mm
            binder_type='PG 64-22',
            binder_percentage=5.5,
            density=2400  # kg/m³
        ),
        AsphaltLayer(
            thickness=0.075,  # 75mm binder course
            aggregate_size=19.0,  # mm
            binder_type='PG 64-22',
            binder_percentage=5.0,
            density=2380  # kg/m³
        ),
        CrushedRockLayer(
            thickness=0.20,  # 200mm base course
            aggregate_size=37.5,  # mm
            density=2200,  # kg/m³
            material_type='crushed_stone'
        ),
    ]

    # Add right lane with flexible pavement
    section.add_component_right(TravelLane(
        width=3.6,
        cross_slope=0.02,
        traffic_direction='outbound',
        pavement_layers=flexible_pavement
    ))

    # Add another right lane
    section.add_component_right(TravelLane(
        width=3.6,
        cross_slope=0.02,
        traffic_direction='outbound',
        pavement_layers=flexible_pavement
    ))

    # Define a rigid pavement structure for comparison
    rigid_pavement = [
        ConcreteLayer(
            thickness=0.25,  # 250mm concrete slab
            compressive_strength=35.0,  # MPa (28-day)
            reinforced=True,
            steel_per_cy=40.0  # lbs/cy³
        ),
        CrushedRockLayer(
            thickness=0.15,  # 150mm subbase
            aggregate_size=50.0,  # mm
            density=2100,  # kg/m³
            material_type='recycled_concrete'
        ),
    ]

    # Add left lane with rigid pavement
    section.add_component_left(TravelLane(
        width=3.6,
        cross_slope=0.02,
        traffic_direction='inbound',
        pavement_layers=rigid_pavement
    ))

    # Validate the section
    print(f"Section: {section}")
    print(f"\nValidation:")
    errors = section.validate()
    if errors:
        print("  Errors found:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("  ✓ Section is valid")

    # Generate geometry
    print(f"\nGenerating geometry...")
    geometry = section.to_geometry()

    print(f"  Total components: {geometry.metadata['total_component_count']}")
    print(f"  Left components: {geometry.metadata['left_component_count']}")
    print(f"  Right components: {geometry.metadata['right_component_count']}")

    # Show component and layer details
    print(f"\nComponent details:")

    # Left components (rigid pavement)
    print(f"\n  Left Side (Rigid Pavement):")
    for i in range(geometry.metadata['left_component_count']):
        comp_geom = geometry.components[i]
        print(f"    Lane {i + 1}:")
        print(f"      Width: {comp_geom.metadata.get('width')} m")
        print(f"      Layer count: {comp_geom.metadata.get('layer_count')}")
        print(f"      Total depth: {comp_geom.metadata.get('total_depth'):.3f} m")
        print(f"      Polygon count: {len(comp_geom.polygons)}")

        if 'layers' in comp_geom.metadata:
            for layer in comp_geom.metadata['layers']:
                print(f"        Layer {layer['layer_index']}: {layer['type']}, "
                      f"{layer['thickness']*1000:.0f}mm")

    # Right components (flexible pavement)
    print(f"\n  Right Side (Flexible Pavement):")
    for i in range(geometry.metadata['right_component_count']):
        idx = geometry.metadata['left_component_count'] + i
        comp_geom = geometry.components[idx]
        print(f"    Lane {i + 1}:")
        print(f"      Width: {comp_geom.metadata.get('width')} m")
        print(f"      Layer count: {comp_geom.metadata.get('layer_count')}")
        print(f"      Total depth: {comp_geom.metadata.get('total_depth'):.3f} m")
        print(f"      Polygon count: {len(comp_geom.polygons)}")

        if 'layers' in comp_geom.metadata:
            for layer in comp_geom.metadata['layers']:
                print(f"        Layer {layer['layer_index']}: {layer['type']}, "
                      f"{layer['thickness']*1000:.0f}mm")

    # Export to SVG
    svg_path = "examples/output/layered_pavement_section.svg"
    print(f"\nExporting to SVG: {svg_path}")

    # Create output directory if it doesn't exist
    import os
    os.makedirs("examples/output", exist_ok=True)

    exporter = SimpleSVGExporter(scale=100.0, vertical_exaggeration=3.0)
    with open(svg_path, 'w') as f:
        exporter.export(geometry, f)

    print(f"✓ SVG exported successfully!")
    print(f"\nOpen {svg_path} in a web browser to view the cross-section.")


if __name__ == "__main__":
    main()
