"""Tests for SVG exporter layout margins."""

import pytest

from cross_section.core.domain.annotations import AnnotationCollection
from cross_section.core.domain.section import SectionGeometry
from cross_section.core.geometry.primitives import ComponentGeometry, Point2D, Polygon
from cross_section.export import AnnotatedSVGExporter
from cross_section.export.svg import SimpleSVGExporter


def _create_section(name: str = "Test Section") -> SectionGeometry:
    polygon = Polygon(exterior=[
        Point2D(0, 99.5),
        Point2D(3.6, 99.5),
        Point2D(3.6, 100.0),
        Point2D(0, 100.0),
    ])
    component = ComponentGeometry(
        polygons=[polygon],
        metadata={
            "component_type": "TravelLane",
            "width": 3.6,
            "layers": [{"type": "AsphaltLayer", "thickness": 0.5}],
        },
    )
    return SectionGeometry(components=[component], metadata={"name": name})


def test_simple_svg_ui_margins_reserve_space():
    geometry = _create_section(name="Long Section Name For Legend Width")
    exporter = SimpleSVGExporter(scale=100.0)
    min_x, min_y, max_x, max_y = geometry.bounds()

    (
        view_min_x,
        _view_min_y,
        _view_max_x,
        _view_max_y,
        scale_length_m,
        _scale_label,
    ) = exporter._compute_view_bounds(min_x, min_y, max_x, max_y, geometry, keyed_notes_count=0)

    left_px, _right_px, _top_px, _bottom_px = exporter._ui_margins_px(
        geometry,
        scale_length_m,
        keyed_notes_count=0,
    )

    left_margin_m = min_x - view_min_x - exporter.content_margin_m
    assert left_margin_m * exporter.scale == pytest.approx(left_px)


def test_annotated_svg_margins_include_keyed_notes():
    geometry = _create_section()
    annotations = AnnotationCollection()
    annotations.add_keyed_note("Test Note")
    exporter = AnnotatedSVGExporter(scale=100.0)

    min_x, min_y, max_x, max_y = geometry.bounds()

    (
        _view_min_x,
        _view_min_y,
        view_max_x,
        _view_max_y,
        scale_length_m,
        _scale_label,
    ) = exporter._compute_view_bounds(
        min_x,
        min_y,
        max_x,
        max_y,
        geometry,
        keyed_notes_count=len(annotations.keyed_notes),
    )

    left_px, right_px, top_px, bottom_px = exporter._ui_margins_px(
        geometry,
        scale_length_m,
        keyed_notes_count=len(annotations.keyed_notes),
    )

    right_margin_m = view_max_x - max_x - exporter.content_margin_m
    assert right_margin_m * exporter.scale == pytest.approx(right_px)
    assert right_px >= exporter.KEYED_NOTES_WIDTH_PX
    assert bottom_px >= exporter.KEYED_NOTES_ROW_HEIGHT_PX + exporter.KEYED_NOTES_PADDING_PX
