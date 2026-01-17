"""Example: Generate annotated crowned road cross-section."""

from cross_section.core.domain.annotations import (
    AnnotationGenerator,
    AnnotationGeneratorOptions,
)
from cross_section.core.domain.section import SectionGeometry
from cross_section.core.geometry.primitives import ComponentGeometry, Point2D, Polygon
from cross_section.export import AnnotatedSVGExporter


def _annotation_options() -> AnnotationGeneratorOptions:
    return AnnotationGeneratorOptions(
        add_component_labels=True,
        add_width_dimensions=True,
        add_material_labels=True,
        add_traffic_symbols=True,
        add_cross_slope_symbols=True,
        add_cross_slope_text=True,
    )


def create_crowned_road_section() -> SectionGeometry:
    """Create a simple crowned road section.

    Returns:
        SectionGeometry with crowned road components
    """
    # Convert feet to meters
    ft_to_m = 0.3048

    # Dimensions in feet
    lane_width_ft = 12.0
    shoulder_width_ft = 8.0
    ditch_depth_ft = 1.0

    # Crown slope (2% typical)
    crown_slope = 0.02

    # Shoulder slope (same as crown, continues downward)
    shoulder_slope = 0.02

    # Ditch side slope (4:1)
    ditch_slope = 4.0

    # Base elevation at crown (centerline)
    crown_elevation = 100.0  # meters

    # Calculate positions (working outward from center)
    # Left lane (from center to left edge)
    left_lane_right = 0.0
    left_lane_left = -lane_width_ft * ft_to_m
    left_lane_left_elev = crown_elevation - (lane_width_ft * ft_to_m * crown_slope)

    # Right lane (from center to right edge)
    right_lane_left = 0.0
    right_lane_right = lane_width_ft * ft_to_m
    right_lane_right_elev = crown_elevation - (lane_width_ft * ft_to_m * crown_slope)

    # Left shoulder
    left_shoulder_right = left_lane_left
    left_shoulder_left = left_shoulder_right - shoulder_width_ft * ft_to_m
    left_shoulder_left_elev = left_lane_left_elev - (shoulder_width_ft * ft_to_m * shoulder_slope)

    # Right shoulder
    right_shoulder_left = right_lane_right
    right_shoulder_right = right_shoulder_left + shoulder_width_ft * ft_to_m
    right_shoulder_right_elev = right_lane_right_elev - (shoulder_width_ft * ft_to_m * shoulder_slope)

    # Left ditch
    left_ditch_top = left_shoulder_left
    left_ditch_top_elev = left_shoulder_left_elev
    left_ditch_bottom_elev = left_ditch_top_elev - ditch_depth_ft * ft_to_m
    left_ditch_bottom = left_ditch_top - (ditch_depth_ft * ft_to_m * ditch_slope)
    left_ditch_far = left_ditch_bottom - (ditch_depth_ft * ft_to_m * ditch_slope)

    # Right ditch
    right_ditch_top = right_shoulder_right
    right_ditch_top_elev = right_shoulder_right_elev
    right_ditch_bottom_elev = right_ditch_top_elev - ditch_depth_ft * ft_to_m
    right_ditch_bottom = right_ditch_top + (ditch_depth_ft * ft_to_m * ditch_slope)
    right_ditch_far = right_ditch_bottom + (ditch_depth_ft * ft_to_m * ditch_slope)

    # Create component geometries
    components = []

    # Left lane
    left_lane_poly = Polygon(exterior=[
        Point2D(left_lane_left, left_lane_left_elev),
        Point2D(left_lane_right, crown_elevation),
        Point2D(left_lane_right, crown_elevation - 0.15),  # Pavement thickness
        Point2D(left_lane_left, left_lane_left_elev - 0.15),
    ])
    components.append(ComponentGeometry(
        polygons=[left_lane_poly],
        metadata={
            "component_type": "TravelLane",
            "width": lane_width_ft * ft_to_m,
            "assembly_direction": "left",
        }
    ))

    # Right lane
    right_lane_poly = Polygon(exterior=[
        Point2D(right_lane_left, crown_elevation),
        Point2D(right_lane_right, right_lane_right_elev),
        Point2D(right_lane_right, right_lane_right_elev - 0.15),
        Point2D(right_lane_left, crown_elevation - 0.15),
    ])
    components.append(ComponentGeometry(
        polygons=[right_lane_poly],
        metadata={
            "component_type": "TravelLane",
            "width": lane_width_ft * ft_to_m,
            "assembly_direction": "right",
        }
    ))

    # Left shoulder
    left_shoulder_poly = Polygon(exterior=[
        Point2D(left_shoulder_left, left_shoulder_left_elev),
        Point2D(left_shoulder_right, left_lane_left_elev),
        Point2D(left_shoulder_right, left_lane_left_elev - 0.15),
        Point2D(left_shoulder_left, left_shoulder_left_elev - 0.15),
    ])
    components.append(ComponentGeometry(
        polygons=[left_shoulder_poly],
        metadata={
            "component_type": "Shoulder",
            "width": shoulder_width_ft * ft_to_m,
            "assembly_direction": "left",
        }
    ))

    # Right shoulder
    right_shoulder_poly = Polygon(exterior=[
        Point2D(right_shoulder_left, right_lane_right_elev),
        Point2D(right_shoulder_right, right_shoulder_right_elev),
        Point2D(right_shoulder_right, right_shoulder_right_elev - 0.15),
        Point2D(right_shoulder_left, right_lane_right_elev - 0.15),
    ])
    components.append(ComponentGeometry(
        polygons=[right_shoulder_poly],
        metadata={
            "component_type": "Shoulder",
            "width": shoulder_width_ft * ft_to_m,
            "assembly_direction": "right",
        }
    ))

    # Left ditch (as polylines - no fill)
    # Attach to top outside edge of shoulder (not bottom)
    left_ditch_line = [
        Point2D(left_ditch_top, left_ditch_top_elev),
        Point2D(left_ditch_bottom, left_ditch_bottom_elev),
        Point2D(left_ditch_far, left_ditch_top_elev),
    ]
    components.append(ComponentGeometry(
        polygons=[],
        polylines=[left_ditch_line],
        metadata={
            "component_type": "Ditch",
            "width": abs(left_ditch_far - left_ditch_top),
            "assembly_direction": "left",
            "depth": ditch_depth_ft * ft_to_m,
        }
    ))

    # Right ditch
    # Attach to top outside edge of shoulder (not bottom)
    right_ditch_line = [
        Point2D(right_ditch_top, right_ditch_top_elev),
        Point2D(right_ditch_bottom, right_ditch_bottom_elev),
        Point2D(right_ditch_far, right_ditch_top_elev),
    ]
    components.append(ComponentGeometry(
        polygons=[],
        polylines=[right_ditch_line],
        metadata={
            "component_type": "Ditch",
            "width": abs(right_ditch_far - right_ditch_top),
            "assembly_direction": "right",
            "depth": ditch_depth_ft * ft_to_m,
        }
    ))

    return SectionGeometry(
        components=components,
        metadata={
            "name": "Crowned Road with Ditches",
            "control_point": {"x": 0.0, "elevation": crown_elevation}
        }
    )


