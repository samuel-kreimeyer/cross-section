"""Dimension line annotation for measuring distances."""

import math
from dataclasses import dataclass, replace
from typing import Callable

from ...geometry.bounds import BoundingBox
from ...geometry.primitives import Point2D
from .base import AnnotationBase


@dataclass(kw_only=True)
class DimensionAnnotation(AnnotationBase):
    """Dimension line with extension lines and arrows.

    Used to show measurements between component edges.

    Attributes:
        start: Start point (on component edge)
        end: End point (on component edge)
        offset: Perpendicular distance from measured edge to dimension line
        text_position: Position for dimension text (auto-calculated if None)
        dimension_text: Override text (auto-calculated from distance if None)
        show_arrows: Whether to show arrows at dimension line ends
        extension_beyond: How far extension lines extend beyond dimension line
        text_size: Font size for dimension text
    """

    start: Point2D
    end: Point2D
    offset: float = 0.3  # 300mm offset from edge
    text_position: Point2D | None = None
    dimension_text: str | None = None
    show_arrows: bool = True
    extension_beyond: float = 0.05  # 50mm extension
    text_size: float = 0.12  # Slightly smaller than regular text

    def __post_init__(self) -> None:
        """Calculate auto-positioned fields if not provided."""
        if self.start.x == self.end.x and self.start.y == self.end.y:
            raise ValueError("Dimension start and end points must be different")

        # Auto-calculate dimension text if not provided
        if self.dimension_text is None:
            distance = self.start.distance_to(self.end)
            self.dimension_text = f"{distance:.2f}m"

        # Auto-calculate text position if not provided
        if self.text_position is None:
            self.text_position = self._calculate_text_position()

    def _calculate_text_position(self) -> Point2D:
        """Calculate text position at midpoint of dimension line with offset.

        Returns:
            Position for dimension text
        """
        # Midpoint of start and end
        mid_x = (self.start.x + self.end.x) / 2
        mid_y = (self.start.y + self.end.y) / 2

        # Direction vector from start to end
        dx = self.end.x - self.start.x
        dy = self.end.y - self.start.y
        length = math.sqrt(dx * dx + dy * dy)

        if length == 0:
            return Point2D(mid_x, mid_y)

        # Perpendicular direction (rotate 90 degrees)
        perp_x = -dy / length
        perp_y = dx / length

        # Offset in perpendicular direction
        return Point2D(
            mid_x + perp_x * self.offset,
            mid_y + perp_y * self.offset
        )

    def get_dimension_line_endpoints(self) -> tuple[Point2D, Point2D]:
        """Get the dimension line endpoints (offset from start/end points).

        Returns:
            Tuple of (dimension_start, dimension_end) points
        """
        # Direction vector
        dx = self.end.x - self.start.x
        dy = self.end.y - self.start.y
        length = math.sqrt(dx * dx + dy * dy)

        if length == 0:
            return (self.start, self.end)

        # Perpendicular direction
        perp_x = -dy / length
        perp_y = dx / length

        # Offset both points
        dim_start = Point2D(
            self.start.x + perp_x * self.offset,
            self.start.y + perp_y * self.offset
        )
        dim_end = Point2D(
            self.end.x + perp_x * self.offset,
            self.end.y + perp_y * self.offset
        )

        return (dim_start, dim_end)

    def get_extension_line_endpoints(self) -> tuple[Point2D, Point2D]:
        """Get the extension line endpoints (including extension beyond).

        Returns:
            Tuple of (extension_start, extension_end) points.
        """
        # Direction vector
        dx = self.end.x - self.start.x
        dy = self.end.y - self.start.y
        length = math.sqrt(dx * dx + dy * dy)

        if length == 0:
            return (self.start, self.end)

        # Perpendicular direction
        perp_x = -dy / length
        perp_y = dx / length

        extension = self.offset + self.extension_beyond
        ext_start = Point2D(
            self.start.x + perp_x * extension,
            self.start.y + perp_y * extension
        )
        ext_end = Point2D(
            self.end.x + perp_x * extension,
            self.end.y + perp_y * extension
        )

        return (ext_start, ext_end)

    def bounds(self) -> BoundingBox:
        """Calculate bounding box including extension lines and text.

        Returns:
            Bounding box containing entire dimension annotation
        """
        dim_start, dim_end = self.get_dimension_line_endpoints()
        ext_start, ext_end = self.get_extension_line_endpoints()

        # Points to include in bounds
        points = [
            self.start,
            self.end,
            dim_start,
            dim_end,
            ext_start,
            ext_end,
        ]

        # Add text bounds (approximate)
        if self.text_position and self.dimension_text:
            text_width = self.text_size * len(self.dimension_text) * 0.6
            text_height = self.text_size

            points.extend([
                Point2D(self.text_position.x - text_width/2, self.text_position.y - text_height/2),
                Point2D(self.text_position.x + text_width/2, self.text_position.y + text_height/2),
            ])

        return BoundingBox.from_points(points)

    def reposition(self, offset: Point2D) -> "DimensionAnnotation":
        """Create a new dimension offset by the given amount.

        Args:
            offset: The offset to apply to all points

        Returns:
            New DimensionAnnotation instance at offset position
        """
        new_start = Point2D(self.start.x + offset.x, self.start.y + offset.y)
        new_end = Point2D(self.end.x + offset.x, self.end.y + offset.y)
        new_text_pos = None
        if self.text_position:
            new_text_pos = Point2D(
                self.text_position.x + offset.x,
                self.text_position.y + offset.y
            )

        return replace(
            self,
            start=new_start,
            end=new_end,
            text_position=new_text_pos
        )

    def to_svg_elements(self, transform: Callable[[Point2D], Point2D]) -> list[str]:
        """Convert this dimension to SVG elements.

        Creates dimension line, extension lines, arrows, and text.

        Args:
            transform: Function to transform annotation coordinates to SVG coordinates

        Returns:
            List of SVG element strings
        """
        elements = []

        dim_start, dim_end = self.get_dimension_line_endpoints()
        ext_start, ext_end = self.get_extension_line_endpoints()

        # Transform points
        t_start = transform(self.start)
        t_end = transform(self.end)
        t_dim_start = transform(dim_start)
        t_dim_end = transform(dim_end)
        t_ext_start = transform(ext_start)
        t_ext_end = transform(ext_end)

        # Extension lines
        elements.append(
            f'<line x1="{t_start.x:.2f}" y1="{t_start.y:.2f}" '
            f'x2="{t_ext_start.x:.2f}" y2="{t_ext_start.y:.2f}" '
            f'stroke="black" stroke-width="0.5" class="dimension-extension"/>'
        )
        elements.append(
            f'<line x1="{t_end.x:.2f}" y1="{t_end.y:.2f}" '
            f'x2="{t_ext_end.x:.2f}" y2="{t_ext_end.y:.2f}" '
            f'stroke="black" stroke-width="0.5" class="dimension-extension"/>'
        )

        # Dimension line
        elements.append(
            f'<line x1="{t_dim_start.x:.2f}" y1="{t_dim_start.y:.2f}" '
            f'x2="{t_dim_end.x:.2f}" y2="{t_dim_end.y:.2f}" '
            f'stroke="black" stroke-width="1.0" class="dimension-line"/>'
        )

        # Arrows (if enabled)
        if self.show_arrows:
            # Calculate arrow direction
            dx = t_dim_end.x - t_dim_start.x
            dy = t_dim_end.y - t_dim_start.y
            length = math.sqrt(dx * dx + dy * dy)

            if length > 0:
                arrow_size = self.text_size * 0.5  # Arrow size relative to text

                # Arrow at start (pointing from dim_start)
                elements.append(self._create_arrow_svg(t_dim_start, dx/length, dy/length, arrow_size))

                # Arrow at end (pointing from dim_end, reversed direction)
                elements.append(self._create_arrow_svg(t_dim_end, -dx/length, -dy/length, arrow_size))

        # Dimension text
        if self.text_position and self.dimension_text:
            t_text_pos = transform(self.text_position)
            elements.append(
                f'<text x="{t_text_pos.x:.2f}" y="{t_text_pos.y:.2f}" '
                f'font-size="{self.text_size * 100:.1f}" '
                f'text-anchor="middle" fill="black" class="dimension-text">'
                f'{self.dimension_text}</text>'
            )

        return elements

    def _create_arrow_svg(self, tip: Point2D, dir_x: float, dir_y: float, size: float) -> str:
        """Create SVG path for an arrow.

        Args:
            tip: Arrow tip point
            dir_x: X component of direction (normalized)
            dir_y: Y component of direction (normalized)
            size: Arrow size

        Returns:
            SVG path element string
        """
        # Perpendicular direction
        perp_x = -dir_y
        perp_y = dir_x

        # Arrow points
        p1 = Point2D(tip.x - dir_x * size + perp_x * size/2, tip.y - dir_y * size + perp_y * size/2)
        p2 = Point2D(tip.x, tip.y)
        p3 = Point2D(tip.x - dir_x * size - perp_x * size/2, tip.y - dir_y * size - perp_y * size/2)

        return (
            f'<path d="M {p1.x:.2f},{p1.y:.2f} L {p2.x:.2f},{p2.y:.2f} '
            f'L {p3.x:.2f},{p3.y:.2f}" '
            f'stroke="black" stroke-width="1.0" fill="black" class="dimension-arrow"/>'
        )

    def validate(self) -> list[str]:
        """Validate dimension annotation.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = super().validate()

        if self.start.x == self.end.x and self.start.y == self.end.y:
            errors.append("Dimension start and end points must be different")

        if self.offset < 0:
            errors.append(f"Dimension offset must be non-negative, got {self.offset}")
        elif self.offset > 2.0:
            errors.append(
                f"Dimension offset {self.offset:.3f}m is very large - verify design"
            )

        if self.extension_beyond < 0:
            errors.append(f"Extension beyond must be non-negative, got {self.extension_beyond}")

        if self.text_size <= 0:
            errors.append(f"Text size must be positive, got {self.text_size}")

        return errors
