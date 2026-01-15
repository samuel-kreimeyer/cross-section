"""Tests for symbol library."""

import pytest

from cross_section.core.domain.annotations.symbols.library import SymbolLibrary


class TestSymbolLibrary:
    """Tests for SymbolLibrary class."""

    def test_library_has_aashto_symbols(self):
        """Test that AASHTO symbols are registered."""
        aashto_symbols = SymbolLibrary.list_symbols(library="aashto")

        # Should have traffic, drainage, and standard symbols
        assert len(aashto_symbols) > 0
        assert "traffic_arrow" in aashto_symbols
        assert "drainage_arrow" in aashto_symbols
        assert "centerpoint" in aashto_symbols

    def test_get_traffic_arrow(self):
        """Test retrieving traffic arrow symbol."""
        symbol = SymbolLibrary.get("traffic_arrow")

        assert symbol is not None
        assert "svg_path" in symbol
        assert "width" in symbol
        assert "height" in symbol
        assert symbol["library"] == "aashto"
        assert "path" in symbol["svg_path"].lower()

    def test_get_drainage_arrow(self):
        """Test retrieving drainage arrow symbol."""
        symbol = SymbolLibrary.get("drainage_arrow")

        assert symbol is not None
        assert symbol["library"] == "aashto"
        # SLOPE text removed from symbol to avoid rotation issues - add separately as TextAnnotation
        assert "path" in symbol["svg_path"]  # Should have arrow path

    def test_get_centerpoint(self):
        """Test retrieving centerpoint symbol."""
        symbol = SymbolLibrary.get("centerpoint")

        assert symbol is not None
        assert symbol["library"] == "aashto"
        # Should have circle and crosshairs
        assert "circle" in symbol["svg_path"]
        assert "line" in symbol["svg_path"]

    def test_get_grade_point(self):
        """Test retrieving grade point symbol."""
        symbol = SymbolLibrary.get("grade_point")

        assert symbol is not None
        assert symbol["width"] > 0
        assert symbol["height"] > 0

    def test_get_unknown_symbol_raises_error(self):
        """Test that unknown symbol raises KeyError."""
        with pytest.raises(KeyError, match="not found"):
            SymbolLibrary.get("nonexistent_symbol")

    def test_list_all_symbols(self):
        """Test listing all registered symbols."""
        all_symbols = SymbolLibrary.list_symbols()

        # Should have at least traffic, drainage, and standard symbols
        assert len(all_symbols) >= 9  # At least the ones we defined
        assert "traffic_arrow" in all_symbols
        assert "lane_marker" in all_symbols
        assert "drainage_arrow" in all_symbols
        assert "drainage_inlet" in all_symbols
        assert "flow_arrow" in all_symbols
        assert "centerpoint" in all_symbols
        assert "grade_point" in all_symbols
        assert "station_mark" in all_symbols
        assert "section_cut" in all_symbols

    def test_list_symbols_by_library(self):
        """Test filtering symbols by library."""
        aashto_symbols = SymbolLibrary.list_symbols(library="aashto")

        # All our symbols are AASHTO (except test_circle)
        assert len(aashto_symbols) >= 9

        # Test library should only have test_circle
        test_symbols = SymbolLibrary.list_symbols(library="test")
        assert "test_circle" in test_symbols

    def test_register_custom_symbol(self):
        """Test registering a custom symbol."""
        SymbolLibrary.register(
            symbol_type="custom_test",
            svg_path='<rect x="0" y="0" width="10" height="10"/>',
            width=0.5,
            height=0.5,
            library="custom"
        )

        symbol = SymbolLibrary.get("custom_test")
        assert symbol is not None
        assert symbol["library"] == "custom"
        assert "rect" in symbol["svg_path"]

        # Clean up
        custom_symbols = SymbolLibrary.list_symbols(library="custom")
        assert "custom_test" in custom_symbols

    def test_symbol_dimensions(self):
        """Test that all symbols have valid dimensions."""
        all_symbols = SymbolLibrary.list_symbols()

        for symbol_type in all_symbols:
            symbol = SymbolLibrary.get(symbol_type)
            assert symbol["width"] > 0, f"{symbol_type} has invalid width"
            assert symbol["height"] > 0, f"{symbol_type} has invalid height"

    def test_traffic_symbols(self):
        """Test traffic-related symbols."""
        traffic_symbols = ["traffic_arrow", "lane_marker"]

        for symbol_type in traffic_symbols:
            symbol = SymbolLibrary.get(symbol_type)
            assert symbol is not None
            assert symbol["library"] == "aashto"

    def test_drainage_symbols(self):
        """Test drainage-related symbols."""
        drainage_symbols = ["drainage_arrow", "drainage_inlet", "flow_arrow"]

        for symbol_type in drainage_symbols:
            symbol = SymbolLibrary.get(symbol_type)
            assert symbol is not None
            assert symbol["library"] == "aashto"

    def test_standard_symbols(self):
        """Test standard geometric marks."""
        standard_symbols = [
            "centerpoint",
            "grade_point",
            "station_mark",
            "elevation_mark",
            "section_cut"
        ]

        for symbol_type in standard_symbols:
            symbol = SymbolLibrary.get(symbol_type)
            assert symbol is not None
            assert symbol["library"] == "aashto"

    def test_symbol_svg_paths_valid(self):
        """Test that all SVG paths are non-empty strings."""
        all_symbols = SymbolLibrary.list_symbols()

        for symbol_type in all_symbols:
            symbol = SymbolLibrary.get(symbol_type)
            svg_path = symbol["svg_path"]
            assert isinstance(svg_path, str)
            assert len(svg_path) > 0
            # Should contain at least one SVG element
            assert any(tag in svg_path.lower() for tag in ["<g", "<path", "<circle", "<rect", "<line"])
