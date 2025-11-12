"""Tests for geometry primitives."""

import pytest
import math
from cross_section.core.geometry.primitives import Point2D, Polygon, ConnectionPoint, ComponentGeometry


class TestPoint2D:
    """Tests for Point2D class."""

    def test_create_point(self):
        """Test creating a point."""
        p = Point2D(x=1.0, y=2.0)
        assert p.x == 1.0
        assert p.y == 2.0

    def test_distance_to(self):
        """Test calculating distance between points."""
        p1 = Point2D(0.0, 0.0)
        p2 = Point2D(3.0, 4.0)
        assert p1.distance_to(p2) == 5.0

    def test_offset(self):
        """Test offsetting a point."""
        p = Point2D(1.0, 2.0)
        p_offset = p.offset(3.0, 4.0)
        assert p_offset.x == 4.0
        assert p_offset.y == 6.0
        # Original point should be unchanged
        assert p.x == 1.0
        assert p.y == 2.0

    def test_repr(self):
        """Test string representation."""
        p = Point2D(1.234, 5.678)
        assert "1.234" in repr(p)
        assert "5.678" in repr(p)


class TestPolygon:
    """Tests for Polygon class."""

    def test_create_polygon(self):
        """Test creating a polygon."""
        vertices = [
            Point2D(0.0, 0.0),
            Point2D(1.0, 0.0),
            Point2D(1.0, 1.0),
            Point2D(0.0, 1.0),
        ]
        polygon = Polygon(exterior=vertices)
        assert len(polygon.exterior) == 4
        assert polygon.holes is None

    def test_bounds(self):
        """Test calculating bounding box."""
        vertices = [
            Point2D(1.0, 2.0),
            Point2D(4.0, 2.0),
            Point2D(4.0, 5.0),
            Point2D(1.0, 5.0),
        ]
        polygon = Polygon(exterior=vertices)
        bounds = polygon.bounds()
        assert bounds == (1.0, 2.0, 4.0, 5.0)

    def test_bounds_empty(self):
        """Test bounds of empty polygon."""
        polygon = Polygon(exterior=[])
        bounds = polygon.bounds()
        assert bounds == (0.0, 0.0, 0.0, 0.0)

    def test_offset_x(self):
        """Test horizontal translation."""
        vertices = [Point2D(0.0, 0.0), Point2D(1.0, 0.0), Point2D(1.0, 1.0)]
        polygon = Polygon(exterior=vertices)
        offset_polygon = polygon.offset_x(5.0)

        assert offset_polygon.exterior[0].x == 5.0
        assert offset_polygon.exterior[1].x == 6.0
        assert offset_polygon.exterior[2].x == 6.0
        # Y coordinates unchanged
        assert offset_polygon.exterior[0].y == 0.0

    def test_area_square(self):
        """Test area calculation for a square."""
        vertices = [
            Point2D(0.0, 0.0),
            Point2D(2.0, 0.0),
            Point2D(2.0, 2.0),
            Point2D(0.0, 2.0),
        ]
        polygon = Polygon(exterior=vertices)
        assert polygon.area() == 4.0

    def test_area_triangle(self):
        """Test area calculation for a triangle."""
        vertices = [
            Point2D(0.0, 0.0),
            Point2D(4.0, 0.0),
            Point2D(2.0, 3.0),
        ]
        polygon = Polygon(exterior=vertices)
        assert polygon.area() == 6.0


class TestConnectionPoint:
    """Tests for ConnectionPoint class."""

    def test_create_connection_point(self):
        """Test creating a connection point."""
        cp = ConnectionPoint(x=1.0, y=2.0, description="Test point")
        assert cp.x == 1.0
        assert cp.y == 2.0
        assert cp.description == "Test point"

    def test_default_description(self):
        """Test default empty description."""
        cp = ConnectionPoint(x=1.0, y=2.0)
        assert cp.description == ""


class TestComponentGeometry:
    """Tests for ComponentGeometry class."""

    def test_create_component_geometry(self):
        """Test creating component geometry."""
        geom = ComponentGeometry()
        assert geom.polygons == []
        assert geom.polylines == []
        assert geom.metadata == {}

    def test_bounds_with_polygons(self):
        """Test bounds calculation with multiple polygons."""
        poly1 = Polygon(exterior=[Point2D(0.0, 0.0), Point2D(1.0, 0.0), Point2D(1.0, 1.0)])
        poly2 = Polygon(exterior=[Point2D(2.0, 2.0), Point2D(5.0, 2.0), Point2D(5.0, 6.0)])

        geom = ComponentGeometry(polygons=[poly1, poly2])
        bounds = geom.bounds()

        assert bounds == (0.0, 0.0, 5.0, 6.0)

    def test_bounds_empty(self):
        """Test bounds of empty geometry."""
        geom = ComponentGeometry()
        bounds = geom.bounds()
        assert bounds == (0.0, 0.0, 0.0, 0.0)
