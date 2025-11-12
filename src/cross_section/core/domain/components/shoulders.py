"""Shoulder components."""

from dataclasses import dataclass, field
from typing import List
from ..base import RoadComponent, Direction
from ..pavement import PavementLayer, AsphaltLayer
from ...geometry.primitives import ConnectionPoint, ComponentGeometry, Polygon, Point2D


@dataclass
class Shoulder(RoadComponent):
    """A paved or unpaved shoulder adjacent to travel lanes.

    Shoulders have two slope sections:
    1. Paved width: matches the cross_slope (typically 2%)
    2. Foreslope: steeper slope beyond paved width (e.g., 6:1 = 16.67%)

    Each pavement layer forms a trapezoid - parallel to the surface within the paved
    width, then extending until it intersects the foreslope line. This means lower
    layers extend further horizontally.

    Example: 2ft paved width, 2% cross slope, 6:1 foreslope, 1ft total pavement depth
    - Top surface: 2ft wide
    - Bottom of pavement: 2 + 1*6 = 8ft wide

    Attributes:
        width: Paved shoulder width in meters
        cross_slope: Cross slope of paved portion (positive slopes down away from lane)
        foreslope_ratio: Horizontal:vertical ratio for foreslope (e.g., 6.0 for 6:1)
        paved: Whether shoulder is paved (if False, uses minimal base layer)
        pavement_layers: List of pavement layers (only if paved=True)
    """

    width: float
    cross_slope: float = 0.02  # 2% default
    foreslope_ratio: float = 6.0  # 6:1 (6 horizontal : 1 vertical)
    paved: bool = True
    pavement_layers: List[PavementLayer] = field(default_factory=lambda: [
        AsphaltLayer(
            thickness=0.05,  # 50mm surface course
            aggregate_size=12.5,
            binder_type='PG 64-22',
            binder_percentage=5.5,
            density=2400
        )
    ])

    def get_insertion_point(
        self, previous_attachment: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Shoulder snaps directly to previous component's attachment point.

        Args:
            previous_attachment: The attachment point from the previous component
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The insertion point (same as previous attachment)
        """
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description=f"Shoulder insertion ({direction})"
        )

    def get_attachment_point(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Calculate the outside edge of the paved shoulder width.

        The attachment point is at the outer edge of the paved width, where
        the foreslope begins. This is where the next component (if any) would attach.

        Args:
            insertion: This shoulder's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The attachment point at the outer edge of paved width
        """
        drop = self.width * self.cross_slope

        if direction == 'right':
            return ConnectionPoint(
                x=insertion.x + self.width,
                y=insertion.y - drop,
                description=f"Shoulder attachment ({direction})"
            )
        else:  # left
            return ConnectionPoint(
                x=insertion.x - self.width,
                y=insertion.y - drop,
                description=f"Shoulder attachment ({direction})"
            )

    def to_geometry(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ComponentGeometry:
        """Create shoulder geometry with trapezoid-shaped pavement layers.

        Each layer extends from the insertion point across the paved width, then
        continues until it intersects the foreslope. Lower layers extend further
        horizontally, creating trapezoids.

        Args:
            insertion: This shoulder's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            ComponentGeometry with one trapezoid polygon per pavement layer
        """
        polygons = []
        current_depth = 0.0

        # Calculate surface elevation at paved edge
        surface_at_paved_edge = insertion.y - self.width * self.cross_slope

        for layer in self.pavement_layers:
            layer_top_depth = current_depth
            layer_bottom_depth = current_depth + layer.thickness

            # Inside edge (at insertion point)
            inside_top_y = insertion.y - layer_top_depth
            inside_bottom_y = insertion.y - layer_bottom_depth

            # Outside edge elevations (constant depth below surface at paved edge)
            outside_top_y = surface_at_paved_edge - layer_top_depth
            outside_bottom_y = surface_at_paved_edge - layer_bottom_depth

            # Calculate horizontal extensions based on depth and foreslope
            # For depth d: horizontal_extension = d * foreslope_ratio
            top_extension = layer_top_depth * self.foreslope_ratio
            bottom_extension = layer_bottom_depth * self.foreslope_ratio

            if direction == 'right':
                # Outside x-coordinates extend beyond paved width
                outside_top_x = insertion.x + self.width + top_extension
                outside_bottom_x = insertion.x + self.width + bottom_extension

                vertices = [
                    Point2D(insertion.x, inside_top_y),        # Inside, top
                    Point2D(outside_top_x, outside_top_y),     # Outside, top
                    Point2D(outside_bottom_x, outside_bottom_y), # Outside, bottom
                    Point2D(insertion.x, inside_bottom_y),     # Inside, bottom
                ]
            else:  # left
                # For left side, extend in negative X direction
                outside_top_x = insertion.x - self.width - top_extension
                outside_bottom_x = insertion.x - self.width - bottom_extension

                vertices = [
                    Point2D(insertion.x, inside_top_y),        # Inside, top
                    Point2D(insertion.x, inside_bottom_y),     # Inside, bottom
                    Point2D(outside_bottom_x, outside_bottom_y), # Outside, bottom
                    Point2D(outside_top_x, outside_top_y),     # Outside, top
                ]

            polygons.append(Polygon(exterior=vertices))
            current_depth = layer_bottom_depth

        # Build layer metadata
        layer_info = []
        for i, layer in enumerate(self.pavement_layers):
            layer_dict = {
                'layer_index': i,
                'type': type(layer).__name__,
                'thickness': layer.thickness,
            }
            if hasattr(layer, 'binder_type'):
                layer_dict['binder_type'] = layer.binder_type
            if hasattr(layer, 'compressive_strength'):
                layer_dict['compressive_strength'] = layer.compressive_strength
            if hasattr(layer, 'material_type'):
                layer_dict['material_type'] = layer.material_type
            layer_info.append(layer_dict)

        return ComponentGeometry(
            polygons=polygons,
            metadata={
                'component_type': 'Shoulder',
                'width': self.width,
                'cross_slope': self.cross_slope,
                'foreslope_ratio': self.foreslope_ratio,
                'paved': self.paved,
                'assembly_direction': direction,
                'layer_count': len(self.pavement_layers),
                'total_depth': sum(layer.thickness for layer in self.pavement_layers),
                'layers': layer_info
            }
        )

    def validate(self) -> List[str]:
        """Validate shoulder parameters and pavement layers.

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Width validation
        if self.width <= 0:
            errors.append("Shoulder width must be positive")
        elif self.width < 0.6:
            errors.append("Shoulder width below typical minimum (0.6m/2ft) - verify design")
        elif self.width > 3.6:
            errors.append("Shoulder width exceeds typical maximum (3.6m/12ft) - verify design")

        # Cross slope validation
        if abs(self.cross_slope) > 0.06:
            errors.append(f"Cross slope {self.cross_slope:.1%} exceeds typical maximum (6%) - verify design")
        elif abs(self.cross_slope) < 0.015:
            errors.append(f"Cross slope {self.cross_slope:.1%} below minimum for drainage (1.5%) - verify design")

        # Foreslope validation
        if self.foreslope_ratio < 2.0:
            errors.append(f"Foreslope {self.foreslope_ratio}:1 is too steep - typical minimum is 2:1")
        elif self.foreslope_ratio > 10.0:
            errors.append(f"Foreslope {self.foreslope_ratio}:1 is very flat - typical maximum is 10:1")
        elif self.foreslope_ratio < 4.0:
            errors.append(f"Foreslope {self.foreslope_ratio}:1 may require barrier - verify design")

        # Pavement layer validation (only if paved)
        if self.paved:
            if not self.pavement_layers:
                errors.append("Paved shoulder must have at least one pavement layer")
            else:
                for i, layer in enumerate(self.pavement_layers):
                    layer_errors = layer.validate()
                    for error in layer_errors:
                        errors.append(f"Layer {i} ({type(layer).__name__}): {error}")

                # Check total pavement depth
                total_depth = sum(layer.thickness for layer in self.pavement_layers)
                if total_depth < 0.10:
                    errors.append(f"Total pavement depth {total_depth:.3f}m below typical minimum for shoulders (0.10m)")
                elif total_depth > 0.50:
                    errors.append(f"Total pavement depth {total_depth:.3f}m exceeds typical maximum for shoulders (0.50m)")

        return errors
