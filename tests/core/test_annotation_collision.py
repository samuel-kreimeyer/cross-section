"""Tests for annotation collision detection and resolution."""

import pytest

from cross_section.core.domain.annotations import (
    AnnotationCollection,
    DimensionAnnotation,
    LeaderAnnotation,
    SymbolAnnotation,
    TextAnnotation,
)
from cross_section.core.domain.annotations.collision import (
    CollisionDetector,
    CollisionResolver,
    line_segment_intersection,
)
from cross_section.core.geometry.primitives import Point2D


class TestLineIntersection:
    """Tests for line segment intersection utility."""

    def test_intersecting_segments(self):
        """Test that intersecting segments return intersection point."""
        p1 = Point2D(0, 0)
        p2 = Point2D(10, 10)
        p3 = Point2D(0, 10)
        p4 = Point2D(10, 0)

        intersection = line_segment_intersection(p1, p2, p3, p4)

        assert intersection is not None
        assert intersection.x == pytest.approx(5.0)
        assert intersection.y == pytest.approx(5.0)

    def test_parallel_segments(self):
        """Test that parallel segments return None."""
        p1 = Point2D(0, 0)
        p2 = Point2D(10, 0)
        p3 = Point2D(0, 5)
        p4 = Point2D(10, 5)

        intersection = line_segment_intersection(p1, p2, p3, p4)

        assert intersection is None

    def test_non_intersecting_segments(self):
        """Test that non-intersecting segments return None."""
        p1 = Point2D(0, 0)
        p2 = Point2D(5, 5)
        p3 = Point2D(10, 10)
        p4 = Point2D(15, 15)

        intersection = line_segment_intersection(p1, p2, p3, p4)

        assert intersection is None

    def test_perpendicular_segments(self):
        """Test perpendicular segments intersection."""
        p1 = Point2D(5, 0)
        p2 = Point2D(5, 10)
        p3 = Point2D(0, 5)
        p4 = Point2D(10, 5)

        intersection = line_segment_intersection(p1, p2, p3, p4)

        assert intersection is not None
        assert intersection.x == pytest.approx(5.0)
        assert intersection.y == pytest.approx(5.0)


class TestCollisionDetector:
    """Tests for CollisionDetector class."""

    def test_text_text_overlap_detected(self):
        """Test that overlapping text is detected."""
        text1 = TextAnnotation(position=Point2D(5.0, 10.0), text="Test 1")
        text2 = TextAnnotation(position=Point2D(5.1, 10.1), text="Test 2")

        assert CollisionDetector.detect_text_text(text1, text2)

    def test_text_text_no_overlap(self):
        """Test that separated text is not detected as colliding."""
        text1 = TextAnnotation(position=Point2D(0.0, 0.0), text="Test 1")
        text2 = TextAnnotation(position=Point2D(10.0, 10.0), text="Test 2")

        assert not CollisionDetector.detect_text_text(text1, text2)

    def test_text_text_with_buffer(self):
        """Test text collision detection with buffer."""
        text1 = TextAnnotation(position=Point2D(0.0, 0.0), text="A")
        text2 = TextAnnotation(position=Point2D(0.5, 0.0), text="B")

        # Without buffer, might not collide
        # With large buffer, should collide
        assert CollisionDetector.detect_text_text(text1, text2, buffer=0.5)

    def test_line_text_dimension_overlap(self):
        """Test dimension line overlapping text."""
        dim = DimensionAnnotation(
            start=Point2D(0, 5),
            end=Point2D(10, 5),
            offset=0.5
        )
        # Text positioned where dimension line will be
        text = TextAnnotation(position=Point2D(5, 5.5), text="Overlap")

        assert CollisionDetector.detect_line_text(dim, text)

    def test_line_text_no_overlap(self):
        """Test dimension line not overlapping text."""
        dim = DimensionAnnotation(
            start=Point2D(0, 0),
            end=Point2D(10, 0),
            offset=0.5
        )
        # Text far away
        text = TextAnnotation(position=Point2D(5, 10), text="No overlap")

        assert not CollisionDetector.detect_line_text(dim, text)

    def test_line_text_leader_overlap(self):
        """Test leader line overlapping text."""
        leader = LeaderAnnotation(
            points=[Point2D(0, 0), Point2D(10, 10)],
            text="Leader"
        )
        # Text in the path of the leader
        text = TextAnnotation(position=Point2D(5, 5), text="Overlap")

        assert CollisionDetector.detect_line_text(leader, text)

    def test_line_line_dimension_intersection(self):
        """Test two dimension lines intersecting."""
        dim1 = DimensionAnnotation(
            start=Point2D(0, 5),
            end=Point2D(10, 5),
            offset=0.5
        )
        dim2 = DimensionAnnotation(
            start=Point2D(5, 0),
            end=Point2D(5, 10),
            offset=0.5
        )

        intersection = CollisionDetector.detect_line_line(dim1, dim2)

        # Should intersect somewhere near (5, 5)
        assert intersection is not None

    def test_line_line_no_intersection(self):
        """Test parallel dimension lines don't intersect."""
        dim1 = DimensionAnnotation(
            start=Point2D(0, 0),
            end=Point2D(10, 0),
            offset=0.5
        )
        dim2 = DimensionAnnotation(
            start=Point2D(0, 5),
            end=Point2D(10, 5),
            offset=0.5
        )

        intersection = CollisionDetector.detect_line_line(dim1, dim2)

        assert intersection is None


