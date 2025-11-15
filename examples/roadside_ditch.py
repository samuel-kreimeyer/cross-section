#!/usr/bin/env python
"""Example demonstrating roadside ditch and slope components."""

from cross_section.core.domain import (
    RoadSection, ControlPoint, TravelLane, Shoulder, Ditch, Slope,
    AsphaltLayer, CrushedRockLayer
)
from cross_section.export.svg import SimpleSVGExporter


def main():
    """Create a road section with ditches and slopes on both sides."""

    # Create a control point at the centerline crown
    control_point = ControlPoint(
        x=0.0,
        elevation=100.0,
        description="Centerline Crown"
    )

    # Create a road section
    section = RoadSection(
        name="Rural Road with Roadside Ditches",
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

    # Shoulder pavement (thinner than lanes)
    shoulder_pavement = [
        AsphaltLayer(
            thickness=0.04,  # 40mm surface
            aggregate_size=12.5,
            binder_type='PG 64-22',
            binder_percentage=5.5,
            density=2400
        ),
        CrushedRockLayer(
            thickness=0.15,  # 150mm base
            aggregate_size=37.5,
            density=2200,
            material_type='crushed_stone'
        ),
    ]

    # Add left side: lane, shoulder, ditch, slope to existing ground
    section.add_component_left(TravelLane(
        width=3.6,
        cross_slope=0.02,
        traffic_direction='inbound',
        pavement_layers=lane_pavement
    ))

    section.add_component_left(Shoulder(
        width=2.4,
        cross_slope=0.02,
        foreslope_ratio=6.0,
        pavement_layers=shoulder_pavement
    ))

    # Trapezoid ditch with crushed rock lining
    section.add_component_left(Ditch(
        depth=0.6,  # 600mm deep
        foreslope_ratio=4.0,  # 4:1 coming down
        backslope_ratio=3.0,  # 3:1 going back up (steeper)
        bottom_width=1.2,  # 1.2m flat bottom
        bottom_slope=0.02,  # 2% slope across bottom
        lining=CrushedRockLayer(
            thickness=0.15,
            aggregate_size=37.5,
            density=2200,
            material_type='crushed_stone'
        ),
        lining_thickness=0.15
    ))

    # Slope from ditch to existing ground
    section.add_component_left(Slope(
        slope_ratio=6.0,  # 6:1 gentle slope
        vertical_drop=-0.6,  # Going back up 600mm (negative = upslope)
        surface_type='grass'
    ))

    # Add right side: lane, shoulder, ditch, slope
    section.add_component_right(TravelLane(
        width=3.6,
        cross_slope=0.02,
        traffic_direction='outbound',
        pavement_layers=lane_pavement
    ))

    section.add_component_right(Shoulder(
        width=2.4,
        cross_slope=0.02,
        foreslope_ratio=6.0,
        pavement_layers=shoulder_pavement
    ))

    section.add_component_right(Ditch(
        depth=0.6,
        foreslope_ratio=4.0,
        backslope_ratio=3.0,
        bottom_width=1.2,
        bottom_slope=0.02,
        lining=CrushedRockLayer(
            thickness=0.15,
            aggregate_size=37.5,
            density=2200,
            material_type='crushed_stone'
        ),
        lining_thickness=0.15
    ))

    section.add_component_right(Slope(
        slope_ratio=6.0,
        vertical_drop=-0.6,
        surface_type='grass'
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
        print(f"    {i+1}. {comp_type}:")

        if comp_type == 'TravelLane':
            print(f"       Width: {comp_geom.metadata.get('width'):.1f} m")
        elif comp_type == 'Shoulder':
            print(f"       Width: {comp_geom.metadata.get('width'):.1f} m")
            print(f"       Foreslope: {comp_geom.metadata.get('foreslope_ratio'):.1f}:1")
        elif comp_type == 'Ditch':
            ditch_type = comp_geom.metadata.get('ditch_type')
            depth = comp_geom.metadata.get('depth')
            foreslope = comp_geom.metadata.get('foreslope_ratio')
            backslope = comp_geom.metadata.get('backslope_ratio')
            bottom_width = comp_geom.metadata.get('bottom_width')
            has_lining = comp_geom.metadata.get('has_lining')
            print(f"       Type: {ditch_type}")
            print(f"       Depth: {depth:.2f} m")
            print(f"       Foreslope: {foreslope:.1f}:1, Backslope: {backslope:.1f}:1")
            print(f"       Bottom width: {bottom_width:.1f} m")
            print(f"       Lining: {'Yes' if has_lining else 'No'}")
        elif comp_type == 'Slope':
            slope_ratio = comp_geom.metadata.get('slope_ratio')
            vertical_drop = comp_geom.metadata.get('vertical_drop')
            surface = comp_geom.metadata.get('surface_type')
            print(f"       Slope: {slope_ratio:.1f}:1")
            print(f"       Rise: {abs(vertical_drop):.2f} m {'up' if vertical_drop < 0 else 'down'}")
            print(f"       Surface: {surface}")

    # Right components
    print(f"\n  Right Side (Outbound):")
    for i in range(geometry.metadata['right_component_count']):
        idx = geometry.metadata['left_component_count'] + i
        comp_geom = geometry.components[idx]
        comp_type = comp_geom.metadata.get('component_type')
        print(f"    {i+1}. {comp_type}:")

        if comp_type == 'TravelLane':
            print(f"       Width: {comp_geom.metadata.get('width'):.1f} m")
        elif comp_type == 'Shoulder':
            print(f"       Width: {comp_geom.metadata.get('width'):.1f} m")
            print(f"       Foreslope: {comp_geom.metadata.get('foreslope_ratio'):.1f}:1")
        elif comp_type == 'Ditch':
            ditch_type = comp_geom.metadata.get('ditch_type')
            depth = comp_geom.metadata.get('depth')
            foreslope = comp_geom.metadata.get('foreslope_ratio')
            backslope = comp_geom.metadata.get('backslope_ratio')
            bottom_width = comp_geom.metadata.get('bottom_width')
            has_lining = comp_geom.metadata.get('has_lining')
            print(f"       Type: {ditch_type}")
            print(f"       Depth: {depth:.2f} m")
            print(f"       Foreslope: {foreslope:.1f}:1, Backslope: {backslope:.1f}:1")
            print(f"       Bottom width: {bottom_width:.1f} m")
            print(f"       Lining: {'Yes' if has_lining else 'No'}")
        elif comp_type == 'Slope':
            slope_ratio = comp_geom.metadata.get('slope_ratio')
            vertical_drop = comp_geom.metadata.get('vertical_drop')
            surface = comp_geom.metadata.get('surface_type')
            print(f"       Slope: {slope_ratio:.1f}:1")
            print(f"       Rise: {abs(vertical_drop):.2f} m {'up' if vertical_drop < 0 else 'down'}")
            print(f"       Surface: {surface}")

    # Export to SVG
    svg_path = "examples/output/roadside_ditch.svg"
    print(f"\nExporting to SVG: {svg_path}")

    import os
    os.makedirs("examples/output", exist_ok=True)

    # Use true proportions
    exporter = SimpleSVGExporter(scale=50.0, vertical_exaggeration=1.0)
    with open(svg_path, 'w') as f:
        exporter.export(geometry, f)

    print(f"✓ SVG exported successfully!")
    print(f"\nOpen {svg_path} in a web browser to view the cross-section.")
    print(f"\nRoadside features:")
    print(f"  - Travel lanes with full-depth pavement")
    print(f"  - Paved shoulders with foreslope")
    print(f"  - Trapezoid ditches (0.6m deep, 1.2m bottom) with crushed rock lining")
    print(f"  - Backslopes returning to existing ground level")


if __name__ == "__main__":
    main()
