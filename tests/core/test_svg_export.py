"""Tests for SVG exporter."""

import io
import re

import pytest

from cross_section.core.domain.annotations import AnnotationCollector
from cross_section.core.domain.section import SectionGeometry
from cross_section.core.geometry.primitives import ComponentGeometry, Point2D, Polygon
from cross_section.export.svg import SVGExporter, SimpleSVGExporter


def _make_section(name: str = "Test Section") -> SectionGeometry:
    polygon = Polygon(
        exterior=[
            Point2D(0, 99.5),
            Point2D(3.6, 99.5),
            Point2D(3.6, 100.0),
            Point2D(0, 100.0),
        ]
    )
    component = ComponentGeometry(
        polygons=[polygon],
        metadata={
            "component_type": "TravelLane",
            "width": 3.6,
            "cross_slope": 0.02,
            "assembly_direction": "right",
            "layers": [{"type": "AsphaltLayer", "thickness": 0.05}],
        },
    )
    return SectionGeometry(components=[component], metadata={"name": name})


def _get_svg_width(svg: str) -> float:
    m = re.search(r'<svg[^>]+width="([\d.]+)"', svg)
    return float(m.group(1)) if m else 0.0


def test_simple_export_produces_valid_svg():
    """Basic geometry export should produce valid SVG markup."""
    section = _make_section()
    exporter = SVGExporter(scale=100.0)
    buf = io.StringIO()
    exporter.export(section, buf)
    content = buf.getvalue()

    assert "<svg" in content
    assert 'xmlns="http://www.w3.org/2000/svg"' in content
    assert "</svg>" in content
    assert "<polygon" in content


def test_empty_section_produces_placeholder_svg():
    section = SectionGeometry(components=[], metadata={"name": "Empty"})
    exporter = SVGExporter(scale=100.0)
    buf = io.StringIO()
    exporter.export(section, buf)
    assert "<svg" in buf.getvalue()


def test_svg_contains_section_name():
    section = _make_section(name="Crowned Highway")
    exporter = SVGExporter(scale=100.0)
    buf = io.StringIO()
    exporter.export(section, buf)
    assert "Crowned Highway" in buf.getvalue()


def test_annotated_export_includes_dimension_line():
    section = _make_section()
    collector = AnnotationCollector(units="metric", include_widths=True,
                                    include_slopes=False, include_layer_labels=False)
    annotations = collector.collect(section)
    per_component_dims = [d for d in annotations.dimensions if d.tier == 0]
    assert len(per_component_dims) == 1

    exporter = SVGExporter(scale=100.0)
    buf = io.StringIO()
    exporter.export_annotated(section, annotations, buf)
    content = buf.getvalue()

    assert "<svg" in content
    assert "<line" in content  # dimension / extension lines
    # Dimension text (metric)
    assert "3.60m" in content or "3.6m" in content


def test_annotated_export_includes_slope_tag():
    section = _make_section()
    collector = AnnotationCollector(units="metric", include_widths=False,
                                    include_slopes=True, include_layer_labels=False)
    annotations = collector.collect(section)
    assert len(annotations.slope_tags) == 1

    exporter = SVGExporter(scale=100.0)
    buf = io.StringIO()
    exporter.export_annotated(section, annotations, buf)
    assert "2.0%" in buf.getvalue()


def test_scale_affects_svg_dimensions():
    section = _make_section()

    buf1 = io.StringIO()
    SVGExporter(scale=50.0).export(section, buf1)

    buf2 = io.StringIO()
    SVGExporter(scale=200.0).export(section, buf2)

    assert _get_svg_width(buf2.getvalue()) > _get_svg_width(buf1.getvalue())


def test_simple_svg_exporter_alias():
    section = _make_section()
    exporter = SimpleSVGExporter(scale=100.0)
    buf = io.StringIO()
    exporter.export(section, buf)
    assert "<svg" in buf.getvalue()


def test_svg_contains_asphalt_color():
    section = _make_section()
    exporter = SVGExporter(scale=100.0)
    buf = io.StringIO()
    exporter.export(section, buf)
    assert "#2C3E50" in buf.getvalue()
