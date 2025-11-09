# Cross-Section Architecture Proposal

## Overview

This document outlines the proposed architecture for a modular road cross-section design system that supports multiple frontends (CLI, Web, VIKTOR) and multiple export formats (DXF, SVG, etc.).

## Technology Stack Recommendation

**Python** is recommended for this project because:
- VIKTOR is Python-based (native integration)
- Excellent geometric libraries (Shapely, scipy)
- Strong CAD export support (ezdxf for DXF, svgwrite for SVG)
- CLI support (Click, Typer)
- Web API support (FastAPI)
- Type safety with type hints
- Scientific computing ecosystem

## Architectural Layers

```
┌─────────────────────────────────────────────────────────┐
│         INTERFACE LAYER (Frontends)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐     │
│  │   CLI    │  │  Web API │  │  VIKTOR Adapter  │     │
│  └──────────┘  └──────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────────┐
│         APPLICATION LAYER (Orchestration)               │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Section Builder, Validation, Use Cases         │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────────┐
│         DOMAIN LAYER (Core Business Logic)              │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Road Components (Lanes, Shoulders, Curbs, etc.) │  │
│  │  Connection Rules & Constraints                  │  │
│  │  Component Interfaces & Protocols                │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────────┐
│         GEOMETRY LAYER (Shape Translation)              │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Geometric Primitives (Polygon, Polyline, etc.)  │  │
│  │  Component → Geometry Transformation              │  │
│  │  Positioning & Assembly Logic                    │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────────┐
│         EXPORT LAYER (Format Output)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐     │
│  │   DXF    │  │   SVG    │  │   Future (PDF)   │     │
│  └──────────┘  └──────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

## Core Design Patterns

### 1. Component Pattern (Domain Layer)

All road components implement a common interface:

```python
from abc import ABC, abstractmethod
from typing import Protocol, Optional
from dataclasses import dataclass
from enum import Enum

class ConnectionSide(Enum):
    LEFT = "left"
    RIGHT = "right"

class ConnectionType(Enum):
    FLUSH = "flush"          # Direct connection, same elevation
    RAISED = "raised"        # Curb height difference
    SLOPED = "sloped"        # Gradual slope connection
    MEDIAN = "median"        # Separated by median

@dataclass
class ConnectionInterface:
    """Defines how a component can connect to neighbors"""
    side: ConnectionSide
    connection_type: ConnectionType
    width: float
    elevation: float
    compatible_types: set[str]  # Which component types can connect

class RoadComponent(ABC):
    """Base interface for all road components"""

    @abstractmethod
    def get_width(self) -> float:
        """Return component width in meters"""
        pass

    @abstractmethod
    def get_default_dimensions(self) -> dict[str, float]:
        """Return dictionary of key dimensions with defaults"""
        pass

    @abstractmethod
    def get_connection_interface(self, side: ConnectionSide) -> ConnectionInterface:
        """Return connection requirements for specified side"""
        pass

    @abstractmethod
    def validate(self) -> list[str]:
        """Return list of validation errors (empty if valid)"""
        pass

    @abstractmethod
    def to_geometry(self, start_x: float, elevation: float) -> 'ComponentGeometry':
        """Convert to geometric representation"""
        pass
```

### 2. Concrete Components

```python
@dataclass
class TravelLane(RoadComponent):
    """Standard travel lane"""
    width: float = 3.6  # meters, typical lane width
    cross_slope: float = 0.02  # 2% typical
    surface_type: str = "asphalt"

    def get_width(self) -> float:
        return self.width

    def get_default_dimensions(self) -> dict[str, float]:
        return {
            "width": 3.6,
            "cross_slope": 0.02,
        }

    def get_connection_interface(self, side: ConnectionSide) -> ConnectionInterface:
        return ConnectionInterface(
            side=side,
            connection_type=ConnectionType.FLUSH,
            width=self.width,
            elevation=0.0,
            compatible_types={"TravelLane", "Shoulder", "TurnLane"}
        )

@dataclass
class Curb(RoadComponent):
    """Curb component with height"""
    width: float = 0.15  # 15cm typical curb width
    height: float = 0.15  # 15cm typical curb height
    curb_type: str = "vertical"  # or "sloped"

    def get_connection_interface(self, side: ConnectionSide) -> ConnectionInterface:
        if side == ConnectionSide.LEFT:
            # Road side - connects flush to pavement
            return ConnectionInterface(
                side=side,
                connection_type=ConnectionType.FLUSH,
                width=0.0,
                elevation=0.0,
                compatible_types={"TravelLane", "Shoulder", "BikeLane"}
            )
        else:
            # Sidewalk side - raised connection
            return ConnectionInterface(
                side=side,
                connection_type=ConnectionType.RAISED,
                width=self.width,
                elevation=self.height,
                compatible_types={"Sidewalk", "Planting"}
            )

