"""Lane components."""

from dataclasses import dataclass
from typing import List, Literal
from ..base import RoadComponent
from ...geometry.primitives import ConnectionPoint, ComponentGeometry, Polygon, Point2D


@dataclass
class TravelLane(RoadComponent):
    """A travel lane for vehicular traffic.

    Attributes:
        width: Lane width in meters (typically 3.0-3.6m)
        cross_slope: Cross slope as ratio (e.g., 0.02 for 2%, positive slopes down away from crown)
        direction: Traffic flow direction ('inbound' or 'outbound')
        surface_type: Pavement surface type (default: 'asphalt')
    """

    width: float
    cross_slope: float = 0.02  # 2% default cross slope
    direction: Literal['inbound', 'outbound'] = 'outbound'
    surface_type: str = 'asphalt'

    def get_insertion_point(self, previous_attachment: ConnectionPoint) -> ConnectionPoint:
        """Lane snaps directly to previous component's attachment point.

        Args:
            previous_attachment: The attachment point from the previous component

        Returns:
            The insertion point (same as previous attachment for continuous assembly)
        """
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description=f"TravelLane insertion ({self.direction})"
        )

    def get_attachment_point(self, insertion: ConnectionPoint) -> ConnectionPoint:
        """Calculate the outside edge of the lane accounting for cross slope.

        Args:
            insertion: This lane's insertion point

        Returns:
            The attachment point at the lane's outside edge
        """
        # Cross slope creates vertical drop across the width
        drop = self.width * self.cross_slope

        return ConnectionPoint(
            x=insertion.x + self.width,
            y=insertion.y - drop,  # Negative because slope goes down
            description=f"TravelLane attachment ({self.direction})"
        )

    def to_geometry(self, insertion: ConnectionPoint) -> ComponentGeometry:
        """Create lane geometry as a rectangular polygon with cross slope.

        Args:
            insertion: This lane's insertion point

        Returns:
            ComponentGeometry with a single polygon representing the lane surface
        """
        attachment = self.get_attachment_point(insertion)

        # Create rectangular polygon with cross slope
        # Vertices in counter-clockwise order
        vertices = [
            Point2D(insertion.x, insertion.y),           # Inside, top
            Point2D(attachment.x, attachment.y),         # Outside, bottom (sloped down)
            Point2D(attachment.x, attachment.y - 0.2),   # Outside, bottom (with depth for visualization)
            Point2D(insertion.x, insertion.y - 0.2),     # Inside, bottom (with depth)
        ]

        polygon = Polygon(exterior=vertices)

        return ComponentGeometry(
            polygons=[polygon],
            metadata={
                'component_type': 'TravelLane',
                'width': self.width,
                'cross_slope': self.cross_slope,
                'direction': self.direction,
                'surface_type': self.surface_type
            }
        )

    def validate(self) -> List[str]:
        """Validate lane parameters.

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Width validation
        if self.width <= 0:
            errors.append("Lane width must be positive")
        elif self.width < 2.7:
            errors.append("Lane width below minimum standard (2.7m) - consider reviewing design")
        elif self.width > 4.0:
            errors.append("Lane width exceeds typical maximum (4.0m) - verify design intent")

        # Cross slope validation
        if abs(self.cross_slope) > 0.06:
            errors.append(f"Cross slope {self.cross_slope:.1%} exceeds typical maximum (6%) - verify design")
        elif abs(self.cross_slope) < 0.015:
            errors.append(f"Cross slope {self.cross_slope:.1%} below minimum for drainage (1.5%) - verify design")

        return errors
