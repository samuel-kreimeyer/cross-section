"""Tests for annotation types."""

import math

import pytest

from cross_section.core.domain.annotations import (
    DimensionAnnotation,
    LeaderAnnotation,
    SymbolAnnotation,
    TextAnnotation,
)
from cross_section.core.domain.annotations.symbols.library import SymbolLibrary
from cross_section.core.geometry.primitives import Point2D


class TestTextAnnotation:
    """Tests for TextAnnotation class."""

    def test_create_text_simple(self):
        """Test creating a simple text annotation."""
        text = TextAnnotation(
            position=Point2D(5.0, 10.0),
            text="Test Label"
        )
        assert text.position.x == 5.0
        assert text.position.y == 10.0
        assert text.text == "Test Label"
        assert text.font_size == 0.15
        assert text.anchor == "middle"
        assert text.angle == 0.0
        assert text.is_keyed_note is False

    def test_create_text_custom(self):
        """Test creating text with custom parameters."""
        text = TextAnnotation(
            position=Point2D(5.0, 10.0),
            text="Custom",
            font_size=0.20,
            anchor="start",
            angle=45.0,
            is_keyed_note=True
        )
        assert text.font_size == 0.20
        assert text.anchor == "start"
        assert text.angle == 45.0
        assert text.is_keyed_note is True

    def test_text_empty_raises_error(self):
        """Test that empty text raises error."""
        with pytest.raises(ValueError, match="Text cannot be empty"):
            TextAnnotation(position=Point2D(0, 0), text="")

    def test_text_negative_font_size_raises_error(self):
        """Test that negative font size raises error."""
        with pytest.raises(ValueError, match="Font size must be positive"):
            TextAnnotation(position=Point2D(0, 0), text="Test", font_size=-0.1)

    def test_text_invalid_angle_raises_error(self):
        """Test that invalid angle raises error."""
        with pytest.raises(ValueError, match="Angle must be between"):
            TextAnnotation(position=Point2D(0, 0), text="Test", angle=400.0)

    def test_text_bounds_middle_anchor(self):
        """Test bounding box calculation for middle-anchored text."""
        text = TextAnnotation(
            position=Point2D(5.0, 10.0),
            text="ABC",  # 3 characters
            font_size=0.10
        )
        bounds = text.bounds()

        # Width estimate: 0.10 * 3 * 0.6 = 0.18
        # Height: 0.10
        # Middle anchor: centered at position

        assert bounds.center().x == pytest.approx(5.0)
        assert bounds.center().y == pytest.approx(10.0)
        assert bounds.width() == pytest.approx(0.18, abs=0.01)
        assert bounds.height() == pytest.approx(0.10, abs=0.01)

    def test_text_bounds_start_anchor(self):
        """Test bounding box for start-anchored text."""
        text = TextAnnotation(
            position=Point2D(5.0, 10.0),
            text="ABC",
            font_size=0.10,
            anchor="start"
        )
        bounds = text.bounds()

        # Start anchor: text extends to the right
        assert bounds.min_x == pytest.approx(5.0)
        assert bounds.max_x == pytest.approx(5.18, abs=0.01)

    def test_text_bounds_end_anchor(self):
        """Test bounding box for end-anchored text."""
        text = TextAnnotation(
            position=Point2D(5.0, 10.0),
            text="ABC",
            font_size=0.10,
            anchor="end"
        )
        bounds = text.bounds()

        # End anchor: text extends to the left
        assert bounds.max_x == pytest.approx(5.0)
        assert bounds.min_x == pytest.approx(4.82, abs=0.01)

    def test_text_bounds_rotated(self):
        """Test bounding box for rotated text."""
        text = TextAnnotation(
            position=Point2D(5.0, 10.0),
            text="ABC",
            font_size=0.10,
            angle=45.0
        )
        bounds = text.bounds()

        # Rotated bounds should be larger than unrotated
        # (diagonal of rectangle)
        assert bounds.width() > 0.18
        assert bounds.height() > 0.10

    def test_text_reposition(self):
        """Test repositioning text."""
        text = TextAnnotation(position=Point2D(5.0, 10.0), text="Test")
        repositioned = text.reposition(Point2D(2.0, 3.0))

        assert repositioned.position.x == 7.0
        assert repositioned.position.y == 13.0
        # Original unchanged
        assert text.position.x == 5.0

    def test_text_to_svg_simple(self):
        """Test SVG generation for simple text."""
        text = TextAnnotation(position=Point2D(5.0, 10.0), text="Test")

        # Identity transform
        def identity(p: Point2D) -> Point2D:
            return p

        svg_elements = text.to_svg_elements(identity)

        assert len(svg_elements) == 1
        assert "<text" in svg_elements[0]
        assert "Test" in svg_elements[0]
        assert 'x="5.00"' in svg_elements[0]
        assert 'y="10.00"' in svg_elements[0]

    def test_text_validate(self):
        """Test validation of text annotation."""
        text = TextAnnotation(position=Point2D(5.0, 10.0), text="Valid")
        errors = text.validate()
        assert errors == []

    def test_text_validate_large_font(self):
        """Test validation warns about large font."""
        text = TextAnnotation(
            position=Point2D(5.0, 10.0),
            text="Test",
            font_size=1.5
        )
        errors = text.validate()
        assert any("very large" in e.lower() for e in errors)


