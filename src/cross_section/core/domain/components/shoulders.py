"""Shoulder components."""

from dataclasses import dataclass, field
from typing import List, Literal
from ..base import RoadComponent, Direction
from ..pavement import PavementLayer, AsphaltLayer, CrushedRockLayer
from ...geometry.primitives import ConnectionPoint, ComponentGeometry, Polygon, Point2D


ShoulderType = Literal['fully_paved', 'paved_top_slumped']


@dataclass
class Shoulder(RoadComponent):
    """A paved or unpaved shoulder adjacent to travel lanes.

    Two types of paved shoulders are supported:

    1. **Fully paved (fully_paved)**: All layers extend to foreslope as trapezoids
       - Each layer extends: paved_width + depth * foreslope_ratio
       - All layers follow the same foreslope angle

    2. **Paved top with slumped asphalt (paved_top_slumped)**:
       - Asphalt layers slump at 1:1 (each layer extends by its thickness)
       - Lower asphalt layers extend to match upper layer bottom width
       - Crushed rock base extends from asphalt edge to foreslope
       - Creates a more complex composite shape

    Attributes:
        width: Paved shoulder width in meters
        cross_slope: Cross slope of paved portion (positive slopes down away from lane)
        foreslope_ratio: Horizontal:vertical ratio for foreslope (e.g., 6.0 for 6:1)
        shoulder_type: Type of shoulder ('fully_paved' or 'paved_top_slumped')
        paved: Whether shoulder is paved (if False, uses minimal base layer)
        pavement_layers: List of pavement layers (only if paved=True)
    """

    width: float
    cross_slope: float = 0.02  # 2% default
    foreslope_ratio: float = 6.0  # 6:1 (6 horizontal : 1 vertical)
    shoulder_type: ShoulderType = 'fully_paved'
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
        """Calculate the outside edge of the shoulder.

        For fully_paved shoulders: attachment is at the outer edge of paved width.
        For paved_top_slumped shoulders: attachment is at the outermost extent of
        the base material (where foreslope begins).

        Args:
            insertion: This shoulder's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The attachment point at the outer edge of shoulder
        """
        drop = self.width * self.cross_slope
        surface_at_paved_edge = insertion.y - drop

        if self.shoulder_type == 'paved_top_slumped':
            # For slumped shoulders, attachment is at outermost extent of base
            # The base extends along the foreslope from the paved edge
            total_depth = sum(layer.thickness for layer in self.pavement_layers)
            base_extension = total_depth * self.foreslope_ratio

            # The attachment elevation follows the foreslope down from paved edge
            # Starting at surface_at_paved_edge, dropping total_depth vertically
            attachment_y = surface_at_paved_edge - total_depth

            if direction == 'right':
                return ConnectionPoint(
                    x=insertion.x + self.width + base_extension,
                    y=attachment_y,
                    description=f"Shoulder attachment ({direction})"
                )
            else:  # left
                return ConnectionPoint(
                    x=insertion.x - self.width - base_extension,
                    y=attachment_y,
                    description=f"Shoulder attachment ({direction})"
                )
        else:  # fully_paved
            # For fully paved, attachment is at paved edge
            if direction == 'right':
                return ConnectionPoint(
                    x=insertion.x + self.width,
                    y=surface_at_paved_edge,
                    description=f"Shoulder attachment ({direction})"
                )
            else:  # left
                return ConnectionPoint(
                    x=insertion.x - self.width,
                    y=surface_at_paved_edge,
                    description=f"Shoulder attachment ({direction})"
                )

    def to_geometry(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ComponentGeometry:
        """Create shoulder geometry based on shoulder type.

        Args:
            insertion: This shoulder's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            ComponentGeometry with one trapezoid polygon per pavement layer
        """
        if self.shoulder_type == 'fully_paved':
            return self._create_fully_paved_geometry(insertion, direction)
        else:  # 'paved_top_slumped'
            return self._create_slumped_geometry(insertion, direction)

    def _create_fully_paved_geometry(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ComponentGeometry:
        """Create fully paved shoulder where all layers extend to foreslope.

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

        return self._build_geometry(polygons, direction)

    def _create_slumped_geometry(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ComponentGeometry:
        """Create slumped shoulder where asphalt slumps at 1:1 and base extends to foreslope.

        - Asphalt layers slump at 1:1 (each layer extends by its thickness)
        - Lower asphalt layers' tops match upper layers' bottom widths
        - Crushed rock base extends from asphalt edge to overall foreslope

        Args:
            insertion: This shoulder's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            ComponentGeometry with trapezoid polygons for each layer
        """
        polygons = []
        current_depth = 0.0

        # Calculate surface elevation at paved edge
        surface_at_paved_edge = insertion.y - self.width * self.cross_slope

        # Separate asphalt and crushed rock layers
        asphalt_layers = [layer for layer in self.pavement_layers if isinstance(layer, AsphaltLayer)]
        base_layers = [layer for layer in self.pavement_layers if isinstance(layer, CrushedRockLayer)]

        # Track current outside width (starts at paved width)
        current_outside_width = self.width

        # Process asphalt layers with 1:1 slump
        for layer in asphalt_layers:
            layer_top_depth = current_depth
            layer_bottom_depth = current_depth + layer.thickness

            # Inside edge (at insertion point)
            inside_top_y = insertion.y - layer_top_depth
            inside_bottom_y = insertion.y - layer_bottom_depth

            # Outside edge elevations
            outside_top_y = surface_at_paved_edge - layer_top_depth
            outside_bottom_y = surface_at_paved_edge - layer_bottom_depth

            # For asphalt: 1:1 slump means horizontal extension = thickness
            top_outside_width = current_outside_width
            bottom_outside_width = current_outside_width + layer.thickness

            if direction == 'right':
                outside_top_x = insertion.x + top_outside_width
                outside_bottom_x = insertion.x + bottom_outside_width

                vertices = [
                    Point2D(insertion.x, inside_top_y),        # Inside, top
                    Point2D(outside_top_x, outside_top_y),     # Outside, top
                    Point2D(outside_bottom_x, outside_bottom_y), # Outside, bottom
                    Point2D(insertion.x, inside_bottom_y),     # Inside, bottom
                ]
            else:  # left
                outside_top_x = insertion.x - top_outside_width
                outside_bottom_x = insertion.x - bottom_outside_width

                vertices = [
                    Point2D(insertion.x, inside_top_y),        # Inside, top
                    Point2D(insertion.x, inside_bottom_y),     # Inside, bottom
                    Point2D(outside_bottom_x, outside_bottom_y), # Outside, bottom
                    Point2D(outside_top_x, outside_top_y),     # Outside, top
                ]

            polygons.append(Polygon(exterior=vertices))
            current_depth = layer_bottom_depth
            current_outside_width = bottom_outside_width

        # Process crushed rock base layers extending to foreslope
        # The base creates a 5-vertex irregular polygon filling the space between
        # the inside edge, slumped asphalt edge, paved edge, and foreslope
        for layer in base_layers:
            layer_top_depth = current_depth
            layer_bottom_depth = current_depth + layer.thickness

            # Inside edge (at insertion point)
            inside_top_y = insertion.y - layer_top_depth
            inside_bottom_y = insertion.y - layer_bottom_depth

            # Outside top at slumped asphalt edge
            # This is where the asphalt layers ended (current_outside_width from asphalt processing)
            outside_slumped_y = surface_at_paved_edge - layer_top_depth

            # Top outside at paved edge (where first asphalt layer starts)
            # This point is at the surface level at the paved edge
            paved_edge_y = surface_at_paved_edge

            # Bottom outside follows foreslope from paved edge
            outside_bottom_y = surface_at_paved_edge - layer_bottom_depth
            bottom_extension = layer_bottom_depth * self.foreslope_ratio

            if direction == 'right':
                # 5-vertex polygon:
                # 1. Inside top (at base of asphalt stack)
                # 2. Outside top at slumped asphalt edge
                # 3. Outside at paved edge (surface level - connects to asphalt)
                # 4. Outside bottom (foreslope intercept)
                # 5. Inside bottom
                vertices = [
                    Point2D(insertion.x, inside_top_y),                              # 1: Inside top
                    Point2D(insertion.x + current_outside_width, outside_slumped_y), # 2: Slumped edge top
                    Point2D(insertion.x + self.width, paved_edge_y),                 # 3: Paved edge (surface)
                    Point2D(insertion.x + self.width + bottom_extension, outside_bottom_y), # 4: Foreslope intercept
                    Point2D(insertion.x, inside_bottom_y),                           # 5: Inside bottom
                ]
            else:  # left
                vertices = [
                    Point2D(insertion.x, inside_top_y),                              # 1: Inside top
                    Point2D(insertion.x, inside_bottom_y),                           # 5: Inside bottom
                    Point2D(insertion.x - self.width - bottom_extension, outside_bottom_y), # 4: Foreslope intercept
                    Point2D(insertion.x - self.width, paved_edge_y),                 # 3: Paved edge (surface)
                    Point2D(insertion.x - current_outside_width, outside_slumped_y), # 2: Slumped edge top
                ]

            polygons.append(Polygon(exterior=vertices))
            current_depth = layer_bottom_depth

        return self._build_geometry(polygons, direction)

    def _build_geometry(
        self, polygons: List[Polygon], direction: Direction
    ) -> ComponentGeometry:
        """Build ComponentGeometry with metadata from polygons.

        Args:
            polygons: List of layer polygons
            direction: Assembly direction

        Returns:
            ComponentGeometry with metadata
        """
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
                'shoulder_type': self.shoulder_type,
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
