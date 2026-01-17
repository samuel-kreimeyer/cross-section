"""Scenario: ARDOT Undivided Highway.

Based on ARDOT standards for undivided highways with:
- Two 11-ft lanes paved with two 2-in surface courses and a 3-in asphalt binder course on 6-in aggregate base
- 4-ft shoulders on both sides:
  - 2-ft paved with 2-in asphalt pavement on 11-in aggregate base
  - 2-ft aggregate extension
- 2% cross slopes on surface and subgrade
- 4% slopes on paved shoulder section
- 4:1 fill slopes extending to 16-ft from edge of traveled way on both sides
- 3:1 back slope on left side

This scenario uses the proper RoadSection API where components automatically
snap together via insertion/attachment points.
"""

from cross_section.core.domain.annotations import (
    AnnotationCollection,
    AnnotationGenerator,
    AnnotationGeneratorOptions,
)
from cross_section.core.domain.components.lanes import TravelLane
from cross_section.core.domain.components.shoulders import Shoulder
from cross_section.core.domain.components.slopes import Slope
from cross_section.core.domain.pavement import AsphaltLayer, CrushedRockLayer
from cross_section.core.domain.section import ControlPoint, RoadSection, SectionGeometry
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
    """Build ARDOT Undivided Highway scenario with annotations.

    Uses the RoadSection API to assemble components that automatically
    snap together via insertion/attachment points.

    Returns:
        Tuple of (SectionGeometry, AnnotationCollection)
    """
    # Convert units
    ft_to_m = 0.3048
    in_to_m = 0.0254

    # Lane dimensions
    lane_width = 11.0 * ft_to_m

    # Shoulder dimensions
    shoulder_paved_width = 2.0 * ft_to_m
    shoulder_aggregate_flat_width = 2.0 * ft_to_m

    # Fill slope offset from ETW (edge of traveled way = lane edge)
    fill_slope_offset_from_etw = 16.0 * ft_to_m

    # Calculate slumped shoulder width (from end of flat aggregate to fill slope top)
    # = 16' - 2' paved - 2' flat aggregate = 12'
    slumped_shoulder_width = (
        fill_slope_offset_from_etw - shoulder_paved_width - shoulder_aggregate_flat_width
    )

    # Pavement thicknesses
    surface_course_thickness = 2.0 * in_to_m  # 2-in surface course
    binder_thickness = 3.0 * in_to_m  # 3-in binder
    lane_aggregate_base = 6.0 * in_to_m  # 6-in aggregate base for lanes
    shoulder_asphalt = 2.0 * in_to_m  # 2-in asphalt for shoulder
    shoulder_aggregate_base = 11.0 * in_to_m  # 11-in aggregate base for shoulder

    # Slopes
    lane_cross_slope = 0.02  # 2%
    shoulder_cross_slope = 0.04  # 4%
    fill_slope_ratio = 4.0  # 4:1
    back_slope_ratio = 3.0  # 3:1

    # Fill slope extends down 2 meters (typical embankment height)
    fill_vertical_drop = 2.0

    # Back slope rises 2 meters
    back_slope_rise = 2.0

    # Base elevation at centerline (crown)
    centerline_elev = 100.0

    # Define pavement layers for lanes
    lane_layers = [
        AsphaltLayer(
            thickness=surface_course_thickness,
            aggregate_size=12.5,
            binder_type="PG 64-22",
            binder_percentage=5.5,
            density=2400,
        ),
        AsphaltLayer(
            thickness=surface_course_thickness,
            aggregate_size=12.5,
            binder_type="PG 64-22",
            binder_percentage=5.5,
            density=2400,
        ),
        AsphaltLayer(
            thickness=binder_thickness,
            aggregate_size=19.0,
            binder_type="PG 64-22",
            binder_percentage=4.5,
            density=2350,
        ),
        CrushedRockLayer(
            thickness=lane_aggregate_base,
            aggregate_size=37.5,
            density=2200,
            material_type="crushed_stone",
        ),
    ]

    # Define pavement layers for paved shoulder
    shoulder_layers = [
        AsphaltLayer(
            thickness=shoulder_asphalt,
            aggregate_size=12.5,
            binder_type="PG 64-22",
            binder_percentage=5.5,
            density=2400,
        ),
        CrushedRockLayer(
            thickness=shoulder_aggregate_base,
            aggregate_size=37.5,
            density=2200,
            material_type="crushed_stone",
        ),
    ]

    # Calculate vertical drops for aggregate shoulder sections
    # Flat aggregate: 2' at 4% slope
    flat_aggregate_drop = shoulder_aggregate_flat_width * shoulder_cross_slope
    # Slumped aggregate: 12' at 4% slope
    slumped_aggregate_drop = slumped_shoulder_width * shoulder_cross_slope

    # Create the road section using the proper API
    section = RoadSection(
        name="ARDOT Undivided Highway",
        control_point=ControlPoint(x=0.0, elevation=centerline_elev),
        left_components=[
            # Left lane (from centerline extending left)
            TravelLane(
                width=lane_width,
                cross_slope=lane_cross_slope,
                traffic_direction="inbound",
                pavement_layers=lane_layers.copy(),
            ),
            # Left paved shoulder (2 ft)
            Shoulder(
                width=shoulder_paved_width,
                cross_slope=shoulder_cross_slope,
                foreslope_ratio=6.0,  # Not used for fully_paved but required
                shoulder_type="fully_paved",
                paved=True,
                pavement_layers=shoulder_layers.copy(),
            ),
            # Left flat aggregate section (2 ft at 4% - represented as thin slope)
            Slope(
                horizontal_run=shoulder_aggregate_flat_width,
                vertical_drop=flat_aggregate_drop,
                surface_type="crushed_rock",
                thickness=0.0,  # Surface only (renders as line)
                is_surface_slope=True,  # This is a roadway surface, not a fill/cut slope
            ),
            # Left slumped aggregate section (12 ft at 4% to fill slope)
            Slope(
                horizontal_run=slumped_shoulder_width,
                vertical_drop=slumped_aggregate_drop,
                surface_type="crushed_rock",
                thickness=0.0,  # Surface only
                is_surface_slope=True,  # This is a roadway surface, not a fill/cut slope
            ),
            # Left fill slope (4:1)
            Slope(
                horizontal_run=fill_vertical_drop * fill_slope_ratio,
                vertical_drop=fill_vertical_drop,
                surface_type="grass",
                thickness=0.0,
            ),
            # Left back slope (3:1, rises)
            Slope(
                horizontal_run=back_slope_rise * back_slope_ratio,
                vertical_drop=-back_slope_rise,  # Negative = rises
                surface_type="grass",
                thickness=0.0,
            ),
        ],
        right_components=[
            # Right lane (from centerline extending right)
            TravelLane(
                width=lane_width,
                cross_slope=lane_cross_slope,
                traffic_direction="outbound",
                pavement_layers=lane_layers.copy(),
            ),
            # Right paved shoulder (2 ft)
            Shoulder(
                width=shoulder_paved_width,
                cross_slope=shoulder_cross_slope,
                foreslope_ratio=6.0,
                shoulder_type="fully_paved",
                paved=True,
                pavement_layers=shoulder_layers.copy(),
            ),
            # Right flat aggregate section (2 ft at 4%)
            Slope(
                horizontal_run=shoulder_aggregate_flat_width,
                vertical_drop=flat_aggregate_drop,
                surface_type="crushed_rock",
                thickness=0.0,
                is_surface_slope=True,  # This is a roadway surface, not a fill/cut slope
            ),
            # Right slumped aggregate section (12 ft at 4% to fill slope)
            Slope(
                horizontal_run=slumped_shoulder_width,
                vertical_drop=slumped_aggregate_drop,
                surface_type="crushed_rock",
                thickness=0.0,
                is_surface_slope=True,  # This is a roadway surface, not a fill/cut slope
            ),
            # Right fill slope (4:1)
            Slope(
                horizontal_run=fill_vertical_drop * fill_slope_ratio,
                vertical_drop=fill_vertical_drop,
                surface_type="grass",
                thickness=0.0,
            ),
        ],
    )

    # Validate the section
    errors = section.validate()
    if errors:
        raise ValueError(f"Section validation failed: {errors}")

    # Generate geometry (components automatically snap together)
    geometry = section.to_geometry()

    # Add ARDOT-specific metadata
    geometry.metadata["standard"] = "ARDOT"

    annotations = AnnotationGenerator.generate(geometry, _annotation_options())
    annotations.resolve_collisions(geometry=geometry)

    return geometry, annotations