class TestDimensionAnnotation:
    """Tests for DimensionAnnotation class."""

    def test_create_dimension_simple(self):
        """Test creating a simple dimension."""
        dim = DimensionAnnotation(
            start=Point2D(0.0, 10.0),
            end=Point2D(3.6, 10.0)
        )
        assert dim.start.x == 0.0
        assert dim.end.x == 3.6
        assert dim.offset == 0.3
        assert dim.show_arrows is True

    def test_dimension_auto_text(self):
        """Test automatic dimension text calculation."""
        dim = DimensionAnnotation(
            start=Point2D(0.0, 0.0),
            end=Point2D(3.0, 4.0)  # Distance = 5.0
        )
        # Should auto-calculate distance
        assert "5.00m" in dim.dimension_text

    def test_dimension_custom_text(self):
        """Test dimension with custom text."""
        dim = DimensionAnnotation(
            start=Point2D(0.0, 0.0),
            end=Point2D(5.0, 0.0),
            dimension_text="Custom 5m"
        )
        assert dim.dimension_text == "Custom 5m"

    def test_dimension_same_points_raises_error(self):
        """Test that same start/end points raises error."""
        with pytest.raises(ValueError, match="must be different"):
            DimensionAnnotation(
                start=Point2D(5.0, 10.0),
                end=Point2D(5.0, 10.0)
            )

    def test_dimension_auto_text_position(self):
        """Test automatic text position calculation."""
        dim = DimensionAnnotation(
            start=Point2D(0.0, 0.0),
            end=Point2D(10.0, 0.0),
            offset=0.5
        )
        # Text should be at midpoint with perpendicular offset
        assert dim.text_position.x == pytest.approx(5.0)
        assert dim.text_position.y == pytest.approx(0.5)  # Offset upward

    def test_dimension_line_endpoints(self):
        """Test dimension line endpoint calculation."""
        dim = DimensionAnnotation(
            start=Point2D(0.0, 0.0),
            end=Point2D(10.0, 0.0),
            offset=0.5
        )
        dim_start, dim_end = dim.get_dimension_line_endpoints()

        # Dimension line should be offset perpendicular to start-end line
        assert dim_start.x == pytest.approx(0.0)
        assert dim_start.y == pytest.approx(0.5)
        assert dim_end.x == pytest.approx(10.0)
        assert dim_end.y == pytest.approx(0.5)

    def test_dimension_bounds(self):
        """Test bounding box includes all elements."""
        dim = DimensionAnnotation(
            start=Point2D(0.0, 0.0),
            end=Point2D(10.0, 0.0),
            offset=0.5
        )
        bounds = dim.bounds()

        # Should include start, end, dimension line, and text
        assert bounds.min_x <= 0.0
        assert bounds.max_x >= 10.0
        assert bounds.min_y <= 0.0
        assert bounds.max_y >= 0.5

    def test_dimension_reposition(self):
        """Test repositioning dimension."""
        dim = DimensionAnnotation(
            start=Point2D(0.0, 0.0),
            end=Point2D(10.0, 0.0)
        )
        repositioned = dim.reposition(Point2D(5.0, 5.0))

        assert repositioned.start.x == 5.0
        assert repositioned.start.y == 5.0
        assert repositioned.end.x == 15.0
        assert repositioned.end.y == 5.0

    def test_dimension_to_svg(self):
        """Test SVG generation for dimension."""
        dim = DimensionAnnotation(
            start=Point2D(0.0, 0.0),
            end=Point2D(10.0, 0.0)
        )

        def identity(p: Point2D) -> Point2D:
            return p

        svg_elements = dim.to_svg_elements(identity)

        # Should have extension lines, dimension line, arrows, and text
        assert len(svg_elements) > 3
        assert any("dimension-extension" in e for e in svg_elements)
        assert any("dimension-line" in e for e in svg_elements)
        assert any("dimension-text" in e for e in svg_elements)

    def test_dimension_validate(self):
        """Test validation of dimension."""
        dim = DimensionAnnotation(
            start=Point2D(0.0, 0.0),
            end=Point2D(10.0, 0.0)
        )
        errors = dim.validate()
        assert errors == []

    def test_dimension_validate_negative_offset(self):
        """Test validation catches negative offset."""
        dim = DimensionAnnotation(
            start=Point2D(0.0, 0.0),
            end=Point2D(10.0, 0.0),
            offset=-0.5
        )
        errors = dim.validate()
        assert any("offset" in e.lower() and "negative" in e.lower() for e in errors)