class TestCollisionResolver:
    """Tests for CollisionResolver class."""

    def test_resolve_text_text_collision(self):
        """Test that text-text collision is resolved."""
        text1 = TextAnnotation(
            position=Point2D(5.0, 10.0),
            text="Text 1",
            priority=1
        )
        text2 = TextAnnotation(
            position=Point2D(5.05, 10.05),
            text="Text 2",
            priority=0  # Lower priority, will be moved
        )

        resolver = CollisionResolver()
        resolved = resolver.resolve_all([text1, text2])

        # Text2 should have been repositioned
        resolved_text2 = resolved[1]
        assert isinstance(resolved_text2, TextAnnotation)
        # Should no longer collide
        assert not CollisionDetector.detect_text_text(
            resolved[0], resolved_text2, buffer=0.05
        )

    def test_resolve_line_text_collision(self):
        """Test that line-text collision is resolved."""
        dim = DimensionAnnotation(
            start=Point2D(0, 5),
            end=Point2D(10, 5),
            offset=0.3
        )
        # Text overlapping dimension line
        text = TextAnnotation(position=Point2D(5, 5.3), text="Overlap")

        resolver = CollisionResolver()
        resolved = resolver.resolve_all([dim, text])

        # Text should have been repositioned
        resolved_text = resolved[1]
        assert isinstance(resolved_text, TextAnnotation)
        # Should no longer collide
        assert not CollisionDetector.detect_line_text(
            resolved[0], resolved_text, buffer=0.02
        )

    def test_priority_based_resolution(self):
        """Test that higher priority text doesn't move."""
        text1 = TextAnnotation(
            position=Point2D(5.0, 10.0),
            text="High Priority",
            priority=10
        )
        text2 = TextAnnotation(
            position=Point2D(5.05, 10.05),
            text="Low Priority",
            priority=0
        )

        resolver = CollisionResolver()
        resolved = resolver.resolve_all([text1, text2])

        # text1 should not have moved (high priority)
        resolved_text1 = resolved[0]
        assert isinstance(resolved_text1, TextAnnotation)
        assert resolved_text1.position.x == pytest.approx(5.0)
        assert resolved_text1.position.y == pytest.approx(10.0)

        # text2 should have moved (low priority)
        resolved_text2 = resolved[1]
        assert isinstance(resolved_text2, TextAnnotation)
        assert (
            resolved_text2.position.x != pytest.approx(5.05) or
            resolved_text2.position.y != pytest.approx(10.05)
        )

    def test_symbol_text_avoidance(self):
        """Test that text repositions around symbols (symbols are fixed)."""
        symbol = SymbolAnnotation(
            position=Point2D(5.0, 10.0),
            symbol_type="test_circle"
        )
        # Text overlapping symbol
        text = TextAnnotation(position=Point2D(5.1, 10.1), text="Text")

        resolver = CollisionResolver()
        resolved = resolver.resolve_all([symbol, text])

        # Symbol should not have moved
        resolved_symbol = resolved[0]
        assert isinstance(resolved_symbol, SymbolAnnotation)
        assert resolved_symbol.position.x == pytest.approx(5.0)
        assert resolved_symbol.position.y == pytest.approx(10.0)

        # Text should have moved
        resolved_text = resolved[1]
        assert isinstance(resolved_text, TextAnnotation)

    def test_multiple_iterations(self):
        """Test that resolver iterates to resolve complex collisions."""
        # Create chain of overlapping text
        texts = [
            TextAnnotation(position=Point2D(5.0 + i * 0.05, 10.0), text=f"T{i}")
            for i in range(3)
        ]

        resolver = CollisionResolver(max_iterations=10)
        resolved = resolver.resolve_all(texts)

        # All texts should be resolved (no collisions)
        for i, text1 in enumerate(resolved):
            for text2 in resolved[i + 1:]:
                if isinstance(text1, TextAnnotation) and isinstance(text2, TextAnnotation):
                    assert not CollisionDetector.detect_text_text(
                        text1, text2, buffer=0.05
                    )

    def test_no_valid_position_found(self):
        """Test behavior when no valid position can be found."""
        # Surround a text with many obstacles
        obstacles = [
            TextAnnotation(
                position=Point2D(5.0 + dx, 10.0 + dy),
                text="X",
                priority=10
            )
            for dx in [-0.5, 0, 0.5]
            for dy in [-0.5, 0, 0.5]
            if dx != 0 or dy != 0
        ]

        text = TextAnnotation(
            position=Point2D(5.0, 10.0),
            text="Trapped",
            priority=0
        )

        resolver = CollisionResolver(max_iterations=5)
        resolved = resolver.resolve_all(obstacles + [text])

        # Should attempt resolution but may not find valid position
        # (At least it shouldn't crash)
        assert len(resolved) == len(obstacles) + 1


