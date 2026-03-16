"""Integration test for annotated cross-section export."""

import os
import tempfile
from pathlib import Path

import pytest

from cross_section.core.domain import AsphaltLayer, ControlPoint, RoadSection, TravelLane
from cross_section.core.domain.annotations import (
    AnnotationCollection,
    DimensionAnnotation,
    LeaderAnnotation,
)
from cross_section.core.geometry.primitives import Point2D
from cross_section.export import AnnotatedSVGExporter


def _asphalt_layer(thickness: float = 0.15) -> AsphaltLayer:
    return AsphaltLayer(
        thickness=thickness,
        aggregate_size=12.5,
        binder_type="PG 64-22",
        binder_percentage=5.5,
        density=2400,
    )


def test_annotated_crowned_road_export():
    """Test full workflow: create section, add annotations, export to SVG."""
    ft_to_m = 0.3048
    lane_width = 12.0 * ft_to_m
    road = RoadSection(
        name="Test Section",
        control_point=ControlPoint(x=0.0, elevation=100.0),
        right_components=[
            TravelLane(width=lane_width, pavement_layers=[_asphalt_layer()]),
        ],
    )
    section = road.to_geometry()

    # Create annotations
    collection = AnnotationCollection()

    # Add dimension
    collection.add(DimensionAnnotation(
        start=Point2D(0, 100.0),
        end=Point2D(lane_width, 100.0),
        offset=0.5,
        dimension_text="12'-0\"",
        layer="dimensions"
    ))

    # Add leader
    collection.add(LeaderAnnotation(
        points=[
            Point2D(lane_width / 2, 99.85),
            Point2D(lane_width / 2 + 1.0, 99.5),
        ],
        text="Test",
        arrow_at_start=True,
        layer="leaders"
    ))

    # Export to SVG
    with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
        temp_path = f.name
        exporter = AnnotatedSVGExporter(scale=100.0, vertical_exaggeration=10.0)
        exporter.export_with_annotations(section, collection, f)

    try:
        # Verify file was created
        assert os.path.exists(temp_path)

        # Read and verify content
        with open(temp_path, 'r') as f:
            content = f.read()

        # Check SVG structure
        assert '<svg' in content
        assert 'xmlns="http://www.w3.org/2000/svg"' in content
        assert '</svg>' in content

        # Check annotations are present
        assert 'dimension-' in content
        assert 'leader-' in content
        assert '12\'-0"' in content
        assert 'Test' in content

        # Check geometry is present
        assert '<polygon' in content

    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_example_script_generates_valid_svg():
    """Test that the example script generates a valid SVG file."""
    # Import and run the example
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "generators"))

    try:
        from crowned_road import build_scenario

        # Create section and annotations
        section, annotations = build_scenario()

        # Verify section structure
        assert len(section.components) == 6
        assert section.metadata["name"] == "Crowned Road with Ditches"

        # Verify annotations
        assert annotations.count() > 0

        # Export to temp file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
            temp_path = f.name
            exporter = AnnotatedSVGExporter(
                scale=100.0,
                vertical_exaggeration=10.0,
                units="imperial"
            )
            exporter.export_with_annotations(section, annotations, f)

        try:
            # Verify file content
            with open(temp_path, 'r') as f:
                content = f.read()

            # Check that automated annotations render
            assert 'dimension-' in content
            assert 'leader-' in content

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    finally:
        sys.path.pop(0)


def test_annotation_text_size_calculation():
    """Verify text size matches requested point size at intended scale."""
    collection = AnnotationCollection()
    collection.add(LeaderAnnotation(
        points=[Point2D(0, 0), Point2D(1, 1)],
        text="Test",
        layer="leaders"
    ))

    road = RoadSection(
        name="Text Size Test",
        control_point=ControlPoint(x=0.0, elevation=0.0),
        right_components=[
            TravelLane(width=1.0, pavement_layers=[_asphalt_layer()]),
        ],
    )
    section = road.to_geometry()

    # Export with text size
    with tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False) as f:
        temp_path = f.name
        exporter = AnnotatedSVGExporter(scale=100.0)
        exporter.export_with_annotations(section, collection, f)

    try:
        with open(temp_path, 'r') as f:
            content = f.read()

        # Default text size should be around 15 pixels (0.15m * 100 px/m)
        # Our custom size would be 13 pixels (0.13m * 100 px/m)
        assert 'font-size="15.0"' in content  # Default leader text size

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
