"""Shoring and temporary retaining wall components."""

from dataclasses import dataclass
from typing import List
from ..base import RoadComponent, Direction
from ...geometry.primitives import ConnectionPoint, ComponentGeometry, Polygon, Point2D


@dataclass
class Shoring(RoadComponent):
    """A temporary shoring wall component.

    Represents temporary shoring typically made of corrugated steel sheets.
    Shoring provides vertical or near-vertical separation between components
    and can be used in either fill or cut conditions.

    In fill condition, the shoring wall extends downward from the insertion point,
    with the attachment point at the bottom of the wall.

    In cut condition, the shoring wall extends upward from the insertion point,
    with the attachment point at the top of the wall.

    Attributes:
        height: Height of the shoring wall in meters (default 1.219m / 4 feet)
        thickness: Thickness of steel sheets in meters (default 0.203m / 8 inches)
        mode: 'fill' or 'cut' - determines if wall extends down or up (default 'fill')
    """

    height: float = 1.219  # 4 feet in meters
    thickness: float = 0.203  # 8 inches in meters
    mode: str = 'fill'  # 'fill' or 'cut'

    def get_insertion_point(
        self, previous_attachment: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Shoring snaps directly to previous component's attachment point.

        In fill mode, this is the top of the shoring wall.
        In cut mode, this is the bottom of the shoring wall.

        Args:
            previous_attachment: The attachment point from the previous component
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The insertion point (same as previous attachment)
        """
        mode_description = "top" if self.mode == 'fill' else "bottom"
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description=f"Shoring insertion ({mode_description}, {direction})"
        )

    def get_attachment_point(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Calculate the attachment point of the shoring wall.

        In fill mode: attachment is at the bottom, offset horizontally by thickness.
        In cut mode: attachment is at the top, offset horizontally by thickness.

        Args:
            insertion: This shoring's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The attachment point for the next component
        """
        if self.mode == 'fill':
            # Fill: attachment is at bottom (down from insertion)
            attachment_y = insertion.y - self.height
        else:  # cut
            # Cut: attachment is at top (up from insertion)
            attachment_y = insertion.y + self.height

        if direction == 'right':
            return ConnectionPoint(
                x=insertion.x + self.thickness,
                y=attachment_y,
                description=f"Shoring attachment ({self.mode}, {direction})"
            )
        else:  # left
            return ConnectionPoint(
                x=insertion.x - self.thickness,
                y=attachment_y,
                description=f"Shoring attachment ({self.mode}, {direction})"
            )

    def to_geometry(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ComponentGeometry:
        """Create shoring wall geometry as a rectangular polygon.

        The geometry represents the corrugated steel sheet wall as a solid
        rectangle. Future enhancements may add hatching patterns to indicate
        the temporary/corrugated nature of the material.

        Args:
            insertion: This shoring's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            ComponentGeometry with a single polygon representing the shoring wall
        """
        attachment = self.get_attachment_point(insertion, direction)

        if self.mode == 'fill':
            # Fill: wall extends downward from insertion point
            if direction == 'right':
                vertices = [
                    Point2D(insertion.x, insertion.y),  # Top inside
                    Point2D(insertion.x + self.thickness, insertion.y),  # Top outside
                    Point2D(insertion.x + self.thickness, insertion.y - self.height),  # Bottom outside
                    Point2D(insertion.x, insertion.y - self.height),  # Bottom inside
                ]
            else:  # left
                vertices = [
                    Point2D(insertion.x, insertion.y),  # Top inside
                    Point2D(insertion.x, insertion.y - self.height),  # Bottom inside
                    Point2D(insertion.x - self.thickness, insertion.y - self.height),  # Bottom outside
                    Point2D(insertion.x - self.thickness, insertion.y),  # Top outside
                ]
        else:  # cut
            # Cut: wall extends upward from insertion point
            if direction == 'right':
                vertices = [
                    Point2D(insertion.x, insertion.y),  # Bottom inside
                    Point2D(insertion.x + self.thickness, insertion.y),  # Bottom outside
                    Point2D(insertion.x + self.thickness, insertion.y + self.height),  # Top outside
                    Point2D(insertion.x, insertion.y + self.height),  # Top inside
                ]
            else:  # left
                vertices = [
                    Point2D(insertion.x, insertion.y),  # Bottom inside
                    Point2D(insertion.x, insertion.y + self.height),  # Top inside
                    Point2D(insertion.x - self.thickness, insertion.y + self.height),  # Top outside
                    Point2D(insertion.x - self.thickness, insertion.y),  # Bottom outside
                ]

        polygon = Polygon(exterior=vertices)

        return ComponentGeometry(
            polygons=[polygon],
            metadata={
                'component_type': 'Shoring',
                'height': self.height,
                'thickness': self.thickness,
                'mode': self.mode,
                'assembly_direction': direction,
                'material': 'corrugated_steel',
            }
        )

    def validate(self) -> List[str]:
        """Validate shoring parameters.

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Height validation
        if self.height <= 0:
            errors.append("Height must be positive")
        elif self.height < 0.3:
            errors.append(
                f"Height {self.height:.3f}m is very short for shoring - verify design"
            )
        elif self.height > 15.0:
            errors.append(
                f"Height {self.height:.3f}m exceeds typical maximum for sheet pile shoring (15m) - "
                "may require special engineering"
            )

        # Thickness validation
        if self.thickness <= 0:
            errors.append("Thickness must be positive")
        elif self.thickness < 0.05:
            errors.append(
                f"Thickness {self.thickness:.3f}m is very thin - verify design"
            )
        elif self.thickness > 0.5:
            errors.append(
                f"Thickness {self.thickness:.3f}m is very large for steel sheet pile - verify design"
            )

        # Mode validation
        if self.mode not in ['fill', 'cut']:
            errors.append(f"Mode must be 'fill' or 'cut', got '{self.mode}'")

        return errors
