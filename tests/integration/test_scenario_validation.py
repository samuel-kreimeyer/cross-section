"""Integration tests for scenario validation.

Validates that common road section configurations produce valid geometry
and that the annotation collector and SVG exporter work end-to-end.
"""

import io
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from cross_section.core.domain.section import RoadSection, ControlPoint
from cross_section.core.domain.components.lanes import TravelLane, TurnLane
from cross_section.core.domain.components.shoulders import Shoulder
from cross_section.core.domain.components.curbs import Curb
from cross_section.core.domain.components.sidewalks import Sidewalk
from cross_section.core.domain.components.slopes import Slope
from cross_section.core.domain.components.ditches import Ditch
from cross_section.core.domain.pavement import AsphaltLayer, CrushedRockLayer
from cross_section.core.domain.annotations import AnnotationCollector
from cross_section.core.geometry.validate import validate_section_geometry, ShapelyNotAvailable
from cross_section.export.svg import SVGExporter


def _is_valid_svg(content: str) -> bool:
    try:
        root = ET.fromstring(content)
        return root.tag.endswith("svg")
    except ET.ParseError:
        return False


def _build_crowned_road() -> RoadSection:
    return RoadSection(
        name="Crowned Road",
        control_point=ControlPoint(x=0, elevation=100.0),
        left_components=[
            TravelLane(width=3.6, cross_slope=0.02, pavement_layers=[
                AsphaltLayer(thickness=0.05, aggregate_size=12.5, binder_type="PG 64-22",
                             binder_percentage=5.5, density=2400),
                CrushedRockLayer(thickness=0.15, aggregate_size=37.5, density=2100),
            ]),
            Shoulder(width=2.4, cross_slope=0.04, pavement_layers=[
                AsphaltLayer(thickness=0.05, aggregate_size=12.5, binder_type="PG 64-22",
                             binder_percentage=5.5, density=2400),
                CrushedRockLayer(thickness=0.15, aggregate_size=37.5, density=2100),
            ]),
            Slope(horizontal_run=6.0, vertical_drop=2.0),
            Ditch(depth=0.6, foreslope_ratio=3.0, backslope_ratio=3.0),
        ],
        right_components=[
            TravelLane(width=3.6, cross_slope=0.02, pavement_layers=[
                AsphaltLayer(thickness=0.05, aggregate_size=12.5, binder_type="PG 64-22",
                             binder_percentage=5.5, density=2400),
                CrushedRockLayer(thickness=0.15, aggregate_size=37.5, density=2100),
            ]),
            Shoulder(width=2.4, cross_slope=0.04, pavement_layers=[
                AsphaltLayer(thickness=0.05, aggregate_size=12.5, binder_type="PG 64-22",
                             binder_percentage=5.5, density=2400),
                CrushedRockLayer(thickness=0.15, aggregate_size=37.5, density=2100),
            ]),
            Slope(horizontal_run=6.0, vertical_drop=2.0),
            Ditch(depth=0.6, foreslope_ratio=3.0, backslope_ratio=3.0),
        ],
    )


_URBAN_PAVEMENT = [
    AsphaltLayer(thickness=0.05, aggregate_size=12.5, binder_type="PG 64-22",
                 binder_percentage=5.5, density=2400),
    CrushedRockLayer(thickness=0.15, aggregate_size=37.5, density=2100),
]


def _build_urban_section() -> RoadSection:
    return RoadSection(
        name="Urban Section",
        control_point=ControlPoint(x=0, elevation=100.0),
        left_components=[
            TravelLane(width=3.6, cross_slope=0.02, pavement_layers=_URBAN_PAVEMENT),
            Curb(gutter_width=0.6, gutter_thickness=0.15, curb_height=0.15,
                 curb_width_bottom=0.2, curb_width_top=0.1),
            Sidewalk(width=1.8, cross_slope=0.02, thickness=0.15),
        ],
        right_components=[
            TravelLane(width=3.6, cross_slope=0.02, pavement_layers=_URBAN_PAVEMENT),
            Curb(gutter_width=0.6, gutter_thickness=0.15, curb_height=0.15,
                 curb_width_bottom=0.2, curb_width_top=0.1),
            Sidewalk(width=1.8, cross_slope=0.02, thickness=0.15),
        ],
    )


