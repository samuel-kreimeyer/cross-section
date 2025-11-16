"""Curb and gutter components."""

from dataclasses import dataclass
from typing import List
from ..base import RoadComponent, Direction
from ..pavement import ConcreteLayer
from ...geometry.primitives import ConnectionPoint, ComponentGeometry, Polygon, Point2D


@dataclass
class Curb(RoadComponent):
    """A curb and gutter component.

    A curb consists of two parts:
    1. Gutter (horizontal portion): Attaches to adjacent component, slopes away
    2. Curb (vertical portion): Rises from outer edge of gutter

    Attributes:
        gutter_width: Width of gutter in meters (can be 0 for curb-only)
        gutter_thickness: Depth/thickness of gutter slab in meters
        gutter_drop: Vertical drop from attachment point to outer edge (typically 0.025m/1in)
        curb_height: Height of curb above gutter surface in meters
        curb_width_bottom: Width of curb at base (at gutter surface) in meters
        curb_width_top: Width of curb at top in meters (≤ bottom width for battered face)
        concrete: Concrete specification for the curb and gutter
    """

    gutter_width: float  # meters
    gutter_thickness: float = 0.15  # 150mm typical
    gutter_drop: float = 0.025  # 25mm (1 inch) typical drop
    curb_height: float = 0.15  # 150mm (6 inch) typical barrier curb
    curb_width_bottom: float = 0.15  # 150mm (6 inch) typical
    curb_width_top: float = 0.15  # 150mm (6 inch) typical (vertical face)
    concrete: ConcreteLayer = None

    def __post_init__(self):
        """Set default concrete if not provided."""
        if self.concrete is None:
            self.concrete = ConcreteLayer(
                thickness=self.gutter_thickness,
                compressive_strength=28.0,  # 28 MPa (4000 psi) typical
                reinforced=False,
                steel_per_cy=None
            )

    def get_insertion_point(
        self, previous_attachment: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Curb snaps directly to previous component's attachment point.

        Args:
            previous_attachment: The attachment point from the previous component
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The insertion point (same as previous attachment)
        """
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description=f"Curb insertion ({direction})"
        )

    def get_attachment_point(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ConnectionPoint:
        """Calculate the back of curb (outer edge).

        The attachment point is at the back of the curb, at the top of gutter surface.

        Args:
            insertion: This curb's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            The attachment point at the back of curb
        """
        total_width = self.gutter_width + self.curb_width_bottom
        attachment_y = insertion.y - self.gutter_drop

        if direction == 'right':
            return ConnectionPoint(
                x=insertion.x + total_width,
                y=attachment_y,
                description=f"Curb attachment ({direction})"
            )
        else:  # left
            return ConnectionPoint(
                x=insertion.x - total_width,
                y=attachment_y,
                description=f"Curb attachment ({direction})"
            )

    def to_geometry(
        self, insertion: ConnectionPoint, direction: Direction
    ) -> ComponentGeometry:
        """Create curb and gutter geometry as a single polygon.

        The geometry includes both the gutter (sloped horizontal portion) and
        the curb (vertical portion with optional battered face).

        Args:
            insertion: This curb's insertion point
            direction: Assembly direction ('left' or 'right' from control point)

        Returns:
            ComponentGeometry with a single polygon representing curb and gutter
        """
        if direction == 'right':
            vertices = self._create_right_geometry(insertion)
        else:
            vertices = self._create_left_geometry(insertion)

        polygon = Polygon(exterior=vertices)

        return ComponentGeometry(
            polygons=[polygon],
            metadata={
                'component_type': 'Curb',
                'gutter_width': self.gutter_width,
                'gutter_thickness': self.gutter_thickness,
                'gutter_drop': self.gutter_drop,
                'curb_height': self.curb_height,
                'curb_width_bottom': self.curb_width_bottom,
                'curb_width_top': self.curb_width_top,
                'assembly_direction': direction,
                'concrete_strength': self.concrete.compressive_strength,
                'layers': [
                    {
                        'layer_index': 0,
                        'type': 'ConcreteLayer',
                        'thickness': self.gutter_thickness,
                        'compressive_strength': self.concrete.compressive_strength,
                    }
                ]
            }
        )

    def _create_right_geometry(self, insertion: ConnectionPoint) -> List[Point2D]:
        """Create geometry for right-side curb.

        Returns vertices in counter-clockwise order for right side.
        Creates a 7-vertex polygon with continuous bottom slope.
        """
        # Top inside of gutter (attachment point)
        p1 = Point2D(insertion.x, insertion.y)

        # Top outside of gutter (at outer edge, with drop)
        gutter_outer_y = insertion.y - self.gutter_drop
        p2 = Point2D(insertion.x + self.gutter_width, gutter_outer_y)

        # Front of curb at top (battered face - narrower than bottom)
        p3 = Point2D(
            insertion.x + self.gutter_width + self.curb_width_top,
            gutter_outer_y + self.curb_height
        )

        # Back of curb at top
        p4 = Point2D(
            insertion.x + self.gutter_width + self.curb_width_bottom,
            gutter_outer_y + self.curb_height
        )

        # Back of curb at gutter surface level
        p5 = Point2D(
            insertion.x + self.gutter_width + self.curb_width_bottom,
            gutter_outer_y
        )

        # Bottom outside of curb (continuous with gutter bottom)
        p6 = Point2D(
            insertion.x + self.gutter_width + self.curb_width_bottom,
            insertion.y - self.gutter_thickness
        )

        # Bottom inside of gutter (straight slope from inside to outside)
        p7 = Point2D(insertion.x, insertion.y - self.gutter_thickness)

        return [p1, p2, p3, p4, p5, p6, p7]

    def _create_left_geometry(self, insertion: ConnectionPoint) -> List[Point2D]:
        """Create geometry for left-side curb.

        Returns vertices in counter-clockwise order for left side.
        Creates a 7-vertex polygon with continuous bottom slope.
        """
        # Top inside of gutter (attachment point)
        p1 = Point2D(insertion.x, insertion.y)

        # Bottom inside of gutter
        p7 = Point2D(insertion.x, insertion.y - self.gutter_thickness)

        # Bottom outside of curb (continuous with gutter bottom)
        gutter_outer_y = insertion.y - self.gutter_drop
        p6 = Point2D(
            insertion.x - self.gutter_width - self.curb_width_bottom,
            insertion.y - self.gutter_thickness
        )

        # Back of curb at gutter surface level
        p5 = Point2D(
            insertion.x - self.gutter_width - self.curb_width_bottom,
            gutter_outer_y
        )

        # Back of curb at top
        p4 = Point2D(
            insertion.x - self.gutter_width - self.curb_width_bottom,
            gutter_outer_y + self.curb_height
        )

        # Front of curb at top (battered face - narrower than bottom)
        p3 = Point2D(
            insertion.x - self.gutter_width - self.curb_width_top,
            gutter_outer_y + self.curb_height
        )

        # Top outside of gutter (at outer edge, with drop)
        p2 = Point2D(insertion.x - self.gutter_width, gutter_outer_y)

        return [p1, p7, p6, p5, p4, p3, p2]

    def validate(self) -> List[str]:
        """Validate curb and gutter parameters.

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Gutter validation
        if self.gutter_width < 0:
            errors.append("Gutter width must be non-negative")
        elif self.gutter_width > 1.0:
            errors.append(f"Gutter width {self.gutter_width:.2f}m exceeds typical maximum (1.0m)")

        if self.gutter_thickness <= 0:
            errors.append("Gutter thickness must be positive")
        elif self.gutter_thickness < 0.10:
            errors.append(f"Gutter thickness {self.gutter_thickness:.3f}m below typical minimum (0.10m)")

        if self.gutter_drop < 0:
            errors.append("Gutter drop must be non-negative")
        elif self.gutter_drop > 0.10:
            errors.append(f"Gutter drop {self.gutter_drop:.3f}m exceeds typical maximum (0.10m)")

        # Curb validation
        if self.curb_height < 0:
            errors.append("Curb height must be non-negative")
        elif self.curb_height > 0.30:
            errors.append(f"Curb height {self.curb_height:.3f}m exceeds typical maximum for barrier curbs (0.30m)")

        if self.curb_width_bottom < 0:
            errors.append("Curb bottom width must be non-negative")
        elif self.curb_width_bottom > 0.30:
            errors.append(f"Curb bottom width {self.curb_width_bottom:.3f}m exceeds typical maximum (0.30m)")

        if self.curb_width_top < 0:
            errors.append("Curb top width must be non-negative")
        elif self.curb_width_top > self.curb_width_bottom:
            errors.append(
                f"Curb top width {self.curb_width_top:.3f}m exceeds bottom width "
                f"{self.curb_width_bottom:.3f}m (curb face would overhang)"
            )

        # Concrete validation
        if self.concrete:
            concrete_errors = self.concrete.validate()
            for error in concrete_errors:
                errors.append(f"Concrete: {error}")

        return errors
