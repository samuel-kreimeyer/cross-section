"""Leader line annotation for callouts and keyed notes."""

from dataclasses import dataclass, replace
from typing import Callable, Literal

from ...geometry.bounds import BoundingBox
from ...geometry.primitives import Point2D
from .base import AnnotationBase


@dataclass(kw_only=True)
class LeaderAnnotation(AnnotationBase):
    """Leader line annotation with 2-3 point path.

    Leader lines point from a feature to callout text or keyed note.
    Lines are kept simple (2-3 points max) to avoid complex routing.

    Attributes:
        points: Path points (2-3 points from target to text)
                - 2 points: straight line from target to text
                - 3 points: target → elbow → text (last segment aligns with text)
        text: Callout text (or keyed note reference)
        arrow_at_start: Whether to show arrow at first point (target)
        text_anchor: Text anchor position ('start', 'middle', 'end')
        text_size: Font size for callout text
    """

    points: list[Point2D]
    text: str
    arrow_at_start: bool = True
    text_anchor: Literal["start", "middle", "end"] = "start"
    text_size: float = 0.12  # Slightly smaller than regular labels
    max_underline_extension: float = 0.006  # ~1/4 inch in meters

    def __post_init__(self) -> None:
        """Validate leader path."""
        if len(self.points) < 2:
            raise ValueError("Leader must have at least 2 points (start and end)")
        if len(self.points) > 3:
            raise ValueError("Leader must have at most 3 points")
        if not self.text:
            raise ValueError("Leader text cannot be empty")

    def get_text_position(self) -> Point2D:
        """Get the position where text should be placed.

        Text is placed at or near the last point.

        Returns:
            Text position
        """
        return self.points[-1]

    def bounds(self) -> BoundingBox:
        """Calculate bounding box including path, arrowhead, and text.

        Returns:
            Bounding box containing leader line and text
        """
        # Start with all path points
        bounds_points = list(self.points)

        # Include arrowhead extent at start point
        if self.arrow_at_start and len(self.points) >= 2:
            arrow_size = self.text_size * 0.4  # Matches to_svg_elements
            dx = self.points[0].x - self.points[1].x
            dy = self.points[0].y - self.points[1].y
            length = (dx * dx + dy * dy) ** 0.5
            if length > 0:
                dir_x = dx / length
                dir_y = dy / length
                perp_x = -dir_y
                perp_y = dir_x
                tip = self.points[0]
                for sign in (1, -1):
                    bounds_points.append(Point2D(
                        tip.x - dir_x * arrow_size + sign * perp_x * arrow_size / 2,
                        tip.y - dir_y * arrow_size + sign * perp_y * arrow_size / 2,
                    ))

        # Add text bounds (approximate)
        text_pos = self.get_text_position()
        text_width = self.text_size * len(self.text) * 0.6
        text_height = self.text_size

        # Expand bounds based on text anchor
        if self.text_anchor == "start":
            # Text extends to the right
            bounds_points.extend([
                Point2D(text_pos.x, text_pos.y - text_height/2),
                Point2D(text_pos.x + text_width, text_pos.y + text_height/2),
            ])
        elif self.text_anchor == "middle":
            # Text centered
            bounds_points.extend([
                Point2D(text_pos.x - text_width/2, text_pos.y - text_height/2),
                Point2D(text_pos.x + text_width/2, text_pos.y + text_height/2),
            ])
        else:  # end
            # Text extends to the left
            bounds_points.extend([
                Point2D(text_pos.x - text_width, text_pos.y - text_height/2),
                Point2D(text_pos.x, text_pos.y + text_height/2),
            ])

        return BoundingBox.from_points(bounds_points)

    def reposition(self, offset: Point2D) -> "LeaderAnnotation":
        """Create a new leader offset by the given amount.

        Args:
            offset: The offset to apply to all points

        Returns:
            New LeaderAnnotation instance at offset position
        """
        new_points = [self.points[0]]
        for p in self.points[1:]:
            new_points.append(Point2D(p.x + offset.x, p.y + offset.y))

        if len(new_points) == 3:
            new_points = self._clamp_elbow_extension(new_points)

        return replace(self, points=new_points)

    def _clamp_elbow_extension(self, points: list[Point2D]) -> list[Point2D]:
        """Clamp elbow-to-text segment length to avoid excessive overhang."""
        text_width = self.text_size * len(self.text) * 0.6
        if self.text_anchor == "middle":
            max_length = text_width / 2 + self.max_underline_extension
        else:
            max_length = text_width + self.max_underline_extension

        elbow = points[1]
        text_point = points[2]
        dx = elbow.x - text_point.x
        dy = elbow.y - text_point.y
        length = (dx * dx + dy * dy) ** 0.5

        if length > max_length and length > 0:
            scale = max_length / length
            elbow = Point2D(
                text_point.x + dx * scale,
                text_point.y + dy * scale,
            )
            return [points[0], elbow, text_point]

        return points

    def to_svg_elements(self, transform: Callable[[Point2D], Point2D]) -> list[str]:
        """Convert this leader to SVG elements.

        Creates polyline for leader path, optional arrow, and text.

        Args:
            transform: Function to transform annotation coordinates to SVG coordinates

        Returns:
            List of SVG element strings
        """
        elements = []

        # Transform points
        t_points = [transform(p) for p in self.points]

        # Create polyline path
        path_points = " ".join([f"{p.x:.2f},{p.y:.2f}" for p in t_points])
        elements.append(
            f'<polyline points="{path_points}" '
            f'stroke="black" stroke-width="0.75" fill="none" class="leader-line"/>'
        )

        # Arrow at start (if enabled) - arrow points TO the first point (target)
        if self.arrow_at_start and len(t_points) >= 2:
            # Direction pointing TOWARDS the first point (from second to first)
            # This makes the arrow point TO the target, not away from it
            dx = t_points[0].x - t_points[1].x
            dy = t_points[0].y - t_points[1].y
            length = (dx * dx + dy * dy) ** 0.5

            if length > 0:
                arrow_size = self.text_size * 0.4
                dir_x = dx / length
                dir_y = dy / length
                perp_x = -dir_y
                perp_y = dir_x

                # Arrow tip at target, barbs pointing back along the line
                tip = t_points[0]
                p1 = Point2D(
                    tip.x - dir_x * arrow_size + perp_x * arrow_size/2,
                    tip.y - dir_y * arrow_size + perp_y * arrow_size/2
                )
                p2 = Point2D(tip.x, tip.y)
                p3 = Point2D(
                    tip.x - dir_x * arrow_size - perp_x * arrow_size/2,
                    tip.y - dir_y * arrow_size - perp_y * arrow_size/2
                )

                elements.append(
                    f'<path d="M {p1.x:.2f},{p1.y:.2f} L {p2.x:.2f},{p2.y:.2f} '
                    f'L {p3.x:.2f},{p3.y:.2f}" '
                    f'stroke="black" stroke-width="0.75" fill="black" class="leader-arrow"/>'
                )

        # Text at end point
        text_pos = transform(self.get_text_position())

        svg_anchor = {
            "start": "start",
            "middle": "middle",
            "end": "end"
        }[self.text_anchor]

        elements.append(
            f'<text x="{text_pos.x:.2f}" y="{text_pos.y:.2f}" '
            f'font-size="{self.text_size * 100:.1f}" '
            f'text-anchor="{svg_anchor}" fill="black" class="leader-text">'
            f'{self.text}</text>'
        )

        return elements

    def validate(self) -> list[str]:
        """Validate leader annotation.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = super().validate()

        if len(self.points) < 2:
            errors.append("Leader must have at least 2 points")
        elif len(self.points) > 3:
            errors.append("Leader must have at most 3 points")

        if not self.text:
            errors.append("Leader text cannot be empty")

        if self.text_size <= 0:
            errors.append(f"Text size must be positive, got {self.text_size}")

        # Check for duplicate consecutive points
        for i in range(len(self.points) - 1):
            if self.points[i].x == self.points[i+1].x and self.points[i].y == self.points[i+1].y:
                errors.append(f"Leader has duplicate consecutive points at index {i}")

        return errors
