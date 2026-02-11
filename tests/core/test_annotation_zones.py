"""Tests for the zone-based annotation placement system."""

import pytest

from cross_section.core.domain.annotations import (
    AnnotationZone,
    ZONE_BASE_OFFSETS,
    SYMBOL_CLEARANCE_BUFFER,
    DimensionAnnotation,
    LeaderAnnotation,
    SymbolAnnotation,
    TextAnnotation,
    get_zone_for_annotation,
    get_zone_y_bounds,
    compute_dimension_offset_for_span,
)
from cross_section.core.geometry.primitives import Point2D


class TestAnnotationZone:
    """Tests for AnnotationZone enum."""

    def test_zone_ordering(self):
        """Test that zones are ordered correctly (lower = closer to geometry)."""
        assert AnnotationZone.GEOMETRY < AnnotationZone.LABEL_TEXT
        assert AnnotationZone.LABEL_TEXT < AnnotationZone.PRIMARY_SYMBOL
        assert AnnotationZone.PRIMARY_SYMBOL < AnnotationZone.SECONDARY_SYMBOL
        assert AnnotationZone.SECONDARY_SYMBOL < AnnotationZone.DIMENSION

    def test_zone_values(self):
        """Test zone integer values."""
        assert AnnotationZone.GEOMETRY == 0
        assert AnnotationZone.LABEL_TEXT == 1
        assert AnnotationZone.PRIMARY_SYMBOL == 2
        assert AnnotationZone.SECONDARY_SYMBOL == 3
        assert AnnotationZone.DIMENSION == 4


class TestZoneBaseOffsets:
    """Tests for zone offset constants."""

    def test_all_zones_have_offsets(self):
        """Test that non-geometry zones have defined offsets."""
        for zone in [
            AnnotationZone.DIMENSION,
            AnnotationZone.PRIMARY_SYMBOL,
            AnnotationZone.SECONDARY_SYMBOL,
            AnnotationZone.LABEL_TEXT,
        ]:
            assert zone in ZONE_BASE_OFFSETS
            assert ZONE_BASE_OFFSETS[zone] > 0

    def test_offset_ordering(self):
        """Test that zone offsets follow the expected ordering.

        Secondary symbols (drainage arrows) sit closest to the road surface,
        then primary symbols (traffic arrows) above them, then labels just
        below the dimension line (furthest from geometry).
        """
        assert ZONE_BASE_OFFSETS[AnnotationZone.SECONDARY_SYMBOL] < ZONE_BASE_OFFSETS[AnnotationZone.PRIMARY_SYMBOL]
        assert ZONE_BASE_OFFSETS[AnnotationZone.PRIMARY_SYMBOL] < ZONE_BASE_OFFSETS[AnnotationZone.LABEL_TEXT]
        assert ZONE_BASE_OFFSETS[AnnotationZone.LABEL_TEXT] < ZONE_BASE_OFFSETS[AnnotationZone.DIMENSION]

    def test_symbol_clearance_buffer_positive(self):
        """Test that symbol clearance buffer is positive."""
        assert SYMBOL_CLEARANCE_BUFFER > 0


class TestGetZoneForAnnotation:
    """Tests for zone assignment logic."""

    def test_dimension_annotation_zone(self):
        """Test that dimension annotations go to DIMENSION zone."""
        dim = DimensionAnnotation(
            start=Point2D(0, 5),
            end=Point2D(10, 5),
            offset=0.5,
        )
        assert get_zone_for_annotation(dim) == AnnotationZone.DIMENSION

    def test_traffic_arrow_zone(self):
        """Test that traffic arrows go to PRIMARY_SYMBOL zone."""
        symbol = SymbolAnnotation(
            position=Point2D(5, 10),
            symbol_type="traffic_arrow",
        )
        assert get_zone_for_annotation(symbol) == AnnotationZone.PRIMARY_SYMBOL

    def test_centerpoint_zone(self):
        """Test that centerpoint marks go to PRIMARY_SYMBOL zone."""
        symbol = SymbolAnnotation(
            position=Point2D(0, 10),
            symbol_type="centerpoint",
        )
        assert get_zone_for_annotation(symbol) == AnnotationZone.PRIMARY_SYMBOL

    def test_drainage_arrow_zone(self):
        """Test that drainage arrows go to SECONDARY_SYMBOL zone."""
        symbol = SymbolAnnotation(
            position=Point2D(5, 10),
            symbol_type="drainage_arrow",
        )
        assert get_zone_for_annotation(symbol) == AnnotationZone.SECONDARY_SYMBOL

    def test_leader_annotation_zone(self):
        """Test that leader annotations go to LABEL_TEXT zone."""
        leader = LeaderAnnotation(
            points=[Point2D(0, 0), Point2D(5, 5)],
            text="Test Leader",
        )
        assert get_zone_for_annotation(leader) == AnnotationZone.LABEL_TEXT

    def test_text_label_zone(self):
        """Test that text labels go to LABEL_TEXT zone."""
        text = TextAnnotation(
            position=Point2D(5, 10),
            text="Test Label",
            layer="labels",
        )
        assert get_zone_for_annotation(text) == AnnotationZone.LABEL_TEXT

    def test_material_text_zone(self):
        """Test that material labels go to LABEL_TEXT zone."""
        text = TextAnnotation(
            position=Point2D(5, 10),
            text="Asphalt",
            layer="materials",
        )
        assert get_zone_for_annotation(text) == AnnotationZone.LABEL_TEXT

    def test_slope_indicator_text_zone(self):
        """Test that slope text goes to SECONDARY_SYMBOL zone."""
        text = TextAnnotation(
            position=Point2D(5, 10),
            text="2%",
            layer="slope_indicators",
        )
        assert get_zone_for_annotation(text) == AnnotationZone.SECONDARY_SYMBOL


