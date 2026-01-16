"""Sidewalk components."""

from dataclasses import dataclass

from ...geometry.primitives import ComponentGeometry, ConnectionPoint, Point2D, Polygon
from ..base import Direction, RoadComponent
from ..pavement import ConcreteLayer


@dataclass
class Sidewalk(RoadComponent):
    """Concrete sidewalk slab."""

    width: float
    cross_slope: float = 0.02
    thickness: float = 0.10
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
            description=f"Sidewalk insertion ({direction})",
        )

    def get_attachment_point(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        drop = self.width * self.cross_slope
        x = insertion.x + self.width if direction == "right" else insertion.x - self.width
        y = insertion.y - drop
        return ConnectionPoint(x=x, y=y, description=f"Sidewalk attachment ({direction})")

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
                "component_type": "Sidewalk",
                "width": self.width,
                "cross_slope": self.cross_slope,
                "thickness": self.thickness,
                "assembly_direction": direction,
                "concrete_strength": self.concrete.compressive_strength,
            },
        )

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.width <= 0:
            errors.append("Sidewalk width must be positive")
        if self.thickness <= 0:
            errors.append("Sidewalk thickness must be positive")
        if abs(self.cross_slope) > 0.06:
            errors.append("Sidewalk cross slope exceeds typical maximum (6%)")
        if self.concrete is not None:
            errors.extend(self.concrete.validate())
        return errors
