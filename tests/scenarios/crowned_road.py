"""Scenario: Simple crowned road cross-section.

Creates a simple crowned road with:
- Two 12-ft travel lanes (24 ft total)
- 8-ft paved shoulders on each side
- 1-ft deep ditches with 4:1 side slopes
- Width dimensions above each component
- Overall width dimension above all components
- Leader pointing to crown with "Crown" text
"""

from cross_section.core.domain.annotations import (
    AnnotationCollection,
    DimensionAnnotation,
    LeaderAnnotation,
)
from cross_section.core.domain.section import SectionGeometry
from cross_section.core.geometry.primitives import ComponentGeometry, Point2D, Polygon


def build_scenario() -> tuple[SectionGeometry, AnnotationCollection]:
    """Build crowned road scenario with annotations.

    Returns:
        Tuple of (SectionGeometry, AnnotationCollection)
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

    # Create section geometry
    section = SectionGeometry(
        components=components,
        metadata={
            "name": "Crowned Road with Ditches",
            "control_point": {"x": 0.0, "elevation": crown_elevation}
        }
    )

    # Create annotations
    lane_width = lane_width_ft * ft_to_m
    shoulder_width = shoulder_width_ft * ft_to_m

    collection = AnnotationCollection()

    # Dimension offset (vertical spacing)
    dim_offset_lower = 0.5  # For component dimensions
    dim_offset_upper = 1.2  # For overall dimension

    # Component dimensions (lower level)
    # Left shoulder
    left_shoulder_right = -lane_width
    left_shoulder_left = left_shoulder_right - shoulder_width
    collection.add(DimensionAnnotation(
        start=Point2D(left_shoulder_left, crown_elevation),
        end=Point2D(left_shoulder_right, crown_elevation),
        offset=dim_offset_lower,
        dimension_text="8'-0\"",
        layer="dimensions"
    ))

    # Left lane
    collection.add(DimensionAnnotation(
        start=Point2D(-lane_width, crown_elevation),
        end=Point2D(0.0, crown_elevation),
        offset=dim_offset_lower,
        dimension_text="12'-0\"",
        layer="dimensions"
    ))

    # Right lane
    collection.add(DimensionAnnotation(
        start=Point2D(0.0, crown_elevation),
        end=Point2D(lane_width, crown_elevation),
        offset=dim_offset_lower,
        dimension_text="12'-0\"",
        layer="dimensions"
    ))

    # Right shoulder
    right_shoulder_left = lane_width
    right_shoulder_right = right_shoulder_left + shoulder_width
    collection.add(DimensionAnnotation(
        start=Point2D(right_shoulder_left, crown_elevation),
        end=Point2D(right_shoulder_right, crown_elevation),
        offset=dim_offset_lower,
        dimension_text="8'-0\"",
        layer="dimensions"
    ))

    # Overall width dimension (upper level)
    collection.add(DimensionAnnotation(
        start=Point2D(-lane_width - shoulder_width, crown_elevation),
        end=Point2D(lane_width + shoulder_width, crown_elevation),
        offset=dim_offset_upper,
        dimension_text="40'-0\"",
        layer="dimensions"
    ))

    # Leader pointing to crown
    collection.add(LeaderAnnotation(
        points=[
            Point2D(0.0, crown_elevation),  # At crown
            Point2D(1.0, crown_elevation + 0.3),  # Up and right
            Point2D(2.5, crown_elevation + 0.3),  # Extend to the right
        ],
        text="Crown",
        arrow_at_start=True,
        layer="leaders"
    ))

    # Resolve annotation collisions with geometry awareness
    collection.resolve_collisions(geometry=section)

    return section, collection
