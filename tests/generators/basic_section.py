#!/usr/bin/env python
"""Generator: Basic two-lane road section.

A simple example demonstrating cross-section creation with:
- Two travel lanes on the right side
- Standard pavement structure
- 2% cross slope
"""

import sys
from pathlib import Path

# Add src to path for imports
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from cross_section.core.domain import RoadSection, ControlPoint, TravelLane
from cross_section.core.domain.annotations import AnnotationCollector
from cross_section.core.domain.pavement import AsphaltLayer, CrushedRockLayer
from cross_section.export.svg import SVGExporter
from _svg_to_png import svg_to_png


def main():
    """Create a simple two-lane road section."""

    # Create a control point (crown/grade point)
    control_point = ControlPoint(
        x=0.0,
        elevation=100.0,
        description="Road Crown"
    )

    # Standard pavement layers
    pavement_layers = [
        AsphaltLayer(
            thickness=0.05,
            aggregate_size=12.5,
            binder_type='PG 64-22',
            binder_percentage=5.5,
            density=2400
        ),
        AsphaltLayer(
            thickness=0.075,
            aggregate_size=19.0,
            binder_type='PG 64-22',
            binder_percentage=5.0,
            density=2380
        ),
        CrushedRockLayer(
            thickness=0.15,
            aggregate_size=37.5,
            density=2200,
            material_type='crushed_stone'
        ),
    ]

    # Create a road section
    section = RoadSection(
        name="Two-Lane Road",
        control_point=control_point
    )

    # Add two lanes on the right side
    section.add_component_right(TravelLane(
        width=3.6,
        cross_slope=0.02,
        traffic_direction='outbound',
        pavement_layers=pavement_layers
    ))

    section.add_component_right(TravelLane(
        width=3.6,
        cross_slope=0.02,
        traffic_direction='outbound',
        pavement_layers=[layer for layer in pavement_layers]  # Copy layers
    ))

    # Generate geometry
    geometry = section.to_geometry()

    # Generate annotations
    annotations = AnnotationCollector(units="imperial").collect(geometry)

    # Export to SVG
    output_dir = SCRIPT_DIR.parent / "output"
    output_dir.mkdir(exist_ok=True)
    svg_path = output_dir / "basic_section.svg"

    print(f"Generating {svg_path.name}...")
    exporter = SVGExporter(scale=50.0)
    with open(svg_path, 'w') as f:
        exporter.export_annotated(geometry, annotations, f)
    svg_to_png(svg_path)

    print(f"  Components: {len(geometry.components)}, Annotations: {len(annotations.dimensions) + len(annotations.slope_tags)}")


if __name__ == "__main__":
    main()
