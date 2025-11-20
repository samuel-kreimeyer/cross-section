#!/usr/bin/env python
"""Example demonstrating temporary shoring walls.

This shows typical scenarios where temporary shoring (corrugated steel sheets)
is used to provide vertical or near-vertical transitions:
- Left side: Fill shoring (wall extends downward from road level)
- Right side: Cut shoring (wall extends upward from excavation level)
"""

from cross_section.core.domain import (
    RoadSection, ControlPoint, TravelLane, Shoulder, Shoring, Slope,
    AsphaltLayer, CrushedRockLayer
)
from cross_section.export.svg import SimpleSVGExporter


def main():
    """Create a two-lane road with shoring on both sides."""

    # Create a control point at the centerline crown
    control_point = ControlPoint(
        x=0.0,
        elevation=100.0,
        description="Centerline Crown"
    )

    # Create a road section
    section = RoadSection(
        name="Two-Lane Road with Temporary Shoring",
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

    # Gravel shoulder structure (unpaved)
    shoulder_base = [
        CrushedRockLayer(
            thickness=0.15,  # 150mm gravel base
            aggregate_size=37.5,
            density=2200,
            material_type='crushed_stone'
        ),
    ]

    # ===== LEFT SIDE: FILL SHORING (wall extends downward) =====
    section.add_component_left(TravelLane(
        width=3.6,
        cross_slope=0.02,
        traffic_direction='inbound',
        pavement_layers=lane_pavement
    ))

    section.add_component_left(Shoulder(
        width=2.4,
        cross_slope=0.04,  # 4% cross-slope for gravel
        foreslope_ratio=4.0,  # 4:1 foreslope
        paved=False,  # Gravel shoulder
        pavement_layers=shoulder_base
    ))

    # Fill shoring: 10 ft (3.05m) wall extending downward
    # Wall is at the bottom of the shoulder, extends down
    section.add_component_left(Shoring(
        height=3.05,  # 10 feet
        thickness=0.203,  # 8 inches (corrugated steel sheets)
        mode='fill'  # Wall extends downward
    ))

    # After shoring, continue with fill slope to existing ground
    section.add_component_left(Slope(
        slope_ratio=4.0,  # 4:1 (4H:1V)
        vertical_drop=2.0,  # 2m additional drop
        surface_type='grass'
    ))

    # ===== RIGHT SIDE: CUT SHORING (wall extends upward) =====
    section.add_component_right(TravelLane(
        width=3.6,
        cross_slope=0.02,
        traffic_direction='outbound',
        pavement_layers=lane_pavement
    ))

    section.add_component_right(Shoulder(
        width=2.4,
        cross_slope=0.04,
        foreslope_ratio=4.0,
        paved=False,  # Gravel shoulder
        pavement_layers=shoulder_base
    ))

    # Cut shoring: 12 ft (3.66m) wall extending upward
    # Wall is at the bottom of excavation, extends up to shoulder level
    section.add_component_right(Shoring(
        height=3.66,  # 12 feet
        thickness=0.203,  # 8 inches (corrugated steel sheets)
        mode='cut'  # Wall extends upward
    ))

    # After shoring, continue with cut slope to existing ground
    section.add_component_right(Slope(
        slope_ratio=4.0,  # 4:1 (4H:1V)
        vertical_drop=-1.5,  # 1.5m rise (negative = upslope, cut)
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

    # Left components (FILL side)
    print(f"\n  Left Side (FILL - Shoring wall extends down):")
    for i in range(geometry.metadata['left_component_count']):
        comp_geom = geometry.components[i]
        comp_type = comp_geom.metadata.get('component_type')
        print(f"    {i+1}. {comp_type}")

        if comp_type == 'TravelLane':
            print(f"       Width: {comp_geom.metadata.get('width'):.1f} m")
        elif comp_type == 'Shoulder':
            print(f"       Width: {comp_geom.metadata.get('width'):.1f} m")
            print(f"       Type: Gravel (unpaved)")
        elif comp_type == 'Shoring':
            height = comp_geom.metadata.get('height')
            thickness = comp_geom.metadata.get('thickness')
            mode = comp_geom.metadata.get('mode')
            print(f"       Height: {height:.2f} m ({height * 3.28084:.1f} ft)")
            print(f"       Thickness: {thickness:.3f} m ({thickness * 39.3701:.1f} in)")
            print(f"       Mode: {mode} (wall extends {'down' if mode == 'fill' else 'up'})")
            print(f"       Material: Corrugated steel sheets")
        elif comp_type == 'Slope':
            slope_ratio = comp_geom.metadata.get('slope_ratio')
            vertical_drop = comp_geom.metadata.get('vertical_drop')
            surface = comp_geom.metadata.get('surface_type')
            print(f"       Slope: {slope_ratio:.1f}:1")
            print(f"       Drop: {abs(vertical_drop):.1f} m down (fill)")
            print(f"       Surface: {surface}")

    # Right components (CUT side)
    print(f"\n  Right Side (CUT - Shoring wall extends up):")
    for i in range(geometry.metadata['right_component_count']):
        idx = geometry.metadata['left_component_count'] + i
        comp_geom = geometry.components[idx]
        comp_type = comp_geom.metadata.get('component_type')
        print(f"    {i+1}. {comp_type}")

        if comp_type == 'TravelLane':
            print(f"       Width: {comp_geom.metadata.get('width'):.1f} m")
        elif comp_type == 'Shoulder':
            print(f"       Width: {comp_geom.metadata.get('width'):.1f} m")
            print(f"       Type: Gravel (unpaved)")
        elif comp_type == 'Shoring':
            height = comp_geom.metadata.get('height')
            thickness = comp_geom.metadata.get('thickness')
            mode = comp_geom.metadata.get('mode')
            print(f"       Height: {height:.2f} m ({height * 3.28084:.1f} ft)")
            print(f"       Thickness: {thickness:.3f} m ({thickness * 39.3701:.1f} in)")
            print(f"       Mode: {mode} (wall extends {'down' if mode == 'fill' else 'up'})")
            print(f"       Material: Corrugated steel sheets")
        elif comp_type == 'Slope':
            slope_ratio = comp_geom.metadata.get('slope_ratio')
            vertical_drop = comp_geom.metadata.get('vertical_drop')
            surface = comp_geom.metadata.get('surface_type')
            print(f"       Slope: {slope_ratio:.1f}:1")
            print(f"       Rise: {abs(vertical_drop):.1f} m up (cut)")
            print(f"       Surface: {surface}")

    # Export to SVG
    svg_path = "examples/output/shoring_example.svg"
    print(f"\nExporting to SVG: {svg_path}")

    import os
    os.makedirs("examples/output", exist_ok=True)

    # Use true proportions
    exporter = SimpleSVGExporter(scale=50.0, vertical_exaggeration=1.0)
    with open(svg_path, 'w') as f:
        exporter.export(geometry, f)

    print(f"✓ SVG exported successfully!")
    print(f"\nOpen {svg_path} in a web browser to view the cross-section.")
    print(f"\nShoring wall geometry:")
    print(f"  Left side (FILL):")
    print(f"    - Lane → Shoulder → 10ft Shoring Wall (down) → 4:1 Fill Slope")
    print(f"    - Wall provides vertical transition before fill slope")
    print(f"  Right side (CUT):")
    print(f"    - Lane → Shoulder → 12ft Shoring Wall (up) → 4:1 Cut Slope")
    print(f"    - Wall provides vertical transition in excavation")
    print(f"\nTemporary shoring is commonly used during construction or")
    print(f"in constrained right-of-way where steep transitions are needed.")


if __name__ == "__main__":
    main()
