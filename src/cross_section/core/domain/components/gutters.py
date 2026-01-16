"""Gutter components."""

from dataclasses import dataclass

from ...geometry.primitives import ComponentGeometry, ConnectionPoint, Point2D, Polygon
from ..base import Direction, RoadComponent
from ..pavement import ConcreteLayer


@dataclass
class Gutter(RoadComponent):
    """A gutter pan component.

    The gutter slopes downward from the insertion point to the flowline.
    """

    width: float
    drop: float = 0.025
    thickness: float = 0.15
    concrete: ConcreteLayer | None = None

    def __post_init__(self) -> None:
        if self.concrete is None:
            self.concrete = ConcreteLayer(
                thickness=self.thickness,
                compressive_strength=28.0,
                reinforced=False,
                steel_per_cy=None,
            )

    def get_insertion_point(
        self, previous_attachment: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description=f"Gutter insertion ({direction})",
        )

    def get_attachment_point(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        y = insertion.y - self.drop
        x = insertion.x + self.width if direction == "right" else insertion.x - self.width
        return ConnectionPoint(x=x, y=y, description=f"Gutter attachment ({direction})")

    def to_geometry(self, insertion: ConnectionPoint, direction: Direction) -> ComponentGeometry:
        attachment = self.get_attachment_point(insertion, direction)
        bottom_inside = insertion.y - self.thickness
        bottom_outside = attachment.y - self.thickness

        if direction == "right":
            vertices = [
                Point2D(insertion.x, insertion.y),
                Point2D(attachment.x, attachment.y),
                Point2D(attachment.x, bottom_outside),
                Point2D(insertion.x, bottom_inside),
            ]
        else:
            vertices = [
                Point2D(insertion.x, insertion.y),
                Point2D(insertion.x, bottom_inside),
                Point2D(attachment.x, bottom_outside),
                Point2D(attachment.x, attachment.y),
            ]

        polygon = Polygon(exterior=vertices)
        assert self.concrete is not None  # nosec B101

        return ComponentGeometry(
            polygons=[polygon],
            metadata={
                "component_type": "Gutter",
                "width": self.width,
                "drop": self.drop,
                "thickness": self.thickness,
                "assembly_direction": direction,
                "concrete_strength": self.concrete.compressive_strength,
            },
        )

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.width <= 0:
            errors.append("Gutter width must be positive")
        if self.thickness <= 0:
            errors.append("Gutter thickness must be positive")
        if self.drop < 0:
            errors.append("Gutter drop must be non-negative")
        if self.drop > self.thickness:
            errors.append("Gutter drop exceeds gutter thickness")
        if self.concrete is not None:
            errors.extend(self.concrete.validate())
        return errors
