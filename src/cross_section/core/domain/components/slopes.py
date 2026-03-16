"""Slope components for roadside features."""

from dataclasses import dataclass

from ...geometry.primitives import (
    ComponentGeometry,
    ConnectionPoint,
    Point2D,
    Polygon,
    profile_segment,
    quad_between_segments,
)
from ..base import Direction, RoadComponent


@dataclass
class Slope(RoadComponent):
    """A simple slope component.

    Represents a sloped surface from the insertion point, useful for foreslopes,
    backslopes, and other graded surfaces. Can be specified by slope ratio or
    by horizontal and vertical dimensions.

    Attributes:
        horizontal_run: Horizontal distance in meters
        vertical_drop: Vertical drop in meters (positive = down, negative = up)
        slope_ratio: Alternative to horizontal_run - H:V ratio (e.g., 4.0 for 4:1)
        surface_type: Type of surface ('grass', 'crushed_rock', 'bare_earth', etc.)
        thickness: Thickness of slope material if applicable (0 for just surface)
        is_surface_slope: If True, indicates this is a roadway surface/aggregate
            slope (e.g., 4% cross slope) rather than a fill/cut slope. Surface
            slopes bypass the typical 1:1 to 20:1 slope ratio validation since
            cross slopes of 2-6% (50:1 to 17:1) are normal for road surfaces.
    """

    horizontal_run: float | None = None
    vertical_drop: float | None = None
    slope_ratio: float | None = None  # H:V ratio (horizontal : vertical)
    surface_type: str = "grass"
    thickness: float = 0.0  # Thickness of material (0 for surface only)
    is_surface_slope: bool = False  # True for roadway surfaces, False for fill/cut slopes

    def __post_init__(self) -> None:
        """Calculate missing parameters if ratio is provided."""
        if self.slope_ratio is not None and self.vertical_drop is not None:
            # Calculate horizontal run from ratio and vertical drop
            self.horizontal_run = abs(self.vertical_drop) * self.slope_ratio
        elif self.slope_ratio is not None and self.horizontal_run is not None:
            # Calculate vertical drop from ratio and horizontal run
            self.vertical_drop = self.horizontal_run / self.slope_ratio

        if self.horizontal_run is None or self.vertical_drop is None:
            raise ValueError(
                "Must specify either (horizontal_run and vertical_drop) or "
                "(slope_ratio with one dimension)"
            )

    def get_insertion_point(
        self, previous_attachment: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Slope snaps directly to previous component's attachment point.

        Args:
            previous_attachment: The attachment point from the previous component
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The insertion point (same as previous attachment)
        """
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description=f"Slope insertion ({direction})",
        )

    def get_attachment_point(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Calculate the end point of the slope.

        Args:
            insertion: This slope's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The attachment point at the end of the slope
        """
        # These are guaranteed non-None after __post_init__
        assert self.vertical_drop is not None  # nosec B101 # Type guard for mypy
        assert self.horizontal_run is not None  # nosec B101 # Type guard for mypy

        attachment_y = insertion.y - self.vertical_drop

        if direction == "right":
            return ConnectionPoint(
                x=insertion.x + self.horizontal_run,
                y=attachment_y,
                description=f"Slope attachment ({direction})",
            )
        else:  # left
            return ConnectionPoint(
                x=insertion.x - self.horizontal_run,
                y=attachment_y,
                description=f"Slope attachment ({direction})",
            )

    def to_geometry(self, insertion: ConnectionPoint, direction: Direction) -> ComponentGeometry:
        """Create slope geometry.

        Creates a surface polyline or a trapezoidal polygon representing the slope.
        If thickness is 0, creates a simple surface line.
        If thickness > 0, creates a trapezoid with material thickness.

        Args:
            insertion: This slope's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            ComponentGeometry with slope polygon
        """
        # These are guaranteed non-None after __post_init__
        assert self.horizontal_run is not None
        assert self.vertical_drop is not None

        top_segment = profile_segment(
            start=Point2D(insertion.x, insertion.y),
            horizontal_run=self.horizontal_run,
            vertical_drop=self.vertical_drop,
            direction=direction,
        )
        attachment = ConnectionPoint(
            x=top_segment.end.x,
            y=top_segment.end.y,
            description=f"Slope attachment ({direction})",
        )

        if self.thickness == 0:
            line = top_segment.to_polyline()
            polygons: list[Polygon] = []
            polylines = [line]
        else:
            bottom_segment = top_segment.translated_y(-self.thickness)
            polygons = [quad_between_segments(top_segment, bottom_segment, direction)]
            polylines = []

        slope_ratio = (
            self.slope_ratio if self.slope_ratio else self.horizontal_run / abs(self.vertical_drop)
        )
        return ComponentGeometry(
            polygons=polygons,
            polylines=polylines,
            metadata={
                "component_type": "Slope",
                "horizontal_run": self.horizontal_run,
                "vertical_drop": self.vertical_drop,
                "slope_ratio": slope_ratio,
                "surface_type": self.surface_type,
                "thickness": self.thickness,
                "assembly_direction": direction,
            },
        )

    def validate(self) -> list[str]:
        """Validate slope parameters.

        Returns:
            List of error messages (empty if valid)
        """
        # These are guaranteed non-None after __post_init__
        assert self.horizontal_run is not None
        assert self.vertical_drop is not None

        errors = []

        if self.horizontal_run <= 0:
            errors.append("Horizontal run must be positive")

        if abs(self.vertical_drop) <= 0:
            errors.append("Vertical drop must be non-zero")
        else:
            # Calculate actual slope ratio (only if vertical_drop is non-zero)
            actual_ratio = self.horizontal_run / abs(self.vertical_drop)

            # Only validate slope ratio for fill/cut slopes, not surface slopes
            # Surface slopes (cross slopes) are typically 2-6% (50:1 to 17:1)
            if not self.is_surface_slope:
                if actual_ratio < 1.0:
                    errors.append(
                        f"Slope ratio {actual_ratio:.1f}:1 is steeper than 1:1 - may be unsafe"
                    )
                elif actual_ratio > 20.0:
                    errors.append(
                        f"Slope ratio {actual_ratio:.1f}:1 is very flat - verify design"
                    )

        if self.thickness < 0:
            errors.append("Thickness must be non-negative")
        elif self.thickness > 1.0:
            errors.append(f"Thickness {self.thickness:.3f}m is very large - verify design")

        return errors
