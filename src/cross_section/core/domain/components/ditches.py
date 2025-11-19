"""Ditch components for roadside drainage."""

from dataclasses import dataclass
from typing import List, Optional, Literal
from ..base import RoadComponent, Direction
from ..pavement import CrushedRockLayer, ConcreteLayer
from ...geometry.primitives import ConnectionPoint, ComponentGeometry, Polygon, Point2D


DitchType = Literal['v_ditch', 'trapezoid']


@dataclass
class Ditch(RoadComponent):
    """A drainage ditch component with foreslope, bottom, and backslope.

    Ditches are complete assemblies that include:
    - Foreslope: Slope down from previous component
    - Bottom: Flat bottom (trapezoid) or point (V-ditch)
    - Backslope: Slope back up to next component
    - Optional lining material (crushed rock, concrete, etc.)

    Attributes:
        depth: Vertical depth of ditch at deepest point (meters)
        foreslope_ratio: Horizontal:vertical ratio for incoming slope (e.g., 4.0 for 4:1)
        backslope_ratio: Horizontal:vertical ratio for outgoing slope (e.g., 3.0 for 3:1)
        bottom_width: Width of flat bottom (0 for V-ditch) in meters
        bottom_slope: Cross slope of bottom (positive = away from foreslope)
        ditch_type: Type of ditch ('v_ditch' or 'trapezoid')
        lining: Optional lining material (crushed rock or concrete)
        lining_thickness: Thickness of lining material if present (meters)
    """

    depth: float
    foreslope_ratio: float = 4.0  # 4:1 typical
    backslope_ratio: float = 3.0  # 3:1 typical (steeper going up)
    bottom_width: float = 1.2  # meters (0 for V-ditch)
    bottom_slope: float = 0.02  # 2% cross slope on bottom
    ditch_type: DitchType = 'trapezoid'
    lining: Optional[object] = None  # CrushedRockLayer or ConcreteLayer
    lining_thickness: float = 0.15  # meters

    def __post_init__(self):
        """Validate and set ditch type based on bottom width."""
        if self.bottom_width == 0:
            self.ditch_type = 'v_ditch'
        else:
            self.ditch_type = 'trapezoid'

    def get_insertion_point(
        self, previous_attachment: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Ditch snaps directly to previous component's attachment point.

        Args:
            previous_attachment: The attachment point from the previous component
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The insertion point (same as previous attachment)
        """
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description=f"Ditch insertion ({direction})"
        )

    def get_attachment_point(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Calculate the top of backslope (end of ditch).

        Args:
            insertion: This ditch's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The attachment point at the top of backslope
        """
        # Calculate horizontal distances
        foreslope_run = self.depth * self.foreslope_ratio
        backslope_run = self.depth * self.backslope_ratio
        total_width = foreslope_run + self.bottom_width + backslope_run

        # Attachment is at the same elevation as insertion (top of backslope)
        if direction == 'right':
            return ConnectionPoint(
                x=insertion.x + total_width,
                y=insertion.y,
                description=f"Ditch attachment ({direction})"
            )
        else:  # left
            return ConnectionPoint(
                x=insertion.x - total_width,
                y=insertion.y,
                description=f"Ditch attachment ({direction})"
            )

    def to_geometry(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ComponentGeometry:
        """Create ditch geometry.

        Creates geometry representing the ditch excavation and lining material:
        1. Void boundary - polyline showing excavation profile (always generated)
        2. Lining polygon - filled shape for material layer (if lining specified)

        Args:
            insertion: This ditch's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            ComponentGeometry with ditch void polyline and optional lining polygon
        """
        polygons = []
        polylines = []
        layers = []

        # Always create void boundary polyline to show the excavation profile
        if direction == 'right':
            void_vertices = self._create_right_geometry(insertion)
        else:
            void_vertices = self._create_left_geometry(insertion)
        polylines.append(void_vertices)

        # Add lining if specified (projected downward from ditch bottom)
        if self.lining is not None:
            if direction == 'right':
                lining_vertices = self._create_right_lining(insertion)
            else:
                lining_vertices = self._create_left_lining(insertion)
            polygons.append(Polygon(exterior=lining_vertices))
            layers.append({
                'layer_index': 0,
                'type': type(self.lining).__name__,
                'thickness': self.lining_thickness,
            })

        return ComponentGeometry(
            polygons=polygons,
            polylines=polylines,
            metadata={
                'component_type': 'Ditch',
                'ditch_type': self.ditch_type,
                'depth': self.depth,
                'foreslope_ratio': self.foreslope_ratio,
                'backslope_ratio': self.backslope_ratio,
                'bottom_width': self.bottom_width,
                'bottom_slope': self.bottom_slope,
                'has_lining': self.lining is not None,
                'lining_thickness': self.lining_thickness if self.lining else 0,
                'assembly_direction': direction,
                'layers': layers
            }
        )

    def _create_right_geometry(self, insertion: ConnectionPoint) -> List[Point2D]:
        """Create geometry for right-side ditch.

        Returns vertices in counter-clockwise order.
        """
        foreslope_run = self.depth * self.foreslope_ratio
        backslope_run = self.depth * self.backslope_ratio

        # Top of foreslope (insertion point)
        p1 = Point2D(insertion.x, insertion.y)

        if self.ditch_type == 'v_ditch':
            # Bottom point (where foreslope and backslope meet)
            bottom_x = insertion.x + foreslope_run
            bottom_y = insertion.y - self.depth
            p2 = Point2D(bottom_x, bottom_y)

            # Top of backslope
            p3 = Point2D(insertion.x + foreslope_run + backslope_run, insertion.y)

            return [p1, p2, p3]
        else:
            # Trapezoid ditch
            # Bottom of foreslope (start of flat bottom)
            bottom_start_x = insertion.x + foreslope_run
            bottom_start_y = insertion.y - self.depth
            p2 = Point2D(bottom_start_x, bottom_start_y)

            # End of flat bottom (start of backslope)
            # Apply bottom slope: drops further across the bottom width
            bottom_drop = self.bottom_width * self.bottom_slope
            bottom_end_x = bottom_start_x + self.bottom_width
            bottom_end_y = bottom_start_y - bottom_drop
            p3 = Point2D(bottom_end_x, bottom_end_y)

            # Top of backslope
            p4 = Point2D(
                insertion.x + foreslope_run + self.bottom_width + backslope_run,
                insertion.y
            )

            return [p1, p2, p3, p4]

    def _create_left_geometry(self, insertion: ConnectionPoint) -> List[Point2D]:
        """Create geometry for left-side ditch.

        Returns vertices in counter-clockwise order.
        """
        foreslope_run = self.depth * self.foreslope_ratio
        backslope_run = self.depth * self.backslope_ratio

        # Top of foreslope (insertion point)
        p1 = Point2D(insertion.x, insertion.y)

        if self.ditch_type == 'v_ditch':
            # Top of backslope
            p3 = Point2D(insertion.x - foreslope_run - backslope_run, insertion.y)

            # Bottom point (where foreslope and backslope meet)
            bottom_x = insertion.x - foreslope_run
            bottom_y = insertion.y - self.depth
            p2 = Point2D(bottom_x, bottom_y)

            return [p1, p3, p2]
        else:
            # Trapezoid ditch
            # Top of backslope
            p4 = Point2D(
                insertion.x - foreslope_run - self.bottom_width - backslope_run,
                insertion.y
            )

            # End of flat bottom (start of backslope)
            bottom_drop = self.bottom_width * self.bottom_slope
            bottom_end_x = insertion.x - foreslope_run - self.bottom_width
            bottom_end_y = insertion.y - self.depth - bottom_drop
            p3 = Point2D(bottom_end_x, bottom_end_y)

            # Bottom of foreslope (start of flat bottom)
            bottom_start_x = insertion.x - foreslope_run
            bottom_start_y = insertion.y - self.depth
            p2 = Point2D(bottom_start_x, bottom_start_y)

            return [p1, p4, p3, p2]

    def _create_right_lining(self, insertion: ConnectionPoint) -> List[Point2D]:
        """Create lining material for right-side ditch.

        The lining is projected downward from the ditch bottom surface.
        Top of lining follows the ditch profile, bottom is offset by lining_thickness.

        Returns vertices in counter-clockwise order.
        """
        foreslope_run = self.depth * self.foreslope_ratio
        backslope_run = self.depth * self.backslope_ratio

        if self.ditch_type == 'v_ditch':
            # V-ditch lining
            # Top of foreslope
            p1 = Point2D(insertion.x, insertion.y)

            # Bottom point (top surface)
            bottom_x = insertion.x + foreslope_run
            bottom_y = insertion.y - self.depth
            p2 = Point2D(bottom_x, bottom_y)

            # Top of backslope
            p3 = Point2D(insertion.x + foreslope_run + backslope_run, insertion.y)

            # Bottom of backslope (bottom surface of lining)
            p4 = Point2D(insertion.x + foreslope_run + backslope_run, insertion.y - self.lining_thickness)

            # Bottom point (bottom surface)
            p5 = Point2D(bottom_x, bottom_y - self.lining_thickness)

            # Bottom of foreslope (bottom surface of lining)
            p6 = Point2D(insertion.x, insertion.y - self.lining_thickness)

            return [p1, p2, p3, p4, p5, p6]
        else:
            # Trapezoid ditch lining
            # Top surface vertices (following ditch profile)
            # Top of foreslope
            p1 = Point2D(insertion.x, insertion.y)

            # Bottom of foreslope (start of flat bottom)
            bottom_start_x = insertion.x + foreslope_run
            bottom_start_y = insertion.y - self.depth
            p2 = Point2D(bottom_start_x, bottom_start_y)

            # End of flat bottom (start of backslope)
            bottom_drop = self.bottom_width * self.bottom_slope
            bottom_end_x = bottom_start_x + self.bottom_width
            bottom_end_y = bottom_start_y - bottom_drop
            p3 = Point2D(bottom_end_x, bottom_end_y)

            # Top of backslope
            p4 = Point2D(
                insertion.x + foreslope_run + self.bottom_width + backslope_run,
                insertion.y
            )

            # Bottom surface vertices (offset downward by lining_thickness)
            # Bottom of backslope
            p5 = Point2D(p4.x, insertion.y - self.lining_thickness)

            # End of flat bottom (bottom surface)
            p6 = Point2D(bottom_end_x, bottom_end_y - self.lining_thickness)

            # Start of flat bottom (bottom surface)
            p7 = Point2D(bottom_start_x, bottom_start_y - self.lining_thickness)

            # Bottom of foreslope
            p8 = Point2D(insertion.x, insertion.y - self.lining_thickness)

            return [p1, p2, p3, p4, p5, p6, p7, p8]

    def _create_left_lining(self, insertion: ConnectionPoint) -> List[Point2D]:
        """Create lining material for left-side ditch.

        The lining is projected downward from the ditch bottom surface.
        Top of lining follows the ditch profile, bottom is offset by lining_thickness.

        Returns vertices in counter-clockwise order.
        """
        foreslope_run = self.depth * self.foreslope_ratio
        backslope_run = self.depth * self.backslope_ratio

        if self.ditch_type == 'v_ditch':
            # V-ditch lining
            # Top of foreslope
            p1 = Point2D(insertion.x, insertion.y)

            # Bottom of foreslope (bottom surface of lining)
            p6 = Point2D(insertion.x, insertion.y - self.lining_thickness)

            # Bottom point (bottom surface)
            bottom_x = insertion.x - foreslope_run
            bottom_y = insertion.y - self.depth
            p5 = Point2D(bottom_x, bottom_y - self.lining_thickness)

            # Bottom of backslope (bottom surface of lining)
            p4 = Point2D(insertion.x - foreslope_run - backslope_run, insertion.y - self.lining_thickness)

            # Top of backslope
            p3 = Point2D(insertion.x - foreslope_run - backslope_run, insertion.y)

            # Bottom point (top surface)
            p2 = Point2D(bottom_x, bottom_y)

            return [p1, p6, p5, p4, p3, p2]
        else:
            # Trapezoid ditch lining
            # Top surface vertices (following ditch profile)
            # Top of foreslope
            p1 = Point2D(insertion.x, insertion.y)

            # Bottom of foreslope (bottom surface of lining)
            p8 = Point2D(insertion.x, insertion.y - self.lining_thickness)

            # Bottom of foreslope (start of flat bottom - bottom surface)
            bottom_start_x = insertion.x - foreslope_run
            bottom_start_y = insertion.y - self.depth
            p7 = Point2D(bottom_start_x, bottom_start_y - self.lining_thickness)

            # End of flat bottom (start of backslope - bottom surface)
            bottom_drop = self.bottom_width * self.bottom_slope
            bottom_end_x = bottom_start_x - self.bottom_width
            bottom_end_y = bottom_start_y - bottom_drop
            p6 = Point2D(bottom_end_x, bottom_end_y - self.lining_thickness)

            # Bottom of backslope (bottom surface)
            p5 = Point2D(
                insertion.x - foreslope_run - self.bottom_width - backslope_run,
                insertion.y - self.lining_thickness
            )

            # Top of backslope (top surface)
            p4 = Point2D(
                insertion.x - foreslope_run - self.bottom_width - backslope_run,
                insertion.y
            )

            # End of flat bottom (start of backslope - top surface)
            p3 = Point2D(bottom_end_x, bottom_end_y)

            # Bottom of foreslope (start of flat bottom - top surface)
            p2 = Point2D(bottom_start_x, bottom_start_y)

            return [p1, p8, p7, p6, p5, p4, p3, p2]

    def validate(self) -> List[str]:
        """Validate ditch parameters.

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        if self.depth <= 0:
            errors.append("Ditch depth must be positive")
        elif self.depth < 0.3:
            errors.append(f"Ditch depth {self.depth:.2f}m is shallow - verify adequate drainage")
        elif self.depth > 3.0:
            errors.append(f"Ditch depth {self.depth:.2f}m is very deep - verify design")

        if self.foreslope_ratio < 2.0:
            errors.append(f"Foreslope {self.foreslope_ratio}:1 is too steep - minimum typically 2:1")
        elif self.foreslope_ratio > 10.0:
            errors.append(f"Foreslope {self.foreslope_ratio}:1 is very flat")

        if self.backslope_ratio < 2.0:
            errors.append(f"Backslope {self.backslope_ratio}:1 is too steep - minimum typically 2:1")
        elif self.backslope_ratio > 10.0:
            errors.append(f"Backslope {self.backslope_ratio}:1 is very flat")

        if self.bottom_width < 0:
            errors.append("Bottom width must be non-negative")
        elif self.bottom_width > 5.0:
            errors.append(f"Bottom width {self.bottom_width:.2f}m is very wide - verify design")

        if abs(self.bottom_slope) > 0.05:
            errors.append(f"Bottom slope {self.bottom_slope:.1%} exceeds typical maximum (5%)")

        if self.lining_thickness < 0:
            errors.append("Lining thickness must be non-negative")
        elif self.lining_thickness >= self.depth:
            errors.append(f"Lining thickness {self.lining_thickness:.3f}m exceeds ditch depth")

        return errors
