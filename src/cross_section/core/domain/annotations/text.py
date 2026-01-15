"""Text annotation for labeling cross-section features."""

import math
from dataclasses import dataclass, replace
from typing import Callable, Literal

from ...geometry.bounds import BoundingBox
from ...geometry.primitives import Point2D
from .base import AnnotationBase


@dataclass(kw_only=True)
class TextAnnotation(AnnotationBase):
    """Text label annotation.

    Text annotations are used for component labels, material descriptions,
    and keyed note references.

    Attributes:
        position: Anchor point for the text
        text: Text content (or keyed note reference like "1", "2", etc.)
        font_size: Font size in drawing units (meters)
        anchor: Text anchor point ('start', 'middle', 'end')
        angle: Rotation angle in degrees (0 = horizontal)
        is_keyed_note: Whether this is a keyed note reference
    """

    position: Point2D
    text: str
    font_size: float = 0.15  # ~150mm text height
    anchor: Literal["start", "middle", "end"] = "middle"
    angle: float = 0.0
    is_keyed_note: bool = False

    def __post_init__(self) -> None:
        """Validate text annotation parameters."""
        if not self.text:
            raise ValueError("Text cannot be empty")
        if self.font_size <= 0:
            raise ValueError(f"Font size must be positive, got {self.font_size}")
        if not (-360 <= self.angle <= 360):
            raise ValueError(f"Angle must be between -360 and 360, got {self.angle}")

    def bounds(self) -> BoundingBox:
        """Calculate bounding box for this text.

        Estimates text width as font_size * len(text) * 0.6 (assuming average
        character width is ~0.6 of height for typical fonts).

        Returns:
            Bounding box containing the text
        """
        # Estimate text dimensions
        text_width = self.font_size * len(self.text) * 0.6
        text_height = self.font_size

        # Account for anchor position
        if self.anchor == "start":
            # Text extends to the right
            x_offset = 0
        elif self.anchor == "middle":
            # Text centered
            x_offset = -text_width / 2
        else:  # end
            # Text extends to the left
            x_offset = -text_width

        # Base bounding box (before rotation)
        base_min_x = self.position.x + x_offset
        base_max_x = self.position.x + x_offset + text_width
        base_min_y = self.position.y - text_height / 2
        base_max_y = self.position.y + text_height / 2

        # If rotated, we need to rotate the corners and find new bounds
        if self.angle != 0:
            angle_rad = math.radians(self.angle)
            cos_a = math.cos(angle_rad)
            sin_a = math.sin(angle_rad)

            # Four corners of the text box
            corners = [
                Point2D(base_min_x, base_min_y),
                Point2D(base_max_x, base_min_y),
                Point2D(base_max_x, base_max_y),
                Point2D(base_min_x, base_max_y),
            ]

            # Rotate corners around position
            rotated_corners = []
            for corner in corners:
                # Translate to origin
                dx = corner.x - self.position.x
                dy = corner.y - self.position.y

                # Rotate
                new_x = dx * cos_a - dy * sin_a
                new_y = dx * sin_a + dy * cos_a

                # Translate back
                rotated_corners.append(
                    Point2D(
                        self.position.x + new_x,
                        self.position.y + new_y
                    )
                )

            return BoundingBox.from_points(rotated_corners)

        return BoundingBox(
            min_x=base_min_x,
            min_y=base_min_y,
            max_x=base_max_x,
            max_y=base_max_y,
        )

    def reposition(self, offset: Point2D) -> "TextAnnotation":
        """Create a new text annotation offset by the given amount.

        Args:
            offset: The offset to apply

        Returns:
            New TextAnnotation instance at offset position
        """
        new_position = Point2D(
            self.position.x + offset.x,
            self.position.y + offset.y
        )
        return replace(self, position=new_position)

    def to_svg_elements(self, transform: Callable[[Point2D], Point2D]) -> list[str]:
        """Convert this text to SVG <text> element.

        Args:
            transform: Function to transform annotation coordinates to SVG coordinates

        Returns:
            List containing single SVG text element string
        """
        transformed_pos = transform(self.position)

        # SVG text anchor mapping
        svg_anchor = {
            "start": "start",
            "middle": "middle",
            "end": "end"
        }[self.anchor]

        # Build SVG element
        svg = f'<text x="{transformed_pos.x:.2f}" y="{transformed_pos.y:.2f}" '
        svg += f'font-size="{self.font_size * 100:.1f}" '  # Convert to SVG units
        svg += f'text-anchor="{svg_anchor}" '
        svg += f'fill="black" '

        if self.angle != 0:
            svg += f'transform="rotate({-self.angle} {transformed_pos.x:.2f} {transformed_pos.y:.2f})" '

        # Add class for styling
        if self.is_keyed_note:
            svg += 'class="keyed-note">'
        else:
            svg += 'class="annotation-text">'

        svg += self.text
        svg += '</text>'

        return [svg]

    def validate(self) -> list[str]:
        """Validate text annotation.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = super().validate()

        if not self.text:
            errors.append("Text cannot be empty")

        if self.font_size <= 0:
            errors.append(f"Font size must be positive, got {self.font_size}")
        elif self.font_size > 1.0:
            errors.append(
                f"Font size {self.font_size:.3f}m is very large - verify design"
            )

        if not (-360 <= self.angle <= 360):
            errors.append(f"Angle must be between -360 and 360, got {self.angle}")

        return errors