@dataclass
class Shoulder(RoadComponent):
    """Paved or unpaved shoulder"""
    width: float = 2.4  # meters
    cross_slope: float = 0.04  # 4% typical for drainage
    paved: bool = True

    # Similar implementation...

@dataclass
class Median(RoadComponent):
    """Center median separator"""
    width: float = 3.0
    median_type: str = "raised"  # or "painted", "barrier"
    barrier: bool = False

    # Similar implementation...

@dataclass
class CutSlope(RoadComponent):
    """Cut slope for excavation"""
    horizontal_ratio: float = 2.0  # 2H:1V typical
    vertical_ratio: float = 1.0
    height: float = 3.0

    def get_width(self) -> float:
        return abs(self.height * self.horizontal_ratio / self.vertical_ratio)

@dataclass
class FillSlope(RoadComponent):
    """Fill slope for embankment"""
    horizontal_ratio: float = 2.0
    vertical_ratio: float = 1.0
    height: float = 3.0

    # Similar to CutSlope
```

### 3. Section Assembly (Application Layer)

```python
from typing import List
from dataclasses import dataclass, field

@dataclass
class RoadSection:
    """Complete road cross-section assembly"""
    name: str
    components: List[RoadComponent] = field(default_factory=list)
    center_elevation: float = 0.0
    stationing: Optional[float] = None

    def add_component(self, component: RoadComponent) -> 'RoadSection':
        """Add component to section (builder pattern)"""
        self.components.append(component)
        return self

    def validate_connections(self) -> List[str]:
        """Validate all component connections"""
        errors = []

        for i in range(len(self.components) - 1):
            left_comp = self.components[i]
            right_comp = self.components[i + 1]

            left_interface = left_comp.get_connection_interface(ConnectionSide.RIGHT)
            right_interface = right_comp.get_connection_interface(ConnectionSide.LEFT)

            # Check compatibility
            if type(right_comp).__name__ not in left_interface.compatible_types:
                errors.append(
                    f"Invalid connection: {type(left_comp).__name__} cannot "
                    f"connect to {type(right_comp).__name__}"
                )

            # Check elevation compatibility
            if left_interface.connection_type != right_interface.connection_type:
                errors.append(
                    f"Connection type mismatch between {type(left_comp).__name__} "
                    f"and {type(right_comp).__name__}"
                )

        return errors

    def to_geometry(self) -> 'SectionGeometry':
        """Convert entire section to geometry"""
        # Implementation in geometry layer
        pass

    def export(self, format: str, filepath: str) -> None:
        """Export to specified format"""
        # Uses strategy pattern for exporters
        pass
```

### 4. Geometry Layer

```python
from shapely.geometry import Polygon, LineString, Point
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class ComponentGeometry:
    """Geometric representation of a component"""
    polygons: List[Polygon] = field(default_factory=list)
    polylines: List[LineString] = field(default_factory=list)
    points: List[Point] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def offset_x(self, dx: float) -> 'ComponentGeometry':
        """Translate geometry horizontally"""
        # Implementation using shapely affine transforms
        pass

@dataclass
class SectionGeometry:
    """Complete section geometry"""
    components: List[Tuple[RoadComponent, ComponentGeometry]]
    bounds: Tuple[float, float, float, float]  # min_x, min_y, max_x, max_y

    def get_total_width(self) -> float:
        return self.bounds[2] - self.bounds[0]
```

### 5. Exporter Strategy Pattern

```python
from abc import ABC, abstractmethod

class SectionExporter(ABC):
    """Base class for all exporters"""

    @abstractmethod
    def export(self, geometry: SectionGeometry, filepath: str, **options) -> None:
        pass

class DXFExporter(SectionExporter):
    """Export to AutoCAD DXF format"""

    def export(self, geometry: SectionGeometry, filepath: str, **options) -> None:
        import ezdxf

        doc = ezdxf.new('R2018')
        msp = doc.modelspace()

        for component, geom in geometry.components:
            layer_name = type(component).__name__

            # Add polygons as polylines
            for polygon in geom.polygons:
                coords = list(polygon.exterior.coords)
                msp.add_lwpolyline(coords, dxfattribs={'layer': layer_name})

        doc.saveas(filepath)

