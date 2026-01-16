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
from cross_section.core.domain import ControlPoint, RoadSection, SurfaceProfile, TravelLane
from cross_section.core.domain.components import Ditch
from cross_section.core.domain.pavement import AsphaltLayer
from cross_section.core.domain.section import SectionGeometry
from cross_section.core.geometry.primitives import Point2D


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

    pavement_layer = AsphaltLayer(
        thickness=0.15,
        aggregate_size=12.5,
        binder_type="PG 64-22",
        binder_percentage=5.5,
        density=2400,
    )

    # Build section using the domain API
    section = RoadSection(
        name="Crowned Road with Ditches",
        control_point=ControlPoint(x=0.0, elevation=crown_elevation),
        left_components=[
            TravelLane(
                width=lane_width_ft * ft_to_m,
                cross_slope=crown_slope,
                traffic_direction="inbound",
                pavement_layers=[pavement_layer],
            ),
            SurfaceProfile(
                segments=[(shoulder_width_ft * ft_to_m, shoulder_width_ft * ft_to_m * shoulder_slope)],
                surface_type="asphalt",
            ),
            Ditch(
                depth=ditch_depth_ft * ft_to_m,
                foreslope_ratio=ditch_slope,
                backslope_ratio=ditch_slope,
                bottom_width=0.0,
            ),
        ],
        right_components=[
            TravelLane(
                width=lane_width_ft * ft_to_m,
                cross_slope=crown_slope,
                traffic_direction="outbound",
                pavement_layers=[pavement_layer],
            ),
            SurfaceProfile(
                segments=[(shoulder_width_ft * ft_to_m, shoulder_width_ft * ft_to_m * shoulder_slope)],
                surface_type="asphalt",
            ),
            Ditch(
                depth=ditch_depth_ft * ft_to_m,
                foreslope_ratio=ditch_slope,
                backslope_ratio=ditch_slope,
                bottom_width=0.0,
            ),
        ],
    )

    geometry = section.to_geometry()

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
    collection.resolve_collisions(geometry=geometry)

    return geometry, collection
