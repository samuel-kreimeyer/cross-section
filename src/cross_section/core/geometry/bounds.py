"""Bounding box utilities for collision detection and spatial queries."""

from dataclasses import dataclass

from .primitives import Point2D


@dataclass
class BoundingBox:
    """Axis-aligned 2D bounding box.

    Attributes:
        min_x: Minimum X coordinate
        min_y: Minimum Y coordinate
        max_x: Maximum X coordinate
        max_y: Maximum Y coordinate
    """

    min_x: float
    min_y: float
    max_x: float
    max_y: float

    def __post_init__(self) -> None:
        """Validate bounding box coordinates."""
        if self.min_x > self.max_x:
            raise ValueError(f"min_x ({self.min_x}) must be <= max_x ({self.max_x})")
        if self.min_y > self.max_y:
            raise ValueError(f"min_y ({self.min_y}) must be <= max_y ({self.max_y})")

    def intersects(self, other: "BoundingBox", buffer: float = 0.0) -> bool:
        """Check if this box intersects another box.

        Args:
            other: The other bounding box to check
            buffer: Optional buffer distance to expand boxes before checking

        Returns:
            True if boxes intersect (or are within buffer distance)
        """
        # Expand both boxes by buffer
        self_expanded = self.expand(buffer) if buffer > 0 else self
        other_expanded = other.expand(buffer) if buffer > 0 else other

        # Boxes don't intersect if one is completely to the side of the other
        if self_expanded.max_x < other_expanded.min_x:
            return False
        if self_expanded.min_x > other_expanded.max_x:
            return False
        if self_expanded.max_y < other_expanded.min_y:
            return False
        if self_expanded.min_y > other_expanded.max_y:
            return False

        return True

    def contains_point(self, point: Point2D) -> bool:
        """Check if a point is inside the bounding box.

        Args:
            point: The point to check

        Returns:
            True if point is inside or on the boundary of the box
        """
        return (
            self.min_x <= point.x <= self.max_x
            and self.min_y <= point.y <= self.max_y
        )

    def expand(self, amount: float) -> "BoundingBox":
        """Return a new bounding box expanded by the given amount.

        Args:
            amount: Distance to expand in all directions (can be negative to shrink)

        Returns:
            New expanded (or shrunk) bounding box
        """
        return BoundingBox(
            min_x=self.min_x - amount,
            min_y=self.min_y - amount,
            max_x=self.max_x + amount,
            max_y=self.max_y + amount,
        )

    def width(self) -> float:
        """Calculate the width of the bounding box."""
        return self.max_x - self.min_x

    def height(self) -> float:
        """Calculate the height of the bounding box."""
        return self.max_y - self.min_y

    def center(self) -> Point2D:
        """Calculate the center point of the bounding box."""
        return Point2D(
            x=(self.min_x + self.max_x) / 2,
            y=(self.min_y + self.max_y) / 2,
        )

    @classmethod
    def from_points(cls, points: list[Point2D]) -> "BoundingBox":
        """Create a bounding box from a list of points.

        Args:
            points: List of points to bound

        Returns:
            Smallest bounding box containing all points

        Raises:
            ValueError: If points list is empty
        """
        if not points:
            raise ValueError("Cannot create bounding box from empty points list")

        min_x = min(p.x for p in points)
        max_x = max(p.x for p in points)
        min_y = min(p.y for p in points)
        max_y = max(p.y for p in points)

        return cls(min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y)

    @classmethod
    def union(cls, boxes: list["BoundingBox"]) -> "BoundingBox":
        """Create a bounding box that contains all given boxes.

        Args:
            boxes: List of bounding boxes to union

        Returns:
            Smallest bounding box containing all input boxes

        Raises:
            ValueError: If boxes list is empty
        """
        if not boxes:
            raise ValueError("Cannot create union from empty boxes list")

        min_x = min(box.min_x for box in boxes)
        max_x = max(box.max_x for box in boxes)
        min_y = min(box.min_y for box in boxes)
        max_y = max(box.max_y for box in boxes)

        return cls(min_x=min_x, min_y=min_y, max_x=max_x, max_y=max_y)
