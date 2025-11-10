# Domain Model and Geometry Solver Architecture

## Overview

The architecture separates **domain representation** from **geometric realization**:

1. **Domain Model**: Describes WHAT components exist and HOW they're connected (tree/graph structure)
2. **Geometry Solver**: Takes domain model and solves for WHERE components are placed spatially
3. **Geometry Output**: The computed spatial representation (Point2D, Polygon)

This separation provides:
- Clear distinction between logical structure and spatial layout
- Domain model is pure business logic (no geometry calculations)
- Solver can use different algorithms/strategies
- Geometry is computed output, not embedded in components

---

## Domain Model Structure

### Tree-Like Representation

The section is represented as a tree/linked structure where components explicitly connect to each other:

```
RoadSection
└── ControlPoint (grade point)
    └── TravelLane
        └── TravelLane
            └── Shoulder
                └── FillSlope
```

Or for a divided road:

```
RoadSection
├── Left Half
│   └── ControlPoint (left edge of traveled way)
│       └── TravelLane
│           └── TravelLane
│               └── Shoulder
│                   └── FillSlope
│
└── Right Half
    └── Median
        └── ControlPoint (right edge of traveled way)
            └── TravelLane
                └── TravelLane
                    └── Shoulder
                        └── CutSlope
```

### Domain Model Classes

```python
from dataclasses import dataclass, field
from typing import Optional, List
from abc import ABC, abstractmethod

@dataclass
class ControlPoint:
    """Reference point for cross-section (grade point/crown)"""
    x: float = 0.0              # Horizontal position
    elevation: float = 0.0       # Vertical elevation
    location_type: str = "crown" # "crown", "edge_tw", "median_cl"

    # For divided roads
    attachment_offset_x: float = 0.0  # Horizontal offset if needed

@dataclass
class ComponentNode(ABC):
    """Base class for components in domain model"""
    # Dimensional properties (what the component IS)
    name: str = ""

    # Connectivity (how it connects to other components)
    next_component: Optional['ComponentNode'] = None

    @abstractmethod
    def get_properties(self) -> dict:
        """Return component properties for solver"""
        pass

@dataclass
class TravelLane(ComponentNode):
    """Travel lane in domain model"""
    width: float = 3.6
    cross_slope: float = 0.02
    direction: str = "forward"
    surface_type: str = "asphalt"

    def get_properties(self) -> dict:
        return {
            'type': 'TravelLane',
            'width': self.width,
            'cross_slope': self.cross_slope,
            'direction': self.direction,
            'surface_type': self.surface_type
        }

@dataclass
class Shoulder(ComponentNode):
    """Shoulder in domain model"""
    width: float = 2.4
    cross_slope: float = 0.04
    paved: bool = True

    def get_properties(self) -> dict:
        return {
            'type': 'Shoulder',
            'width': self.width,
            'cross_slope': self.cross_slope,
            'paved': self.paved
        }

@dataclass
class Curb(ComponentNode):
    """Curb in domain model"""
    width: float = 0.15
    height: float = 0.15
    curb_type: str = "barrier"

    def get_properties(self) -> dict:
        return {
            'type': 'Curb',
            'width': self.width,
            'height': self.height,
            'curb_type': self.curb_type
        }

@dataclass
class FillSlope(ComponentNode):
    """Fill slope in domain model"""
    horizontal_ratio: float = 2.0
    vertical_ratio: float = 1.0
    height: float = 3.0

    def get_properties(self) -> dict:
        return {
            'type': 'FillSlope',
            'h_ratio': self.horizontal_ratio,
            'v_ratio': self.vertical_ratio,
            'height': self.height
        }

@dataclass
class RoadSection:
    """Complete road section - domain model"""
    name: str
    control_point: ControlPoint
    first_component: Optional[ComponentNode] = None

    def add_component(self, component: ComponentNode) -> 'RoadSection':
        """Add component to chain"""
        if self.first_component is None:
            self.first_component = component
        else:
            # Find last component and attach
            current = self.first_component
            while current.next_component is not None:
                current = current.next_component
            current.next_component = component
        return self

    def get_component_chain(self) -> List[ComponentNode]:
        """Return ordered list of components"""
        components = []
        current = self.first_component
        while current is not None:
            components.append(current)
            current = current.next_component
        return components
```