class TestLeaderAnnotation:
    """Tests for LeaderAnnotation class."""

    def test_create_leader_2_points(self):
        """Test creating a leader with 2 points."""
        leader = LeaderAnnotation(
            points=[Point2D(0.0, 0.0), Point2D(5.0, 5.0)],
            text="Test"
        )
        assert len(leader.points) == 2
        assert leader.text == "Test"
        assert leader.arrow_at_start is True

    def test_create_leader_3_points(self):
        """Test creating a leader with 3 points (elbow)."""
        leader = LeaderAnnotation(
            points=[
                Point2D(0.0, 0.0),
                Point2D(3.0, 3.0),
                Point2D(6.0, 3.0)
            ],
            text="Elbow"
        )
        assert len(leader.points) == 3

    def test_leader_too_few_points_raises_error(self):
        """Test that leader with <2 points raises error."""
        with pytest.raises(ValueError, match="at least 2 points"):
            LeaderAnnotation(points=[Point2D(0, 0)], text="Test")

    def test_leader_too_many_points_raises_error(self):
        """Test that leader with >3 points raises error."""
        with pytest.raises(ValueError, match="at most 3 points"):
            LeaderAnnotation(
                points=[
                    Point2D(0, 0),
                    Point2D(1, 1),
                    Point2D(2, 2),
                    Point2D(3, 3)
                ],
                text="Test"
            )

    def test_leader_empty_text_raises_error(self):
        """Test that empty text raises error."""
        with pytest.raises(ValueError, match="text cannot be empty"):
            LeaderAnnotation(
                points=[Point2D(0, 0), Point2D(1, 1)],
                text=""
            )

    def test_leader_text_position(self):
        """Test text position is at last point."""
        leader = LeaderAnnotation(
            points=[Point2D(0, 0), Point2D(5, 5)],
            text="Test"
        )
        text_pos = leader.get_text_position()
        assert text_pos.x == 5.0
        assert text_pos.y == 5.0

    def test_leader_bounds(self):
        """Test bounding box includes path and text."""
        leader = LeaderAnnotation(
            points=[Point2D(0, 0), Point2D(5, 5)],
            text="ABC"
        )
        bounds = leader.bounds()

        # Should include all path points and text
        assert bounds.min_x <= 0.0
        assert bounds.max_x >= 5.0
        assert bounds.min_y <= 0.0
        assert bounds.max_y >= 5.0

    def test_leader_reposition(self):
        """Test repositioning leader."""
        leader = LeaderAnnotation(
            points=[Point2D(0, 0), Point2D(5, 5)],
            text="Test"
        )
        repositioned = leader.reposition(Point2D(10.0, 10.0))

        assert repositioned.points[0].x == 0.0
        assert repositioned.points[0].y == 0.0
        assert repositioned.points[1].x == 15.0
        assert repositioned.points[1].y == 15.0
        # Original unchanged
        assert leader.points[0].x == 0.0

    def test_leader_reposition_clamps_elbow(self):
        """Test leader elbow is clamped to a short extension."""
        leader = LeaderAnnotation(
            points=[Point2D(0, 0), Point2D(2, 0), Point2D(4, 0)],
            text="Test",
            text_size=0.10,
        )
        repositioned = leader.reposition(Point2D(0.0, 0.0))

        elbow = repositioned.points[1]
        text_point = repositioned.points[2]
        segment_length = ((elbow.x - text_point.x) ** 2 + (elbow.y - text_point.y) ** 2) ** 0.5
        max_length = leader.text_size * len(leader.text) * 0.6 + leader.max_underline_extension
        assert segment_length <= max_length + 1e-6

    def test_leader_to_svg(self):
        """Test SVG generation for leader."""
        leader = LeaderAnnotation(
            points=[Point2D(0, 0), Point2D(5, 5)],
            text="Test"
        )

        def identity(p: Point2D) -> Point2D:
            return p

        svg_elements = leader.to_svg_elements(identity)

        # Should have polyline, arrow, and text
        assert len(svg_elements) > 1
        assert any("<polyline" in e for e in svg_elements)
        assert any("Test" in e for e in svg_elements)

    def test_leader_validate(self):
        """Test validation of leader."""
        leader = LeaderAnnotation(
            points=[Point2D(0, 0), Point2D(5, 5)],
            text="Valid"
        )
        errors = leader.validate()
        assert errors == []

    def test_leader_validate_duplicate_points(self):
        """Test validation catches duplicate consecutive points."""
        leader = LeaderAnnotation(
            points=[Point2D(0, 0), Point2D(0, 0)],
            text="Test"
        )
        errors = leader.validate()
        assert any("duplicate" in e.lower() for e in errors)


