"""Tests for BoundingBox class."""

import pytest

from cross_section.core.geometry.bounds import BoundingBox
from cross_section.core.geometry.primitives import Point2D


class TestBoundingBox:
    """Tests for BoundingBox class."""

    def test_create_bounding_box(self):
        """Test creating a bounding box."""
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=5.0)
        assert bbox.min_x == 0.0
        assert bbox.min_y == 0.0
        assert bbox.max_x == 10.0
        assert bbox.max_y == 5.0

    def test_invalid_bounding_box_x(self):
        """Test that creating invalid box (min_x > max_x) raises error."""
        with pytest.raises(ValueError, match="min_x.*must be <= max_x"):
            BoundingBox(min_x=10.0, min_y=0.0, max_x=5.0, max_y=5.0)

    def test_invalid_bounding_box_y(self):
        """Test that creating invalid box (min_y > max_y) raises error."""
        with pytest.raises(ValueError, match="min_y.*must be <= max_y"):
            BoundingBox(min_x=0.0, min_y=10.0, max_x=5.0, max_y=5.0)

    def test_intersects_overlapping_boxes(self):
        """Test that overlapping boxes are detected."""
        box1 = BoundingBox(min_x=0.0, min_y=0.0, max_x=5.0, max_y=5.0)
        box2 = BoundingBox(min_x=3.0, min_y=3.0, max_x=8.0, max_y=8.0)
        assert box1.intersects(box2)
        assert box2.intersects(box1)

    def test_intersects_touching_boxes(self):
        """Test that boxes touching at edge are detected as intersecting."""
        box1 = BoundingBox(min_x=0.0, min_y=0.0, max_x=5.0, max_y=5.0)
        box2 = BoundingBox(min_x=5.0, min_y=0.0, max_x=10.0, max_y=5.0)
        assert box1.intersects(box2)

    def test_intersects_separated_boxes(self):
        """Test that separated boxes don't intersect."""
        box1 = BoundingBox(min_x=0.0, min_y=0.0, max_x=5.0, max_y=5.0)
        box2 = BoundingBox(min_x=10.0, min_y=10.0, max_x=15.0, max_y=15.0)
        assert not box1.intersects(box2)
        assert not box2.intersects(box1)

    def test_intersects_with_buffer(self):
        """Test intersection with buffer distance."""
        box1 = BoundingBox(min_x=0.0, min_y=0.0, max_x=5.0, max_y=5.0)
        box2 = BoundingBox(min_x=6.0, min_y=6.0, max_x=10.0, max_y=10.0)

        # Without buffer, they don't intersect
        assert not box1.intersects(box2)

        # With buffer of 1.5, they do intersect
        assert box1.intersects(box2, buffer=1.5)

    def test_contains_point_inside(self):
        """Test that point inside box is detected."""
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=5.0)
        point = Point2D(5.0, 2.5)
        assert bbox.contains_point(point)

    def test_contains_point_on_boundary(self):
        """Test that point on boundary is considered inside."""
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=5.0)
        assert bbox.contains_point(Point2D(0.0, 0.0))
        assert bbox.contains_point(Point2D(10.0, 5.0))
        assert bbox.contains_point(Point2D(5.0, 0.0))

    def test_contains_point_outside(self):
        """Test that point outside box is not detected."""
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=5.0)
        assert not bbox.contains_point(Point2D(-1.0, 2.5))
        assert not bbox.contains_point(Point2D(11.0, 2.5))
        assert not bbox.contains_point(Point2D(5.0, 6.0))

    def test_expand_positive(self):
        """Test expanding bounding box."""
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=5.0)
        expanded = bbox.expand(1.0)

        assert expanded.min_x == -1.0
        assert expanded.min_y == -1.0
        assert expanded.max_x == 11.0
        assert expanded.max_y == 6.0

        # Original should be unchanged
        assert bbox.min_x == 0.0
        assert bbox.max_x == 10.0

    def test_expand_negative(self):
        """Test shrinking bounding box."""
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=5.0)
        shrunk = bbox.expand(-1.0)

        assert shrunk.min_x == 1.0
        assert shrunk.min_y == 1.0
        assert shrunk.max_x == 9.0
        assert shrunk.max_y == 4.0

    def test_width(self):
        """Test width calculation."""
        bbox = BoundingBox(min_x=2.0, min_y=0.0, max_x=12.0, max_y=5.0)
        assert bbox.width() == 10.0

    def test_height(self):
        """Test height calculation."""
        bbox = BoundingBox(min_x=0.0, min_y=3.0, max_x=10.0, max_y=8.0)
        assert bbox.height() == 5.0

    def test_center(self):
        """Test center point calculation."""
        bbox = BoundingBox(min_x=0.0, min_y=0.0, max_x=10.0, max_y=5.0)
        center = bbox.center()
        assert center.x == 5.0
        assert center.y == 2.5

    def test_from_points(self):
        """Test creating bounding box from points."""
        points = [
            Point2D(1.0, 2.0),
            Point2D(5.0, 1.0),
            Point2D(3.0, 6.0),
            Point2D(0.0, 3.0),
        ]
        bbox = BoundingBox.from_points(points)

        assert bbox.min_x == 0.0
        assert bbox.max_x == 5.0
        assert bbox.min_y == 1.0
        assert bbox.max_y == 6.0

    def test_from_points_empty(self):
        """Test that creating box from empty points raises error."""
        with pytest.raises(ValueError, match="empty points list"):
            BoundingBox.from_points([])

    def test_from_points_single(self):
        """Test creating box from single point."""
        points = [Point2D(5.0, 3.0)]
        bbox = BoundingBox.from_points(points)

        assert bbox.min_x == 5.0
        assert bbox.max_x == 5.0
        assert bbox.min_y == 3.0
        assert bbox.max_y == 3.0

    def test_union_multiple_boxes(self):
        """Test creating union of multiple boxes."""
        box1 = BoundingBox(min_x=0.0, min_y=0.0, max_x=5.0, max_y=5.0)
        box2 = BoundingBox(min_x=3.0, min_y=3.0, max_x=8.0, max_y=8.0)
        box3 = BoundingBox(min_x=1.0, min_y=1.0, max_x=4.0, max_y=4.0)

        union = BoundingBox.union([box1, box2, box3])

        assert union.min_x == 0.0
        assert union.max_x == 8.0
        assert union.min_y == 0.0
        assert union.max_y == 8.0

    def test_union_empty(self):
        """Test that creating union from empty list raises error."""
        with pytest.raises(ValueError, match="empty boxes list"):
            BoundingBox.union([])

    def test_union_single(self):
        """Test union of single box returns equivalent box."""
        box = BoundingBox(min_x=0.0, min_y=0.0, max_x=5.0, max_y=5.0)
        union = BoundingBox.union([box])

        assert union.min_x == box.min_x
        assert union.max_x == box.max_x
        assert union.min_y == box.min_y
        assert union.max_y == box.max_y