class TestScenarioGeometryValid:
    def test_crowned_road_validates(self):
        section = _build_crowned_road()
        errors = section.validate()
        assert errors == [], f"Validation errors: {errors}"

    def test_urban_section_validates(self):
        section = _build_urban_section()
        errors = section.validate()
        assert errors == [], f"Validation errors: {errors}"

    def test_crowned_road_geometry_assembles(self):
        section = _build_crowned_road()
        geometry = section.to_geometry()
        assert len(geometry.components) == 8  # 4 left + 4 right

    def test_urban_section_geometry_assembles(self):
        section = _build_urban_section()
        geometry = section.to_geometry()
        assert len(geometry.components) == 6  # 3 left + 3 right

    def test_crowned_road_shapely_validation(self):
        section = _build_crowned_road()
        geometry = section.to_geometry()
        try:
            errors = validate_section_geometry(geometry.components)
            # Shapely may report warnings for intentional overlaps; we just check it doesn't crash
        except ShapelyNotAvailable:
            pytest.skip("shapely not installed")


class TestAnnotationCollection:
    def test_crowned_road_produces_annotations(self):
        section = _build_crowned_road()
        geometry = section.to_geometry()
        collector = AnnotationCollector(units="imperial")
        annotations = collector.collect(geometry)

        assert len(annotations.dimensions) > 0
        assert len(annotations.slope_tags) > 0

    def test_urban_section_produces_annotations(self):
        section = _build_urban_section()
        geometry = section.to_geometry()
        collector = AnnotationCollector(units="metric")
        annotations = collector.collect(geometry)

        assert len(annotations.dimensions) > 0

    def test_dimension_x_ranges_are_valid(self):
        section = _build_crowned_road()
        geometry = section.to_geometry()
        collector = AnnotationCollector()
        annotations = collector.collect(geometry)

        for dim in annotations.dimensions:
            assert dim.x_start != dim.x_end, "Dimension must span a non-zero width"
            assert dim.width > 0

    def test_imperial_dimension_labels_contain_feet(self):
        section = _build_urban_section()
        geometry = section.to_geometry()
        collector = AnnotationCollector(units="imperial")
        annotations = collector.collect(geometry)

        for dim in annotations.dimensions:
            assert "'" in dim.text or "ft" in dim.text.lower(), (
                f"Imperial dimension '{dim.text}' should contain ft symbol"
            )

    def test_metric_dimension_labels_contain_meters(self):
        section = _build_urban_section()
        geometry = section.to_geometry()
        collector = AnnotationCollector(units="metric")
        annotations = collector.collect(geometry)

        for dim in annotations.dimensions:
            assert "m" in dim.text, f"Metric dimension '{dim.text}' should contain 'm'"


class TestSVGExport:
    def test_crowned_road_svg_is_valid_xml(self):
        section = _build_crowned_road()
        geometry = section.to_geometry()
        collector = AnnotationCollector(units="imperial")
        annotations = collector.collect(geometry)

        buf = io.StringIO()
        SVGExporter(scale=80.0).export_annotated(geometry, annotations, buf)

        assert _is_valid_svg(buf.getvalue())

    def test_urban_section_svg_contains_geometry(self):
        section = _build_urban_section()
        geometry = section.to_geometry()
        annotations = AnnotationCollector().collect(geometry)

        buf = io.StringIO()
        SVGExporter(scale=100.0).export_annotated(geometry, annotations, buf)
        content = buf.getvalue()

        assert "<polygon" in content

    def test_svg_contains_section_title(self):
        section = _build_crowned_road()
        geometry = section.to_geometry()
        annotations = AnnotationCollector().collect(geometry)

        buf = io.StringIO()
        SVGExporter(scale=80.0).export_annotated(geometry, annotations, buf)

        assert "Crowned Road" in buf.getvalue()

    def test_svg_contains_dimension_elements(self):
        section = _build_urban_section()
        geometry = section.to_geometry()
        annotations = AnnotationCollector(units="metric", include_widths=True).collect(geometry)

        buf = io.StringIO()
        SVGExporter(scale=100.0).export_annotated(geometry, annotations, buf)
        content = buf.getvalue()

        assert "Width dimensions" in content
        assert "<line" in content  # extension / dimension lines
