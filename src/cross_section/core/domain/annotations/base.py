"""Base classes for annotation system."""

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable

from ...geometry.bounds import BoundingBox
from ...geometry.primitives import Point2D


@dataclass
class AnnotationBase(ABC):
    """Abstract base class for all annotations.

    All annotation types must implement methods for:
    - Calculating bounding boxes (for collision detection)
    - Repositioning (for collision resolution)
    - SVG rendering (for export)

    Attributes:
        id: Unique identifier for this annotation
        layer: Layer name for organization (e.g., "dimensions", "labels", "symbols")
        priority: Priority for collision resolution (higher priority annotations
                  are less likely to be moved). Default is 0.
        metadata: Additional metadata for the annotation
    """

    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    layer: str = "default"
    priority: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    @abstractmethod
    def bounds(self) -> BoundingBox:
        """Calculate the bounding box of this annotation.

        Used for collision detection and spatial queries.

        Returns:
            Axis-aligned bounding box containing this annotation
        """
        pass

    @abstractmethod
    def reposition(self, offset: Point2D) -> "AnnotationBase":
        """Create a new annotation offset by the given amount.

        Used for collision resolution. Returns a new instance rather than
        modifying in place (immutable pattern).

        Args:
            offset: The offset to apply (dx=offset.x, dy=offset.y)

        Returns:
            New annotation instance offset by the given amount
        """
        pass

    @abstractmethod
    def to_svg_elements(self, transform: Callable[[Point2D], Point2D]) -> list[str]:
        """Convert this annotation to SVG element strings.

        Args:
            transform: Function to transform annotation coordinates to SVG coordinates.
                      Handles coordinate system conversion (e.g., Y-axis flip).

        Returns:
            List of SVG element strings (e.g., ["<text>...</text>", "<line>...</line>"])
        """
        pass

    def validate(self) -> list[str]:
        """Validate this annotation.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not self.id:
            errors.append("Annotation ID cannot be empty")

        if self.priority < 0:
            errors.append(f"Priority must be non-negative, got {self.priority}")

        return errors
