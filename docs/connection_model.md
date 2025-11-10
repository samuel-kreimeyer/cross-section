# Component Connection Model

## Overview

Components connect geometrically through **insertion points** and **attachment points**. Rather than categorical connection types (FLUSH/RAISED/SLOPED), components define specific geometric locations where they connect, and components naturally "snap together" at these points.

## Connection Principles

### Insertion Point
**Where this component connects to the previous component.**

The insertion point is the geometric location (x, y) where this component begins. It snaps to the previous component's attachment point.

### Attachment Point
**Where the next component connects to this component.**

The attachment point is the geometric location (x, y) where the next component will begin. It defines where subsequent components snap to.

### Snap-Together Model

Components form a continuous geometric chain:

```
Control Point
    ↓ (attachment point)
    ┌─────────────┐
    │   Lane 1    │ ← insertion point snaps to control point
    └─────────────┘
                  ↓ (attachment point)
                  ┌─────────────┐
                  │   Lane 2    │ ← insertion point snaps to Lane 1
                  └─────────────┘
                                ↓ (attachment point)
                                ┌─────────────┐
                                │  Shoulder   │ ← snaps to Lane 2
                                └─────────────┘
```

The geometry naturally handles:
- Vertical offsets (curbs create elevation changes)
- Slope transitions (slopes connect at their toe)
- Pavement edges (lanes/shoulders meet at edge of pavement)

---

## Component Interface

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class ConnectionPoint:
    """Geometric point where components connect"""
    x: float                    # Horizontal position (meters)
    y: float                    # Vertical position (meters)
    description: str = ""       # Optional description

class RoadComponent(ABC):
    """Base interface for all road components"""

    @abstractmethod
    def get_insertion_point(self, previous_attachment: ConnectionPoint) -> ConnectionPoint:
        """
        Return the point where this component inserts/begins.

        Args:
            previous_attachment: The attachment point from the previous component

        Returns:
            ConnectionPoint where this component begins (usually same as previous_attachment)
        """
        pass

    @abstractmethod
    def get_attachment_point(self, insertion_point: ConnectionPoint) -> ConnectionPoint:
        """
        Return the point where next component attaches.

        Args:
            insertion_point: Where this component was inserted

        Returns:
            ConnectionPoint where next component should begin
        """
        pass

    @abstractmethod
    def to_geometry(self, insertion_point: ConnectionPoint) -> ComponentGeometry:
        """
        Generate component geometry from insertion point.

        Args:
            insertion_point: Where component begins

        Returns:
            ComponentGeometry with polygons defining this component
        """
        pass
```

---

## Control Point (Special Case)

The control point is the origin of the section. It has no insertion point (it's the first element), but provides an attachment point for the first actual component.

```python
@dataclass
class ControlPoint:
    """Reference point for cross-section geometry"""
    x: float = 0.0              # Horizontal position
    elevation: float = 0.0      # Vertical position (datum)
    location_type: str = "crown" # "crown", "median_cl", "edge_tw"

    # For divided roads with offset median
    attachment_offset_x: float = 0.0  # Horizontal offset for attachment

    def get_attachment_point(self) -> ConnectionPoint:
        """Return point where first component attaches"""
        return ConnectionPoint(
            x=self.x + self.attachment_offset_x,
            y=self.elevation,
            description=f"Control point ({self.location_type})"
        )
```

**Special Cases:**
- **Undivided road**: Insertion and attachment at same point (crown)
- **Divided road**: May attach at edge of traveled way with offset for median width
- **Vertical alignment**: Attachment could be offset vertically to match edge of traveled way

---

## Example Implementations

### Travel Lane

```python
@dataclass
class TravelLane(RoadComponent):
    """Standard travel lane"""
    width: float = 3.6          # meters
    cross_slope: float = 0.02   # decimal (2%)

    def get_insertion_point(self, previous_attachment: ConnectionPoint) -> ConnectionPoint:
        """Lane inserts at top inside edge (previous component's attachment)"""
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description="Lane inside edge (top of pavement)"
        )

    def get_attachment_point(self, insertion_point: ConnectionPoint) -> ConnectionPoint:
        """Next component attaches at outside edge of lane"""
        # Calculate outside edge position with cross-slope
        outside_x = insertion_point.x + self.width
        outside_y = insertion_point.y - (self.width * self.cross_slope)

        return ConnectionPoint(
            x=outside_x,
            y=outside_y,
            description="Lane outside edge (top of pavement)"
        )

    def to_geometry(self, insertion_point: ConnectionPoint) -> ComponentGeometry:
        """Generate lane geometry from insertion point"""
        attachment = self.get_attachment_point(insertion_point)

        # Rectangle with cross-slope
        points = [
            Point2D(insertion_point.x, insertion_point.y),      # Inside edge, top
            Point2D(attachment.x, attachment.y),                 # Outside edge, top
            Point2D(attachment.x, 0),                           # Outside edge, bottom
            Point2D(insertion_point.x, 0),                      # Inside edge, bottom
        ]

        return ComponentGeometry(
            polygons=[Polygon(exterior=points)],
            metadata={'type': 'TravelLane', 'width': self.width}
        )
