#!/usr/bin/env python
"""Generator: ARDOT Undivided Notch and Widen.

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
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cross_section.core.domain.annotations import (
    AnnotationGenerator,
    default_annotation_options,
)
from cross_section.core.domain.components.rehabilitation import (
    ExistingPavement,
    MillAndOverlay,
    NotchAndWidening,
)
from cross_section.core.domain.components.shoulders import Shoulder
from cross_section.core.domain.components.slopes import Slope
from cross_section.core.domain.pavement import AsphaltLayer, CrushedRockLayer
from cross_section.core.domain.section import ControlPoint, RoadSection
from cross_section.export.svg_annotations import AnnotatedSVGExporter
from _svg_to_png import svg_to_png


def main():
    """Create and export ARDOT notch and widen cross-section."""
    # Convert units
    ft_to_m = 0.3048
    in_to_m = 0.0254

    # Dimensions
    existing_pavement_half_width = 10.0 * ft_to_m
    lane_width = 11.0 * ft_to_m
    widen_width = 1.0 * ft_to_m
    shoulder_paved_width = 2.0 * ft_to_m
    shoulder_aggregate_flat_width = 2.0 * ft_to_m

    # Fill slope offset from ETW
    fill_slope_offset_from_etw = 16.0 * ft_to_m

    # Calculate slumped shoulder width
    slumped_shoulder_width = (
        fill_slope_offset_from_etw - shoulder_paved_width - shoulder_aggregate_flat_width
    )

    # Pavement thicknesses
    overlay_thickness = 2.0 * in_to_m
    notch_depth = 11.0 * in_to_m
    notch_horizontal = 11.0 * in_to_m
    surface_course_thickness = 2.0 * in_to_m
    binder_thickness = 3.0 * in_to_m
    aggregate_base_thickness = 6.0 * in_to_m
    shoulder_asphalt = 2.0 * in_to_m
    shoulder_aggregate_base = 11.0 * in_to_m

    # Existing pavement depth
    existing_pavement_depth = 0.3

    # Slopes
    existing_cross_slope = 0.02
    overlay_cross_slope = 0.02
    widening_cross_slope = 0.04
    shoulder_cross_slope = 0.04
    fill_slope_ratio = 4.0

    # Fill slope extends down 2 meters
    fill_vertical_drop = 2.0

    # Base elevation at centerline (crown)
    centerline_elev = 100.0

    # Define overlay layers
    overlay_layers = [
        AsphaltLayer(
            thickness=overlay_thickness,
            aggregate_size=12.5,
            binder_type="PG 64-22",
            binder_percentage=5.5,
            density=2400,
        ),
    ]

    # Define widening layers
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
            ExistingPavement(
                half_width=existing_pavement_half_width,
                total_depth=existing_pavement_depth,
                cross_slope=existing_cross_slope,
            ),
            MillAndOverlay(
                width=existing_pavement_half_width,
                mill_depth=0.0,
                overlay_layers=[layer for layer in overlay_layers],
                cross_slope=overlay_cross_slope,
            ),
            NotchAndWidening(
                notch_depth=notch_depth,
                notch_horizontal=notch_horizontal,
                widening_width=widen_width,
                widening_layers=[layer for layer in widening_layers],
                cross_slope=widening_cross_slope,
            ),
            Shoulder(
                width=shoulder_paved_width,
                cross_slope=shoulder_cross_slope,
                foreslope_ratio=6.0,
                shoulder_type="fully_paved",
                paved=True,
                pavement_layers=[layer for layer in shoulder_layers],
            ),
            Slope(
                horizontal_run=shoulder_aggregate_flat_width,
                vertical_drop=flat_aggregate_drop,
                surface_type="crushed_rock",
                thickness=0.0,
                is_surface_slope=True,
            ),
            Slope(
                horizontal_run=slumped_shoulder_width,
                vertical_drop=slumped_aggregate_drop,
                surface_type="crushed_rock",
                thickness=0.0,
                is_surface_slope=True,
            ),
            Slope(
                horizontal_run=fill_vertical_drop * fill_slope_ratio,
                vertical_drop=fill_vertical_drop,
                surface_type="grass",
                thickness=0.0,
            ),
        ],
        right_components=[
            ExistingPavement(
                half_width=existing_pavement_half_width,
                total_depth=existing_pavement_depth,
                cross_slope=existing_cross_slope,
            ),
            MillAndOverlay(
                width=existing_pavement_half_width,
                mill_depth=0.0,
                overlay_layers=[layer for layer in overlay_layers],
                cross_slope=overlay_cross_slope,
            ),
            NotchAndWidening(
                notch_depth=notch_depth,
                notch_horizontal=notch_horizontal,
                widening_width=widen_width,
                widening_layers=[layer for layer in widening_layers],
                cross_slope=widening_cross_slope,
            ),
            Shoulder(
                width=shoulder_paved_width,
                cross_slope=shoulder_cross_slope,
                foreslope_ratio=6.0,
                shoulder_type="fully_paved",
                paved=True,
                pavement_layers=[layer for layer in shoulder_layers],
            ),
            Slope(
                horizontal_run=shoulder_aggregate_flat_width,
                vertical_drop=flat_aggregate_drop,
                surface_type="crushed_rock",
                thickness=0.0,
                is_surface_slope=True,
            ),
            Slope(
                horizontal_run=slumped_shoulder_width,
                vertical_drop=slumped_aggregate_drop,
                surface_type="crushed_rock",
                thickness=0.0,
                is_surface_slope=True,
            ),
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

    geometry = section.to_geometry()
    geometry.metadata["standard"] = "ARDOT"

    # Generate annotations
    options = default_annotation_options()
    annotations = AnnotationGenerator.generate(geometry, options)
    result = annotations.resolve_collisions(geometry=geometry)
    if not result.success:
        print(f"  WARN: {result.overflow_count} overflow, {result.remaining_collisions} collisions", file=sys.stderr)

    # Export to SVG
    output_dir = SCRIPT_DIR.parent / "output"
    output_dir.mkdir(exist_ok=True)
    svg_path = output_dir / "ardot_undivided_notch_and_widen.svg"

    print(f"Generating {svg_path.name}...")
    exporter = AnnotatedSVGExporter(scale=30.48)
    with open(svg_path, 'w') as f:
        exporter.export_with_annotations(geometry, annotations, f)
    svg_to_png(svg_path)

    print(f"  Components: {len(geometry.components)}, Annotations: {annotations.count()}")


if __name__ == "__main__":
    main()
