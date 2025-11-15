"""Slope components for roadside features."""

from dataclasses import dataclass
from typing import List, Optional
from ..base import RoadComponent, Direction
from ...geometry.primitives import ConnectionPoint, ComponentGeometry, Polygon, Point2D


@dataclass
class Slope(RoadComponent):
    """A simple slope component.

    Represents a sloped surface from the insertion point, useful for foreslopes,
    backslopes, and other graded surfaces. Can be specified by slope ratio or
    by horizontal and vertical dimensions.

    Attributes:
        horizontal_run: Horizontal distance in meters
        vertical_drop: Vertical drop in meters (positive = down, negative = up)
        slope_ratio: Alternative to horizontal_run - H:V ratio (e.g., 4.0 for 4:1)
        surface_type: Type of surface ('grass', 'crushed_rock', 'bare_earth', etc.)
        thickness: Thickness of slope material if applicable (0 for just surface)
    """

    horizontal_run: Optional[float] = None
    vertical_drop: Optional[float] = None
    slope_ratio: Optional[float] = None  # H:V ratio (horizontal : vertical)
    surface_type: str = 'grass'
    thickness: float = 0.0  # Thickness of material (0 for surface only)

    def __post_init__(self):
        """Calculate missing parameters if ratio is provided."""
        if self.slope_ratio is not None and self.vertical_drop is not None:
            # Calculate horizontal run from ratio and vertical drop
            self.horizontal_run = abs(self.vertical_drop) * self.slope_ratio
        elif self.slope_ratio is not None and self.horizontal_run is not None:
            # Calculate vertical drop from ratio and horizontal run
            self.vertical_drop = self.horizontal_run / self.slope_ratio

        if self.horizontal_run is None or self.vertical_drop is None:
            raise ValueError(
                "Must specify either (horizontal_run and vertical_drop) or "
                "(slope_ratio with one dimension)"
            )

    def get_insertion_point(
        self, previous_attachment: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Slope snaps directly to previous component's attachment point.

        Args:
            previous_attachment: The attachment point from the previous component
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The insertion point (same as previous attachment)
        """
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description=f"Slope insertion ({direction})"
        )

    def get_attachment_point(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Calculate the end point of the slope.

        Args:
            insertion: This slope's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The attachment point at the end of the slope
        """
        attachment_y = insertion.y - self.vertical_drop

        if direction == 'right':
            return ConnectionPoint(
                x=insertion.x + self.horizontal_run,
                y=attachment_y,
                description=f"Slope attachment ({direction})"
            )
        else:  # left
            return ConnectionPoint(
                x=insertion.x - self.horizontal_run,
                y=attachment_y,
                description=f"Slope attachment ({direction})"
            )

    def to_geometry(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ComponentGeometry:
        """Create slope geometry.

        Creates a triangular or trapezoidal polygon representing the slope.
        If thickness is 0, creates a simple triangular surface.
        If thickness > 0, creates a trapezoid with material thickness.

        Args:
            insertion: This slope's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            ComponentGeometry with slope polygon
        """
        attachment = self.get_attachment_point(insertion, direction)

        if self.thickness == 0:
            # Simple surface line (represented as very thin polygon)
            if direction == 'right':
                vertices = [
                    Point2D(insertion.x, insertion.y),
                    Point2D(attachment.x, attachment.y),
                    Point2D(attachment.x, attachment.y - 0.01),  # Minimal thickness
                    Point2D(insertion.x, insertion.y - 0.01),
                ]
            else:  # left
                vertices = [
                    Point2D(insertion.x, insertion.y),
                    Point2D(insertion.x, insertion.y - 0.01),
                    Point2D(attachment.x, attachment.y - 0.01),
                    Point2D(attachment.x, attachment.y),
                ]
        else:
            # Material with thickness
            if direction == 'right':
                vertices = [
                    Point2D(insertion.x, insertion.y),  # Top inside
                    Point2D(attachment.x, attachment.y),  # Top outside
                    Point2D(attachment.x, attachment.y - self.thickness),  # Bottom outside
                    Point2D(insertion.x, insertion.y - self.thickness),  # Bottom inside
                ]
            else:  # left
                vertices = [
                    Point2D(insertion.x, insertion.y),  # Top inside
                    Point2D(insertion.x, insertion.y - self.thickness),  # Bottom inside
                    Point2D(attachment.x, attachment.y - self.thickness),  # Bottom outside
                    Point2D(attachment.x, attachment.y),  # Top outside
                ]

        polygon = Polygon(exterior=vertices)

        return ComponentGeometry(
            polygons=[polygon],
            metadata={
                'component_type': 'Slope',
                'horizontal_run': self.horizontal_run,
                'vertical_drop': self.vertical_drop,
                'slope_ratio': self.slope_ratio if self.slope_ratio else self.horizontal_run / abs(self.vertical_drop),
                'surface_type': self.surface_type,
                'thickness': self.thickness,
                'assembly_direction': direction,
            }
        )

    def validate(self) -> List[str]:
        """Validate slope parameters.

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        if self.horizontal_run <= 0:
            errors.append("Horizontal run must be positive")

        if abs(self.vertical_drop) <= 0:
            errors.append("Vertical drop must be non-zero")

        # Calculate actual slope ratio
        actual_ratio = self.horizontal_run / abs(self.vertical_drop)

        if actual_ratio < 1.0:
            errors.append(
                f"Slope ratio {actual_ratio:.1f}:1 is steeper than 1:1 - may be unsafe"
            )
        elif actual_ratio > 20.0:
            errors.append(
                f"Slope ratio {actual_ratio:.1f}:1 is very flat - verify design"
            )

        if self.thickness < 0:
            errors.append("Thickness must be non-negative")
        elif self.thickness > 1.0:
            errors.append(
                f"Thickness {self.thickness:.3f}m is very large - verify design"
            )

        return errors
