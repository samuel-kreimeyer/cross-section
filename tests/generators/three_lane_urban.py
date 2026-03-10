#!/usr/bin/env python
"""Generator: 3-lane urban section with turn lane.

Creates a complex urban road section with:
- Two 10-ft travel lanes and one 12-ft center turn lane
- 4-layer asphalt pavement (surface, intermediate, base, cement-treated subgrade)
- 6-inch barrier curbs with 1.5-ft gutters
- 3-ft grass buffers
- 5-ft concrete sidewalks (4-inch thick)
- 6:1 fill slopes off back of sidewalks
- Crowned at center of turn lane, 2% cross slope
- Automated annotations
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cross_section.core.domain.annotations import AnnotationCollector
from cross_section.core.domain import (
    Buffer,
    ControlPoint,
    Gutter,
    RoadSection,
    Sidewalk,
    TurnLane,
    TravelLane,
)
from cross_section.core.domain.components import Curb
from cross_section.core.domain.components.slopes import Slope
from cross_section.core.domain.pavement import AsphaltLayer, CrushedRockLayer
from cross_section.export.svg import SVGExporter
from _svg_to_png import svg_to_png


def main():
    """Create and export 3-lane urban cross-section."""
    ft_to_m = 0.3048
    in_to_m = 0.0254

    left_lane_width = 10.0 * ft_to_m
    center_lane_width = 12.0 * ft_to_m
    right_lane_width = 10.0 * ft_to_m

    surface_thickness = 2.0 * in_to_m
    intermediate_thickness = 3.0 * in_to_m
    base_thickness = 4.0 * in_to_m
    subgrade_thickness = 6.0 * in_to_m

    curb_height = 6.0 * in_to_m
    curb_thickness = 12.0 * in_to_m
    gutter_width = 1.5 * ft_to_m
    buffer_width = 3.0 * ft_to_m
    sidewalk_width = 5.0 * ft_to_m
    sidewalk_thickness = 4.0 * in_to_m

    cross_slope = 0.02
    sidewalk_slope = 0.02
    fill_slope = 6.0

    crown_elevation = 100.0

    lane_layers = [
        AsphaltLayer(
            thickness=surface_thickness,
            aggregate_size=12.5,
            binder_type="PG 64-22",
            binder_percentage=5.5,
            density=2400,
        ),
        AsphaltLayer(
            thickness=intermediate_thickness,
            aggregate_size=19.0,
            binder_type="PG 64-22",
            binder_percentage=5.0,
            density=2350,
        ),
        CrushedRockLayer(
            thickness=base_thickness,
            aggregate_size=37.5,
            density=2200,
            material_type="aggregate_base",
        ),
        CrushedRockLayer(
            thickness=subgrade_thickness,
            aggregate_size=50.0,
            density=2100,
            material_type="cement_treated",
        ),
    ]

    turn_lane = TurnLane(
        width=center_lane_width,
        cross_slope=cross_slope,
        pavement_layers=[layer for layer in lane_layers],
    )
    left_turn, right_turn = turn_lane.split()

    section = RoadSection(
        name="3-Lane Urban Section with Turn Lane",
        control_point=ControlPoint(x=0.0, elevation=crown_elevation),
        left_components=[
            left_turn,
            TravelLane(
                width=left_lane_width,
                cross_slope=cross_slope,
                traffic_direction="inbound",
                pavement_layers=[layer for layer in lane_layers],
            ),
            Gutter(width=gutter_width, drop=curb_height, thickness=curb_height),
            Curb(
                gutter_width=0.0,
                gutter_drop=0.0,
                curb_height=curb_height,
                curb_width_bottom=curb_thickness,
                curb_width_top=curb_thickness,
            ),
            Buffer(width=buffer_width, cross_slope=0.0),
            Sidewalk(
                width=sidewalk_width,
                cross_slope=sidewalk_slope,
                thickness=sidewalk_thickness,
            ),
            Slope(
                horizontal_run=fill_slope * 2.0,
                vertical_drop=2.0,
                surface_type="grass",
                thickness=0.0,
            ),
        ],
        right_components=[
            right_turn,
            TravelLane(
                width=right_lane_width,
                cross_slope=cross_slope,
                traffic_direction="outbound",
                pavement_layers=[layer for layer in lane_layers],
            ),
            Gutter(width=gutter_width, drop=curb_height, thickness=curb_height),
            Curb(
                gutter_width=0.0,
                gutter_drop=0.0,
                curb_height=curb_height,
                curb_width_bottom=curb_thickness,
                curb_width_top=curb_thickness,
            ),
            Buffer(width=buffer_width, cross_slope=0.0),
            Sidewalk(
                width=sidewalk_width,
                cross_slope=sidewalk_slope,
                thickness=sidewalk_thickness,
            ),
            Slope(
                horizontal_run=fill_slope * 2.0,
                vertical_drop=2.0,
                surface_type="grass",
                thickness=0.0,
            ),
        ],
    )

    geometry = section.to_geometry()

    # Generate annotations
    annotations = AnnotationCollector(units="imperial").collect(geometry)

    # Export to SVG
    output_dir = SCRIPT_DIR.parent / "output"
    output_dir.mkdir(exist_ok=True)
    svg_path = output_dir / "3lane_urban.svg"

    print(f"Generating {svg_path.name}...")
    exporter = SVGExporter(scale=30.48)
    with open(svg_path, 'w') as f:
        exporter.export_annotated(geometry, annotations, f)
    svg_to_png(svg_path)

    print(f"  Components: {len(geometry.components)}, Annotations: {len(annotations.dimensions) + len(annotations.slope_tags)}")


if __name__ == "__main__":
    main()
