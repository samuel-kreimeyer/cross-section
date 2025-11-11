"""Road section assembly and coordination."""

from dataclasses import dataclass, field
from typing import List
from .base import RoadComponent, Direction
from ..geometry.primitives import ConnectionPoint, ComponentGeometry


@dataclass
class ControlPoint:
    """Reference point for cross-section assembly (typically the crown/grade point).

    The control point provides the initial attachment point for the first component.
    All components are positioned relative to this point.

    Attributes:
        x: Horizontal position (typically 0 for centerline)
        elevation: Vertical position (grade elevation)
        description: Optional description of this control point
    """

    x: float
    elevation: float
    description: str = "Control Point"

    def to_connection_point(self) -> ConnectionPoint:
        """Convert to a ConnectionPoint for component attachment."""
        return ConnectionPoint(x=self.x, y=self.elevation, description=self.description)


@dataclass
class SectionGeometry:
    """Complete geometry for a road section.

    Attributes:
        components: List of component geometries in assembly order
        metadata: Section-level metadata
    """

    components: List[ComponentGeometry] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def bounds(self) -> tuple[float, float, float, float]:
        """Calculate bounding box of entire section.

        Returns:
            Tuple of (min_x, min_y, max_x, max_y)
        """
        if not self.components:
            return (0.0, 0.0, 0.0, 0.0)

        all_bounds = [comp.bounds() for comp in self.components]
        min_x = min(b[0] for b in all_bounds)
        min_y = min(b[1] for b in all_bounds)
        max_x = max(b[2] for b in all_bounds)
        max_y = max(b[3] for b in all_bounds)

        return (min_x, min_y, max_x, max_y)


@dataclass
class RoadSection:
    """Coordinates assembly of road components into a complete cross-section.

    The RoadSection class is responsible for:
    - Managing the sequence of components on left and right sides
    - Coordinating geometric assembly (translating attachment points)
    - Validating the complete section
    - Generating the final geometry

    Components can be added to either side of the control point and automatically
    snap together using insertion and attachment points.

    Typical section: Left Shoulder ← Left Lane ← Control Point → Right Lane → Right Shoulder

    Attributes:
        name: Descriptive name for this section
        control_point: Reference point for assembly (typically crown/grade point)
        left_components: Components extending left (negative X) from control point
        right_components: Components extending right (positive X) from control point
    """

    name: str
    control_point: ControlPoint
    left_components: List[RoadComponent] = field(default_factory=list)
    right_components: List[RoadComponent] = field(default_factory=list)

    def add_component_left(self, component: RoadComponent) -> None:
        """Add a component to the left side of the control point.

        Left components extend in the negative X direction from the control point.

        Args:
            component: The component to add
        """
        self.left_components.append(component)

    def add_component_right(self, component: RoadComponent) -> None:
        """Add a component to the right side of the control point.

        Right components extend in the positive X direction from the control point.

        Args:
            component: The component to add
        """
        self.right_components.append(component)

    def add_component(self, component: RoadComponent, direction: Direction) -> None:
        """Add a component to the specified side of the control point.

        Args:
            component: The component to add
            direction: Which side to add the component ('left' or 'right')
        """
        if direction == 'left':
            self.add_component_left(component)
        else:
            self.add_component_right(component)

    def validate(self) -> List[str]:
        """Validate the complete section.

        This validates:
        - Each component's individual parameters
        - Geometric continuity between components
        - Section-level rules

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Basic validation
        if not self.left_components and not self.right_components:
            errors.append("Section must contain at least one component")
            return errors

        # Validate left components
        for i, component in enumerate(self.left_components):
            component_errors = component.validate()
            for error in component_errors:
                errors.append(f"Left component {i} ({type(component).__name__}): {error}")

        # Validate right components
        for i, component in enumerate(self.right_components):
            component_errors = component.validate()
            for error in component_errors:
                errors.append(f"Right component {i} ({type(component).__name__}): {error}")

        # Validate geometric continuity for left side
        current_attachment = self.control_point.to_connection_point()
        for i, component in enumerate(self.left_components):
            try:
                insertion = component.get_insertion_point(current_attachment, 'left')
                current_attachment = component.get_attachment_point(insertion, 'left')
            except Exception as e:
                errors.append(f"Left component {i} ({type(component).__name__}): Failed geometric calculation - {e}")

        # Validate geometric continuity for right side
        current_attachment = self.control_point.to_connection_point()
        for i, component in enumerate(self.right_components):
            try:
                insertion = component.get_insertion_point(current_attachment, 'right')
                current_attachment = component.get_attachment_point(insertion, 'right')
            except Exception as e:
                errors.append(f"Right component {i} ({type(component).__name__}): Failed geometric calculation - {e}")

        return errors

    def to_geometry(self) -> SectionGeometry:
        """Generate complete section geometry by coordinating component assembly.

        This method:
        1. Starts from the control point for both left and right sides
        2. For each component, calculates its insertion point based on previous attachment
        3. Generates component geometry at the insertion point with correct direction
        4. Uses component's attachment point for next component's insertion

        Returns:
            SectionGeometry containing all component geometries (left side first, then right side)
        """
        geometries = []

        # Assemble left components (extending in negative X direction)
        current_attachment = self.control_point.to_connection_point()
        for component in self.left_components:
            insertion = component.get_insertion_point(current_attachment, 'left')
            component_geom = component.to_geometry(insertion, 'left')
            geometries.append(component_geom)
            current_attachment = component.get_attachment_point(insertion, 'left')

        # Assemble right components (extending in positive X direction)
        current_attachment = self.control_point.to_connection_point()
        for component in self.right_components:
            insertion = component.get_insertion_point(current_attachment, 'right')
            component_geom = component.to_geometry(insertion, 'right')
            geometries.append(component_geom)
            current_attachment = component.get_attachment_point(insertion, 'right')

        return SectionGeometry(
            components=geometries,
            metadata={
                'name': self.name,
                'control_point': {
                    'x': self.control_point.x,
                    'elevation': self.control_point.elevation
                },
                'left_component_count': len(self.left_components),
                'right_component_count': len(self.right_components),
                'total_component_count': len(self.left_components) + len(self.right_components)
            }
        )

    def __repr__(self) -> str:
        total = len(self.left_components) + len(self.right_components)
        return f"RoadSection('{self.name}', {total} components: {len(self.left_components)} left, {len(self.right_components)} right)"
