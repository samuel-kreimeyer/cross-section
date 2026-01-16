"""Surface-only components represented as polylines."""

from dataclasses import dataclass

from ...geometry.primitives import ComponentGeometry, ConnectionPoint, Point2D
from ..base import Direction, RoadComponent


@dataclass
class SurfaceProfile(RoadComponent):
    """Surface-only polyline defined by horizontal segments and vertical drops.

    Segments are defined as a sequence of (horizontal_run, vertical_drop) pairs.
    Positive vertical_drop indicates a drop (downward) in elevation.
    """

    segments: list[tuple[float, float]]
    surface_type: str = "grass"
    description: str = "Surface Profile"

    def get_insertion_point(
        self, previous_attachment: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description=f"SurfaceProfile insertion ({direction})",
        )

    def get_attachment_point(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        if not self.segments:
            return insertion

        total_run = sum(run for run, _ in self.segments)
        total_drop = sum(drop for _, drop in self.segments)
        x = insertion.x + total_run if direction == "right" else insertion.x - total_run
        y = insertion.y - total_drop
        return ConnectionPoint(x=x, y=y, description=f"SurfaceProfile attachment ({direction})")

    def to_geometry(self, insertion: ConnectionPoint, direction: Direction) -> ComponentGeometry:
        points = [Point2D(insertion.x, insertion.y)]
        current_x = insertion.x
        current_y = insertion.y

        for run, drop in self.segments:
            current_x = current_x + run if direction == "right" else current_x - run
            current_y = current_y - drop
            points.append(Point2D(current_x, current_y))

        return ComponentGeometry(
            polygons=[],
            polylines=[points],
            metadata={
                "component_type": "SurfaceProfile",
                "segments": self.segments,
                "surface_type": self.surface_type,
                "description": self.description,
                "assembly_direction": direction,
            },
        )

    def validate(self) -> list[str]:
        errors: list[str] = []
        if not self.segments:
            errors.append("Surface profile must include at least one segment")
            return errors

        for index, (run, _drop) in enumerate(self.segments):
            if run <= 0:
                errors.append(f"Segment {index} horizontal run must be positive")

        return errors


@dataclass
class Buffer(RoadComponent):
    """Buffer strip represented as a surface-only polyline."""

    width: float
    cross_slope: float = 0.0
    surface_type: str = "grass"

    def get_insertion_point(
        self, previous_attachment: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description=f"Buffer insertion ({direction})",
        )

    def get_attachment_point(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        drop = self.width * self.cross_slope
        x = insertion.x + self.width if direction == "right" else insertion.x - self.width
        y = insertion.y - drop
        return ConnectionPoint(x=x, y=y, description=f"Buffer attachment ({direction})")

    def to_geometry(self, insertion: ConnectionPoint, direction: Direction) -> ComponentGeometry:
        attachment = self.get_attachment_point(insertion, direction)
        line = [Point2D(insertion.x, insertion.y), Point2D(attachment.x, attachment.y)]
        return ComponentGeometry(
            polygons=[],
            polylines=[line],
            metadata={
                "component_type": "Buffer",
                "width": self.width,
                "cross_slope": self.cross_slope,
                "surface_type": self.surface_type,
                "assembly_direction": direction,
            },
        )

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.width <= 0:
            errors.append("Buffer width must be positive")
        if abs(self.cross_slope) > 0.2:
            errors.append("Buffer cross slope is unusually steep - verify design")
        return errors