### Building a Section (Domain Model)

```python
# Create domain model (no geometry yet!)
section = RoadSection(
    name="Rural Highway",
    control_point=ControlPoint(x=0, elevation=0, location_type="crown")
)

# Build component chain
lane1 = TravelLane(width=3.6, cross_slope=0.02, name="Lane 1")
lane2 = TravelLane(width=3.6, cross_slope=0.02, name="Lane 2")
shoulder = Shoulder(width=2.4, cross_slope=0.04, paved=True, name="Paved Shoulder")
slope = FillSlope(horizontal_ratio=2.0, vertical_ratio=1.0, height=3.0, name="Fill Slope")

# Connect components
lane1.next_component = lane2
lane2.next_component = shoulder
shoulder.next_component = slope

section.first_component = lane1

# Or use fluent builder API
section = (RoadSection("Rural Highway", ControlPoint(0, 0))
    .add_component(TravelLane(width=3.6, name="Lane 1"))
    .add_component(TravelLane(width=3.6, name="Lane 2"))
    .add_component(Shoulder(width=2.4, name="Shoulder"))
    .add_component(FillSlope(h_ratio=2.0, v_ratio=1.0, height=3.0, name="Slope")))
```

At this point, we have a **domain model** describing the section structure. No geometry has been computed.

---

## Geometry Solver

The solver takes the domain model and computes spatial placement using the insertion point/attachment point logic.

### Solver Interface

