"""Pure Python geometry primitives - no external dependencies."""

from dataclasses import dataclass, field
from typing import List, Optional
import math


@dataclass
class Point2D:
    """2D point - pure Python, no library dependencies."""

    x: float
    y: float

    def distance_to(self, other: "Point2D") -> float:
        """Calculate Euclidean distance to another point."""
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def offset(self, dx: float, dy: float) -> "Point2D":
        """Create new point offset by dx, dy."""
        return Point2D(self.x + dx, self.y + dy)

    def __repr__(self) -> str:
        return f"Point2D({self.x:.3f}, {self.y:.3f})"


@dataclass
class Polygon:
    """2D polygon - pure Python, no library dependencies."""

    exterior: List[Point2D]
    holes: Optional[List[List[Point2D]]] = None

    def bounds(self) -> tuple[float, float, float, float]:
        """
        Calculate bounding box.

        Returns:
            Tuple of (min_x, min_y, max_x, max_y)
        """
        if not self.exterior:
            return (0.0, 0.0, 0.0, 0.0)

        xs = [p.x for p in self.exterior]
        ys = [p.y for p in self.exterior]
        return (min(xs), min(ys), max(xs), max(ys))

    def offset_x(self, dx: float) -> "Polygon":
        """Translate polygon horizontally."""
        new_exterior = [p.offset(dx, 0) for p in self.exterior]
        new_holes = None
        if self.holes:
            new_holes = [[p.offset(dx, 0) for p in hole] for hole in self.holes]
        return Polygon(exterior=new_exterior, holes=new_holes)

    def area(self) -> float:
        """
        Calculate polygon area using shoelace formula.

        Returns:
            Area in square units (can be negative for clockwise winding)
        """
        if len(self.exterior) < 3:
            return 0.0

        area = 0.0
        for i in range(len(self.exterior)):
            j = (i + 1) % len(self.exterior)
            area += self.exterior[i].x * self.exterior[j].y
            area -= self.exterior[j].x * self.exterior[i].y

        return abs(area) / 2.0


@dataclass
class ConnectionPoint:
    """Geometric point where components connect."""

    x: float
    y: float
    description: str = ""

    def __repr__(self) -> str:
        return f"ConnectionPoint({self.x:.3f}, {self.y:.3f}, '{self.description}')"


@dataclass
class ComponentGeometry:
    """Geometric representation of a road component."""

    polygons: List[Polygon] = field(default_factory=list)
    polylines: List[List[Point2D]] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def bounds(self) -> tuple[float, float, float, float]:
        """
        Calculate bounding box of all polygons and polylines.

        Returns:
            Tuple of (min_x, min_y, max_x, max_y)
        """
        if not self.polygons and not self.polylines:
            return (0.0, 0.0, 0.0, 0.0)

        all_bounds = []

        # Add polygon bounds
        if self.polygons:
            all_bounds.extend([p.bounds() for p in self.polygons])

        # Add polyline bounds
        if self.polylines:
            for polyline in self.polylines:
                if polyline:
                    xs = [p.x for p in polyline]
                    ys = [p.y for p in polyline]
                    all_bounds.append((min(xs), min(ys), max(xs), max(ys)))

        if not all_bounds:
            return (0.0, 0.0, 0.0, 0.0)

        min_x = min(b[0] for b in all_bounds)
        min_y = min(b[1] for b in all_bounds)
        max_x = max(b[2] for b in all_bounds)
        max_y = max(b[3] for b in all_bounds)

        return (min_x, min_y, max_x, max_y)
