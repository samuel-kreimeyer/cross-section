"""Scenario: Simple crowned road cross-section."""

from cross_section.core.domain.annotations import (
    AnnotationCollection,
    AnnotationGenerator,
    AnnotationGeneratorOptions,
)
from cross_section.core.domain import ControlPoint, RoadSection, SurfaceProfile, TravelLane
from cross_section.core.domain.components import Ditch
from cross_section.core.domain.pavement import AsphaltLayer
from cross_section.core.domain.section import SectionGeometry
def _annotation_options() -> AnnotationGeneratorOptions:
    return AnnotationGeneratorOptions(
        add_component_labels=True,
        add_width_dimensions=True,
        add_material_labels=True,
        add_traffic_symbols=True,
        add_cross_slope_symbols=True,
        add_cross_slope_text=True,
    )


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

    annotations = AnnotationGenerator.generate(geometry, _annotation_options())
    annotations.resolve_collisions(geometry=geometry)

    return geometry, annotations