```python
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class ConnectionPoint:
    """Geometric point where components connect"""
    x: float
    y: float
    description: str = ""

@dataclass
class ComponentGeometry:
    """Geometric representation of a component"""
    polygons: List[Polygon]
    polylines: List[List[Point2D]]
    metadata: dict

@dataclass
class SectionGeometry:
    """Complete geometric realization of section"""
    components: List[Tuple[ComponentNode, ComponentGeometry]]
    control_point: ConnectionPoint

    def get_total_width(self) -> float:
        """Calculate total section width"""
        if not self.components:
            return 0.0
        last_geom = self.components[-1][1]
        if last_geom.polygons:
            bounds = last_geom.polygons[0].bounds()
            return bounds[2]  # max_x
        return 0.0

class GeometrySolver:
    """Solves for component geometry from domain model"""

    def solve(self, section: RoadSection) -> SectionGeometry:
        """
        Solve for geometry given domain model.

        Args:
            section: Domain model describing components and connectivity

        Returns:
            SectionGeometry with computed spatial placement
        """
        geometries = []

        # Start at control point
        current_attachment = ConnectionPoint(
            x=section.control_point.x + section.control_point.attachment_offset_x,
            y=section.control_point.elevation,
            description=f"Control point ({section.control_point.location_type})"
        )

        # Process component chain
        components = section.get_component_chain()
        for component in components:
            # Get insertion point for this component
            insertion = self._get_insertion_point(component, current_attachment)

            # Compute geometry for this component
            geom = self._compute_geometry(component, insertion)
            geometries.append((component, geom))

            # Get attachment point for next component
            current_attachment = self._get_attachment_point(component, insertion, geom)

        return SectionGeometry(
            components=geometries,
            control_point=ConnectionPoint(
                section.control_point.x,
                section.control_point.elevation,
                "Control Point"
            )
        )

    def _get_insertion_point(
        self,
        component: ComponentNode,
        previous_attachment: ConnectionPoint
    ) -> ConnectionPoint:
        """
        Determine where component inserts (snaps to previous attachment).

        Default: component inserts at previous attachment point.
        Can be overridden for special cases (e.g., barrier with offset).
        """
        props = component.get_properties()
        component_type = props['type']

        # Special case: Barrier with lateral offset
        if component_type == 'Barrier' and 'offset' in props:
            return ConnectionPoint(
                x=previous_attachment.x + props['offset'],
                y=previous_attachment.y,
                description=f"{component.name} base (offset)"
            )

        # Default: insert at previous attachment
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description=f"{component.name} insertion"
        )

    def _compute_geometry(
        self,
        component: ComponentNode,
        insertion: ConnectionPoint
    ) -> ComponentGeometry:
        """
        Compute geometry for component given insertion point.

        This is where the spatial calculation happens.
        """
        props = component.get_properties()
        component_type = props['type']

        if component_type == 'TravelLane':
            return self._compute_lane_geometry(props, insertion)
        elif component_type == 'Shoulder':
            return self._compute_shoulder_geometry(props, insertion)
        elif component_type == 'Curb':
            return self._compute_curb_geometry(props, insertion)
        elif component_type == 'FillSlope':
            return self._compute_slope_geometry(props, insertion)
        else:
            raise ValueError(f"Unknown component type: {component_type}")

    def _compute_lane_geometry(
        self,
        props: dict,
        insertion: ConnectionPoint
    ) -> ComponentGeometry:
        """Compute travel lane geometry"""
        width = props['width']
        cross_slope = props['cross_slope']

        # Calculate outside edge with cross-slope
        outside_x = insertion.x + width
        outside_y = insertion.y - (width * cross_slope)

        # Create rectangular polygon
        points = [
            Point2D(insertion.x, insertion.y),      # Inside edge, top
            Point2D(outside_x, outside_y),          # Outside edge, top
            Point2D(outside_x, 0),                  # Outside edge, bottom
            Point2D(insertion.x, 0),                # Inside edge, bottom
        ]

        return ComponentGeometry(
            polygons=[Polygon(exterior=points)],
            polylines=[],
            metadata=props
        )

    def _compute_shoulder_geometry(
        self,
        props: dict,
        insertion: ConnectionPoint
    ) -> ComponentGeometry:
        """Compute shoulder geometry"""
        width = props['width']
        cross_slope = props['cross_slope']

        outside_x = insertion.x + width
        outside_y = insertion.y - (width * cross_slope)

        points = [
            Point2D(insertion.x, insertion.y),
            Point2D(outside_x, outside_y),
            Point2D(outside_x, 0),
            Point2D(insertion.x, 0),
        ]

        return ComponentGeometry(
            polygons=[Polygon(exterior=points)],
            polylines=[],
            metadata=props
        )

    def _compute_curb_geometry(
        self,
        props: dict,
        insertion: ConnectionPoint
    ) -> ComponentGeometry:
        """Compute curb geometry with vertical face"""
        width = props['width']
        height = props['height']

        # Curb creates vertical offset
        points = [
            Point2D(insertion.x, insertion.y),              # Base left
            Point2D(insertion.x, insertion.y + height),     # Top left (vertical)
            Point2D(insertion.x + width, insertion.y + height),  # Top right
            Point2D(insertion.x + width, insertion.y),      # Base right
        ]

        return ComponentGeometry(
            polygons=[Polygon(exterior=points)],
            polylines=[],
            metadata=props
        )

    def _compute_slope_geometry(
        self,
        props: dict,
        insertion: ConnectionPoint
    ) -> ComponentGeometry:
        """Compute slope geometry"""
        h_ratio = props['h_ratio']
        v_ratio = props['v_ratio']
        height = props['height']

        # Calculate horizontal extent
        horizontal_extent = abs(height * h_ratio / v_ratio)

        # Triangular slope
        points = [
            Point2D(insertion.x, insertion.y),              # Toe
            Point2D(insertion.x + horizontal_extent, insertion.y - height),  # Top
            Point2D(insertion.x + horizontal_extent, -10),  # Bottom of section
            Point2D(insertion.x, -10),                      # Toe bottom
        ]

        return ComponentGeometry(
            polygons=[Polygon(exterior=points)],
            polylines=[],
            metadata=props
        )

    def _get_attachment_point(
        self,
        component: ComponentNode,
        insertion: ConnectionPoint,
        geometry: ComponentGeometry
    ) -> ConnectionPoint:
        """
        Determine where next component attaches.

        Based on component type and computed geometry.
        """
        props = component.get_properties()
        component_type = props['type']

        if component_type in ['TravelLane', 'Shoulder']:
            # Attach at outside edge with cross-slope
            width = props['width']
            cross_slope = props['cross_slope']
            return ConnectionPoint(
                x=insertion.x + width,
                y=insertion.y - (width * cross_slope),
                description=f"{component.name} outside edge"
            )

        elif component_type == 'Curb':
            # Attach at top of curb (elevated)
            width = props['width']
            height = props['height']
            return ConnectionPoint(
                x=insertion.x + width,
                y=insertion.y + height,
                description=f"{component.name} top"
            )

        elif component_type == 'FillSlope':
            # Attach at top of slope
            h_ratio = props['h_ratio']
            v_ratio = props['v_ratio']
            height = props['height']
            horizontal_extent = abs(height * h_ratio / v_ratio)
            return ConnectionPoint(
                x=insertion.x + horizontal_extent,
                y=insertion.y - height,
                description=f"{component.name} top"
            )

        else:
            # Default: no change
            return insertion
```

