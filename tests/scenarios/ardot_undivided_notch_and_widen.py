"""Scenario: ARDOT Undivided Notch and Widen.

Based on ARDOT standards for pavement widening with:
- 20-ft existing pavement with 2-in asphalt overlay
- 11-in notch cut into existing pavement edges
- Two 11-ft lanes completed with 1-ft of full-depth pavement on each side:
  - Two 2-in surface courses
  - One 3-in binder course
  - 6-in aggregate base
- 4-ft shoulders on both sides (2-ft paved + 2-ft aggregate)
- 4% cross slope on shoulders
- 4:1 cut slope (for shoulders)
- 4:1 fill slopes extending to 16-ft from edge of traveled way

This scenario uses the rehabilitation API where components automatically
snap together via insertion/attachment points. The key components are:
- ExistingPavement: Reference for existing pavement structure
- MillAndOverlay: Overlay placed on top of existing pavement
- NotchAndWidening: Notch cut + full-depth widening at edges
"""

from cross_section.core.domain.annotations import (
    AnnotationCollection,
    AnnotationGenerator,
    AnnotationGeneratorOptions,
)
from cross_section.core.domain.components.rehabilitation import (
    ExistingPavement,
    MillAndOverlay,
    NotchAndWidening,
)
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
    """Build ARDOT Undivided Notch and Widen scenario with annotations.

    Uses the RoadSection API with rehabilitation components that automatically
    snap together via insertion/attachment points.

    Returns:
        Tuple of (SectionGeometry, AnnotationCollection)
    """
    # Convert units
    ft_to_m = 0.3048
    in_to_m = 0.0254

    # Dimensions
    existing_pavement_half_width = 10.0 * ft_to_m  # 20' total (10' per side)
    lane_width = 11.0 * ft_to_m  # Final lane width after widening
    widen_width = 1.0 * ft_to_m  # 1 ft on each side
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
    overlay_thickness = 2.0 * in_to_m  # 2-in overlay
    notch_depth = 11.0 * in_to_m  # 11-in notch (vertical)
    notch_horizontal = 11.0 * in_to_m  # 11-in notch (horizontal)
    surface_course_thickness = 2.0 * in_to_m  # Two 2-in courses
    binder_thickness = 3.0 * in_to_m  # 3-in binder
    aggregate_base_thickness = 6.0 * in_to_m  # 6-in aggregate base
    shoulder_asphalt = 2.0 * in_to_m  # 2-in asphalt for shoulder
    shoulder_aggregate_base = 11.0 * in_to_m  # 11-in aggregate base for shoulder

    # Existing pavement depth (simplified)
    existing_pavement_depth = 0.3  # meters

    # Slopes
    existing_cross_slope = 0.02  # 2% for existing pavement
    overlay_cross_slope = 0.02  # 2% for overlay
    widening_cross_slope = 0.04  # 4% for notch/widening
    shoulder_cross_slope = 0.04  # 4%
    fill_slope_ratio = 4.0  # 4:1

    # Fill slope extends down 2 meters (typical embankment height)
    fill_vertical_drop = 2.0

    # Base elevation at centerline (crown)
    centerline_elev = 100.0

    # Define overlay layers (2" asphalt)
    overlay_layers = [
        AsphaltLayer(
            thickness=overlay_thickness,
            aggregate_size=12.5,
            binder_type="PG 64-22",
            binder_percentage=5.5,
            density=2400,
        ),
    ]

    # Define widening layers (full pavement structure)
    widening_layers = [
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
            thickness=aggregate_base_thickness,
            aggregate_size=37.5,
            density=2200,
            material_type="crushed_stone",
        ),
    ]

    # Define shoulder layers
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
    flat_aggregate_drop = shoulder_aggregate_flat_width * shoulder_cross_slope
    slumped_aggregate_drop = slumped_shoulder_width * shoulder_cross_slope

    # Create the road section using rehabilitation API
    section = RoadSection(
        name="ARDOT Undivided Notch and Widen",
        control_point=ControlPoint(x=0.0, elevation=centerline_elev),
        left_components=[
            # Existing pavement (reference for overlay/widening)
            ExistingPavement(
                half_width=existing_pavement_half_width,
                total_depth=existing_pavement_depth,
                cross_slope=existing_cross_slope,
            ),
            # Overlay on existing pavement (2" asphalt)
            MillAndOverlay(
                width=existing_pavement_half_width,  # Full coverage
                mill_depth=0.0,  # No milling in this scenario
                overlay_layers=[layer for layer in overlay_layers],
                cross_slope=overlay_cross_slope,
            ),
            # Notch and widening (11" notch + 1' full-depth widening)
            NotchAndWidening(
                notch_depth=notch_depth,
                notch_horizontal=notch_horizontal,
                widening_width=widen_width,
                widening_layers=[layer for layer in widening_layers],
                cross_slope=widening_cross_slope,
            ),
            # Paved shoulder (2 ft)
            Shoulder(
                width=shoulder_paved_width,
                cross_slope=shoulder_cross_slope,
                foreslope_ratio=6.0,
                shoulder_type="fully_paved",
                paved=True,
                pavement_layers=[layer for layer in shoulder_layers],
            ),
            # Flat aggregate section (2 ft at 4%)
            Slope(
                horizontal_run=shoulder_aggregate_flat_width,
                vertical_drop=flat_aggregate_drop,
                surface_type="crushed_rock",
                thickness=0.0,
                is_surface_slope=True,
            ),
            # Slumped aggregate section (12 ft at 4% to fill slope)
            Slope(
                horizontal_run=slumped_shoulder_width,
                vertical_drop=slumped_aggregate_drop,
                surface_type="crushed_rock",
                thickness=0.0,
                is_surface_slope=True,
            ),
            # Fill slope (4:1)
            Slope(
                horizontal_run=fill_vertical_drop * fill_slope_ratio,
                vertical_drop=fill_vertical_drop,
                surface_type="grass",
                thickness=0.0,
            ),
        ],
        right_components=[
            # Existing pavement (right side)
            ExistingPavement(
                half_width=existing_pavement_half_width,
                total_depth=existing_pavement_depth,
                cross_slope=existing_cross_slope,
            ),
            # Overlay on existing pavement
            MillAndOverlay(
                width=existing_pavement_half_width,
                mill_depth=0.0,
                overlay_layers=[layer for layer in overlay_layers],
                cross_slope=overlay_cross_slope,
            ),
            # Notch and widening
            NotchAndWidening(
                notch_depth=notch_depth,
                notch_horizontal=notch_horizontal,
                widening_width=widen_width,
                widening_layers=[layer for layer in widening_layers],
                cross_slope=widening_cross_slope,
            ),
            # Paved shoulder
            Shoulder(
                width=shoulder_paved_width,
                cross_slope=shoulder_cross_slope,
                foreslope_ratio=6.0,
                shoulder_type="fully_paved",
                paved=True,
                pavement_layers=[layer for layer in shoulder_layers],
            ),
            # Flat aggregate section
            Slope(
                horizontal_run=shoulder_aggregate_flat_width,
                vertical_drop=flat_aggregate_drop,
                surface_type="crushed_rock",
                thickness=0.0,
                is_surface_slope=True,
            ),
            # Slumped aggregate section
            Slope(
                horizontal_run=slumped_shoulder_width,
                vertical_drop=slumped_aggregate_drop,
                surface_type="crushed_rock",
                thickness=0.0,
                is_surface_slope=True,
            ),
            # Fill slope (4:1)
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
