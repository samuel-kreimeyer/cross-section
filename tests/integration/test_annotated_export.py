"""Integration tests for annotated cross-section export."""

import io
import tempfile
import os

import pytest

from cross_section.core.domain.annotations import AnnotationCollector, SectionAnnotations
from cross_section.core.domain.section import RoadSection, SectionGeometry, ControlPoint
from cross_section.core.domain.components.lanes import TravelLane
from cross_section.core.domain.components.shoulders import Shoulder
from cross_section.core.domain.pavement import AsphaltLayer, CrushedRockLayer
from cross_section.core.geometry.primitives import ComponentGeometry, Point2D, Polygon
from cross_section.export.svg import SVGExporter


def _simple_section() -> SectionGeometry:
    polygon = Polygon(exterior=[
        Point2D(0, 100.0), Point2D(3.6, 100.0),
        Point2D(3.6, 99.93), Point2D(0, 99.93),
    ])
    return SectionGeometry(
        components=[ComponentGeometry(
            polygons=[polygon],
            metadata={
                "component_type": "TravelLane",
                "width": 3.6,
                "cross_slope": 0.02,
                "assembly_direction": "right",
                "layers": [{"type": "AsphaltLayer", "thickness": 0.05}],
            },
        )],
        metadata={"name": "Test Section"},
    )


def test_export_annotated_produces_svg_file():
    """Full workflow: section → collect annotations → export annotated SVG."""
    section = _simple_section()
    collector = AnnotationCollector(units="metric")
    annotations = collector.collect(section)

    exporter = SVGExporter(scale=100.0)
    buf = io.StringIO()
    exporter.export_annotated(section, annotations, buf)
    content = buf.getvalue()

    assert "<svg" in content
    assert "</svg>" in content
    assert "<polygon" in content


def test_collector_derives_width_dimensions():
    section = _simple_section()
    collector = AnnotationCollector(units="metric", include_widths=True,
                                    include_slopes=False, include_layer_labels=False)
    annotations = collector.collect(section)

    assert len(annotations.dimensions) == 1
    dim = annotations.dimensions[0]
    assert abs(dim.width - 3.6) < 0.01
    assert "3.60m" in dim.text or "3.6m" in dim.text


def test_collector_derives_slope_tags():
    section = _simple_section()
    collector = AnnotationCollector(units="metric", include_widths=False,
                                    include_slopes=True, include_layer_labels=False)
    annotations = collector.collect(section)

    assert len(annotations.slope_tags) == 1
    assert "2.0%" in annotations.slope_tags[0].text


def test_collector_derives_layer_labels():
    section = _simple_section()
    collector = AnnotationCollector(include_widths=False, include_slopes=False,
                                    include_layer_labels=True)
    annotations = collector.collect(section)

    assert len(annotations.labels) == 1
    assert "AC" in annotations.labels[0].text or "Asphalt" in annotations.labels[0].text


def test_full_road_section_annotated_export():
    """End-to-end: build RoadSection, generate geometry, collect annotations, export SVG."""
    section = RoadSection(
        name="Urban Arterial",
        control_point=ControlPoint(x=0, elevation=100.0),
        left_components=[
            TravelLane(width=3.6, cross_slope=0.02, pavement_layers=[
                AsphaltLayer(thickness=0.05, aggregate_size=12.5, binder_type="PG 64-22",
                             binder_percentage=5.5, density=2400),
                CrushedRockLayer(thickness=0.15, aggregate_size=37.5, density=2100),
            ]),
            Shoulder(width=2.4, cross_slope=0.04),
        ],
        right_components=[
            TravelLane(width=3.6, cross_slope=0.02, pavement_layers=[
                AsphaltLayer(thickness=0.05, aggregate_size=12.5, binder_type="PG 64-22",
                             binder_percentage=5.5, density=2400),
                CrushedRockLayer(thickness=0.15, aggregate_size=37.5, density=2100),
            ]),
            Shoulder(width=2.4, cross_slope=0.04),
        ],
    )

    geometry = section.to_geometry()
    assert len(geometry.components) == 4

    collector = AnnotationCollector(units="metric")
    annotations = collector.collect(geometry)

    # Should have dimensions for each component that has a width
    assert len(annotations.dimensions) >= 4  # 2 lanes + 2 shoulders

    exporter = SVGExporter(scale=80.0)
    buf = io.StringIO()
    exporter.export_annotated(geometry, annotations, buf)
    content = buf.getvalue()

    assert "<svg" in content
    assert "Urban Arterial" in content
    assert "<polygon" in content
    # Dimensions annotation group present
    assert "Width dimensions" in content


def test_annotated_export_to_file():
    """Annotated export should write a valid SVG file to disk."""
    section = _simple_section()
    annotations = AnnotationCollector(units="imperial").collect(section)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".svg", delete=False) as f:
        path = f.name
        SVGExporter(scale=100.0).export_annotated(section, annotations, f)

    try:
        assert os.path.exists(path)
        content = open(path).read()
        assert "<svg" in content
        assert "</svg>" in content
    finally:
        os.remove(path)
