#!/usr/bin/env python
"""Basic example demonstrating cross-section creation."""

from cross_section.core.domain import RoadSection, ControlPoint, TravelLane


def main():
    """Create a simple two-lane road section."""

    # Create a control point (crown/grade point)
    control_point = ControlPoint(
        x=0.0,
        elevation=100.0,
        description="Road Crown"
    )

    # Create a road section
    section = RoadSection(
        name="Two-Lane Road",
        control_point=control_point
    )

    # Add components (they snap together automatically)
    section.add_component(TravelLane(
        width=3.6,
        cross_slope=0.02,
        direction='outbound',
        surface_type='asphalt'
    ))

    section.add_component(TravelLane(
        width=3.6,
        cross_slope=0.02,
        direction='outbound',
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

    print(f"  Components: {len(geometry.components)}")
    print(f"  Section bounds: {geometry.bounds()}")

    # Show individual component details
    print(f"\nComponent details:")
    for i, comp_geom in enumerate(geometry.components):
        print(f"  Component {i}:")
        print(f"    Type: {comp_geom.metadata.get('component_type', 'Unknown')}")
        print(f"    Width: {comp_geom.metadata.get('width', 'N/A')} m")
        print(f"    Cross slope: {comp_geom.metadata.get('cross_slope', 'N/A')}")
        print(f"    Direction: {comp_geom.metadata.get('direction', 'N/A')}")
        print(f"    Bounds: {comp_geom.bounds()}")
        print(f"    Polygons: {len(comp_geom.polygons)}")


if __name__ == "__main__":
    main()