class TestSymbolAnnotation:
    """Tests for SymbolAnnotation class."""

    def setup_method(self):
        """Set up test symbols."""
        # Save current library state
        self._saved_symbols = SymbolLibrary._symbols.copy()

        # Add test symbol
        SymbolLibrary.register(
            symbol_type="test_arrow",
            svg_path='<path d="M 0,-10 L 5,0 L 0,10 Z"/>',
            width=0.5,
            height=1.0,
            library="test"
        )

    def teardown_method(self):
        """Clean up test symbols."""
        # Restore original library state
        SymbolLibrary._symbols = self._saved_symbols

    def test_create_symbol(self):
        """Test creating a symbol annotation."""
        symbol = SymbolAnnotation(
            position=Point2D(5.0, 10.0),
            symbol_type="test_arrow"
        )
        assert symbol.position.x == 5.0
        assert symbol.position.y == 10.0
        assert symbol.symbol_type == "test_arrow"
        assert symbol.scale == 1.0
        assert symbol.angle == 0.0

    def test_create_symbol_custom(self):
        """Test creating symbol with custom scale and angle."""
        symbol = SymbolAnnotation(
            position=Point2D(5.0, 10.0),
            symbol_type="test_arrow",
            scale=2.0,
            angle=90.0
        )
        assert symbol.scale == 2.0
        assert symbol.angle == 90.0

    def test_symbol_empty_type_raises_error(self):
        """Test that empty symbol type raises error."""
        with pytest.raises(ValueError, match="Symbol type cannot be empty"):
            SymbolAnnotation(position=Point2D(0, 0), symbol_type="")

    def test_symbol_negative_scale_raises_error(self):
        """Test that negative scale raises error."""
        with pytest.raises(ValueError, match="Scale must be positive"):
            SymbolAnnotation(
                position=Point2D(0, 0),
                symbol_type="test_arrow",
                scale=-1.0
            )

    def test_symbol_invalid_angle_raises_error(self):
        """Test that invalid angle raises error."""
        with pytest.raises(ValueError, match="Angle must be between"):
            SymbolAnnotation(
                position=Point2D(0, 0),
                symbol_type="test_arrow",
                angle=400.0
            )

    def test_symbol_bounds_unrotated(self):
        """Test bounding box for unrotated symbol."""
        symbol = SymbolAnnotation(
            position=Point2D(10.0, 20.0),
            symbol_type="test_arrow"
        )
        bounds = symbol.bounds()

        # Symbol is 0.5m wide, 1.0m high, centered at position
        assert bounds.center().x == pytest.approx(10.0)
        assert bounds.center().y == pytest.approx(20.0)
        assert bounds.width() == pytest.approx(0.5)
        assert bounds.height() == pytest.approx(1.0)

    def test_symbol_bounds_rotated(self):
        """Test bounding box for rotated symbol."""
        symbol = SymbolAnnotation(
            position=Point2D(10.0, 20.0),
            symbol_type="test_arrow",
            angle=45.0
        )
        bounds = symbol.bounds()

        # Rotated bounds should be conservative (diagonal)
        diagonal = math.sqrt(0.5**2 + 1.0**2)
        expected_size = diagonal

        assert bounds.width() == pytest.approx(expected_size, abs=0.01)
        assert bounds.height() == pytest.approx(expected_size, abs=0.01)

    def test_symbol_bounds_scaled(self):
        """Test bounding box for scaled symbol."""
        symbol = SymbolAnnotation(
            position=Point2D(10.0, 20.0),
            symbol_type="test_arrow",
            scale=2.0
        )
        bounds = symbol.bounds()

        # Scaled bounds: 0.5 * 2 = 1.0, 1.0 * 2 = 2.0
        assert bounds.width() == pytest.approx(1.0)
        assert bounds.height() == pytest.approx(2.0)

    def test_symbol_reposition(self):
        """Test repositioning symbol."""
        symbol = SymbolAnnotation(
            position=Point2D(5.0, 10.0),
            symbol_type="test_arrow"
        )
        repositioned = symbol.reposition(Point2D(3.0, 4.0))

        assert repositioned.position.x == 8.0
        assert repositioned.position.y == 14.0
        # Original unchanged
        assert symbol.position.x == 5.0

    def test_symbol_to_svg(self):
        """Test SVG generation for symbol."""
        symbol = SymbolAnnotation(
            position=Point2D(5.0, 10.0),
            symbol_type="test_arrow"
        )

        def identity(p: Point2D) -> Point2D:
            return p

        svg_elements = symbol.to_svg_elements(identity)

        # Should have group with transform and path
        svg_str = " ".join(svg_elements)
        assert "<g" in svg_str
        assert "transform=" in svg_str
        assert "test_arrow" in svg_str

    def test_symbol_validate(self):
        """Test validation of symbol."""
        symbol = SymbolAnnotation(
            position=Point2D(5.0, 10.0),
            symbol_type="test_arrow"
        )
        errors = symbol.validate()
        assert errors == []

    def test_symbol_validate_unknown_type(self):
        """Test validation catches unknown symbol type."""
        symbol = SymbolAnnotation(
            position=Point2D(5.0, 10.0),
            symbol_type="nonexistent_symbol"
        )
        errors = symbol.validate()
        assert any("not found" in e.lower() for e in errors)

    def test_symbol_validate_large_scale(self):
        """Test validation warns about large scale."""
        symbol = SymbolAnnotation(
            position=Point2D(5.0, 10.0),
            symbol_type="test_arrow",
            scale=10.0
        )
        errors = symbol.validate()
        assert any("very large" in e.lower() for e in errors)
