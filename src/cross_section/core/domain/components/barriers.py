"""Barrier components with dimensionally accurate profiles."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from ...geometry.primitives import ComponentGeometry, ConnectionPoint, Point2D, Polygon
from ..base import Direction, RoadComponent
from ..pavement import PavementLayer

BarrierRigidity = Literal["rigid", "semi_rigid"]
BarrierKind = Literal["concrete", "guardrail", "cable"]

INCH_TO_M = 0.0254


def inches(value: float) -> float:
    """Convert inches to meters."""
    return value * INCH_TO_M


@dataclass(frozen=True)
class ConcreteBarrierSpec:
    """Concrete barrier profile definition."""

    name: str
    rigidity: BarrierRigidity
    base_width: float
    height: float
    profile_points: list[Point2D]

    @property
    def kind(self) -> BarrierKind:
        return "concrete"

    @property
    def footprint_width(self) -> float:
        return self.base_width

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.base_width <= 0:
            errors.append("Concrete barrier base width must be positive")
        if self.height <= 0:
            errors.append("Concrete barrier height must be positive")
        if not self.profile_points:
            errors.append("Concrete barrier profile points are required")
        return errors


@dataclass(frozen=True)
class GuardrailSpec:
    """Guardrail profile definition (block-out W-beam style)."""

    name: str
    rigidity: BarrierRigidity
    post_height: float
    post_width: float
    post_embed_depth: float
    block_width: float
    block_height: float
    rail_height: float
    rail_width: float

    @property
    def kind(self) -> BarrierKind:
        return "guardrail"

    @property
    def footprint_width(self) -> float:
        return self.block_width + self.post_width

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.post_height <= 0:
            errors.append("Guardrail post height must be positive")
        if self.post_width <= 0:
            errors.append("Guardrail post width must be positive")
        if self.post_embed_depth <= 0:
            errors.append("Guardrail post embed depth must be positive")
        if self.block_width <= 0 or self.block_height <= 0:
            errors.append("Guardrail block dimensions must be positive")
        if self.rail_height <= 0:
            errors.append("Guardrail rail height must be positive")
        if self.rail_width <= 0:
            errors.append("Guardrail rail width must be positive")
        return errors


@dataclass(frozen=True)
class CableBarrierSpec:
    """Cable barrier profile definition (post + cable holes)."""

    name: str
    rigidity: BarrierRigidity
    post_height: float
    post_width: float
    post_embed_depth: float
    hole_diameter: float
    hole_count: int
    hole_offset_top: float
    hole_offset_bottom: float

    @property
    def kind(self) -> BarrierKind:
        return "cable"

    @property
    def footprint_width(self) -> float:
        return self.post_width

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.post_height <= 0:
            errors.append("Cable barrier post height must be positive")
        if self.post_width <= 0:
            errors.append("Cable barrier post width must be positive")
        if self.post_embed_depth <= 0:
            errors.append("Cable barrier post embed depth must be positive")
        if self.hole_diameter <= 0:
            errors.append("Cable barrier hole diameter must be positive")
        if self.hole_count < 1:
            errors.append("Cable barrier hole count must be at least 1")
        if self.hole_offset_top < 0 or self.hole_offset_bottom < 0:
            errors.append("Cable barrier hole offsets must be non-negative")
        return errors


BarrierSpec = ConcreteBarrierSpec | GuardrailSpec | CableBarrierSpec


def _jersey_32_profile_points() -> list[Point2D]:
    """Return two-sided Jersey barrier profile points (32 in tall)."""
    toe_height = inches(3)
    bottom_slope_width = inches(7)
    bottom_slope_height = inches(10)
    upper_slope_width = inches(2)
    upper_slope_height = inches(19)
    base_width = inches(24)
    top_width = inches(6)
    height = inches(32)

    # Left face points (from left base moving up)
    left_top_x = (base_width - top_width) / 2.0
    left_top_y = toe_height + bottom_slope_height + upper_slope_height
    right_top_x = base_width - left_top_x
    right_break_x = base_width - bottom_slope_width

    return [
        Point2D(0.0, 0.0),
        Point2D(0.0, toe_height),
        Point2D(bottom_slope_width, toe_height + bottom_slope_height),
        Point2D(left_top_x, left_top_y),
        Point2D(right_top_x, height),
        Point2D(right_break_x, toe_height + bottom_slope_height),
        Point2D(base_width, toe_height),
        Point2D(base_width, 0.0),
    ]


JERSEY_32 = ConcreteBarrierSpec(
    name="jersey_32",
    rigidity="rigid",
    base_width=inches(24),
    height=inches(32),
    profile_points=_jersey_32_profile_points(),
)

W_BEAM_BLOCKOUT = GuardrailSpec(
    name="w_beam_blockout",
    rigidity="semi_rigid",
    post_height=inches(32),
    post_width=inches(9),
    post_embed_depth=inches(40),
    block_width=inches(8),
    block_height=inches(14),
    rail_height=inches(14),
    rail_width=inches(3),
)

CABLE_3_STRAND = CableBarrierSpec(
    name="cable_3_strand",
    rigidity="semi_rigid",
    post_height=inches(32),
    post_width=inches(4),
    post_embed_depth=inches(36),
    hole_diameter=inches(1),
    hole_count=3,
    hole_offset_top=inches(3),
    hole_offset_bottom=inches(20),
)


@dataclass
class Barrier(RoadComponent):
    """Barrier component with prepared surface and overlay geometry."""

    spec: BarrierSpec
    front_prepared_width: float
    back_prepared_width: float | None = None
    two_sided: bool = False
    prepared_layers: list[PavementLayer] = field(default_factory=list)
    foundation_layers: list[PavementLayer] = field(default_factory=list)
    back_surface_delta: float = 0.0
    embed_depth: float = 0.0

    def __post_init__(self) -> None:
        if self.back_prepared_width is None:
            self.back_prepared_width = (
                self.front_prepared_width if self.two_sided else 0.0
            )

    def get_insertion_point(
        self, previous_attachment: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Barrier snaps to previous component's attachment point."""
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description=f"Barrier insertion ({direction})",
        )

    def get_attachment_point(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Return attachment at the end of the prepared surface."""
        total_width = self._total_width()
        x = insertion.x + total_width if direction == "right" else insertion.x - total_width
        y = insertion.y + self.back_surface_delta
        return ConnectionPoint(x=x, y=y, description=f"Barrier attachment ({direction})")

    def to_geometry(self, insertion: ConnectionPoint, direction: Direction) -> ComponentGeometry:
        """Create barrier geometry with prepared surface and overlay features."""
        polygons: list[Polygon] = []
        polylines: list[list[Point2D]] = []

        total_width = self._total_width()

        # Prepared surface (single unit across front + barrier + back)
        if self.prepared_layers:
            polygons.extend(
                self._build_layers(
                    insertion,
                    direction,
                    0.0,
                    total_width,
                    self.prepared_layers,
                )
            )

        # Foundation layers (under barrier footprint only)
        if self.foundation_layers:
            start = self.front_prepared_width
            end = self.front_prepared_width + self.spec.footprint_width
            polygons.extend(
                self._build_layers(
                    insertion,
                    direction,
                    start,
                    end,
                    self.foundation_layers,
                )
            )

        # Barrier body
        if isinstance(self.spec, ConcreteBarrierSpec):
            polygons.append(self._build_concrete_polygon(insertion, direction, total_width))
        elif isinstance(self.spec, GuardrailSpec):
            guardrail_polys, guardrail_lines = self._build_guardrail(insertion, direction)
            polygons.extend(guardrail_polys)
            polylines.extend(guardrail_lines)
        elif isinstance(self.spec, CableBarrierSpec):
            cable_polys, cable_lines = self._build_cable_barrier(insertion, direction)
            polygons.extend(cable_polys)
            polylines.extend(cable_lines)

        return ComponentGeometry(
            polygons=polygons,
            polylines=polylines,
            metadata={
                "component_type": "Barrier",
                "spec": self.spec.name,
                "kind": self.spec.kind,
                "rigidity": self.spec.rigidity,
                "front_prepared_width": self.front_prepared_width,
                "back_prepared_width": self.back_prepared_width,
                "two_sided": self.two_sided,
                "footprint_width": self.spec.footprint_width,
                "back_surface_delta": self.back_surface_delta,
                "embed_depth": self.embed_depth,
            },
        )

    def validate(self) -> list[str]:
        """Validate barrier dimensions and spec definitions."""
        errors: list[str] = []

        if self.front_prepared_width < 0:
            errors.append("Barrier front prepared width must be non-negative")
        if self.back_prepared_width is None or self.back_prepared_width < 0:
            errors.append("Barrier back prepared width must be non-negative")
        if self.spec.footprint_width <= 0:
            errors.append("Barrier footprint width must be positive")

        errors.extend(self.spec.validate())

        for layer in self.prepared_layers:
            errors.extend(layer.validate())
        for layer in self.foundation_layers:
            errors.extend(layer.validate())

        return errors

    def _total_width(self) -> float:
        return (
            self.front_prepared_width
            + self.spec.footprint_width
            + (self.back_prepared_width or 0.0)
        )

    def _surface_y(self, insertion: ConnectionPoint, distance: float, total_width: float) -> float:
        if total_width <= 0:
            return insertion.y
        return insertion.y + (distance / total_width) * self.back_surface_delta

    def _x_at(self, insertion: ConnectionPoint, direction: Direction, distance: float) -> float:
        return insertion.x + distance if direction == "right" else insertion.x - distance

    def _build_layers(
        self,
        insertion: ConnectionPoint,
        direction: Direction,
        start: float,
        end: float,
        layers: list[PavementLayer],
    ) -> list[Polygon]:
        total_width = self._total_width()
        polygons: list[Polygon] = []
        current_depth = 0.0

        for layer in layers:
            top_depth = current_depth
            bottom_depth = current_depth + layer.thickness

            x0 = self._x_at(insertion, direction, start)
            x1 = self._x_at(insertion, direction, end)
            y0_top = self._surface_y(insertion, start, total_width) - top_depth
            y1_top = self._surface_y(insertion, end, total_width) - top_depth
            y0_bottom = self._surface_y(insertion, start, total_width) - bottom_depth
            y1_bottom = self._surface_y(insertion, end, total_width) - bottom_depth

            if direction == "right":
                vertices = [
                    Point2D(x0, y0_top),
                    Point2D(x1, y1_top),
                    Point2D(x1, y1_bottom),
                    Point2D(x0, y0_bottom),
                ]
            else:
                vertices = [
                    Point2D(x0, y0_top),
                    Point2D(x0, y0_bottom),
                    Point2D(x1, y1_bottom),
                    Point2D(x1, y1_top),
                ]

            polygons.append(Polygon(exterior=vertices))
            current_depth = bottom_depth

        return polygons

    def _build_concrete_polygon(
        self, insertion: ConnectionPoint, direction: Direction, total_width: float
    ) -> Polygon:
        base_offset = self.front_prepared_width
        points: list[Point2D] = []

        for point in self.spec.profile_points:
            distance = base_offset + point.x
            x = self._x_at(insertion, direction, distance)
            base_y = self._surface_y(insertion, distance, total_width) - self.embed_depth
            y = base_y + point.y
            points.append(Point2D(x, y))

        if direction == "left":
            points.reverse()

        return Polygon(exterior=points)

    def _build_guardrail(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> tuple[list[Polygon], list[list[Point2D]]]:
        spec = self.spec
        assert isinstance(spec, GuardrailSpec)

        total_width = self._total_width()
        base_offset = self.front_prepared_width

        block_face = base_offset
        block_back = block_face + spec.block_width
        post_back = block_back + spec.post_width

        polygons: list[Polygon] = []
        polylines: list[list[Point2D]] = []

        # Block polygon
        block_bottom_offset = spec.post_height - spec.block_height
        polygons.append(
            self._rect_polygon(
                insertion,
                direction,
                block_face,
                block_back,
                block_bottom_offset,
                block_bottom_offset + spec.block_height,
                total_width,
            )
        )

        # Post polygon (extends below surface)
        post_poly = self._rect_polygon(
            insertion,
            direction,
            block_back,
            post_back,
            -spec.post_embed_depth,
            spec.post_height,
            total_width,
        )
        polygons.append(post_poly)

        # W-beam profile on traffic-facing side of block
        rail_polyline = self._build_w_beam_polyline(
            insertion,
            direction,
            block_face,
            total_width,
            block_bottom_offset,
            spec,
        )
        polylines.append(rail_polyline)

        return polygons, polylines

    def _build_cable_barrier(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> tuple[list[Polygon], list[list[Point2D]]]:
        spec = self.spec
        assert isinstance(spec, CableBarrierSpec)

        total_width = self._total_width()
        base_offset = self.front_prepared_width
        post_back = base_offset + spec.post_width

        polygons: list[Polygon] = []
        polylines: list[list[Point2D]] = []

        # Post polygon with cable holes (holes are stored for future exporters)
        post_poly = self._rect_polygon(
            insertion,
            direction,
            base_offset,
            post_back,
            -spec.post_embed_depth,
            spec.post_height,
            total_width,
        )

        hole_centers = self._cable_hole_centers(
            insertion, direction, spec, base_offset, total_width
        )
        hole_radius = spec.hole_diameter / 2.0
        holes = [self._circle_points(center, hole_radius) for center in hole_centers]

        if holes:
            post_poly = Polygon(exterior=post_poly.exterior, holes=holes)

        polygons.append(post_poly)

        for hole in holes:
            polylines.append(hole + [hole[0]])

        return polygons, polylines

    def _rect_polygon(
        self,
        insertion: ConnectionPoint,
        direction: Direction,
        start: float,
        end: float,
        bottom_offset: float,
        height: float,
        total_width: float,
    ) -> Polygon:
        x0 = self._x_at(insertion, direction, start)
        x1 = self._x_at(insertion, direction, end)
        y0_surface = self._surface_y(insertion, start, total_width)
        y1_surface = self._surface_y(insertion, end, total_width)

        y0_bottom = y0_surface + bottom_offset
        y1_bottom = y1_surface + bottom_offset
        y0_top = y0_surface + height
        y1_top = y1_surface + height

        if direction == "right":
            vertices = [
                Point2D(x0, y0_top),
                Point2D(x1, y1_top),
                Point2D(x1, y1_bottom),
                Point2D(x0, y0_bottom),
            ]
        else:
            vertices = [
                Point2D(x0, y0_top),
                Point2D(x0, y0_bottom),
                Point2D(x1, y1_bottom),
                Point2D(x1, y1_top),
            ]

        return Polygon(exterior=vertices)

    def _cable_hole_centers(
        self,
        insertion: ConnectionPoint,
        direction: Direction,
        spec: CableBarrierSpec,
        base_offset: float,
        total_width: float,
    ) -> list[Point2D]:
        face_offset = spec.post_width * 0.25
        x_center = self._x_at(insertion, direction, base_offset + face_offset)
        surface_y = self._surface_y(insertion, base_offset, total_width)
        top_y = surface_y + spec.post_height
        bottom_y = surface_y
        top_center = top_y - spec.hole_offset_top
        bottom_center = bottom_y + spec.hole_offset_bottom

        if spec.hole_count == 1:
            centers_y = [top_center]
        else:
            spacing = (top_center - bottom_center) / (spec.hole_count - 1)
            centers_y = [top_center - i * spacing for i in range(spec.hole_count)]

        return [Point2D(x_center, y) for y in centers_y]

    def _circle_points(self, center: Point2D, radius: float, segments: int = 12) -> list[Point2D]:
        import math

        points = []
        for i in range(segments):
            angle = (2 * math.pi * i) / segments
            points.append(
                Point2D(
                    center.x + radius * math.cos(angle),
                    center.y + radius * math.sin(angle),
                )
            )
        return points

    def _build_w_beam_polyline(
        self,
        insertion: ConnectionPoint,
        direction: Direction,
        block_face: float,
        total_width: float,
        block_bottom_offset: float,
        spec: GuardrailSpec,
    ) -> list[Point2D]:
        x_face = self._x_at(insertion, direction, block_face)
        traffic_sign = -1 if direction == "right" else 1
        x_bulge = x_face + (traffic_sign * spec.rail_width)

        surface_y = self._surface_y(insertion, block_face, total_width)
        y_bottom = surface_y + block_bottom_offset
        y_top = y_bottom + spec.rail_height
        y_mid = (y_bottom + y_top) / 2.0
        y_low_bulge = y_bottom + (spec.rail_height * 0.25)
        y_high_bulge = y_bottom + (spec.rail_height * 0.75)

        return [
            Point2D(x_face, y_bottom),
            Point2D(x_bulge, y_low_bulge),
            Point2D(x_face, y_mid),
            Point2D(x_bulge, y_high_bulge),
            Point2D(x_face, y_top),
        ]
