"""Tests for ComponentSpan / multi-component spanning dimensions."""

import io

import pytest

from cross_section.core.domain.annotations import (
    AnnotationCollector,
    ComponentSpan,
    DEFAULT_SPANS,
)
from cross_section.core.domain.section import RoadSection, ControlPoint, SectionGeometry
from cross_section.core.domain.components.lanes import TravelLane, TurnLane
from cross_section.core.domain.components.shoulders import Shoulder
from cross_section.core.domain.components.curbs import Curb
from cross_section.core.domain.components.sidewalks import Sidewalk
from cross_section.core.domain.pavement import AsphaltLayer, CrushedRockLayer
from cross_section.export.svg import SVGExporter


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_AC = AsphaltLayer(thickness=0.05, aggregate_size=12.5, binder_type="PG 64-22",
                   binder_percentage=5.5, density=2400)
_AGG = CrushedRockLayer(thickness=0.15, aggregate_size=37.5, density=2100)


def _two_lane_section() -> SectionGeometry:
    """Simple 2-lane crowned road with shoulders."""
    section = RoadSection(
        name="Two-Lane",
        control_point=ControlPoint(x=0, elevation=100.0),
        left_components=[
            TravelLane(width=3.6, cross_slope=0.02, pavement_layers=[_AC, _AGG]),
            Shoulder(width=2.4, cross_slope=0.04, pavement_layers=[_AC, _AGG]),
        ],
        right_components=[
            TravelLane(width=3.6, cross_slope=0.02, pavement_layers=[_AC, _AGG]),
            Shoulder(width=2.4, cross_slope=0.04, pavement_layers=[_AC, _AGG]),
        ],
    )
    return section.to_geometry()


def _urban_section() -> SectionGeometry:
    """Urban section: lanes + curbs + sidewalks."""
    section = RoadSection(
        name="Urban",
        control_point=ControlPoint(x=0, elevation=100.0),
        left_components=[
            TravelLane(width=3.6, cross_slope=0.02, pavement_layers=[_AC, _AGG]),
            Curb(gutter_width=0.6, gutter_thickness=0.15, curb_height=0.15,
                 curb_width_bottom=0.2, curb_width_top=0.1),
            Sidewalk(width=1.8, cross_slope=0.02, thickness=0.15),
        ],
        right_components=[
            TravelLane(width=3.6, cross_slope=0.02, pavement_layers=[_AC, _AGG]),
            Curb(gutter_width=0.6, gutter_thickness=0.15, curb_height=0.15,
                 curb_width_bottom=0.2, curb_width_top=0.1),
            Sidewalk(width=1.8, cross_slope=0.02, thickness=0.15),
        ],
    )
    return section.to_geometry()


# ---------------------------------------------------------------------------
# ComponentSpan type tests
# ---------------------------------------------------------------------------

class TestComponentSpan:
    def test_defaults(self):
        span = ComponentSpan(types=["TravelLane"])
        assert span.tier == 1
        assert span.sides == "both"
        assert span.label is None

    def test_custom_label_and_tier(self):
        span = ComponentSpan(
            types=["TravelLane", "TurnLane"],
            label="Traveled Way",
            tier=2,
        )
        assert span.label == "Traveled Way"
        assert span.tier == 2

    def test_default_spans_not_empty(self):
        assert len(DEFAULT_SPANS) > 0
        assert any("TravelLane" in s.types for s in DEFAULT_SPANS)


# ---------------------------------------------------------------------------
# Collector with spans
# ---------------------------------------------------------------------------

