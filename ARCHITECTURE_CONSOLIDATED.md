# Cross-Section Architecture (Consolidated)

## Core Principle

**Components create their own geometry** given an insertion point. The **RoadSection coordinates** the assembly by managing attachment points and translating coordinates.

No separate "solver" class needed - the section IS the solver.

---

## Architecture Overview

```
┌─────────────────────────────────────────┐
│  RoadSection                            │
│  • Manages component chain              │
│  • Coordinates geometry generation      │
│  • Translates attachment points         │
│  • Validates assembly                   │
└─────────────────────────────────────────┘
              ↓ calls
┌─────────────────────────────────────────┐
│  Components (Lane, Shoulder, Curb...)   │
│  • Know their own attributes            │
│  • Create their own geometry            │
│  • Define insertion/attachment points   │
└─────────────────────────────────────────┘
              ↓ produces
┌─────────────────────────────────────────┐
│  Geometry (Point2D, Polygon)            │
│  • Pure spatial data                    │
│  • Used by exporters                    │
└─────────────────────────────────────────┘
```

---

## Component Interface

Each component type has different attributes with different meanings, but all implement:

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List

@dataclass
class ConnectionPoint:
    """Where components connect"""
    x: float
    y: float
    description: str = ""

class RoadComponent(ABC):
    """Base interface for all road components"""

    @abstractmethod
    def get_insertion_point(self, previous_attachment: ConnectionPoint) -> ConnectionPoint:
        """
        Where this component begins (usually snaps to previous attachment).
        Can be overridden for special cases (e.g., barrier with offset).
        """
        pass

    @abstractmethod
    def get_attachment_point(self, insertion: ConnectionPoint) -> ConnectionPoint:
        """
        Where next component attaches (based on this component's geometry).
        """
        pass

    @abstractmethod
    def to_geometry(self, insertion: ConnectionPoint) -> ComponentGeometry:
        """
        Create this component's geometry given insertion point.
        Each component type implements its own geometry logic.
        """
        pass

    def validate(self) -> List[str]:
        """
        Validate component properties (can be overridden).
        Default: check basic constraints.
        """
        return []
```

---

## Example Components

### TravelLane

```python
@dataclass
class TravelLane(RoadComponent):
    """Travel lane with width and cross-slope"""
    width: float = 3.6
    cross_slope: float = 0.02
    direction: str = "forward"
    surface_type: str = "asphalt"

    def get_insertion_point(self, previous_attachment: ConnectionPoint) -> ConnectionPoint:
        """Lane inserts at previous attachment (snaps together)"""
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description=f"Lane inside edge"
        )

    def get_attachment_point(self, insertion: ConnectionPoint) -> ConnectionPoint:
        """Next component attaches at outside edge with cross-slope"""
        return ConnectionPoint(
            x=insertion.x + self.width,
            y=insertion.y - (self.width * self.cross_slope),
            description=f"Lane outside edge"
        )

    def to_geometry(self, insertion: ConnectionPoint) -> ComponentGeometry:
        """Create rectangular lane geometry"""
        attachment = self.get_attachment_point(insertion)

        points = [
            Point2D(insertion.x, insertion.y),
            Point2D(attachment.x, attachment.y),
            Point2D(attachment.x, 0),
            Point2D(insertion.x, 0),
        ]

        return ComponentGeometry(
            polygons=[Polygon(exterior=points)],
            metadata={'type': 'TravelLane', 'width': self.width}
        )

    def validate(self) -> List[str]:
        """Validate lane properties"""
        errors = []
        if self.width <= 0:
            errors.append("Lane width must be positive")
        if abs(self.cross_slope) > 0.10:
            errors.append("Cross-slope > 10% is unusual")
        return errors
