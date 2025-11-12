#!/usr/bin/env python
"""Example demonstrating symmetric road section with left and right components."""

from cross_section.core.domain import RoadSection, ControlPoint, TravelLane


def main():
    """Create a symmetric four-lane divided highway section."""

    # Create a control point at the centerline crown
    control_point = ControlPoint(
        x=0.0,
        elevation=100.0,
        description="Centerline Crown"
    )

    # Create a road section
    section = RoadSection(
        name="Four-Lane Divided Highway",
        control_point=control_point
    )

    # Add left side components (extending in negative X direction)
    # Traffic flows inbound (toward the crown/centerline conceptually)
    section.add_component_left(TravelLane(
        width=3.6,
        cross_slope=0.02,
        traffic_direction='inbound',
        surface_type='asphalt'
    ))

    section.add_component_left(TravelLane(
        width=3.6,
        cross_slope=0.02,
        traffic_direction='inbound',
        surface_type='asphalt'
    ))

    # Add right side components (extending in positive X direction)
    # Traffic flows outbound (away from the crown/centerline conceptually)
    section.add_component_right(TravelLane(
        width=3.6,
        cross_slope=0.02,
        traffic_direction='outbound',
        surface_type='asphalt'
    ))

    section.add_component_right(TravelLane(
        width=3.6,
        cross_slope=0.02,
        traffic_direction='outbound',
        surface_type='asphalt'
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
    print(f"  Section bounds: {geometry.bounds()}")

    # Show individual component details
    print(f"\nComponent details:")

    # Left components are first in the geometry list
    print(f"\n  Left Side (extending in negative X):")
    for i in range(geometry.metadata['left_component_count']):
        comp_geom = geometry.components[i]
        print(f"    Lane {i + 1}:")
        print(f"      Assembly direction: {comp_geom.metadata.get('assembly_direction')}")
        print(f"      Traffic direction: {comp_geom.metadata.get('traffic_direction')}")
        print(f"      Width: {comp_geom.metadata.get('width')} m")
        print(f"      Cross slope: {comp_geom.metadata.get('cross_slope')}")
        print(f"      Bounds: {comp_geom.bounds()}")

    # Right components follow in the geometry list
    print(f"\n  Right Side (extending in positive X):")
    for i in range(geometry.metadata['right_component_count']):
        idx = geometry.metadata['left_component_count'] + i
        comp_geom = geometry.components[idx]
        print(f"    Lane {i + 1}:")
        print(f"      Assembly direction: {comp_geom.metadata.get('assembly_direction')}")
        print(f"      Traffic direction: {comp_geom.metadata.get('traffic_direction')}")
        print(f"      Width: {comp_geom.metadata.get('width')} m")
        print(f"      Cross slope: {comp_geom.metadata.get('cross_slope')}")
        print(f"      Bounds: {comp_geom.bounds()}")

    print(f"\n✓ Symmetric section successfully created!")
    print(f"  Total width: {geometry.bounds()[2] - geometry.bounds()[0]:.1f} m")


if __name__ == "__main__":
    main()
