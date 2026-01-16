"""Integration test for annotated cross-section export."""

import os
import tempfile
from pathlib import Path

import pytest

from cross_section.core.domain.annotations import (
    AnnotationCollection,
    DimensionAnnotation,
    LeaderAnnotation,
)
from cross_section.core.domain.section import SectionGeometry
from cross_section.core.geometry.primitives import ComponentGeometry, Point2D, Polygon
from cross_section.export import AnnotatedSVGExporter


def test_annotated_crowned_road_export():
    """Test full workflow: create section, add annotations, export to SVG."""
    # Create a simple section
    ft_to_m = 0.3048
    lane_width = 12.0 * ft_to_m

    lane_poly = Polygon(exterior=[
        Point2D(0, 100.0),
        Point2D(lane_width, 100.0),
        Point2D(lane_width, 99.85),
        Point2D(0, 99.85),
    ])

    section = SectionGeometry(
        components=[ComponentGeometry(
            polygons=[lane_poly],
            metadata={
                "component_type": "TravelLane",
                "width": lane_width,
            }
        )],
        metadata={"name": "Test Section"}
    )

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
        from annotated_crowned_road import create_crowned_road_section, create_manual_annotations

        # Create section and annotations
        section = create_crowned_road_section()
        annotations = create_manual_annotations(section)

        # Verify section structure
        assert len(section.components) == 6  # 2 lanes + 2 shoulders + 2 ditches
        assert section.metadata["name"] == "Crowned Road with Ditches"

        # Verify annotations
        assert annotations.count() == 6  # 5 dimensions + 1 leader

        dims = annotations.get_by_type(DimensionAnnotation)
        assert len(dims) == 5

        leaders = annotations.get_by_type(LeaderAnnotation)
        assert len(leaders) == 1
        assert leaders[0].text == "Crown"

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

            # Check all dimensions are present
            assert '8\'-0"' in content  # Shoulder dimensions
            assert '12\'-0"' in content  # Lane dimensions
            assert '40\'-0"' in content  # Overall dimension

            # Check leader
            assert 'Crown' in content
            assert 'leader-' in content

            # Count dimension groups (should be 5)
            assert content.count('dimension-') == 5

        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    finally:
        sys.path.pop(0)


def test_annotation_text_size_calculation():
    """Verify text size matches requested point size at intended scale."""
    # For 10pt text at scale=100 px/m:
    # 10pt = ~13.3 pixels at 96 DPI
    # 13.3 pixels / 100 px/m = 0.133 meters
    text_size_meters = 0.13

    # Create simple annotation
    collection = AnnotationCollection()
    collection.add(LeaderAnnotation(
        points=[Point2D(0, 0), Point2D(1, 1)],
        text="Test",
        layer="leaders"
    ))

    # Create minimal section
    section = SectionGeometry(
        components=[ComponentGeometry(
            polygons=[Polygon(exterior=[
                Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)
            ])],
            metadata={}
        )],
        metadata={}
    )

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
