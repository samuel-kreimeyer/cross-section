"""Base classes for road components."""

from abc import ABC, abstractmethod
from typing import List, Literal
from ..geometry.primitives import ConnectionPoint, ComponentGeometry

# Type alias for assembly direction
Direction = Literal['left', 'right']


class RoadComponent(ABC):
    """Base class for all road cross-section components.

    Components snap together using insertion and attachment points:
    - Insertion point: Where this component begins (snaps to previous component's attachment)
    - Attachment point: Where the next component will connect (this component's outside edge)

    Components can be assembled in two directions from a control point:
    - Right: Extends in positive X direction (typical for right-side components)
    - Left: Extends in negative X direction (typical for left-side components)

    Each component creates its own geometry based on its specific attributes and
    the direction of assembly.
    """

    @abstractmethod
    def get_insertion_point(
        self, previous_attachment: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Calculate where this component begins.

        Args:
            previous_attachment: The attachment point from the previous component
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The insertion point for this component (typically same as previous_attachment)
        """
        pass

    @abstractmethod
    def get_attachment_point(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Calculate where the next component will attach.

        Args:
            insertion: This component's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The attachment point for the next component (this component's outside edge)
        """
        pass

    @abstractmethod
    def to_geometry(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ComponentGeometry:
        """Create this component's geometry.

        Args:
            insertion: This component's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The geometric representation of this component
        """
        pass

    @abstractmethod
    def validate(self) -> List[str]:
        """Validate this component's parameters.

        Returns:
            List of error messages (empty if valid)
        """
        pass
