#!/usr/bin/env python
"""Example demonstrating slumped shoulder geometry with 1:1 asphalt slump."""

from cross_section.core.domain import (
    RoadSection, ControlPoint, TravelLane, Shoulder,
    AsphaltLayer, CrushedRockLayer
)
from cross_section.export.svg import SimpleSVGExporter


def main():
    """Create a road section with slumped shoulders demonstrating 1:1 asphalt geometry."""

    # Create a control point at the centerline crown
    control_point = ControlPoint(
        x=0.0,
        elevation=100.0,
        description="Centerline Crown"
    )

    # Create a road section
    section = RoadSection(
        name="Two-Lane Road with Slumped Shoulders",
        control_point=control_point
    )

    # Define pavement structure for travel lanes
    lane_pavement = [
        AsphaltLayer(
            thickness=0.05,  # 50mm surface course
            aggregate_size=12.5,
            binder_type='PG 64-22',
            binder_percentage=5.5,
            density=2400
        ),
        AsphaltLayer(
            thickness=0.075,  # 75mm binder course
            aggregate_size=19.0,
            binder_type='PG 64-22',
            binder_percentage=5.0,
            density=2380
        ),
        CrushedRockLayer(
            thickness=0.20,  # 200mm base course
            aggregate_size=37.5,
            density=2200,
            material_type='crushed_stone'
        ),
    ]

    # Define pavement structure for slumped shoulders
    # Multiple asphalt layers to show the 1:1 slump effect
    shoulder_pavement = [
        AsphaltLayer(
            thickness=0.04,  # 40mm surface course
            aggregate_size=12.5,
            binder_type='PG 64-22',
            binder_percentage=5.5,
            density=2400
        ),
        AsphaltLayer(
            thickness=0.05,  # 50mm binder course
            aggregate_size=19.0,
            binder_type='PG 64-22',
            binder_percentage=5.0,
            density=2380
        ),
        AsphaltLayer(
            thickness=0.06,  # 60mm base asphalt
            aggregate_size=19.0,
            binder_type='PG 64-22',
            binder_percentage=5.0,
            density=2380
        ),
        CrushedRockLayer(
            thickness=0.20,  # 200mm crushed rock base
            aggregate_size=37.5,
            density=2200,
            material_type='crushed_stone'
        ),
    ]

    # Add left side: shoulder, then lane
    section.add_component_left(TravelLane(
        width=3.6,
        cross_slope=0.02,
        traffic_direction='inbound',
        pavement_layers=lane_pavement
    ))

    section.add_component_left(Shoulder(
        width=2.4,  # 2.4m (about 8ft) paved shoulder
        cross_slope=0.02,
        foreslope_ratio=4.0,  # 4:1 foreslope (shallower than typical 6:1)
        shoulder_type='paved_top_slumped',  # Slumped asphalt type
        paved=True,
        pavement_layers=shoulder_pavement
    ))

    # Add right side: lane, then shoulder
    section.add_component_right(TravelLane(
        width=3.6,
        cross_slope=0.02,
        traffic_direction='outbound',
        pavement_layers=lane_pavement
    ))

    section.add_component_right(Shoulder(
        width=2.4,  # 2.4m (about 8ft) paved shoulder
        cross_slope=0.02,
        foreslope_ratio=4.0,  # 4:1 foreslope
        shoulder_type='paved_top_slumped',  # Slumped asphalt type
        paved=True,
        pavement_layers=shoulder_pavement
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

    # Show component details
    print(f"\nComponent details:")

    # Left components
    print(f"\n  Left Side (Inbound):")
    for i in range(geometry.metadata['left_component_count']):
        comp_geom = geometry.components[i]
        comp_type = comp_geom.metadata.get('component_type')
        print(f"    {comp_type} {i + 1}:")
        print(f"      Width: {comp_geom.metadata.get('width')} m")
        if comp_type == 'Shoulder':
            print(f"      Shoulder type: {comp_geom.metadata.get('shoulder_type')}")
            print(f"      Foreslope: {comp_geom.metadata.get('foreslope_ratio')}:1")
        print(f"      Layer count: {comp_geom.metadata.get('layer_count')}")
        print(f"      Total depth: {comp_geom.metadata.get('total_depth'):.3f} m")
        print(f"      Polygon count: {len(comp_geom.polygons)}")

        # Show how slumped shoulder geometry works
        if comp_type == 'Shoulder':
            print(f"      Layer geometry (showing width extension):")
            for j, polygon in enumerate(comp_geom.polygons):
                # Get the x-coordinates to show the trapezoid widths
                x_coords = [p.x for p in polygon.exterior]
                width_top = abs(max(x_coords) - min(x_coords))
                layer_info = comp_geom.metadata['layers'][j]
                layer_type = layer_info['type']
                thickness = layer_info['thickness']

                if layer_type == 'AsphaltLayer':
                    print(f"        Layer {j} ({layer_type}, {thickness*1000:.0f}mm): {width_top:.3f}m wide (1:1 slump)")
                else:
                    print(f"        Layer {j} ({layer_type}, {thickness*1000:.0f}mm): {width_top:.3f}m wide (to foreslope)")

    # Right components
    print(f"\n  Right Side (Outbound):")
    for i in range(geometry.metadata['right_component_count']):
        idx = geometry.metadata['left_component_count'] + i
        comp_geom = geometry.components[idx]
        comp_type = comp_geom.metadata.get('component_type')
        print(f"    {comp_type} {i + 1}:")
        print(f"      Width: {comp_geom.metadata.get('width')} m")
        if comp_type == 'Shoulder':
            print(f"      Shoulder type: {comp_geom.metadata.get('shoulder_type')}")
            print(f"      Foreslope: {comp_geom.metadata.get('foreslope_ratio')}:1")
        print(f"      Layer count: {comp_geom.metadata.get('layer_count')}")
        print(f"      Total depth: {comp_geom.metadata.get('total_depth'):.3f} m")
        print(f"      Polygon count: {len(comp_geom.polygons)}")

        # Show how slumped shoulder geometry works
        if comp_type == 'Shoulder':
            print(f"      Layer geometry (showing width extension):")
            for j, polygon in enumerate(comp_geom.polygons):
                x_coords = [p.x for p in polygon.exterior]
                width_top = abs(max(x_coords) - min(x_coords))
                layer_info = comp_geom.metadata['layers'][j]
                layer_type = layer_info['type']
                thickness = layer_info['thickness']

                if layer_type == 'AsphaltLayer':
                    print(f"        Layer {j} ({layer_type}, {thickness*1000:.0f}mm): {width_top:.3f}m wide (1:1 slump)")
                else:
                    print(f"        Layer {j} ({layer_type}, {thickness*1000:.0f}mm): {width_top:.3f}m wide (to foreslope)")

    # Export to SVG
    svg_path = "examples/output/slumped_shoulder.svg"
    print(f"\nExporting to SVG: {svg_path}")

    import os
    os.makedirs("examples/output", exist_ok=True)

    # Use higher vertical exaggeration to make the geometry visible
    exporter = SimpleSVGExporter(scale=50.0, vertical_exaggeration=10.0)
    with open(svg_path, 'w') as f:
        exporter.export(geometry, f)

    print(f"✓ SVG exported successfully!")
    print(f"\nOpen {svg_path} in a web browser to view the cross-section.")
    print(f"\nNote the slumped shoulder geometry:")
    print(f"  - Asphalt layers extend at 1:1 slope (horizontal = thickness)")
    print(f"  - Each lower asphalt layer starts where the upper ended")
    print(f"  - Surface: 2.4m wide")
    print(f"  - After 3 asphalt layers (0.04+0.05+0.06 = 0.15m): 2.4 + 0.15 = 2.55m wide")
    print(f"  - Crushed rock extends from 2.55m to the 4:1 foreslope")
    print(f"  - Bottom at 0.35m depth: 2.4 + 0.35*4 = 3.8m wide")


if __name__ == "__main__":
    main()
