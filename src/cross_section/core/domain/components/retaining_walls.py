"""Retaining wall components with shared cross-section behavior."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from ...geometry.primitives import ComponentGeometry, ConnectionPoint, Point2D, Polygon
from ..base import Direction, RoadComponent

WallMode = Literal["fill", "cut"]

INCH_TO_M = 0.0254
FOOT_TO_M = 0.3048


def inches(value: float) -> float:
    """Convert inches to meters."""
    return value * INCH_TO_M


def feet(value: float) -> float:
    """Convert feet to meters."""
    return value * FOOT_TO_M


@dataclass
class RetainingWall(RoadComponent):
    """Parametric retaining wall with optional backfill wedge.

    The wall uses a consistent fit with the cross-section chain. In fill mode,
    the wall inserts at the top/back (soil side) and attaches at the front
    grade point. In cut mode, the wall inserts at the front grade point and
    attaches at the top/back.
    """

    height: float = feet(4)
    thickness: float = feet(1)
    mode: WallMode = "fill"
    cover_depth: float = feet(2)
    foundation_thickness: float = feet(1)
    foundation_front: float = feet(2)
    foundation_back: float = feet(2)
    show_backfill: bool = True
    backfill_slope_ratio: float = 2.0
    backfill_height: float | None = None

    def get_insertion_point(
        self, previous_attachment: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        if self.mode == "fill":
            description = "Retaining wall insertion (top/back)"
        else:
            description = "Retaining wall insertion (front/grade)"
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description=f"{description}, {direction}",
        )

    def get_attachment_point(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        context = self._wall_context(insertion, direction)
        if self.mode == "fill":
            attachment_x = context.front_face_x
            attachment_y = context.grade_y
            description = "Retaining wall attachment (front/grade)"
        else:
            attachment_x = context.back_face_x
            attachment_y = context.top_y
            description = "Retaining wall attachment (top/back)"
        return ConnectionPoint(
            x=attachment_x,
            y=attachment_y,
            description=f"{description}, {direction}",
        )

    def to_geometry(self, insertion: ConnectionPoint, direction: Direction) -> ComponentGeometry:
        context = self._wall_context(insertion, direction)
        polygons: list[Polygon] = []

        wall_polygon = self._wall_polygon(context)
        polygons.append(wall_polygon)

        foundation_polygon = self._foundation_polygon(context)
        polygons.append(foundation_polygon)

        if self.show_backfill:
            polygons.append(self._backfill_polygon(context))

        overlap_allow = [2] if self.show_backfill else []

        return ComponentGeometry(
            polygons=polygons,
            metadata={
                "component_type": "RetainingWall",
                "height": self.height,
                "thickness": self.thickness,
                "mode": self.mode,
                "cover_depth": self.cover_depth,
                "foundation_thickness": self.foundation_thickness,
                "foundation_front": self.foundation_front,
                "foundation_back": self.foundation_back,
                "show_backfill": self.show_backfill,
                "backfill_slope_ratio": self.backfill_slope_ratio,
                "overlap_allow_polygons": overlap_allow,
            },
        )

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.height <= 0:
            errors.append("Wall height must be positive")
        if self.thickness <= 0:
            errors.append("Wall thickness must be positive")
        if self.cover_depth < 0:
            errors.append("Cover depth must be non-negative")
        if self.foundation_thickness <= 0:
            errors.append("Foundation thickness must be positive")
        if self.foundation_front < 0 or self.foundation_back < 0:
            errors.append("Foundation extensions must be non-negative")
        if self.backfill_slope_ratio <= 0:
            errors.append("Backfill slope ratio must be positive")
        if self.mode not in ("fill", "cut"):
            errors.append(f"Mode must be 'fill' or 'cut', got '{self.mode}'")
        return errors

    def _wall_context(self, insertion: ConnectionPoint, direction: Direction) -> "_WallContext":
        direction_sign = 1.0 if direction == "right" else -1.0
        if self.mode == "fill":
            front_sign = direction_sign
            top_y = insertion.y
            grade_y = insertion.y - self.height
            back_face_x = insertion.x
            front_face_x = insertion.x + (front_sign * self.thickness)
        else:
            front_sign = -direction_sign
            grade_y = insertion.y
            top_y = insertion.y + self.height
            front_face_x = insertion.x
            back_face_x = insertion.x - (front_sign * self.thickness)

        foundation_top_y = grade_y - self.cover_depth
        foundation_bottom_y = foundation_top_y - self.foundation_thickness

        backfill_height = self.backfill_height
        if backfill_height is None:
            backfill_height = self.height

        return _WallContext(
            direction=direction,
            front_sign=front_sign,
            front_face_x=front_face_x,
            back_face_x=back_face_x,
            top_y=top_y,
            grade_y=grade_y,
            foundation_top_y=foundation_top_y,
            foundation_bottom_y=foundation_bottom_y,
            backfill_height=backfill_height,
        )

    def _wall_polygon(self, context: "_WallContext") -> Polygon:
        if context.direction == "right":
            vertices = [
                Point2D(context.front_face_x, context.top_y),
                Point2D(context.back_face_x, context.top_y),
                Point2D(context.back_face_x, context.foundation_top_y),
                Point2D(context.front_face_x, context.foundation_top_y),
            ]
        else:
            vertices = [
                Point2D(context.front_face_x, context.top_y),
                Point2D(context.front_face_x, context.foundation_top_y),
                Point2D(context.back_face_x, context.foundation_top_y),
                Point2D(context.back_face_x, context.top_y),
            ]
        return Polygon(exterior=vertices)

    def _foundation_polygon(self, context: "_WallContext") -> Polygon:
        front_ext = context.front_face_x + (context.front_sign * self.foundation_front)
        back_ext = context.back_face_x - (context.front_sign * self.foundation_back)

        if context.direction == "right":
            vertices = [
                Point2D(front_ext, context.foundation_top_y),
                Point2D(back_ext, context.foundation_top_y),
                Point2D(back_ext, context.foundation_bottom_y),
                Point2D(front_ext, context.foundation_bottom_y),
            ]
        else:
            vertices = [
                Point2D(front_ext, context.foundation_top_y),
                Point2D(front_ext, context.foundation_bottom_y),
                Point2D(back_ext, context.foundation_bottom_y),
                Point2D(back_ext, context.foundation_top_y),
            ]
        return Polygon(exterior=vertices)

    def _backfill_polygon(self, context: "_WallContext") -> Polygon:
        back_sign = -context.front_sign
        run = self.backfill_slope_ratio * context.backfill_height
        slope_x = context.back_face_x + (back_sign * run)
        slope_y = context.top_y - context.backfill_height

        if context.direction == "right":
            vertices = [
                Point2D(context.back_face_x, context.top_y),
                Point2D(slope_x, slope_y),
                Point2D(context.back_face_x, context.grade_y),
            ]
        else:
            vertices = [
                Point2D(context.back_face_x, context.top_y),
                Point2D(context.back_face_x, context.grade_y),
                Point2D(slope_x, slope_y),
            ]
        return Polygon(exterior=vertices)


@dataclass
class MSEWall(RoadComponent):
    """MSE retaining wall with vertical panel and coping."""

    height: float = feet(4)
    mode: WallMode = "fill"
    cover_depth: float = feet(2)
    panel_thickness: float = inches(6)
    foundation_width: float = feet(2)
    foundation_thickness: float = feet(1)
    coping_width: float = inches(18)
    coping_above: float = inches(9)
    coping_below: float = inches(11)
    show_backfill: bool = True
    structural_fill_min_width: float = feet(8)
    structural_fill_slope_ratio: float = 0.0
    structural_fill_hatch_spacing: float = feet(0.5)
    backfill_height: float | None = None

    def get_insertion_point(
        self, previous_attachment: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        if self.mode == "fill":
            direction_sign = 1.0 if direction == "right" else -1.0
            insertion_x = previous_attachment.x - (direction_sign * self.coping_width)
            description = "MSE wall insertion (top/back)"
        else:
            insertion_x = previous_attachment.x
            description = "MSE wall insertion (front/grade)"
        return ConnectionPoint(
            x=insertion_x,
            y=previous_attachment.y,
            description=f"{description}, {direction}",
        )

    def get_attachment_point(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        context = self._wall_context(insertion, direction)
        if self.mode == "fill":
            attachment_x = context.front_face_x
            attachment_y = context.grade_y
            description = "MSE wall attachment (front/grade)"
        else:
            attachment_x = context.back_face_x - (context.front_sign * context.coping_overhang)
            attachment_y = context.top_y
            description = "MSE wall attachment (top/back)"
        return ConnectionPoint(
            x=attachment_x,
            y=attachment_y,
            description=f"{description}, {direction}",
        )

    def to_geometry(self, insertion: ConnectionPoint, direction: Direction) -> ComponentGeometry:
        context = self._wall_context(insertion, direction)
        polygons: list[Polygon] = []
        polylines: list[list[Point2D]] = []
        polyline_styles: list[dict[str, str]] = []

        if self.show_backfill:
            boundary, hatch_lines = self._structural_fill_hatch(context)
            polylines.append(boundary)
            polyline_styles.append({"stroke_dasharray": "6,4"})
            for hatch in hatch_lines:
                polylines.append(hatch)
                polyline_styles.append({"stroke_width": "1"})

        foundation_polygon = self._foundation_polygon(context)
        polygons.append(foundation_polygon)

        coping_polygon = self._coping_polygon(context)
        polygons.append(coping_polygon)

        wall_polygon = self._panel_polygon(context)
        polygons.append(wall_polygon)

        return ComponentGeometry(
            polygons=polygons,
            polylines=polylines,
            metadata={
                "component_type": "MSEWall",
                "height": self.height,
                "panel_thickness": self.panel_thickness,
                "mode": self.mode,
                "cover_depth": self.cover_depth,
                "foundation_width": self.foundation_width,
                "foundation_thickness": self.foundation_thickness,
                "coping_width": self.coping_width,
                "coping_above": self.coping_above,
                "coping_below": self.coping_below,
                "show_backfill": self.show_backfill,
                "structural_fill_min_width": self.structural_fill_min_width,
                "structural_fill_slope_ratio": self.structural_fill_slope_ratio,
                "hatch_boundary_index": 0 if self.show_backfill else None,
                "hatch_spacing": self.structural_fill_hatch_spacing,
                "hatch_orientation": "horizontal",
                "polyline_styles": polyline_styles,
            },
        )

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.height <= 0:
            errors.append("MSE wall height must be positive")
        if self.panel_thickness <= 0:
            errors.append("MSE panel thickness must be positive")
        if self.foundation_width <= 0:
            errors.append("MSE foundation width must be positive")
        if self.foundation_thickness <= 0:
            errors.append("MSE foundation thickness must be positive")
        if self.coping_width <= 0:
            errors.append("MSE coping width must be positive")
        if self.structural_fill_min_width <= 0:
            errors.append("MSE structural fill minimum width must be positive")
        if self.structural_fill_slope_ratio < 0:
            errors.append("MSE structural fill slope ratio must be non-negative")
        if self.structural_fill_hatch_spacing <= 0:
            errors.append("MSE structural fill hatch spacing must be positive")
        if self.mode not in ("fill", "cut"):
            errors.append(f"Mode must be 'fill' or 'cut', got '{self.mode}'")
        return errors

    def _wall_context(self, insertion: ConnectionPoint, direction: Direction) -> "_WallContext":
        direction_sign = 1.0 if direction == "right" else -1.0
        coping_overhang = max(0.0, (self.coping_width - self.panel_thickness) / 2.0)
        if self.mode == "fill":
            front_sign = direction_sign
            top_y = insertion.y
            grade_y = insertion.y - self.height
            back_face_x = insertion.x + (front_sign * coping_overhang)
            front_face_x = back_face_x + (front_sign * self.panel_thickness)
        else:
            front_sign = -direction_sign
            grade_y = insertion.y
            top_y = insertion.y + self.height
            front_face_x = insertion.x
            back_face_x = insertion.x - (front_sign * self.panel_thickness)

        foundation_top_y = grade_y - self.cover_depth
        foundation_bottom_y = foundation_top_y - self.foundation_thickness

        backfill_height = self.backfill_height
        if backfill_height is None:
            backfill_height = self.height

        return _WallContext(
            direction=direction,
            front_sign=front_sign,
            front_face_x=front_face_x,
            back_face_x=back_face_x,
            top_y=top_y,
            grade_y=grade_y,
            foundation_top_y=foundation_top_y,
            foundation_bottom_y=foundation_bottom_y,
            backfill_height=backfill_height,
            coping_overhang=coping_overhang,
        )

    def _panel_polygon(self, context: "_WallContext") -> Polygon:
        if context.direction == "right":
            vertices = [
                Point2D(context.front_face_x, context.top_y),
                Point2D(context.back_face_x, context.top_y),
                Point2D(context.back_face_x, context.foundation_top_y),
                Point2D(context.front_face_x, context.foundation_top_y),
            ]
        else:
            vertices = [
                Point2D(context.front_face_x, context.top_y),
                Point2D(context.front_face_x, context.foundation_top_y),
                Point2D(context.back_face_x, context.foundation_top_y),
                Point2D(context.back_face_x, context.top_y),
            ]
        return Polygon(exterior=vertices)

    def _foundation_polygon(self, context: "_WallContext") -> Polygon:
        overhang = max(0.0, (self.foundation_width - self.panel_thickness) / 2.0)
        front_ext = context.front_face_x + (context.front_sign * overhang)
        back_ext = context.back_face_x - (context.front_sign * overhang)

        if context.direction == "right":
            vertices = [
                Point2D(front_ext, context.foundation_top_y),
                Point2D(back_ext, context.foundation_top_y),
                Point2D(back_ext, context.foundation_bottom_y),
                Point2D(front_ext, context.foundation_bottom_y),
            ]
        else:
            vertices = [
                Point2D(front_ext, context.foundation_top_y),
                Point2D(front_ext, context.foundation_bottom_y),
                Point2D(back_ext, context.foundation_bottom_y),
                Point2D(back_ext, context.foundation_top_y),
            ]
        return Polygon(exterior=vertices)

    def _coping_polygon(self, context: "_WallContext") -> Polygon:
        center_x = (context.front_face_x + context.back_face_x) / 2.0
        half_width = self.coping_width / 2.0
        left_x = center_x - half_width
        right_x = center_x + half_width
        top_y = context.top_y + self.coping_above
        bottom_y = context.top_y - self.coping_below

        if context.direction == "right":
            vertices = [
                Point2D(left_x, top_y),
                Point2D(right_x, top_y),
                Point2D(right_x, bottom_y),
                Point2D(left_x, bottom_y),
            ]
        else:
            vertices = [
                Point2D(left_x, top_y),
                Point2D(left_x, bottom_y),
                Point2D(right_x, bottom_y),
                Point2D(right_x, top_y),
            ]
        return Polygon(exterior=vertices)

    def _structural_fill_polygon(self, context: "_WallContext") -> Polygon:
        back_sign = -context.front_sign
        bottom_width = self.structural_fill_min_width
        top_width = bottom_width + (self.structural_fill_slope_ratio * context.backfill_height)
        top_width = max(bottom_width, top_width)

        bottom_back_x = context.back_face_x + (back_sign * bottom_width)
        top_back_x = context.back_face_x + (back_sign * top_width)
        bottom_y = context.foundation_top_y

        if context.direction == "right":
            vertices = [
                Point2D(context.back_face_x, context.top_y),
                Point2D(top_back_x, context.top_y),
                Point2D(bottom_back_x, bottom_y),
                Point2D(context.back_face_x, bottom_y),
            ]
        else:
            vertices = [
                Point2D(context.back_face_x, context.top_y),
                Point2D(context.back_face_x, bottom_y),
                Point2D(bottom_back_x, bottom_y),
                Point2D(top_back_x, context.top_y),
            ]
        return Polygon(exterior=vertices)

    def _structural_fill_hatch(
        self, context: "_WallContext"
    ) -> tuple[list[Point2D], list[list[Point2D]]]:
        polygon = self._structural_fill_polygon(context)
        boundary = polygon.exterior + [polygon.exterior[0]]

        back_sign = -context.front_sign
        bottom_width = self.structural_fill_min_width
        top_width = bottom_width + (self.structural_fill_slope_ratio * context.backfill_height)
        top_width = max(bottom_width, top_width)
        top_y = context.top_y
        bottom_y = context.foundation_top_y

        hatch_lines: list[list[Point2D]] = []
        spacing = self.structural_fill_hatch_spacing
        height = top_y - bottom_y
        steps = max(1, int(height / spacing))

        for i in range(steps + 1):
            y = top_y - min(height, i * spacing)
            if top_width == bottom_width:
                width_at_y = top_width
            else:
                ratio = (y - bottom_y) / height
                width_at_y = bottom_width + (top_width - bottom_width) * ratio

            x_back = context.back_face_x + (back_sign * width_at_y)
            hatch_lines.append([Point2D(context.back_face_x, y), Point2D(x_back, y)])

        return boundary, hatch_lines


@dataclass(frozen=True)
class _WallContext:
    direction: Direction
    front_sign: float
    front_face_x: float
    back_face_x: float
    top_y: float
    grade_y: float
    foundation_top_y: float
    foundation_bottom_y: float
    backfill_height: float
    coping_overhang: float = 0.0