def main():
    """Generate and export annotated crowned road section."""
    print("Generating crowned road cross-section...")

    # Create section geometry
    section = create_crowned_road_section()
    print(f"  Created section with {len(section.components)} components")

    annotations = AnnotationGenerator.generate(section, _annotation_options())
    annotations.resolve_collisions(geometry=section)
    print(f"  Created {annotations.count()} annotations")

    # Export to SVG
    exporter = AnnotatedSVGExporter(
        scale=100.0,  # 100 pixels per meter
        vertical_exaggeration=1.0,  # No vertical exaggeration for demonstration
        units="imperial"
    )

    output_path = "crowned_road_annotated.svg"
    with open(output_path, "w") as f:
        exporter.export_with_annotations(section, annotations, f)

    print(f"  Exported to {output_path}")
    print("\nSection details:")
    print(f"  - Two 12-ft travel lanes")
    print(f"  - Two 8-ft paved shoulders")
    print(f"  - 1-ft deep ditches with 4:1 side slopes")
    print(f"  - Total paved width: 40 ft")
    print(f"  - Crown at centerline, 2% cross slope")
    print("\nAnnotations:")
    print(f"  - Automated annotation set (generator defaults with slope/traffic symbols)")
    print(f"  - No vertical exaggeration (1:1 scale)")


if __name__ == "__main__":
    main()