```

### Curb

```python
@dataclass
class Curb(RoadComponent):
    """Curb with vertical offset"""
    width: float = 0.15
    height: float = 0.15
    curb_type: str = "barrier"

    def get_insertion_point(self, previous_attachment: ConnectionPoint) -> ConnectionPoint:
        """Curb inserts at pavement edge"""
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description="Curb base"
        )

    def get_attachment_point(self, insertion: ConnectionPoint) -> ConnectionPoint:
        """Next component attaches at TOP of curb (elevated)"""
        return ConnectionPoint(
            x=insertion.x + self.width,
            y=insertion.y + self.height,  # Elevation change!
            description="Curb top"
        )

    def to_geometry(self, insertion: ConnectionPoint) -> ComponentGeometry:
        """Create curb profile with vertical face"""
        attachment = self.get_attachment_point(insertion)

        points = [
            Point2D(insertion.x, insertion.y),
            Point2D(insertion.x, attachment.y),      # Vertical face
            Point2D(attachment.x, attachment.y),
            Point2D(attachment.x, insertion.y),
        ]

        return ComponentGeometry(
            polygons=[Polygon(exterior=points)],
            metadata={'type': 'Curb', 'height': self.height}
        )
```

---

## RoadSection: The Coordinator

The section object contains methods for composing components, translating coordinates, and validation.

```python
@dataclass
class RoadSection:
    """
    Complete road cross-section.
    Coordinates component geometry generation and validates assembly.
    """
    name: str
    control_point: ControlPoint
    components: List[RoadComponent] = field(default_factory=list)

    def add_component(self, component: RoadComponent) -> 'RoadSection':
        """Add component to section (builder pattern)"""
        self.components.append(component)
        return self

    def to_geometry(self) -> SectionGeometry:
        """
        Generate complete section geometry.
        Section coordinates geometry generation and translates attachment points.
        """
        geometries = []

        # Start at control point
        current_attachment = ConnectionPoint(
            x=self.control_point.x,
            y=self.control_point.elevation,
            description="Control point"
        )

        # Process each component
        for component in self.components:
            # Component determines its insertion point (usually snaps to attachment)
            insertion = component.get_insertion_point(current_attachment)

            # Component creates its own geometry
            geom = component.to_geometry(insertion)
            geometries.append((component, geom))

            # Component determines where next one attaches
            current_attachment = component.get_attachment_point(insertion)

        return SectionGeometry(components=geometries)

    def validate(self) -> List[str]:
        """
        Validate section assembly.
        Section contains validation logic.
        """
        errors = []

        # Check we have components
        if not self.components:
            errors.append("Section has no components")
            return errors

        # Validate each component's properties
        for i, component in enumerate(self.components):
            component_errors = component.validate()
            for err in component_errors:
                errors.append(f"Component {i} ({type(component).__name__}): {err}")

        # Validate connections (geometric continuity)
        current_attachment = ConnectionPoint(
            self.control_point.x,
            self.control_point.elevation
        )

        for i, component in enumerate(self.components):
            insertion = component.get_insertion_point(current_attachment)

            # Check insertion matches attachment (within tolerance)
            dx = abs(insertion.x - current_attachment.x)
            dy = abs(insertion.y - current_attachment.y)

            if dx > 0.001 or dy > 0.001:  # 1mm tolerance
                errors.append(
                    f"Component {i} ({type(component).__name__}) insertion "
                    f"({insertion.x:.3f}, {insertion.y:.3f}) doesn't match "
                    f"previous attachment ({current_attachment.x:.3f}, "
                    f"{current_attachment.y:.3f})"
                )

            current_attachment = component.get_attachment_point(insertion)

        return errors

    def get_total_width(self) -> float:
        """Calculate total section width"""
        if not self.components:
            return 0.0

        # Get final attachment point
        current_attachment = ConnectionPoint(
            self.control_point.x,
            self.control_point.elevation
        )

        for component in self.components:
            insertion = component.get_insertion_point(current_attachment)
            current_attachment = component.get_attachment_point(insertion)

        return current_attachment.x - self.control_point.x