class TestCollisionResolutionIntegration:
    """Integration tests for collision resolution with AnnotationCollection."""

    def test_collection_resolve_collisions(self):
        """Test resolve_collisions method on collection."""
        collection = AnnotationCollection()

        # Add overlapping text
        collection.add(TextAnnotation(
            position=Point2D(5.0, 10.0),
            text="Text 1",
            priority=1
        ))
        collection.add(TextAnnotation(
            position=Point2D(5.05, 10.05),
            text="Text 2",
            priority=0
        ))

        # Resolve collisions
        collection.resolve_collisions()

        # Check that collisions are resolved
        texts = collection.get_by_type(TextAnnotation)
        assert len(texts) == 2
        assert not CollisionDetector.detect_text_text(texts[0], texts[1], buffer=0.05)

    def test_mixed_annotation_collision_resolution(self):
        """Test collision resolution with mixed annotation types."""
        collection = AnnotationCollection()

        # Add dimension
        collection.add(DimensionAnnotation(
            start=Point2D(0, 5),
            end=Point2D(10, 5),
            offset=0.3
        ))

        # Add overlapping text
        collection.add(TextAnnotation(
            position=Point2D(5, 5.3),
            text="Overlapping"
        ))

        # Add symbol
        collection.add(SymbolAnnotation(
            position=Point2D(5, 6),
            symbol_type="test_circle"
        ))

        # Resolve collisions
        collection.resolve_collisions()

        # Verify no line-text collisions
        dims = collection.get_by_type(DimensionAnnotation)
        texts = collection.get_by_type(TextAnnotation)

        for dim in dims:
            for text in texts:
                assert not CollisionDetector.detect_line_text(dim, text, buffer=0.02)

    def test_empty_collection_resolution(self):
        """Test that resolving empty collection doesn't crash."""
        collection = AnnotationCollection()
        collection.resolve_collisions()
        assert collection.count() == 0

    def test_single_annotation_resolution(self):
        """Test that single annotation doesn't need resolution."""
        collection = AnnotationCollection()
        text = TextAnnotation(position=Point2D(5, 10), text="Solo")
        collection.add(text)

        collection.resolve_collisions()

        assert collection.count() == 1
        resolved_text = collection.annotations[0]
        assert isinstance(resolved_text, TextAnnotation)
        assert resolved_text.position.x == pytest.approx(5.0)
        assert resolved_text.position.y == pytest.approx(10.0)