---

## Usage Example

### 1. Create Domain Model

```python
# Define the section structure (what components and how they connect)
section = RoadSection(
    name="Rural Two-Lane Highway",
    control_point=ControlPoint(x=0, elevation=0, location_type="crown")
)

# Build component chain
section.add_component(TravelLane(width=3.6, cross_slope=0.02, name="NB Lane"))
section.add_component(TravelLane(width=3.6, cross_slope=0.02, name="SB Lane"))
section.add_component(Shoulder(width=2.4, cross_slope=0.04, paved=True, name="Shoulder"))
section.add_component(FillSlope(h_ratio=2.0, v_ratio=1.0, height=3.0, name="Fill"))
```

### 2. Solve for Geometry

```python
# Use solver to compute spatial placement
solver = GeometrySolver()
geometry = solver.solve(section)

# Now we have computed geometry
print(f"Total width: {geometry.get_total_width():.2f}m")

# Access geometry for each component
for component, geom in geometry.components:
    print(f"{component.name}:")
    for polygon in geom.polygons:
        bounds = polygon.bounds()
        print(f"  Bounds: x=[{bounds[0]:.2f}, {bounds[2]:.2f}], "
              f"y=[{bounds[1]:.2f}, {bounds[3]:.2f}]")
```

### 3. Export Geometry

```python
# Export using adapters
from cross_section.adapters.cadquery_adapter import CadQueryAdapter
from cross_section.export.dxf_exporter import DXFExporter

exporter = DXFExporter()
exporter.export(geometry, 'section.dxf')
```

---

## Benefits of This Separation

### 1. Clear Separation of Concerns
- **Domain Model**: Business logic, connectivity, properties
- **Geometry Solver**: Spatial calculation, placement algorithm
- **Geometry Output**: Pure data (Point2D, Polygon)

### 2. Flexible Solver Strategies

Different solvers for different needs:

```python
class GeometrySolver:
    """Standard solver"""
    pass

class SuperelevationSolver(GeometrySolver):
    """Solver that handles superelevation in curves"""
    def solve(self, section: RoadSection) -> SectionGeometry:
        # Apply banking calculations
        pass

class OptimizingSolver(GeometrySolver):
    """Solver that optimizes for minimum earthwork"""
    def solve(self, section: RoadSection) -> SectionGeometry:
        # Optimization algorithm
        pass
```