class TestCollectorSpans:
    def test_default_spans_produce_traveled_way(self):
        """Default collector should produce a 'Traveled Way' spanning dim."""
        geometry = _two_lane_section()
        collector = AnnotationCollector(units="metric")
        annotations = collector.collect(geometry)

        span_dims = [d for d in annotations.dimensions if d.tier > 0]
        assert len(span_dims) >= 1
        assert any("Traveled Way" in d.text for d in span_dims)

    def test_spanning_dim_tier_is_above_per_component(self):
        geometry = _two_lane_section()
        collector = AnnotationCollector(units="metric")
        annotations = collector.collect(geometry)

        tier0 = [d for d in annotations.dimensions if d.tier == 0]
        tier1_plus = [d for d in annotations.dimensions if d.tier > 0]
        assert len(tier0) > 0
        assert len(tier1_plus) > 0

    def test_spanning_dim_x_range_covers_both_sides(self):
        """Traveled Way dim should span from left lane edge to right lane edge."""
        geometry = _two_lane_section()
        collector = AnnotationCollector(units="metric")
        annotations = collector.collect(geometry)

        traveled_way = next(d for d in annotations.dimensions
                            if d.tier > 0 and "Traveled Way" in d.text)
        # With 2x 3.6m lanes either side of centerline: total width = 7.2m
        assert abs(traveled_way.width - 7.2) < 0.01

    def test_empty_spans_list_produces_no_span_dims(self):
        geometry = _two_lane_section()
        collector = AnnotationCollector(units="metric", spans=[])
        annotations = collector.collect(geometry)

        span_dims = [d for d in annotations.dimensions if d.tier > 0]
        assert len(span_dims) == 0

    def test_custom_curb_to_curb_span(self):
        geometry = _urban_section()
        collector = AnnotationCollector(
            units="metric",
            spans=[
                ComponentSpan(
                    types=["TravelLane", "Curb", "Gutter"],
                    label="Curb to Curb",
                    tier=1,
                )
            ],
        )
        annotations = collector.collect(geometry)

        span_dims = [d for d in annotations.dimensions if d.tier > 0]
        assert len(span_dims) == 1
        assert "Curb to Curb" in span_dims[0].text
        # lane (3.6) + curb gutter (0.6+0.2) each side → wider than lane-only
        lane_dims = [d for d in annotations.dimensions
                     if d.tier == 0 and abs(d.width - 3.6) < 0.05]
        assert span_dims[0].width > lane_dims[0].width

    def test_multi_tier_spans(self):
        """Two separate spans at different tiers."""
        geometry = _urban_section()
        collector = AnnotationCollector(
            units="metric",
            spans=[
                ComponentSpan(types=["TravelLane"], label="Lane Width", tier=1),
                ComponentSpan(types=["TravelLane", "Curb"], label="Curb to Curb", tier=2),
            ],
        )
        annotations = collector.collect(geometry)

        tier1 = [d for d in annotations.dimensions if d.tier == 1]
        tier2 = [d for d in annotations.dimensions if d.tier == 2]
        assert len(tier1) == 1
        assert len(tier2) == 1
        # Tier 2 span should be wider
        assert tier2[0].width > tier1[0].width

    def test_sides_filtering_right_only(self):
        """Span with sides='right' should only cover right-side components."""
        geometry = _two_lane_section()
        collector = AnnotationCollector(
            units="metric",
            spans=[
                ComponentSpan(types=["TravelLane"], label="Right Lane", tier=1, sides="right"),
            ],
        )
        annotations = collector.collect(geometry)
        span_dims = [d for d in annotations.dimensions if d.tier > 0]
        assert len(span_dims) == 1
        # Right lane spans from 0 to +3.6
        assert span_dims[0].x_start >= -0.01  # not negative (left side)
        assert abs(span_dims[0].width - 3.6) < 0.05

    def test_span_with_no_label_formats_width_only(self):
        geometry = _two_lane_section()
        collector = AnnotationCollector(
            units="metric",
            spans=[ComponentSpan(types=["TravelLane"], label=None, tier=1)],
        )
        annotations = collector.collect(geometry)
        span_dims = [d for d in annotations.dimensions if d.tier > 0]
        assert len(span_dims) == 1
        assert "m" in span_dims[0].text  # metric width label
        assert "=" not in span_dims[0].text  # no label prefix

    def test_span_text_includes_label_and_width(self):
        geometry = _two_lane_section()
        collector = AnnotationCollector(
            units="metric",
            spans=[ComponentSpan(types=["TravelLane"], label="Traveled Way", tier=1)],
        )
        annotations = collector.collect(geometry)
        dim = next(d for d in annotations.dimensions if d.tier > 0)
        assert "Traveled Way" in dim.text
        assert "7.20m" in dim.text or "7.2m" in dim.text


# ---------------------------------------------------------------------------
# SVG rendering of spanning dimensions
# ---------------------------------------------------------------------------

class TestSpanningDimensionSVG:
    def test_svg_includes_span_text(self):
        geometry = _two_lane_section()
        annotations = AnnotationCollector(units="metric").collect(geometry)

        buf = io.StringIO()
        SVGExporter(scale=80.0).export_annotated(geometry, annotations, buf)
        content = buf.getvalue()

        assert "Traveled Way" in content

    def test_svg_has_two_tier_groups(self):
        """With tier-0 and tier-1 dims both present, SVG should have two <g> groups."""
        geometry = _two_lane_section()
        annotations = AnnotationCollector(units="metric").collect(geometry)

        tier0 = [d for d in annotations.dimensions if d.tier == 0]
        tier1 = [d for d in annotations.dimensions if d.tier == 1]
        assert len(tier0) > 0
        assert len(tier1) > 0

        buf = io.StringIO()
        SVGExporter(scale=80.0).export_annotated(geometry, annotations, buf)
        content = buf.getvalue()
        assert "<svg" in content  # well-formed

    def test_svg_is_valid_with_multi_tier(self):
        import xml.etree.ElementTree as ET
        geometry = _urban_section()
        collector = AnnotationCollector(
            units="metric",
            spans=[
                ComponentSpan(types=["TravelLane"], label="Lane Area", tier=1),
                ComponentSpan(types=["TravelLane", "Curb"], label="Curb to Curb", tier=2),
            ],
        )
        annotations = collector.collect(geometry)

        buf = io.StringIO()
        SVGExporter(scale=100.0).export_annotated(geometry, annotations, buf)
        root = ET.fromstring(buf.getvalue())
        assert root.tag.endswith("svg")
