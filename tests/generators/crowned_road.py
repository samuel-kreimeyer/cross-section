#!/usr/bin/env python
"""Generator: Simple crowned road cross-section.

Creates a crowned road with:
- Two 12-ft travel lanes
- 8-ft surface profiles (shoulder area)
- V-ditches on both sides
- 2% cross slope
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
from cross_section.core.domain import ControlPoint, RoadSection, SurfaceProfile, TravelLane
from cross_section.core.domain.components import Ditch
from cross_section.core.domain.pavement import AsphaltLayer
from cross_section.export.svg import SVGExporter
from _svg_to_png import svg_to_png


def main():
    """Create and export crowned road cross-section."""
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

    # Generate annotations
    annotations = AnnotationCollector(units="imperial").collect(geometry)

    # Export to SVG
    output_dir = SCRIPT_DIR.parent / "output"
    output_dir.mkdir(exist_ok=True)
    svg_path = output_dir / "crowned_road.svg"

    print(f"Generating {svg_path.name}...")
    exporter = SVGExporter(scale=30.48)
    with open(svg_path, 'w') as f:
        exporter.export_annotated(geometry, annotations, f)
    svg_to_png(svg_path)

    print(f"  Components: {len(geometry.components)}, Annotations: {len(annotations.dimensions) + len(annotations.slope_tags)}")


if __name__ == "__main__":
    main()