class SVGExporter(SectionExporter):
    """Export to SVG format"""

    def export(self, geometry: SectionGeometry, filepath: str, **options) -> None:
        import svgwrite

        width = geometry.get_total_width()
        height = options.get('height', 10.0)
        scale = options.get('scale', 100)  # pixels per meter

        dwg = svgwrite.Drawing(filepath, size=(width * scale, height * scale))

        for component, geom in geometry.components:
            for polygon in geom.polygons:
                points = [(x * scale, y * scale) for x, y in polygon.exterior.coords]
                dwg.add(dwg.polygon(points, fill='lightgray', stroke='black'))

        dwg.save()

class ExporterFactory:
    """Factory for creating exporters"""

    _exporters = {
        'dxf': DXFExporter,
        'svg': SVGExporter,
        # Future: 'pdf': PDFExporter, etc.
    }

    @classmethod
    def get_exporter(cls, format: str) -> SectionExporter:
        if format not in cls._exporters:
            raise ValueError(f"Unsupported format: {format}")
        return cls._exporters[format]()

    @classmethod
    def register_exporter(cls, format: str, exporter_class: type):
        """Allow registration of custom exporters"""
        cls._exporters[format] = exporter_class
```

## Project Structure

```
cross-section/
├── pyproject.toml                 # Python project configuration
├── README.md
├── ARCHITECTURE.md
│
├── src/
│   └── cross_section/
│       ├── __init__.py
│       │
│       ├── domain/                # Domain Layer
│       │   ├── __init__.py
│       │   ├── base.py           # RoadComponent, ConnectionInterface
│       │   ├── components/
│       │   │   ├── __init__.py
│       │   │   ├── lanes.py      # TravelLane, TurnLane, BikeLane
│       │   │   ├── shoulders.py  # Shoulder
│       │   │   ├── curbs.py      # Curb, Gutter
│       │   │   ├── medians.py    # Median
│       │   │   ├── slopes.py     # CutSlope, FillSlope
│       │   │   └── sidewalks.py  # Sidewalk, Planting
│       │   └── section.py        # RoadSection
│       │
│       ├── geometry/              # Geometry Layer
│       │   ├── __init__.py
│       │   ├── primitives.py     # ComponentGeometry, SectionGeometry
│       │   ├── transforms.py     # Positioning, rotation, scaling
│       │   └── assembler.py      # Component → Geometry conversion
│       │
│       ├── export/                # Export Layer
│       │   ├── __init__.py
│       │   ├── base.py           # SectionExporter, ExporterFactory
│       │   ├── dxf_exporter.py   # DXF export implementation
│       │   ├── svg_exporter.py   # SVG export implementation
│       │   └── formats/
│       │       └── __init__.py
│       │
│       ├── application/           # Application Layer
│       │   ├── __init__.py
│       │   ├── builder.py        # Section builder/assembler
│       │   ├── validation.py     # Validation rules & logic
│       │   ├── templates.py      # Standard section templates
│       │   └── use_cases/
│       │       ├── __init__.py
│       │       ├── create_section.py
│       │       └── export_section.py
│       │
│       ├── interfaces/            # Interface Layer
│       │   ├── __init__.py
│       │   ├── cli/
│       │   │   ├── __init__.py
│       │   │   ├── main.py       # CLI entry point
│       │   │   └── commands/
│       │   │       ├── create.py
│       │   │       ├── export.py
│       │   │       └── validate.py
│       │   │
│       │   ├── web/
│       │   │   ├── __init__.py
│       │   │   ├── app.py        # FastAPI application
│       │   │   ├── routers/
│       │   │   │   ├── sections.py
│       │   │   │   └── export.py
│       │   │   └── schemas/
│       │   │       └── section_schema.py
│       │   │
│       │   └── viktor/
│       │       ├── __init__.py
│       │       ├── adapter.py    # VIKTOR integration adapter
│       │       └── parametrization.py
│       │
│       └── utils/
│           ├── __init__.py
│           ├── units.py          # Unit conversion utilities
│           └── validators.py     # Common validators
│
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_components.py
│   │   ├── test_geometry.py
│   │   └── test_exporters.py
│   ├── integration/
│   │   ├── test_section_creation.py
│   │   └── test_export_workflow.py
│   └── fixtures/
│       └── sample_sections.py
│
├── examples/
│   ├── simple_two_lane.py
│   ├── highway_section.py
│   └── urban_street.py
│
└── docs/
    ├── user_guide.md
    ├── api_reference.md
    └── component_catalog.md