```

---

## Key Design Decisions

### 1. Components Create Their Own Geometry

**Why:** Each component type has different attributes with different meanings.
- Lane: width + cross_slope → rectangle
- Curb: width + height → vertical face
- Slope: h_ratio + v_ratio + height → triangle

Each component knows how to translate its attributes into geometry.

### 2. Section Coordinates Assembly

**What section does:**
- Manages component list
- Calls each component with correct insertion point
- **Translates coordinates** based on attachment points
- Validates overall assembly

**What section doesn't do:**
- Know specifics of component geometry (that's component's job)
- Hard-code component types (extensible)

### 3. Attachment Points Enable Composition

Components snap together via attachment points:
```
Lane → attachment at (3.6, -0.072)
  ↓
Curb inserts at (3.6, -0.072)
  → attachment at (3.75, 0.078)  [elevated!]
  ↓
Sidewalk inserts at (3.75, 0.078)  [starts on top of curb]
```

Section translates these coordinates automatically.

### 4. Validation Lives in Section

Section validates:
- Component properties (calls component.validate())
- Geometric continuity (insertion matches attachment)
- Overall assembly constraints

---

## Usage Example

### Build Section

```python
# Create section
section = RoadSection(
    name="Urban Street",
    control_point=ControlPoint(x=0, elevation=0, location_type="crown")
)

# Add components (each knows its own attributes and geometry)
section.add_component(TravelLane(width=3.3, cross_slope=0.02))
section.add_component(TravelLane(width=3.3, cross_slope=0.02))
section.add_component(Curb(width=0.15, height=0.15))
section.add_component(Sidewalk(width=1.8, cross_slope=0.02))
```

### Validate

```python
# Section validates assembly
errors = section.validate()
if errors:
    for error in errors:
        print(f"❌ {error}")
else:
    print("✅ Section valid")
```

### Generate Geometry

```python
# Section coordinates geometry generation
geometry = section.to_geometry()

print(f"Total width: {section.get_total_width():.2f}m")

# Access component geometries
for component, geom in geometry.components:
    print(f"{type(component).__name__}: {len(geom.polygons)} polygons")
```

### Export

```python
# Use adapters for export
from cross_section.adapters.cadquery_adapter import CadQueryAdapter
from cross_section.export.dxf_exporter import DXFExporter

exporter = DXFExporter()
exporter.export(geometry, 'street.dxf')
```

---

## Benefits

✅ **Clear Responsibilities**
- Component: knows its attributes, creates its geometry
- Section: coordinates assembly, validates, translates coordinates

✅ **Extensible**
- New component types: implement interface
- No changes to RoadSection needed

✅ **Components are Self-Contained**
- Each component type has different attributes
- Geometry logic matches component's nature

✅ **Section is the Coordinator**
- Contains composition methods
- Translates attachment points
- Validates assembly

✅ **Pure Python Core**
- Components: pure Python (dataclasses, math)
- Section: pure Python (coordinate management)
- Vendorable to VIKTOR without dependencies

---

## Comparison to Previous Docs

### ❌ What Was Wrong

**domain_and_solver.md** had:
- Separate GeometrySolver class (unnecessary complexity)
- Components return properties dict (too generic)
- Solver has all geometry logic (components can't be self-contained)

**connection_model.md** had:
- Right idea (components create geometry)
- But didn't show section's coordination role clearly
- Validation logic location unclear

### ✅ What's Correct Now

- **Components create their own geometry** (different attributes → different logic)
- **Section coordinates assembly** (manages attachment points)
- **Section validates** (geometric continuity + component properties)
- **No separate solver class** (section IS the coordinator)

---

## Pure Python Core

Everything described here is pure Python:
```python
# Only stdlib imports
from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List
import math  # For any calculations
```

**Vendorable to VIKTOR:** Copy entire core module without dependencies.

**Adapters are separate:** CadQuery, Shapely used ONLY in export/validation adapters.

---

## Summary

**Component Responsibilities:**
1. Define attributes (width, slope, height, etc.)
2. Create own geometry given insertion point
3. Define attachment point based on geometry
4. Validate own properties

**Section Responsibilities:**
1. Manage component list
2. Coordinate geometry generation
3. Translate coordinates via attachment points
4. Validate overall assembly

**Architecture:**
- No separate solver class
- Section coordinates, components execute
- Clean, simple, extensible
- Pure Python core for VIKTOR vendoring