### 3. Domain Model is Portable

The domain model has **no geometry calculations**, so it's:
- Easy to serialize (JSON, YAML)
- Easy to store (database)
- Easy to version
- Easy to validate (check properties, not geometry)

```python
# Serialize domain model
import json

def serialize_section(section: RoadSection) -> str:
    """Serialize domain model to JSON"""
    components = []
    for comp in section.get_component_chain():
        components.append({
            'type': comp.get_properties()['type'],
            'properties': comp.get_properties(),
            'name': comp.name
        })

    return json.dumps({
        'name': section.name,
        'control_point': {
            'x': section.control_point.x,
            'elevation': section.control_point.elevation,
            'location_type': section.control_point.location_type
        },
        'components': components
    })
```

### 4. Easier Testing

```python
def test_domain_model():
    """Test domain model without geometry"""
    section = RoadSection("Test", ControlPoint(0, 0))
    section.add_component(TravelLane(width=3.6))
    section.add_component(Shoulder(width=2.4))

    # Test structure
    components = section.get_component_chain()
    assert len(components) == 2
    assert components[0].get_properties()['type'] == 'TravelLane'
    assert components[1].get_properties()['type'] == 'Shoulder'
    # No geometry involved!

def test_solver():
    """Test solver separately"""
    section = RoadSection("Test", ControlPoint(0, 0))
    section.add_component(TravelLane(width=3.6, cross_slope=0.02))

    solver = GeometrySolver()
    geometry = solver.solve(section)

    # Test geometry output
    assert geometry.get_total_width() == 3.6
    assert len(geometry.components) == 1
    # Geometry is computed, can test placement
```

### 5. Validation at Domain Level

Validate the model before solving for geometry:

```python
def validate_section(section: RoadSection) -> List[str]:
    """Validate domain model (no geometry needed)"""
    errors = []

    # Check we have components
    if section.first_component is None:
        errors.append("Section has no components")
        return errors

    # Check component properties
    for component in section.get_component_chain():
        props = component.get_properties()

        # Width must be positive
        if 'width' in props and props['width'] <= 0:
            errors.append(f"{component.name}: width must be positive")

        # Cross-slope must be reasonable
        if 'cross_slope' in props and abs(props['cross_slope']) > 0.10:
            errors.append(f"{component.name}: cross-slope > 10% is unusual")

    return errors
```

---

## Architecture Layers Revisited

```
┌─────────────────────────────────────────┐
│  DOMAIN MODEL                           │
│  • RoadSection                          │
│  • ComponentNode (Lane, Shoulder, etc.) │
│  • ControlPoint                         │
│  • Pure structure/connectivity          │
│  • No geometry calculations             │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  GEOMETRY SOLVER                        │
│  • Takes domain model as input          │
│  • Computes spatial placement           │
│  • Returns geometry output              │
│  • Can have multiple solver strategies  │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  GEOMETRY OUTPUT                        │
│  • Point2D, Polygon                     │
│  • SectionGeometry                      │
│  • Pure spatial data                    │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│  ADAPTERS & EXPORT                      │
│  • Convert to library formats           │
│  • Export to DXF, SVG, etc.            │
└─────────────────────────────────────────┘
```

---

## Summary

**Domain Model (Tree/List Structure):**
- Describes WHAT components exist
- Describes HOW they're connected
- Component properties (width, slope, height)
- NO geometry calculations
- Serializable, portable, easy to validate

**Geometry Solver:**
- Takes domain model as input
- SOLVES for spatial placement
- Uses insertion/attachment point logic
- Produces geometry output
- Can be swapped (standard, superelevation, optimizing)

**Geometry Output:**
- Pure spatial data (Point2D, Polygon)
- Result of solver
- Used by exporters

This separation is cleaner and more flexible than having components compute their own geometry!
