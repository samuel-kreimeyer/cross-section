"""Road section assembly and coordination."""

from dataclasses import dataclass, field
from typing import List
from .base import RoadComponent
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
    - Managing the sequence of components
    - Coordinating geometric assembly (translating attachment points)
    - Validating the complete section
    - Generating the final geometry

    Components are added in sequence and automatically snap together using
    insertion and attachment points.

    Attributes:
        name: Descriptive name for this section
        control_point: Reference point for assembly (typically crown/grade point)
        components: List of components in assembly order
    """

    name: str
    control_point: ControlPoint
    components: List[RoadComponent] = field(default_factory=list)

    def add_component(self, component: RoadComponent) -> None:
        """Add a component to the section.

        Components are added in sequence and will snap together during geometry generation.

        Args:
            component: The component to add
        """
        self.components.append(component)

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
        if not self.components:
            errors.append("Section must contain at least one component")
            return errors

        # Validate each component
        for i, component in enumerate(self.components):
            component_errors = component.validate()
            for error in component_errors:
                errors.append(f"Component {i} ({type(component).__name__}): {error}")

        # Validate geometric continuity
        # (This will be expanded as we add more component types)
        current_attachment = self.control_point.to_connection_point()

        for i, component in enumerate(self.components):
            try:
                insertion = component.get_insertion_point(current_attachment)
                current_attachment = component.get_attachment_point(insertion)
            except Exception as e:
                errors.append(f"Component {i} ({type(component).__name__}): Failed geometric calculation - {e}")

        return errors

    def to_geometry(self) -> SectionGeometry:
        """Generate complete section geometry by coordinating component assembly.

        This method:
        1. Starts from the control point
        2. For each component, calculates its insertion point based on previous attachment
        3. Generates component geometry at the insertion point
        4. Uses component's attachment point for next component's insertion

        Returns:
            SectionGeometry containing all component geometries
        """
        geometries = []
        current_attachment = self.control_point.to_connection_point()

        for component in self.components:
            # Calculate where this component begins (snaps to previous attachment)
            insertion = component.get_insertion_point(current_attachment)

            # Generate this component's geometry
            component_geom = component.to_geometry(insertion)
            geometries.append(component_geom)

            # Calculate where next component will attach
            current_attachment = component.get_attachment_point(insertion)

        return SectionGeometry(
            components=geometries,
            metadata={
                'name': self.name,
                'control_point': {
                    'x': self.control_point.x,
                    'elevation': self.control_point.elevation
                },
                'component_count': len(self.components)
            }
        )

    def __repr__(self) -> str:
        return f"RoadSection('{self.name}', {len(self.components)} components)"
