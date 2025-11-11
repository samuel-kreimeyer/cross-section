"""Lane components."""

from dataclasses import dataclass
from typing import List, Literal
from ..base import RoadComponent, Direction
from ...geometry.primitives import ConnectionPoint, ComponentGeometry, Polygon, Point2D


@dataclass
class TravelLane(RoadComponent):
    """A travel lane for vehicular traffic.

    Attributes:
        width: Lane width in meters (typically 3.0-3.6m)
        cross_slope: Cross slope as ratio (e.g., 0.02 for 2%, positive slopes down away from crown)
        traffic_direction: Traffic flow direction ('inbound' or 'outbound')
        surface_type: Pavement surface type (default: 'asphalt')
    """

    width: float
    cross_slope: float = 0.02  # 2% default cross slope
    traffic_direction: Literal['inbound', 'outbound'] = 'outbound'
    surface_type: str = 'asphalt'

    def get_insertion_point(
        self, previous_attachment: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Lane snaps directly to previous component's attachment point.

        Args:
            previous_attachment: The attachment point from the previous component
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The insertion point (same as previous attachment for continuous assembly)
        """
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description=f"TravelLane insertion ({direction}, {self.traffic_direction})"
        )

    def get_attachment_point(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Calculate the outside edge of the lane accounting for cross slope.

        Args:
            insertion: This lane's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The attachment point at the lane's outside edge
        """
        # Cross slope creates vertical drop across the width
        # Positive cross_slope means it slopes DOWN away from crown
        drop = self.width * self.cross_slope

        # For right-side: extends in +X direction, slopes down
        # For left-side: extends in -X direction, slopes down
        if direction == 'right':
            return ConnectionPoint(
                x=insertion.x + self.width,
                y=insertion.y - drop,  # Slopes down away from crown
                description=f"TravelLane attachment ({direction}, {self.traffic_direction})"
            )
        else:  # left
            return ConnectionPoint(
                x=insertion.x - self.width,
                y=insertion.y - drop,  # Also slopes down away from crown
                description=f"TravelLane attachment ({direction}, {self.traffic_direction})"
            )

    def to_geometry(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ComponentGeometry:
        """Create lane geometry as a rectangular polygon with cross slope.

        Args:
            insertion: This lane's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            ComponentGeometry with a single polygon representing the lane surface
        """
        attachment = self.get_attachment_point(insertion, direction)

        # Create rectangular polygon with cross slope
        # Vertices in counter-clockwise order
        if direction == 'right':
            vertices = [
                Point2D(insertion.x, insertion.y),           # Inside (crown side), top
                Point2D(attachment.x, attachment.y),         # Outside, bottom (sloped down)
                Point2D(attachment.x, attachment.y - 0.2),   # Outside, bottom (with depth)
                Point2D(insertion.x, insertion.y - 0.2),     # Inside, bottom (with depth)
            ]
        else:  # left
            vertices = [
                Point2D(insertion.x, insertion.y),           # Inside (crown side), top
                Point2D(insertion.x, insertion.y - 0.2),     # Inside, bottom (with depth)
                Point2D(attachment.x, attachment.y - 0.2),   # Outside, bottom (with depth)
                Point2D(attachment.x, attachment.y),         # Outside, bottom (sloped down)
            ]

        polygon = Polygon(exterior=vertices)

        return ComponentGeometry(
            polygons=[polygon],
            metadata={
                'component_type': 'TravelLane',
                'width': self.width,
                'cross_slope': self.cross_slope,
                'assembly_direction': direction,
                'traffic_direction': self.traffic_direction,
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
