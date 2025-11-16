#!/usr/bin/env python
"""Example demonstrating curb and gutter component."""

from cross_section.core.domain import (
    RoadSection, ControlPoint, TravelLane, Curb,
    AsphaltLayer, CrushedRockLayer, ConcreteLayer
)
from cross_section.export.svg import SimpleSVGExporter


def main():
    """Create a road section with curb and gutter."""

    # Create a control point at the centerline crown
    control_point = ControlPoint(
        x=0.0,
        elevation=100.0,
        description="Centerline Crown"
    )

    # Create a road section
    section = RoadSection(
        name="Two-Lane Road with Curb and Gutter",
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

    # Create curb and gutter specification
    # Classic barrier curb dimensions (converting from inches to meters)
    curb = Curb(
        gutter_width=0.4572,  # 18 inches
        gutter_thickness=0.3048,  # 12 inches
        gutter_drop=0.025,  # 1 inch drop from attachment to curb
        curb_height=0.1016,  # 4 inches
        curb_width_bottom=0.1524,  # 6 inches
        curb_width_top=0.1016,  # 4 inches (battered face)
        concrete=ConcreteLayer(
            thickness=0.3048,  # 12 inches
            compressive_strength=28.0,  # 28 MPa (4000 psi)
            reinforced=False,
            steel_per_cy=None
        )
    )

    # Add left side: lane, then curb
    section.add_component_left(TravelLane(
        width=3.6,
        cross_slope=0.02,
        traffic_direction='inbound',
        pavement_layers=lane_pavement
    ))

    section.add_component_left(curb)

    # Add right side: lane, then curb
    section.add_component_right(TravelLane(
        width=3.6,
        cross_slope=0.02,
        traffic_direction='outbound',
        pavement_layers=lane_pavement
    ))

    section.add_component_right(curb)

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

        if comp_type == 'TravelLane':
            print(f"      Width: {comp_geom.metadata.get('width')} m")
            print(f"      Layer count: {comp_geom.metadata.get('layer_count')}")
            print(f"      Total depth: {comp_geom.metadata.get('total_depth'):.3f} m")
        elif comp_type == 'Curb':
            gutter_width = comp_geom.metadata.get('gutter_width')
            gutter_thickness = comp_geom.metadata.get('gutter_thickness')
            curb_height = comp_geom.metadata.get('curb_height')
            curb_width = comp_geom.metadata.get('curb_width_bottom')

            print(f"      Gutter width: {gutter_width*39.37:.1f} in ({gutter_width:.3f} m)")
            print(f"      Gutter thickness: {gutter_thickness*39.37:.1f} in ({gutter_thickness:.3f} m)")
            print(f"      Curb height: {curb_height*39.37:.1f} in ({curb_height:.3f} m)")
            print(f"      Curb width: {curb_width*39.37:.1f} in ({curb_width:.3f} m)")
            print(f"      Polygon vertices: {len(comp_geom.polygons[0].exterior)}")

    # Right components
    print(f"\n  Right Side (Outbound):")
    for i in range(geometry.metadata['right_component_count']):
        idx = geometry.metadata['left_component_count'] + i
        comp_geom = geometry.components[idx]
        comp_type = comp_geom.metadata.get('component_type')
        print(f"    {comp_type} {i + 1}:")

        if comp_type == 'TravelLane':
            print(f"      Width: {comp_geom.metadata.get('width')} m")
            print(f"      Layer count: {comp_geom.metadata.get('layer_count')}")
            print(f"      Total depth: {comp_geom.metadata.get('total_depth'):.3f} m")
        elif comp_type == 'Curb':
            gutter_width = comp_geom.metadata.get('gutter_width')
            gutter_thickness = comp_geom.metadata.get('gutter_thickness')
            curb_height = comp_geom.metadata.get('curb_height')
            curb_width = comp_geom.metadata.get('curb_width_bottom')

            print(f"      Gutter width: {gutter_width*39.37:.1f} in ({gutter_width:.3f} m)")
            print(f"      Gutter thickness: {gutter_thickness*39.37:.1f} in ({gutter_thickness:.3f} m)")
            print(f"      Curb height: {curb_height*39.37:.1f} in ({curb_height:.3f} m)")
            print(f"      Curb width: {curb_width*39.37:.1f} in ({curb_width:.3f} m)")
            print(f"      Polygon vertices: {len(comp_geom.polygons[0].exterior)}")

    # Export to SVG
    svg_path = "examples/output/curb_and_gutter.svg"
    print(f"\nExporting to SVG: {svg_path}")

    import os
    os.makedirs("examples/output", exist_ok=True)

    # Use true proportions (no vertical exaggeration)
    exporter = SimpleSVGExporter(scale=50.0, vertical_exaggeration=1.0)
    with open(svg_path, 'w') as f:
        exporter.export(geometry, f)

    print(f"✓ SVG exported successfully!")
    print(f"\nOpen {svg_path} in a web browser to view the cross-section.")
    print(f"\nCurb and gutter geometry:")
    print(f"  - Gutter: 18 inches wide, 12 inches thick")
    print(f"  - Gutter slopes down 1 inch from attachment to curb")
    print(f"  - Curb: 4 inches tall, 6 inches wide at base")
    print(f"  - Curb top: 4 inches wide (battered face)")
    print(f"  - Bottom has continuous slope from inside to outside")
    print(f"  - 7-vertex polygon for complete curb and gutter profile")


if __name__ == "__main__":
    main()