```

### Curb

A curb creates a vertical offset - its attachment point is elevated relative to its insertion point.

```python
@dataclass
class Curb(RoadComponent):
    """Curb with vertical face"""
    width: float = 0.15         # Base width (meters)
    height: float = 0.15        # Height (meters)
    face_angle: float = 90.0    # Degrees from horizontal

    def get_insertion_point(self, previous_attachment: ConnectionPoint) -> ConnectionPoint:
        """Curb inserts at edge of pavement (usually lane or shoulder)"""
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description="Curb base (pavement edge)"
        )

    def get_attachment_point(self, insertion_point: ConnectionPoint) -> ConnectionPoint:
        """Sidewalk/next component attaches at TOP of curb"""
        return ConnectionPoint(
            x=insertion_point.x + self.width,
            y=insertion_point.y + self.height,  # Elevated!
            description="Curb top"
        )

    def to_geometry(self, insertion_point: ConnectionPoint) -> ComponentGeometry:
        """Generate curb profile"""
        attachment = self.get_attachment_point(insertion_point)

        # Vertical face curb profile
        points = [
            Point2D(insertion_point.x, insertion_point.y),      # Base left
            Point2D(insertion_point.x, attachment.y),           # Top left (vertical face)
            Point2D(attachment.x, attachment.y),                # Top right
            Point2D(attachment.x, insertion_point.y),           # Base right
        ]

        return ComponentGeometry(
            polygons=[Polygon(exterior=points)],
            metadata={'type': 'Curb', 'height': self.height}
        )
```

### Shoulder

```python
@dataclass
class Shoulder(RoadComponent):
    """Shoulder at edge of traveled way"""
    width: float = 2.4
    cross_slope: float = 0.04   # Steeper than lane for drainage
    paved: bool = True

    def get_insertion_point(self, previous_attachment: ConnectionPoint) -> ConnectionPoint:
        """Shoulder inserts at edge of travel lane"""
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description="Shoulder inside edge (lane edge)"
        )

    def get_attachment_point(self, insertion_point: ConnectionPoint) -> ConnectionPoint:
        """Next component (slope, barrier) attaches at outside edge"""
        outside_x = insertion_point.x + self.width
        outside_y = insertion_point.y - (self.width * self.cross_slope)

        return ConnectionPoint(
            x=outside_x,
            y=outside_y,
            description="Shoulder outside edge"
        )

    def to_geometry(self, insertion_point: ConnectionPoint) -> ComponentGeometry:
        """Generate shoulder geometry"""
        attachment = self.get_attachment_point(insertion_point)

        points = [
            Point2D(insertion_point.x, insertion_point.y),
            Point2D(attachment.x, attachment.y),
            Point2D(attachment.x, 0),
            Point2D(insertion_point.x, 0),
        ]

        return ComponentGeometry(
            polygons=[Polygon(exterior=points)],
            metadata={'type': 'Shoulder', 'paved': self.paved}
        )
```

### Slope (Cut or Fill)

Slopes connect at their toe (bottom) to the previous component.

```python
@dataclass
class FillSlope(RoadComponent):
    """Fill slope (embankment)"""
    horizontal_ratio: float = 2.0   # H:V ratio
    vertical_ratio: float = 1.0
    height: float = 3.0             # Vertical drop from insertion

    def get_insertion_point(self, previous_attachment: ConnectionPoint) -> ConnectionPoint:
        """Slope inserts at toe (bottom of slope)"""
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description="Slope toe (bottom)"
        )

    def get_attachment_point(self, insertion_point: ConnectionPoint) -> ConnectionPoint:
        """Slope attaches at natural ground (top of slope)"""
        # Slope runs down and out
        horizontal_extent = abs(self.height * self.horizontal_ratio / self.vertical_ratio)

        return ConnectionPoint(
            x=insertion_point.x + horizontal_extent,
            y=insertion_point.y - self.height,
            description="Slope top (natural ground)"
        )

    def to_geometry(self, insertion_point: ConnectionPoint) -> ComponentGeometry:
        """Generate triangular slope"""
        attachment = self.get_attachment_point(insertion_point)

        # Triangular fill slope
        points = [
            Point2D(insertion_point.x, insertion_point.y),      # Toe
            Point2D(attachment.x, attachment.y),                 # Top of slope
            Point2D(attachment.x, attachment.y - 10),           # Extend down (to section bottom)
            Point2D(insertion_point.x, insertion_point.y - 10),  # Extend toe down
        ]

        return ComponentGeometry(
            polygons=[Polygon(exterior=points)],
            metadata={'type': 'FillSlope', 'ratio': f"{self.horizontal_ratio}:{self.vertical_ratio}"}
        )
