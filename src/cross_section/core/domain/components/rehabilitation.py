"""Rehabilitation components for pavement overlay, notch, and widening.

These components support roadway rehabilitation scenarios where:
- Existing pavement serves as a reference for overlay/widening operations
- Overlays are placed on top of existing pavement (vertical stacking)
- Notches are cut into existing pavement edges for mechanical bonding
- Widening extends the pavement structure with new full-depth construction
"""

from dataclasses import dataclass, field

from ...geometry.primitives import ComponentGeometry, ConnectionPoint, Point2D, Polygon
from ..base import Direction, RoadComponent
from ..pavement import PavementLayer


@dataclass
class ExistingPavement(RoadComponent):
    """Reference component representing existing pavement to be rehabilitated.

    This component generates geometry for the existing pavement structure and
    provides the reference points for overlay and widening components.

    The component spans from the centerline (control point) outward to the
    edge of existing pavement. Both left and right sides should be created
    to represent the full existing pavement width.

    Attributes:
        half_width: Distance from centerline to edge of existing pavement (meters)
        total_depth: Total depth of existing pavement structure (meters)
        cross_slope: Cross slope of existing surface (positive = down from crown)
    """

    half_width: float
    total_depth: float
    cross_slope: float = 0.02

    def get_insertion_point(
        self, previous_attachment: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Existing pavement inserts at the control point (centerline).

        Args:
            previous_attachment: The attachment point from the previous component
                (typically the control point)
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The insertion point at centerline
        """
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description=f"ExistingPavement insertion ({direction})",
        )

    def get_attachment_point(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Calculate attachment at edge of existing pavement.

        Args:
            insertion: This component's insertion point (at centerline)
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The attachment point at the existing pavement edge, at surface elevation
        """
        # Surface drops due to cross slope
        surface_drop = self.half_width * self.cross_slope

        if direction == "right":
            return ConnectionPoint(
                x=insertion.x + self.half_width,
                y=insertion.y - surface_drop,
                description=f"ExistingPavement attachment ({direction})",
            )
        else:  # left
            return ConnectionPoint(
                x=insertion.x - self.half_width,
                y=insertion.y - surface_drop,
                description=f"ExistingPavement attachment ({direction})",
            )

    def to_geometry(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ComponentGeometry:
        """Create existing pavement geometry as a simple rectangular cross-section.

        Args:
            insertion: This component's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            ComponentGeometry with a single polygon representing existing pavement
        """
        attachment = self.get_attachment_point(insertion, direction)

        # Create a simple rectangular representation of existing pavement
        # Top surface follows cross slope, bottom is flat (simplified)
        if direction == "right":
            vertices = [
                Point2D(insertion.x, insertion.y),  # Inside top (crown)
                Point2D(attachment.x, attachment.y),  # Outside top (edge)
                Point2D(attachment.x, attachment.y - self.total_depth),  # Outside bottom
                Point2D(insertion.x, insertion.y - self.total_depth),  # Inside bottom
            ]
        else:  # left
            vertices = [
                Point2D(insertion.x, insertion.y),  # Inside top (crown)
                Point2D(insertion.x, insertion.y - self.total_depth),  # Inside bottom
                Point2D(attachment.x, attachment.y - self.total_depth),  # Outside bottom
                Point2D(attachment.x, attachment.y),  # Outside top (edge)
            ]

        polygon = Polygon(exterior=vertices)

        return ComponentGeometry(
            polygons=[polygon],
            metadata={
                "component_type": "ExistingPavement",
                "half_width": self.half_width,
                "total_depth": self.total_depth,
                "cross_slope": self.cross_slope,
                "assembly_direction": direction,
            },
        )

    def validate(self) -> list[str]:
        """Validate existing pavement parameters.

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        if self.half_width <= 0:
            errors.append("Half width must be positive")
        elif self.half_width < 1.0:
            errors.append(
                f"Half width {self.half_width:.2f}m is very narrow - verify design"
            )

        if self.total_depth <= 0:
            errors.append("Total depth must be positive")
        elif self.total_depth < 0.1:
            errors.append(
                f"Total depth {self.total_depth:.3f}m below typical minimum (0.1m)"
            )
        elif self.total_depth > 1.0:
            errors.append(
                f"Total depth {self.total_depth:.3f}m exceeds typical maximum (1.0m)"
            )

        if abs(self.cross_slope) > 0.06:
            errors.append(
                f"Cross slope {self.cross_slope:.1%} exceeds typical maximum (6%)"
            )

        return errors


@dataclass
class MillAndOverlay(RoadComponent):
    """Milling and overlay operations on existing pavement.

    This component supports:
    - Full or partial width coverage (can be less than existing pavement width)
    - Milling (removal) of existing surface material
    - One or more overlay layers
    - Optional leveling/shimming course for irregular surfaces

    The component generates geometry that sits ON TOP of the previous component
    (existing pavement), with the attachment point at the outer edge of the
    overlay at the finished surface elevation.

    Attributes:
        width: Width of milling/overlay from centerline (can be < existing width)
        mill_depth: Depth of material removed from existing surface (0 if no milling)
        overlay_layers: List of pavement layers for the overlay
        leveling_thickness: Optional variable-thickness leveling course
        cross_slope: Cross slope of finished surface
    """

    width: float
    mill_depth: float = 0.0
    overlay_layers: list[PavementLayer] = field(default_factory=list)
    leveling_thickness: float = 0.0  # Average thickness of leveling course
    cross_slope: float = 0.02

    def get_insertion_point(
        self, previous_attachment: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Overlay inserts at the previous attachment point.

        For rehabilitation, this is typically the edge of existing pavement,
        but the overlay generates geometry that extends back toward centerline.

        Args:
            previous_attachment: The attachment point from ExistingPavement
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The insertion point (same as previous attachment)
        """
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description=f"MillAndOverlay insertion ({direction})",
        )

    def get_attachment_point(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Calculate attachment at outer edge of overlay, at finished surface.

        The attachment point:
        - X: At the outer edge of the overlay (which may be at or inside the
             existing pavement edge)
        - Y: Elevated by net overlay thickness (overlay - milling + leveling)

        Args:
            insertion: This component's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The attachment point for the next component (NotchAndWidening)
        """
        # Net elevation change: overlay adds, milling removes
        overlay_thickness = sum(layer.thickness for layer in self.overlay_layers)
        net_elevation_change = (
            overlay_thickness - self.mill_depth + self.leveling_thickness
        )

        # Attachment is at the same X as insertion (outer edge of overlay),
        # but elevated by net overlay thickness
        return ConnectionPoint(
            x=insertion.x,
            y=insertion.y + net_elevation_change,
            description=f"MillAndOverlay attachment ({direction})",
        )

    def to_geometry(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ComponentGeometry:
        """Create overlay geometry that sits on top of existing pavement.

        Generates polygons for:
        1. Milling void (if mill_depth > 0) - shown as removal
        2. Leveling course (if leveling_thickness > 0)
        3. Each overlay layer

        Args:
            insertion: This component's insertion point (at existing pavement edge)
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            ComponentGeometry with overlay layer polygons
        """
        polygons = []

        # Calculate the centerline position (where overlay extends to)
        # The insertion is at the existing pavement edge, overlay extends inward
        if direction == "right":
            centerline_x = insertion.x - self.width
            edge_x = insertion.x
        else:  # left
            centerline_x = insertion.x + self.width
            edge_x = insertion.x

        # Start at the existing surface (insertion.y) minus any milling
        current_surface_centerline = insertion.y - self.mill_depth
        # Account for cross slope across the width
        current_surface_edge = (
            insertion.y - self.mill_depth + self.width * self.cross_slope
        )

        # Generate leveling course if present (variable thickness, simplified as constant)
        if self.leveling_thickness > 0:
            leveling_top_centerline = current_surface_centerline + self.leveling_thickness
            leveling_top_edge = current_surface_edge + self.leveling_thickness

            if direction == "right":
                vertices = [
                    Point2D(centerline_x, leveling_top_centerline),
                    Point2D(edge_x, leveling_top_edge),
                    Point2D(edge_x, current_surface_edge),
                    Point2D(centerline_x, current_surface_centerline),
                ]
            else:  # left
                vertices = [
                    Point2D(centerline_x, leveling_top_centerline),
                    Point2D(centerline_x, current_surface_centerline),
                    Point2D(edge_x, current_surface_edge),
                    Point2D(edge_x, leveling_top_edge),
                ]

            polygons.append(Polygon(exterior=vertices))
            current_surface_centerline = leveling_top_centerline
            current_surface_edge = leveling_top_edge

        # Generate overlay layers from bottom to top
        for layer in self.overlay_layers:
            layer_top_centerline = current_surface_centerline + layer.thickness
            layer_top_edge = current_surface_edge + layer.thickness

            if direction == "right":
                vertices = [
                    Point2D(centerline_x, layer_top_centerline),
                    Point2D(edge_x, layer_top_edge),
                    Point2D(edge_x, current_surface_edge),
                    Point2D(centerline_x, current_surface_centerline),
                ]
            else:  # left
                vertices = [
                    Point2D(centerline_x, layer_top_centerline),
                    Point2D(centerline_x, current_surface_centerline),
                    Point2D(edge_x, current_surface_edge),
                    Point2D(edge_x, layer_top_edge),
                ]

            polygons.append(Polygon(exterior=vertices))
            current_surface_centerline = layer_top_centerline
            current_surface_edge = layer_top_edge

        # Build layer metadata
        layer_info = []
        for i, layer in enumerate(self.overlay_layers):
            layer_dict = {
                "layer_index": i,
                "type": type(layer).__name__,
                "thickness": layer.thickness,
            }
            if hasattr(layer, "binder_type"):
                layer_dict["binder_type"] = layer.binder_type
            layer_info.append(layer_dict)

        return ComponentGeometry(
            polygons=polygons,
            metadata={
                "component_type": "MillAndOverlay",
                "width": self.width,
                "mill_depth": self.mill_depth,
                "leveling_thickness": self.leveling_thickness,
                "overlay_thickness": sum(layer.thickness for layer in self.overlay_layers),
                "cross_slope": self.cross_slope,
                "assembly_direction": direction,
                "layer_count": len(self.overlay_layers),
                "layers": layer_info,
            },
        )

    def validate(self) -> list[str]:
        """Validate mill and overlay parameters.

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        if self.width <= 0:
            errors.append("Width must be positive")

        if self.mill_depth < 0:
            errors.append("Mill depth must be non-negative")
        elif self.mill_depth > 0.15:
            errors.append(
                f"Mill depth {self.mill_depth:.3f}m exceeds typical maximum (0.15m)"
            )

        if self.leveling_thickness < 0:
            errors.append("Leveling thickness must be non-negative")

        overlay_thickness = sum(layer.thickness for layer in self.overlay_layers)
        if overlay_thickness <= 0 and self.mill_depth == 0:
            errors.append("Must have overlay layers or milling operation")

        for i, layer in enumerate(self.overlay_layers):
            layer_errors = layer.validate()
            for error in layer_errors:
                errors.append(f"Overlay layer {i} ({type(layer).__name__}): {error}")

        return errors


@dataclass
class NotchAndWidening(RoadComponent):
    """Notch cut into existing pavement edge plus full-depth widening.

    This component creates the mechanical bond between existing and new pavement:
    - Notch: A cut into the existing pavement edge to create a keyed joint
    - Widening: Full-depth new pavement structure adjacent to the notch

    The notch depth should match or exceed the full pavement depth to ensure
    proper mechanical interlock. The widening uses the same layer structure
    as the original pavement to maintain structural continuity.

    Attributes:
        notch_depth: Vertical depth of notch cut into existing pavement
        notch_horizontal: Horizontal extent of notch (typically ≈ notch_depth for 1:1)
        widening_width: Horizontal width of new full-depth pavement
        widening_layers: Full pavement layer stack for widening
        cross_slope: Cross slope for finished surface
    """

    notch_depth: float
    notch_horizontal: float
    widening_width: float
    widening_layers: list[PavementLayer] = field(default_factory=list)
    cross_slope: float = 0.04  # Typically steeper on shoulders

    def get_insertion_point(
        self, previous_attachment: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Notch and widening inserts at the overlay edge (or existing edge).

        Args:
            previous_attachment: The attachment point from MillAndOverlay
                (at finished overlay surface at pavement edge)
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The insertion point (same as previous attachment)
        """
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description=f"NotchAndWidening insertion ({direction})",
        )

    def get_attachment_point(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Calculate attachment at outer edge of widening.

        Args:
            insertion: This component's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The attachment point at outer edge of widening, at finished surface
        """
        # Total horizontal extent: notch + widening
        total_width = self.notch_horizontal + self.widening_width

        # Surface drop due to cross slope across the widening
        surface_drop = total_width * self.cross_slope

        if direction == "right":
            return ConnectionPoint(
                x=insertion.x + total_width,
                y=insertion.y - surface_drop,
                description=f"NotchAndWidening attachment ({direction})",
            )
        else:  # left
            return ConnectionPoint(
                x=insertion.x - total_width,
                y=insertion.y - surface_drop,
                description=f"NotchAndWidening attachment ({direction})",
            )

    def to_geometry(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ComponentGeometry:
        """Create notch and widening geometry.

        Generates polygons for:
        1. Notch fill (pavement layers filling the notch void)
        2. Widening layers (full-depth pavement structure)

        Args:
            insertion: This component's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            ComponentGeometry with notch and widening layer polygons
        """
        polygons = []
        attachment = self.get_attachment_point(insertion, direction)

        # Calculate key X positions
        if direction == "right":
            notch_inside_x = insertion.x
            notch_outside_x = insertion.x + self.notch_horizontal
            widening_outside_x = attachment.x
        else:  # left
            notch_inside_x = insertion.x
            notch_outside_x = insertion.x - self.notch_horizontal
            widening_outside_x = attachment.x

        # Generate layer-by-layer geometry
        # The notch and widening share the same layer structure
        current_depth = 0.0
        total_depth = sum(layer.thickness for layer in self.widening_layers)

        for layer in self.widening_layers:
            layer_top_depth = current_depth
            layer_bottom_depth = current_depth + layer.thickness

            # Calculate elevations at each position
            # Surface drops with cross slope from insertion to attachment
            slope_per_unit = self.cross_slope

            # Notch inside (at insertion)
            notch_inside_top_y = insertion.y - layer_top_depth
            notch_inside_bottom_y = insertion.y - layer_bottom_depth

            # Notch outside
            notch_slope_drop = self.notch_horizontal * slope_per_unit
            notch_outside_top_y = insertion.y - notch_slope_drop - layer_top_depth
            notch_outside_bottom_y = insertion.y - notch_slope_drop - layer_bottom_depth

            # Widening outside (at attachment)
            widening_outside_top_y = attachment.y - layer_top_depth
            widening_outside_bottom_y = attachment.y - layer_bottom_depth

            # Create combined notch + widening polygon for this layer
            if direction == "right":
                vertices = [
                    Point2D(notch_inside_x, notch_inside_top_y),  # Notch inside top
                    Point2D(notch_outside_x, notch_outside_top_y),  # Notch outside top
                    Point2D(widening_outside_x, widening_outside_top_y),  # Widening outside top
                    Point2D(widening_outside_x, widening_outside_bottom_y),  # Widening outside bottom
                    Point2D(notch_outside_x, notch_outside_bottom_y),  # Notch outside bottom
                    Point2D(notch_inside_x, notch_inside_bottom_y),  # Notch inside bottom
                ]
            else:  # left
                vertices = [
                    Point2D(notch_inside_x, notch_inside_top_y),  # Notch inside top
                    Point2D(notch_inside_x, notch_inside_bottom_y),  # Notch inside bottom
                    Point2D(notch_outside_x, notch_outside_bottom_y),  # Notch outside bottom
                    Point2D(widening_outside_x, widening_outside_bottom_y),  # Widening outside bottom
                    Point2D(widening_outside_x, widening_outside_top_y),  # Widening outside top
                    Point2D(notch_outside_x, notch_outside_top_y),  # Notch outside top
                ]

            polygons.append(Polygon(exterior=vertices))
            current_depth = layer_bottom_depth

        # Build layer metadata
        layer_info = []
        for i, layer in enumerate(self.widening_layers):
            layer_dict = {
                "layer_index": i,
                "type": type(layer).__name__,
                "thickness": layer.thickness,
            }
            if hasattr(layer, "binder_type"):
                layer_dict["binder_type"] = layer.binder_type
            if hasattr(layer, "material_type"):
                layer_dict["material_type"] = layer.material_type
            layer_info.append(layer_dict)

        return ComponentGeometry(
            polygons=polygons,
            metadata={
                "component_type": "NotchAndWidening",
                "notch_depth": self.notch_depth,
                "notch_horizontal": self.notch_horizontal,
                "widening_width": self.widening_width,
                "total_width": self.notch_horizontal + self.widening_width,
                "cross_slope": self.cross_slope,
                "assembly_direction": direction,
                "layer_count": len(self.widening_layers),
                "total_depth": sum(layer.thickness for layer in self.widening_layers),
                "layers": layer_info,
            },
        )

    def validate(self) -> list[str]:
        """Validate notch and widening parameters.

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        if self.notch_depth <= 0:
            errors.append("Notch depth must be positive")

        if self.notch_horizontal <= 0:
            errors.append("Notch horizontal extent must be positive")

        if self.widening_width <= 0:
            errors.append("Widening width must be positive")

        if not self.widening_layers:
            errors.append("Widening must have at least one pavement layer")

        total_layer_depth = sum(layer.thickness for layer in self.widening_layers)
        if total_layer_depth < self.notch_depth:
            errors.append(
                f"Widening layer depth ({total_layer_depth:.3f}m) should match or "
                f"exceed notch depth ({self.notch_depth:.3f}m)"
            )

        for i, layer in enumerate(self.widening_layers):
            layer_errors = layer.validate()
            for error in layer_errors:
                errors.append(f"Widening layer {i} ({type(layer).__name__}): {error}")

        if abs(self.cross_slope) > 0.08:
            errors.append(
                f"Cross slope {self.cross_slope:.1%} exceeds typical maximum (8%)"
            )

        return errors
