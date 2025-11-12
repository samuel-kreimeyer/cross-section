"""Lane components."""

from dataclasses import dataclass, field
from typing import List, Literal
from ..base import RoadComponent, Direction
from ..pavement import PavementLayer, AsphaltLayer
from ...geometry.primitives import ConnectionPoint, ComponentGeometry, Polygon, Point2D


@dataclass
class TravelLane(RoadComponent):
    """A travel lane for vehicular traffic.

    The lane includes a layered pavement structure from top (surface) to bottom (subbase).
    Each layer is represented as a separate polygon in the geometry.

    Attributes:
        width: Lane width in meters (typically 3.0-3.6m)
        cross_slope: Cross slope as ratio (e.g., 0.02 for 2%, positive slopes down away from crown)
        traffic_direction: Traffic flow direction ('inbound' or 'outbound')
        pavement_layers: List of pavement layers from top (surface) to bottom (subbase)
    """

    width: float
    cross_slope: float = 0.02  # 2% default cross slope
    traffic_direction: Literal['inbound', 'outbound'] = 'outbound'
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
        """Lane snaps directly to previous component's attachment point.

        Args:
            previous_attachment: The attachment point from the previous component
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The insertion point (same as previous attachment for continuous assembly)
        """
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description=f"TravelLane insertion ({direction}, {self.traffic_direction})"
        )

    def get_attachment_point(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Calculate the outside edge of the lane accounting for cross slope.

        Args:
            insertion: This lane's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The attachment point at the lane's outside edge
        """
        # Cross slope creates vertical drop across the width
        # Positive cross_slope means it slopes DOWN away from crown
        drop = self.width * self.cross_slope

        # For right-side: extends in +X direction, slopes down
        # For left-side: extends in -X direction, slopes down
        if direction == 'right':
            return ConnectionPoint(
                x=insertion.x + self.width,
                y=insertion.y - drop,  # Slopes down away from crown
                description=f"TravelLane attachment ({direction}, {self.traffic_direction})"
            )
        else:  # left
            return ConnectionPoint(
                x=insertion.x - self.width,
                y=insertion.y - drop,  # Also slopes down away from crown
                description=f"TravelLane attachment ({direction}, {self.traffic_direction})"
            )

    def to_geometry(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ComponentGeometry:
        """Create lane geometry with stacked pavement layers.

        Each pavement layer is represented as a separate polygon.
        Layers are stacked from top (surface) to bottom (subbase).

        Args:
            insertion: This lane's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            ComponentGeometry with one polygon per pavement layer
        """
        attachment = self.get_attachment_point(insertion, direction)

        polygons = []
        current_depth = 0.0  # Depth below surface

        # Create one polygon per layer, stacked vertically
        for layer in self.pavement_layers:
            layer_top = current_depth
            layer_bottom = current_depth + layer.thickness

            # Calculate elevations at inside (insertion) and outside (attachment) edges
            # Cross slope applies to the surface
            inside_top = insertion.y - layer_top
            inside_bottom = insertion.y - layer_bottom
            outside_top = attachment.y - layer_top
            outside_bottom = attachment.y - layer_bottom

            # Create polygon vertices (counter-clockwise)
            if direction == 'right':
                vertices = [
                    Point2D(insertion.x, inside_top),      # Inside, top
                    Point2D(attachment.x, outside_top),    # Outside, top
                    Point2D(attachment.x, outside_bottom), # Outside, bottom
                    Point2D(insertion.x, inside_bottom),   # Inside, bottom
                ]
            else:  # left
                vertices = [
                    Point2D(insertion.x, inside_top),      # Inside, top
                    Point2D(insertion.x, inside_bottom),   # Inside, bottom
                    Point2D(attachment.x, outside_bottom), # Outside, bottom
                    Point2D(attachment.x, outside_top),    # Outside, top
                ]

            polygons.append(Polygon(exterior=vertices))
            current_depth = layer_bottom

        # Build layer metadata
        layer_info = []
        for i, layer in enumerate(self.pavement_layers):
            layer_dict = {
                'layer_index': i,
                'type': type(layer).__name__,
                'thickness': layer.thickness,
            }
            # Add layer-specific attributes
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
                'component_type': 'TravelLane',
                'width': self.width,
                'cross_slope': self.cross_slope,
                'assembly_direction': direction,
                'traffic_direction': self.traffic_direction,
                'layer_count': len(self.pavement_layers),
                'total_depth': sum(layer.thickness for layer in self.pavement_layers),
                'layers': layer_info
            }
        )

    def validate(self) -> List[str]:
        """Validate lane parameters and pavement layers.

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Width validation
        if self.width <= 0:
            errors.append("Lane width must be positive")
        elif self.width < 2.7:
            errors.append("Lane width below minimum standard (2.7m) - consider reviewing design")
        elif self.width > 4.0:
            errors.append("Lane width exceeds typical maximum (4.0m) - verify design intent")

        # Cross slope validation
        if abs(self.cross_slope) > 0.06:
            errors.append(f"Cross slope {self.cross_slope:.1%} exceeds typical maximum (6%) - verify design")
        elif abs(self.cross_slope) < 0.015:
            errors.append(f"Cross slope {self.cross_slope:.1%} below minimum for drainage (1.5%) - verify design")

        # Pavement layer validation
        if not self.pavement_layers:
            errors.append("Lane must have at least one pavement layer")
        else:
            for i, layer in enumerate(self.pavement_layers):
                layer_errors = layer.validate()
                for error in layer_errors:
                    errors.append(f"Layer {i} ({type(layer).__name__}): {error}")

            # Check total pavement depth
            total_depth = sum(layer.thickness for layer in self.pavement_layers)
            if total_depth < 0.15:
                errors.append(f"Total pavement depth {total_depth:.3f}m below typical minimum (0.15m)")
            elif total_depth > 0.80:
                errors.append(f"Total pavement depth {total_depth:.3f}m exceeds typical maximum (0.80m)")

        return errors