```

### Sidewalk

```python
@dataclass
class Sidewalk(RoadComponent):
    """Pedestrian sidewalk"""
    width: float = 1.8
    cross_slope: float = 0.02
    thickness: float = 0.1      # Concrete thickness

    def get_insertion_point(self, previous_attachment: ConnectionPoint) -> ConnectionPoint:
        """Sidewalk inserts at curb top (if preceded by curb)"""
        return ConnectionPoint(
            x=previous_attachment.x,
            y=previous_attachment.y,
            description="Sidewalk inside edge (curb top)"
        )

    def get_attachment_point(self, insertion_point: ConnectionPoint) -> ConnectionPoint:
        """Next component attaches at outside edge of sidewalk"""
        outside_x = insertion_point.x + self.width
        outside_y = insertion_point.y - (self.width * self.cross_slope)

        return ConnectionPoint(
            x=outside_x,
            y=outside_y,
            description="Sidewalk outside edge"
        )

    def to_geometry(self, insertion_point: ConnectionPoint) -> ComponentGeometry:
        """Generate sidewalk slab"""
        attachment = self.get_attachment_point(insertion_point)

        # Top surface
        points = [
            Point2D(insertion_point.x, insertion_point.y),
            Point2D(attachment.x, attachment.y),
            Point2D(attachment.x, attachment.y - self.thickness),
            Point2D(insertion_point.x, insertion_point.y - self.thickness),
        ]

        return ComponentGeometry(
            polygons=[Polygon(exterior=points)],
            metadata={'type': 'Sidewalk', 'width': self.width}
        )
```

---

## Section Assembly Algorithm

```python
class RoadSection:
    """Complete road cross-section"""

    def __init__(self, control_point: ControlPoint):
        self.control_point = control_point
        self.components: List[RoadComponent] = []

    def add_component(self, component: RoadComponent) -> 'RoadSection':
        """Add component to section"""
        self.components.append(component)
        return self

    def to_geometry(self) -> SectionGeometry:
        """Generate complete section geometry"""
        geometries = []

        # Start at control point
        current_attachment = self.control_point.get_attachment_point()

        for component in self.components:
            # Component inserts at current attachment point
            insertion = component.get_insertion_point(current_attachment)

            # Generate geometry
            geom = component.to_geometry(insertion)
            geometries.append((component, geom))

            # Get attachment point for next component
            current_attachment = component.get_attachment_point(insertion)

        return SectionGeometry(components=geometries)
```

---

## Validation

Instead of checking categorical connection types, validation checks geometric compatibility:

```python
def validate_connections(self) -> List[str]:
    """Validate component connections"""
    errors = []

    current_attachment = self.control_point.get_attachment_point()

    for i, component in enumerate(self.components):
        insertion = component.get_insertion_point(current_attachment)

        # Check 1: Insertion point should match (or be very close to) attachment point
        dx = abs(insertion.x - current_attachment.x)
        dy = abs(insertion.y - current_attachment.y)

        if dx > 0.001 or dy > 0.001:  # 1mm tolerance
            errors.append(
                f"Component {i} ({type(component).__name__}) insertion point "
                f"({insertion.x:.3f}, {insertion.y:.3f}) does not match previous "
                f"attachment point ({current_attachment.x:.3f}, {current_attachment.y:.3f})"
            )

        # Check 2: Component-specific validation
        component_errors = component.validate()
        errors.extend([f"Component {i}: {e}" for e in component_errors])

        # Move to next attachment
        current_attachment = component.get_attachment_point(insertion)

    return errors
```

---

## Rare Exception: Alternate Connections

In rare cases, a component might need to connect differently (e.g., barrier offset from shoulder). This can be handled by having the component adjust its insertion point:

```python
@dataclass
class Barrier(RoadComponent):
    """Safety barrier with optional offset"""
    offset: float = 0.6         # Lateral offset from previous component

    def get_insertion_point(self, previous_attachment: ConnectionPoint) -> ConnectionPoint:
        """Barrier can be offset from previous component"""
        return ConnectionPoint(
            x=previous_attachment.x + self.offset,  # Offset insertion
            y=previous_attachment.y,
            description=f"Barrier base (offset {self.offset}m)"
        )
```

This creates a gap that could be filled by a small buffer component if needed.

---

## Benefits of Geometric Connection Model

1. **Natural geometry**: Components define their own shape and connection points
2. **No categorical types**: Elevation changes, slopes naturally emerge from geometry
3. **Snap-together**: Simple, intuitive assembly
4. **Extensible**: New components just implement insertion/attachment methods
5. **Validation is geometric**: Check continuity, not categories
6. **Flexible**: Can handle offsets and special cases naturally
7. **Visual**: Easy to understand and debug (plot connection points)

---

## Summary

**Key Concepts:**
- **Control Point**: Origin with attachment point for first component
- **Insertion Point**: Where component begins (snaps to previous attachment)
- **Attachment Point**: Where next component begins (function of geometry)
- **Snap-Together**: Components form continuous geometric chain

**Special Cases:**
- **Control point offset**: For divided roads, attachment can be offset
- **Vertical offsets**: Curbs provide elevated attachment points
- **Slope transitions**: Slopes connect at toe, attach at top
- **Component offsets**: Rare exceptions can offset insertion point

This geometric model is simpler, more flexible, and more natural than categorical connection types.
