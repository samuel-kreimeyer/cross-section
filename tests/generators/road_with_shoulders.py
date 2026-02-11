#!/usr/bin/env python
"""Example demonstrating road section with shoulders showing trapezoid geometry."""

import sys
from pathlib import Path

# Add src to path for imports
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cross_section.core.domain import (
    RoadSection, ControlPoint, TravelLane, Shoulder,
    AsphaltLayer, CrushedRockLayer
)
from cross_section.core.domain.annotations import (
    AnnotationGenerator,
    default_annotation_options,
)
from cross_section.export.svg_annotations import AnnotatedSVGExporter
from _svg_to_png import svg_to_png


def main():
    """Create a road section with travel lanes and paved shoulders on both sides."""

    # Create a control point at the centerline crown
    control_point = ControlPoint(
        x=0.0,
        elevation=100.0,
        description="Centerline Crown"
    )

    # Create a road section
    section = RoadSection(
        name="Two-Lane Road with Shoulders",
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

    # Define pavement structure for shoulders (thinner than lanes)
    shoulder_pavement = [
        AsphaltLayer(
            thickness=0.04,  # 40mm surface course
            aggregate_size=12.5,
            binder_type='PG 64-22',
            binder_percentage=5.5,
            density=2400
        ),
        CrushedRockLayer(
            thickness=0.15,  # 150mm base course
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
        foreslope_ratio=6.0,  # 6:1 foreslope
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
        foreslope_ratio=6.0,  # 6:1 foreslope
        paved=True,
        pavement_layers=shoulder_pavement
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

    # Left components
    print("\n  Left Side (Inbound):")
    for i in range(geometry.metadata['left_component_count']):
        comp_geom = geometry.components[i]
        comp_type = comp_geom.metadata.get('component_type')
        print(f"    {comp_type} {i + 1}:")
        print(f"      Width: {comp_geom.metadata.get('width')} m")
        if comp_type == 'Shoulder':
            print(f"      Foreslope: {comp_geom.metadata.get('foreslope_ratio')}:1")
        print(f"      Layer count: {comp_geom.metadata.get('layer_count')}")
        print(f"      Total depth: {comp_geom.metadata.get('total_depth'):.3f} m")
        print(f"      Polygon count: {len(comp_geom.polygons)}")

        # Show how shoulder trapezoids work
        if comp_type == 'Shoulder':
            print("      Trapezoid geometry (showing layer width extension):")
            for j, polygon in enumerate(comp_geom.polygons):
                # Get the x-coordinates to show the trapezoid widths
                x_coords = [p.x for p in polygon.exterior]
                width_top = abs(max(x_coords) - min(x_coords))
                print(f"        Layer {j}: ~{width_top:.2f}m wide")

    # Right components
    print("\n  Right Side (Outbound):")
    for i in range(geometry.metadata['right_component_count']):
        idx = geometry.metadata['left_component_count'] + i
        comp_geom = geometry.components[idx]
        comp_type = comp_geom.metadata.get('component_type')
        print(f"    {comp_type} {i + 1}:")
        print(f"      Width: {comp_geom.metadata.get('width')} m")
        if comp_type == 'Shoulder':
            print(f"      Foreslope: {comp_geom.metadata.get('foreslope_ratio')}:1")
        print(f"      Layer count: {comp_geom.metadata.get('layer_count')}")
        print(f"      Total depth: {comp_geom.metadata.get('total_depth'):.3f} m")
        print(f"      Polygon count: {len(comp_geom.polygons)}")

        # Show how shoulder trapezoids work
        if comp_type == 'Shoulder':
            print("      Trapezoid geometry (showing layer width extension):")
            for j, polygon in enumerate(comp_geom.polygons):
                x_coords = [p.x for p in polygon.exterior]
                width_top = abs(max(x_coords) - min(x_coords))
                print(f"        Layer {j}: ~{width_top:.2f}m wide")

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
    svg_path = output_dir / "road_with_shoulders.svg"

    print(f"\nExporting to SVG: {svg_path.name}")
    exporter = AnnotatedSVGExporter(scale=50.0, vertical_exaggeration=1.0)
    with open(svg_path, 'w') as f:
        exporter.export_with_annotations(geometry, annotations, f)
    svg_to_png(svg_path)

    print("✓ SVG exported successfully!")
    print(f"\nOpen {svg_path} in a web browser to view the cross-section.")
    print("\nNote the trapezoid shapes in the shoulders:")
    print("  - Surface layers are narrow (paved width only)")
    print("  - Bottom layers extend further due to 6:1 foreslope")
    print("  - This creates the characteristic tapered shoulder profile")


if __name__ == "__main__":
    main()