class TestGetZoneYBounds:
    """Tests for zone Y coordinate bounds."""

    def test_dimension_zone_bounds(self):
        """Test dimension zone Y bounds."""
        component_top = 10.0
        min_y, max_y = get_zone_y_bounds(AnnotationZone.DIMENSION, component_top)

        assert min_y > component_top
        assert max_y > min_y

    def test_dimension_zone_with_symbols(self):
        """Test dimension zone adjusts for symbol height."""
        component_top = 10.0
        symbol_height = 1.8  # Taller than base offset (1.70) to force adjustment

        min_y_no_sym, _ = get_zone_y_bounds(AnnotationZone.DIMENSION, component_top, 0.0)
        min_y_with_sym, _ = get_zone_y_bounds(AnnotationZone.DIMENSION, component_top, symbol_height)

        # With symbols, dimension zone should be higher
        assert min_y_with_sym > min_y_no_sym

    def test_primary_symbol_zone_bounds(self):
        """Test primary symbol zone Y bounds."""
        component_top = 10.0
        min_y, max_y = get_zone_y_bounds(AnnotationZone.PRIMARY_SYMBOL, component_top)

        assert min_y > component_top
        assert max_y > min_y

    def test_secondary_symbol_zone_bounds(self):
        """Test primary symbol zone (traffic arrows) is above secondary (drainage)."""
        component_top = 10.0
        primary_min, _ = get_zone_y_bounds(AnnotationZone.PRIMARY_SYMBOL, component_top)
        secondary_min, _ = get_zone_y_bounds(AnnotationZone.SECONDARY_SYMBOL, component_top)

        # Primary symbols (traffic arrows) sit above secondary (drainage arrows)
        assert primary_min > secondary_min

    def test_dimension_zone_expands_upward(self):
        """Test that dimension zone can expand upward infinitely."""
        component_top = 10.0
        _, max_y = get_zone_y_bounds(AnnotationZone.DIMENSION, component_top)

        assert max_y == float("inf")


class TestComputeDimensionOffsetForSpan:
    """Tests for per-span dimension offset computation."""

    def test_no_symbols_returns_base_offset(self):
        """Test that empty span returns base offset."""
        component_top = 10.0
        base_offset = 0.5

        offset = compute_dimension_offset_for_span(component_top, [], base_offset)

        assert offset == base_offset

    def test_single_symbol_clears_it(self):
        """Test offset increases to clear single symbol."""
        component_top = 10.0
        base_offset = 0.5

        symbol = SymbolAnnotation(
            position=Point2D(5, component_top + 0.35),  # Symbol above surface
            symbol_type="traffic_arrow",
        )

        offset = compute_dimension_offset_for_span(component_top, [symbol], base_offset)

        # Offset should clear the symbol plus buffer
        symbol_top = symbol.bounds().max_y
        expected_min = symbol_top - component_top + SYMBOL_CLEARANCE_BUFFER
        assert offset >= expected_min

    def test_multiple_symbols_clears_highest(self):
        """Test offset clears highest of multiple symbols."""
        component_top = 10.0
        base_offset = 0.5

        low_symbol = SymbolAnnotation(
            position=Point2D(5, component_top + 0.30),
            symbol_type="traffic_arrow",
        )
        high_symbol = SymbolAnnotation(
            position=Point2D(5, component_top + 0.55),
            symbol_type="drainage_arrow",
        )

        offset = compute_dimension_offset_for_span(
            component_top, [low_symbol, high_symbol], base_offset
        )

        # Offset should clear the highest symbol
        high_symbol_top = high_symbol.bounds().max_y
        expected_min = high_symbol_top - component_top + SYMBOL_CLEARANCE_BUFFER
        assert offset >= expected_min

    def test_low_symbol_keeps_base_offset(self):
        """Test base offset is used if symbols are lower."""
        component_top = 10.0
        base_offset = 0.5

        # Symbol positioned lower than base offset
        symbol = SymbolAnnotation(
            position=Point2D(5, component_top + 0.1),
            symbol_type="traffic_arrow",
            scale=0.5,  # Small scale
        )

        offset = compute_dimension_offset_for_span(component_top, [symbol], base_offset)

        # Should keep base offset if symbol is lower
        assert offset >= base_offset


class TestZoneIntegration:
    """Integration tests for zone system."""

    def test_stacked_symbols_have_different_zones(self):
        """Test that traffic and slope arrows are in different zones."""
        traffic = SymbolAnnotation(
            position=Point2D(5, 10.35),
            symbol_type="traffic_arrow",
        )
        slope = SymbolAnnotation(
            position=Point2D(5, 10.55),
            symbol_type="drainage_arrow",
        )

        traffic_zone = get_zone_for_annotation(traffic)
        slope_zone = get_zone_for_annotation(slope)

        assert traffic_zone != slope_zone
        assert traffic_zone == AnnotationZone.PRIMARY_SYMBOL
        assert slope_zone == AnnotationZone.SECONDARY_SYMBOL

    def test_dimension_and_symbol_zones_separate(self):
        """Test dimensions and symbols are in separate zones."""
        dim = DimensionAnnotation(
            start=Point2D(0, 10),
            end=Point2D(10, 10),
            offset=0.5,
        )
        symbol = SymbolAnnotation(
            position=Point2D(5, 10.35),
            symbol_type="traffic_arrow",
        )

        dim_zone = get_zone_for_annotation(dim)
        symbol_zone = get_zone_for_annotation(symbol)

        assert dim_zone != symbol_zone
