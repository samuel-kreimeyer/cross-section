"""Symbol annotation for traffic arrows, drainage marks, etc."""

import math
from dataclasses import dataclass, replace
from typing import Callable

from ...geometry.bounds import BoundingBox
from ...geometry.primitives import Point2D
from .base import AnnotationBase


@dataclass(kw_only=True)
class SymbolAnnotation(AnnotationBase):
    """Symbol annotation (traffic arrows, drainage, centerpoint marks, etc).

    Symbols are typically fixed position (don't move during collision resolution).
    They reference predefined SVG paths from the symbol library.

    Attributes:
        position: Symbol center position
        symbol_type: Symbol type identifier (e.g., "traffic_arrow", "drainage_arrow")
        scale: Scale factor (1.0 = normal size)
        angle: Rotation angle in degrees (0 = default orientation)
    """

    position: Point2D
    symbol_type: str
    scale: float = 1.0
    angle: float = 0.0

    def __post_init__(self) -> None:
        """Validate symbol parameters."""
        if not self.symbol_type:
            raise ValueError("Symbol type cannot be empty")
        if self.scale <= 0:
            raise ValueError(f"Scale must be positive, got {self.scale}")
        if not (-360 <= self.angle <= 360):
            raise ValueError(f"Angle must be between -360 and 360, got {self.angle}")

    def bounds(self) -> BoundingBox:
        """Calculate bounding box for this symbol.

        Uses estimated size from symbol library metadata.
        Actual size depends on symbol type.

        Returns:
            Bounding box containing the symbol
        """
        # Import here to avoid circular dependency
        from .symbols.library import SymbolLibrary

        # Get symbol definition (use default if not found)
        try:
            symbol_def = SymbolLibrary.get(self.symbol_type)
            base_width = symbol_def.get("width", 0.5)  # Default 0.5m
            base_height = symbol_def.get("height", 0.5)
        except KeyError:
            # Symbol not found, use default size for placeholder
            base_width = 0.5
            base_height = 0.5

        # Apply scale
        width = base_width * self.scale
        height = base_height * self.scale

        # Calculate bounds (centered at position, accounting for rotation)
        if self.angle != 0:
            # For rotated symbols, use conservative bounding box
            # (diagonal of rectangle)
            diagonal = math.sqrt(width * width + height * height)
            half_diag = diagonal / 2

            return BoundingBox(
                min_x=self.position.x - half_diag,
                min_y=self.position.y - half_diag,
                max_x=self.position.x + half_diag,
                max_y=self.position.y + half_diag,
            )

        # Unrotated - simple axis-aligned bounds
        return BoundingBox(
            min_x=self.position.x - width / 2,
            min_y=self.position.y - height / 2,
            max_x=self.position.x + width / 2,
            max_y=self.position.y + height / 2,
        )

    def reposition(self, offset: Point2D) -> "SymbolAnnotation":
        """Create a new symbol offset by the given amount.

        Note: Symbols are typically fixed position, so this is rarely used
        (collision resolution repositions text around symbols, not symbols themselves).

        Args:
            offset: The offset to apply

        Returns:
            New SymbolAnnotation instance at offset position
        """
        new_position = Point2D(
            self.position.x + offset.x,
            self.position.y + offset.y
        )
        return replace(self, position=new_position)

    def to_svg_elements(self, transform: Callable[[Point2D], Point2D]) -> list[str]:
        """Convert this symbol to SVG elements.

        Retrieves symbol path from library and applies transform/rotation.

        Args:
            transform: Function to transform annotation coordinates to SVG coordinates

        Returns:
            List of SVG element strings
        """
        # Import here to avoid circular dependency
        from .symbols.library import SymbolLibrary

        # Get symbol definition
        symbol_def = SymbolLibrary.get(self.symbol_type)
        svg_path = symbol_def.get("svg_path", "")

        if not svg_path:
            # Fallback: render as circle if symbol not found
            t_pos = transform(self.position)
            return [
                f'<circle cx="{t_pos.x:.2f}" cy="{t_pos.y:.2f}" r="5" '
                f'fill="red" stroke="black" class="symbol-missing"/>'
            ]

        # Transform position
        t_pos = transform(self.position)

        # Build transform attribute
        transforms = []
        transforms.append(f"translate({t_pos.x:.2f} {t_pos.y:.2f})")
        if self.angle != 0:
            transforms.append(f"rotate({-self.angle})")  # Negative for SVG coordinate system
        if self.scale != 1.0:
            transforms.append(f"scale({self.scale})")

        transform_attr = " ".join(transforms)

        # Wrap symbol in group with transforms
        elements = [
            f'<g transform="{transform_attr}" class="symbol symbol-{self.symbol_type}">',
            f'  {svg_path}',
            '</g>'
        ]

        return elements

    def validate(self) -> list[str]:
        """Validate symbol annotation.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = super().validate()

        if not self.symbol_type:
            errors.append("Symbol type cannot be empty")

        if self.scale <= 0:
            errors.append(f"Scale must be positive, got {self.scale}")
        elif self.scale > 5.0:
            errors.append(f"Scale {self.scale:.1f} is very large - verify design")

        if not (-360 <= self.angle <= 360):
            errors.append(f"Angle must be between -360 and 360, got {self.angle}")

        # Check if symbol type exists in library
        try:
            from .symbols.library import SymbolLibrary
            SymbolLibrary.get(self.symbol_type)
        except (KeyError, ValueError) as e:
            errors.append(f"Symbol type '{self.symbol_type}' not found in library: {e}")

        return errors
