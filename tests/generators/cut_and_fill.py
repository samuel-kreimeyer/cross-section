#!/usr/bin/env python
"""Example demonstrating cut and fill cross-section.

This shows a typical scenario where a road is built on varying terrain:
- Left side: Fill slope (embankment going down)
- Right side: Cut with V-ditch and backslope (excavation going up)
"""

import sys
from pathlib import Path

# Add src to path for imports
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cross_section.core.domain import (
    RoadSection, ControlPoint, TravelLane, Shoulder, Ditch, Slope,
    AsphaltLayer, CrushedRockLayer
)
from cross_section.core.domain.annotations import (
    AnnotationGenerator,
    default_annotation_options,
)
from cross_section.export.svg_annotations import AnnotatedSVGExporter
from _svg_to_png import svg_to_png


def main():
    """Create a two-lane road with cut on one side and fill on the other."""

    # Create a control point at the centerline crown
    control_point = ControlPoint(
        x=0.0,
        elevation=100.0,
        description="Centerline Crown"
    )

    # Create a road section
    section = RoadSection(
        name="Two-Lane Road with Cut and Fill",
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

    # ===== LEFT SIDE: FILL SLOPE (embankment going down) =====
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

    # Fill slope: simple 4:1 slope going down 3 meters
    section.add_component_left(Slope(
        slope_ratio=4.0,  # 4:1 (4H:1V)
        vertical_drop=3.0,  # 3m drop (embankment)
        surface_type='grass'
    ))

    # ===== RIGHT SIDE: CUT SLOPE (excavation with ditch and backslope) =====
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

    # V-shaped ditch (no flat bottom, no lining)
    section.add_component_right(Ditch(
        depth=0.8,  # 800mm deep V-ditch
        foreslope_ratio=4.0,  # 4:1 slope down
        backslope_ratio=4.0,  # 4:1 slope back up
        bottom_width=0.0,  # V-ditch (no flat bottom)
        bottom_slope=0.0,  # No bottom slope (point at bottom)
        lining=None,  # No lining
        lining_thickness=0.0
    ))

    # Cut slope: 4:1 slope going back up 2.5 meters to existing ground
    section.add_component_right(Slope(
        slope_ratio=4.0,  # 4:1 (4H:1V)
        vertical_drop=-2.5,  # 2.5m rise (negative = upslope, cut)
        surface_type='grass'
    ))

    # Validate the section
    print(f"Section: {section}")
    print("\nValidation:")
    errors = section.validate()
    if errors:
        print("  Errors found:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("  ✓ Section is valid")

    # Generate geometry
    print("\nGenerating geometry...")
    geometry = section.to_geometry()

    print(f"  Total components: {geometry.metadata['total_component_count']}")
    print(f"  Left components: {geometry.metadata['left_component_count']}")
    print(f"  Right components: {geometry.metadata['right_component_count']}")

    # Show component details
    print("\nComponent details:")

    # Left components (FILL side)
    print("\n  Left Side (FILL - Embankment):")
    for i in range(geometry.metadata['left_component_count']):
        comp_geom = geometry.components[i]
        comp_type = comp_geom.metadata.get('component_type')
        print(f"    {i+1}. {comp_type}")

        if comp_type == 'TravelLane':
            print(f"       Width: {comp_geom.metadata.get('width'):.1f} m")
        elif comp_type == 'Shoulder':
            print(f"       Width: {comp_geom.metadata.get('width'):.1f} m")
            print("       Type: Gravel (unpaved)")
            print(f"       Foreslope: {comp_geom.metadata.get('foreslope_ratio'):.1f}:1")
        elif comp_type == 'Slope':
            slope_ratio = comp_geom.metadata.get('slope_ratio')
            vertical_drop = comp_geom.metadata.get('vertical_drop')
            surface = comp_geom.metadata.get('surface_type')
            print(f"       Slope: {slope_ratio:.1f}:1")
            print(f"       Drop: {abs(vertical_drop):.1f} m down (fill/embankment)")
            print(f"       Surface: {surface}")

    # Right components (CUT side)
    print("\n  Right Side (CUT - Excavation):")
    for i in range(geometry.metadata['right_component_count']):
        idx = geometry.metadata['left_component_count'] + i
        comp_geom = geometry.components[idx]
        comp_type = comp_geom.metadata.get('component_type')
        print(f"    {i+1}. {comp_type}")

        if comp_type == 'TravelLane':
            print(f"       Width: {comp_geom.metadata.get('width'):.1f} m")
        elif comp_type == 'Shoulder':
            print(f"       Width: {comp_geom.metadata.get('width'):.1f} m")
            print("       Type: Gravel (unpaved)")
            print(f"       Foreslope: {comp_geom.metadata.get('foreslope_ratio'):.1f}:1")
        elif comp_type == 'Ditch':
            ditch_type = comp_geom.metadata.get('ditch_type')
            depth = comp_geom.metadata.get('depth')
            foreslope = comp_geom.metadata.get('foreslope_ratio')
            backslope = comp_geom.metadata.get('backslope_ratio')
            has_lining = comp_geom.metadata.get('has_lining')
            print(f"       Type: {ditch_type}")
            print(f"       Depth: {depth:.2f} m")
            print(f"       Foreslope: {foreslope:.1f}:1, Backslope: {backslope:.1f}:1")
            print(f"       Lining: {'Yes' if has_lining else 'No (unlined)'}")
        elif comp_type == 'Slope':
            slope_ratio = comp_geom.metadata.get('slope_ratio')
            vertical_drop = comp_geom.metadata.get('vertical_drop')
            surface = comp_geom.metadata.get('surface_type')
            print(f"       Slope: {slope_ratio:.1f}:1")
            print(f"       Rise: {abs(vertical_drop):.1f} m up (cut/backslope)")
            print(f"       Surface: {surface}")

    # Generate automated annotations
    print("\nGenerating annotations...")
    options = default_annotation_options()
    annotations = AnnotationGenerator.generate(geometry, options)
    result = annotations.resolve_collisions(geometry=geometry)
    if not result.success:
        print(f"  WARN: {result.overflow_count} overflow, {result.remaining_collisions} collisions", file=sys.stderr)
    print(f"  Generated {annotations.count()} annotations")

    # Export to SVG
    output_dir = SCRIPT_DIR.parent / "output"
    output_dir.mkdir(exist_ok=True)
    svg_path = output_dir / "cut_and_fill.svg"

    print(f"\nExporting to SVG: {svg_path.name}")
    exporter = AnnotatedSVGExporter(scale=50.0, vertical_exaggeration=1.0)
    with open(svg_path, 'w') as f:
        exporter.export_with_annotations(geometry, annotations, f)
    svg_to_png(svg_path)

    print("✓ SVG exported successfully!")
    print(f"\nOpen {svg_path} in a web browser to view the cross-section.")
    print("\nCut and Fill geometry:")
    print("  Left side (FILL):")
    print("    - Lane → Gravel Shoulder → 4:1 Fill Slope (3m down)")
    print("    - Embankment descends to existing ground")
    print("  Right side (CUT):")
    print("    - Lane → Gravel Shoulder → V-Ditch (0.8m deep) → 4:1 Cut Slope (2.5m up)")
    print("    - Excavation rises to existing ground")
    print("\nThis demonstrates typical highway construction on side-hill terrain.")


if __name__ == "__main__":
    main()