```

## Key Architectural Principles

### 1. Dependency Rule
- Dependencies point inward (toward domain)
- Domain layer has no external dependencies
- Outer layers depend on inner layers, never vice versa

### 2. Interface Segregation
- Each component implements minimal required interface
- Connection logic separated from geometry logic
- Export logic independent of domain

### 3. Open/Closed Principle
- Easy to add new component types
- Easy to add new export formats
- Existing code unchanged when extending

### 4. Single Responsibility
- Each component responsible for own dimensions
- Validators separate from domain objects
- Exporters handle only format-specific concerns

## Design Decisions

### Why Python?
- VIKTOR native support
- Strong geometric libraries (Shapely)
- Excellent CAD export libraries
- Type hints for safety
- Good for all three frontends

### Why Shapely for Geometry?
- Industry-standard geometric operations
- Well-tested and maintained
- Efficient spatial calculations
- Easy conversion to export formats

### Why Dataclasses?
- Clean, readable component definitions
- Built-in equality, hashing
- Type hints support
- Immutable options available

### Why Strategy Pattern for Export?
- Easy to add new formats
- Format-specific logic isolated
- Plugin architecture possible
- Testing simplified

## Example Usage

### CLI
```bash
# Create a simple road section
cross-section create \
  --name "Rural Two-Lane" \
  --components "shoulder:2.4,lane:3.6,lane:3.6,shoulder:2.4" \
  --export dxf \
  --output rural_road.dxf

# Use a template
cross-section create --template urban_arterial --export svg
```

### Python API
```python
from cross_section.domain.components import TravelLane, Shoulder, Median
from cross_section.domain.section import RoadSection
from cross_section.export.base import ExporterFactory

# Create section programmatically
section = RoadSection(name="Highway Section")
section.add_component(Shoulder(width=3.0, paved=True))
section.add_component(TravelLane(width=3.6))
section.add_component(TravelLane(width=3.6))
section.add_component(Median(width=4.0, barrier=True))
section.add_component(TravelLane(width=3.6))
section.add_component(TravelLane(width=3.6))
section.add_component(Shoulder(width=3.0, paved=True))

# Validate
errors = section.validate_connections()
if errors:
    print("Validation errors:", errors)

# Export
geometry = section.to_geometry()
exporter = ExporterFactory.get_exporter('dxf')
exporter.export(geometry, 'highway.dxf')
```

### Web API
```bash
curl -X POST http://localhost:8000/api/sections \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Urban Street",
    "components": [
      {"type": "Sidewalk", "width": 2.0},
      {"type": "Curb", "height": 0.15},
      {"type": "ParkingLane", "width": 2.4},
      {"type": "TravelLane", "width": 3.3},
      {"type": "TravelLane", "width": 3.3},
      {"type": "ParkingLane", "width": 2.4},
      {"type": "Curb", "height": 0.15},
      {"type": "Sidewalk", "width": 2.0}
    ]
  }'
```

### VIKTOR
```python
from viktor import ViktorController
from viktor.parametrization import ViktorParametrization
from cross_section.interfaces.viktor.adapter import CrossSectionAdapter

class RoadSectionController(ViktorController):
    parametrization = ViktorParametrization

    @GeometryView("3D View")
    def create_geometry(self, params, **kwargs):
        adapter = CrossSectionAdapter()
        section = adapter.from_viktor_params(params)
        return adapter.to_viktor_geometry(section)
```

## Implementation Phases

### Phase 1: Core Domain (Week 1-2)
- Base component interface
- Basic components (Lane, Shoulder)
- Connection rules
- Section assembly
- Basic validation

### Phase 2: Geometry Layer (Week 2-3)
- Shapely integration
- Component → Geometry conversion
- Positioning logic
- Assembly algorithm

### Phase 3: Export Layer (Week 3-4)
- DXF exporter
- SVG exporter
- Exporter factory
- Export validation

### Phase 4: CLI Interface (Week 4)
- CLI framework setup
- Basic commands
- Template system
- Documentation

### Phase 5: Web API (Week 5)
- FastAPI setup
- REST endpoints
- JSON schemas
- API documentation

### Phase 6: VIKTOR Integration (Week 6)
- VIKTOR adapter
- Parametrization mapping
- Geometry visualization
- Testing with VIKTOR

## Testing Strategy

- **Unit Tests**: Each component, validator, exporter
- **Integration Tests**: Full workflow end-to-end
- **Property Tests**: Geometric invariants (using hypothesis)
- **Fixture Tests**: Standard road sections
- **Export Tests**: Validate output file formats

## Future Enhancements

- 3D extrusion along alignment
- Material/cost estimation
- Drainage design integration
- ADA compliance checking
- Multiple cross-sections along alignment
- Superelevation transitions
- PDF report generation
- Interactive web editor
