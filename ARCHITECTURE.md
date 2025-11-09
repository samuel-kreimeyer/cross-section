# Cross-Section Architecture Proposal

## Overview

This document outlines the proposed architecture for a modular road cross-section design system that supports multiple frontends (CLI, Web, VIKTOR) and multiple export formats (DXF, SVG, etc.).

## Technology Stack Recommendation

**Python** is recommended for this project because:
- VIKTOR is Python-based (native integration)
- Excellent geometric libraries (CadQuery, Shapely for optional adapters)
- Strong CAD export support (CadQuery for DXF/STEP, svgwrite for SVG)
- CLI support (Click, Typer)
- Web API support (FastAPI)
- Type safety with type hints
- Scientific computing ecosystem

## Critical Constraint: VIKTOR Vendoring

**VIKTOR projects cannot import from parent folders.** This architectural constraint drives a key design decision:

- **Core domain logic must be pure Python** (no external dependencies)
- Core will be **vendored (copied)** into the VIKTOR project folder
- Heavy libraries (CadQuery, Shapely) are used via **adapters** outside the core
- Clean separation between portable core and library-specific adapters

## Architectural Layers

```
┌─────────────────────────────────────────────────────────┐
│         INTERFACE LAYER (Frontends)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐     │
│  │   CLI    │  │  Web API │  │  VIKTOR App      │     │
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
│  ╔═══════════════════════════════════════════════════╗ │
│  ║ CORE (Pure Python - Vendorable to VIKTOR)        ║ │
│  ╠═══════════════════════════════════════════════════╣ │
│  ║ DOMAIN LAYER                                      ║ │
│  ║  • Road Components (Lanes, Shoulders, etc.)       ║ │
│  ║  • Connection Rules & Constraints                 ║ │
│  ║  • Component Interfaces & Protocols               ║ │
│  ╠═══════════════════════════════════════════════════╣ │
│  ║ GEOMETRY LAYER (Abstract)                         ║ │
│  ║  • Point2D, Polygon, Polyline (pure data)         ║ │
│  ║  • Component → Geometry Transformation            ║ │
│  ║  • Positioning & Assembly Logic                   ║ │
│  ╚═══════════════════════════════════════════════════╝ │
│         NO EXTERNAL DEPENDENCIES (stdlib only)          │
└─────────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────────┐
│         ADAPTER LAYER (Library Conversions)             │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────┐   │
│  │  CadQuery    │  │   Shapely    │  │   VIKTOR   │   │
│  │  Adapter     │  │   Adapter    │  │  Adapter   │   │
│  └──────────────┘  └──────────────┘  └────────────┘   │
└─────────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────────┐
│         EXPORT/VISUALIZATION LAYER                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐     │
│  │ DXF/STEP │  │   SVG    │  │  VIKTOR Views    │     │
│  └──────────┘  └──────────┘  └──────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

**Key Innovation: The boxed "CORE" module is completely self-contained and can be copied into VIKTOR projects without any external dependencies.**

## Core Design Patterns

### 1. Abstract Geometry Primitives (Pure Python)

The core uses **pure Python data structures** with no external dependencies:

```python
# src/cross_section/core/geometry/primitives.py
"""Pure Python geometry - NO external dependencies"""
from dataclasses import dataclass, field
from typing import List, Optional
import math

@dataclass
class Point2D:
    """2D point - pure Python, no library dependencies"""
    x: float
    y: float

    def distance_to(self, other: 'Point2D') -> float:
        """Calculate distance to another point"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def offset(self, dx: float, dy: float) -> 'Point2D':
        """Create new point offset by dx, dy"""
        return Point2D(self.x + dx, self.y + dy)

@dataclass
class Polygon:
    """2D polygon - pure Python, no library dependencies"""
    exterior: List[Point2D]
    holes: Optional[List[List[Point2D]]] = None

    def bounds(self) -> tuple[float, float, float, float]:
        """Returns (min_x, min_y, max_x, max_y)"""
        xs = [p.x for p in self.exterior]
        ys = [p.y for p in self.exterior]
        return (min(xs), min(ys), max(xs), max(ys))

    def offset_x(self, dx: float) -> 'Polygon':
        """Translate polygon horizontally"""
        return Polygon(
            exterior=[p.offset(dx, 0) for p in self.exterior],
            holes=[[p.offset(dx, 0) for p in hole] for hole in (self.holes or [])]
        )

@dataclass
class ComponentGeometry:
    """Complete geometry for a road component - pure data structure"""
    polygons: List[Polygon] = field(default_factory=list)
    polylines: List[List[Point2D]] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
```

### 2. Component Pattern (Domain Layer)

All road components implement a common interface:

```python
from abc import ABC, abstractmethod
from typing import Protocol, Optional
from dataclasses import dataclass
from enum import Enum
from ..geometry.primitives import ComponentGeometry

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
    def to_geometry(self, start_x: float, elevation: float) -> ComponentGeometry:
        """Convert to abstract geometric representation (pure Python)"""
        pass
```

### 3. Concrete Components (Pure Python)

```python
from dataclasses import dataclass
from ..geometry.primitives import Point2D, Polygon, ComponentGeometry

@dataclass
class TravelLane(RoadComponent):
    """Standard travel lane - pure Python, no dependencies"""
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

    def to_geometry(self, start_x: float, elevation: float) -> ComponentGeometry:
        """Returns pure Python geometry (no library dependencies)"""
        # Calculate rectangular lane with cross-slope
        end_x = start_x + self.width
        end_elevation = elevation - (self.width * self.cross_slope)

        points = [
            Point2D(start_x, elevation),
            Point2D(end_x, end_elevation),
            Point2D(end_x, 0),
            Point2D(start_x, 0)
        ]

        return ComponentGeometry(
            polygons=[Polygon(exterior=points)],
            polylines=[],
            metadata={
                'type': 'TravelLane',
                'width': self.width,
                'cross_slope': self.cross_slope,
                'surface_type': self.surface_type
            }
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

### 4. Adapter Pattern (Library Conversions)

The adapter layer converts abstract geometry to library-specific formats:

```python
# src/cross_section/adapters/cadquery_adapter.py
"""CadQuery adapter - converts abstract geometry to CadQuery"""
import cadquery as cq
from ..core.geometry.primitives import ComponentGeometry, Polygon, Point2D

class CadQueryAdapter:
    """Convert abstract geometry to CadQuery for export/3D operations"""

    @staticmethod
    def polygon_to_cadquery(polygon: Polygon) -> cq.Workplane:
        """Convert pure Python polygon to CadQuery sketch"""
        if not polygon.exterior:
            return cq.Workplane("XY")

        # Start sketch at first point
        points = polygon.exterior
        sketch = cq.Workplane("XY").moveTo(points[0].x, points[0].y)

        # Add lines to other points
        for p in points[1:]:
            sketch = sketch.lineTo(p.x, p.y)

        return sketch.close()

    @staticmethod
    def component_to_cadquery(geom: ComponentGeometry) -> cq.Workplane:
        """Convert component geometry to CadQuery"""
        # For multiple polygons, union them
        result = None
        for polygon in geom.polygons:
            sketch = CadQueryAdapter.polygon_to_cadquery(polygon)
            if result is None:
                result = sketch
            else:
                result = result.union(sketch)
        return result if result else cq.Workplane("XY")
```

```python
# src/cross_section/adapters/shapely_adapter.py
"""Shapely adapter - for geometric validation and analysis"""
from shapely.geometry import Polygon as ShapelyPolygon, Point as ShapelyPoint
from ..core.geometry.primitives import ComponentGeometry, Polygon, Point2D

class ShapelyAdapter:
    """Convert abstract geometry to Shapely for validation/analysis"""

    @staticmethod
    def polygon_to_shapely(polygon: Polygon) -> ShapelyPolygon:
        """Convert pure Python polygon to Shapely"""
        coords = [(p.x, p.y) for p in polygon.exterior]
        holes = None
        if polygon.holes:
            holes = [[(p.x, p.y) for p in hole] for hole in polygon.holes]
        return ShapelyPolygon(shell=coords, holes=holes)

    @staticmethod
    def component_to_shapely(geom: ComponentGeometry) -> list[ShapelyPolygon]:
        """Convert component geometry to Shapely polygons"""
        return [ShapelyAdapter.polygon_to_shapely(p) for p in geom.polygons]
```

```python
# src/cross_section/interfaces/viktor/viktor_adapter.py
"""VIKTOR adapter - converts to VIKTOR geometry types"""
import viktor.geometry as vgeo
from ...vendor.cross_section_core.geometry.primitives import ComponentGeometry, Polygon

class ViktorAdapter:
    """Convert abstract geometry to VIKTOR geometry (in VIKTOR project)"""

    @staticmethod
    def polygon_to_viktor(polygon: Polygon) -> vgeo.GeoPolygon:
        """Convert pure Python polygon to VIKTOR polygon"""
        points = [vgeo.Point(p.x, p.y, 0) for p in polygon.exterior]
        return vgeo.GeoPolygon(points)

    @staticmethod
    def component_to_viktor(geom: ComponentGeometry) -> list[vgeo.GeoPolygon]:
        """Convert component geometry to VIKTOR polygons"""
        return [ViktorAdapter.polygon_to_viktor(p) for p in geom.polygons]
```

### 5. Exporter Strategy Pattern (Uses Adapters)

```python
from abc import ABC, abstractmethod
from ..adapters.cadquery_adapter import CadQueryAdapter
from ..core.geometry.primitives import ComponentGeometry

class SectionExporter(ABC):
    """Base class for all exporters"""

    @abstractmethod
    def export(self, geometry: SectionGeometry, filepath: str, **options) -> None:
        pass

class DXFExporter(SectionExporter):
    """Export to AutoCAD DXF format using CadQuery"""

    def export(self, geometry: SectionGeometry, filepath: str, **options) -> None:
        import cadquery as cq

        # Combine all component geometries
        combined = None

        for component, geom in geometry.components:
            # Convert abstract geometry to CadQuery
            cq_sketch = CadQueryAdapter.component_to_cadquery(geom)

            if combined is None:
                combined = cq_sketch
            else:
                combined = combined.union(cq_sketch)

        # Export using CadQuery's built-in DXF exporter
        if combined:
            cq.exporters.export(combined, filepath, 'DXF')

class SVGExporter(SectionExporter):
    """Export to SVG format - direct from abstract geometry"""

    def export(self, geometry: SectionGeometry, filepath: str, **options) -> None:
        import svgwrite

        width = geometry.get_total_width()
        height = options.get('height', 10.0)
        scale = options.get('scale', 100)  # pixels per meter

        dwg = svgwrite.Drawing(filepath, size=(width * scale, height * scale))

        for component, geom in geometry.components:
            # Work directly with abstract geometry (no adapter needed)
            for polygon in geom.polygons:
                points = [(p.x * scale, p.y * scale) for p in polygon.exterior]
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
│       ├── ╔══════════════════════════════════════════╗
│       │   ║ CORE (Pure Python - Vendorable)         ║
│       │   ╚══════════════════════════════════════════╝
│       ├── core/                   # NO external dependencies
│       │   ├── __init__.py
│       │   │
│       │   ├── geometry/           # Abstract geometry primitives
│       │   │   ├── __init__.py
│       │   │   ├── primitives.py  # Point2D, Polygon, ComponentGeometry
│       │   │   ├── transforms.py  # Pure math transformations
│       │   │   └── assembler.py   # Section geometry assembly
│       │   │
│       │   ├── domain/             # Domain model (pure Python)
│       │   │   ├── __init__.py
│       │   │   ├── base.py        # RoadComponent, ConnectionInterface
│       │   │   ├── components/
│       │   │   │   ├── __init__.py
│       │   │   │   ├── lanes.py   # TravelLane, TurnLane, BikeLane
│       │   │   │   ├── shoulders.py  # Shoulder
│       │   │   │   ├── curbs.py   # Curb, Gutter
│       │   │   │   ├── medians.py # Median
│       │   │   │   ├── slopes.py  # CutSlope, FillSlope
│       │   │   │   └── sidewalks.py # Sidewalk, Planting
│       │   │   └── section.py     # RoadSection
│       │   │
│       │   └── validation/         # Pure Python validation
│       │       ├── __init__.py
│       │       └── rules.py       # Connection rules, constraints
│       │
│       ├── adapters/               # Library conversions (NOT vendored)
│       │   ├── __init__.py
│       │   ├── cadquery_adapter.py   # Core → CadQuery
│       │   ├── shapely_adapter.py    # Core → Shapely
│       │   └── svg_adapter.py        # Core → SVG (optional)
│       │
│       ├── export/                 # Export Layer (NOT vendored)
│       │   ├── __init__.py
│       │   ├── base.py            # SectionExporter, ExporterFactory
│       │   ├── dxf_exporter.py    # DXF export (uses CadQuery adapter)
│       │   ├── svg_exporter.py    # SVG export (direct or adapter)
│       │   └── step_exporter.py   # STEP export (uses CadQuery adapter)
│       │
│       ├── application/            # Application Layer (NOT vendored)
│       │   ├── __init__.py
│       │   ├── builder.py         # Section builder/assembler
│       │   ├── templates.py       # Standard section templates
│       │   └── use_cases/
│       │       ├── __init__.py
│       │       ├── create_section.py
│       │       └── export_section.py
│       │
│       └── interfaces/             # Interface Layer
│           ├── __init__.py
│           │
│           ├── cli/                # Command-line interface
│           │   ├── __init__.py
│           │   ├── main.py        # CLI entry point
│           │   └── commands/
│           │       ├── create.py
│           │       ├── export.py
│           │       └── validate.py
│           │
│           ├── web/                # Web API
│           │   ├── __init__.py
│           │   ├── app.py         # FastAPI application
│           │   ├── routers/
│           │   │   ├── sections.py
│           │   │   └── export.py
│           │   └── schemas/
│           │       └── section_schema.py
│           │
│           └── viktor/             # VIKTOR integration
│               ├── __init__.py
│               ├── app.py         # VIKTOR app entry point
│               ├── parametrization.py
│               ├── viktor_adapter.py  # Core → VIKTOR geometry
│               │
│               └── vendor/         # ← VENDORED CORE (copied)
│                   └── cross_section_core/
│                       ├── __init__.py
│                       ├── geometry/    # Copied from core/geometry
│                       ├── domain/      # Copied from core/domain
│                       └── validation/  # Copied from core/validation
│
├── scripts/
│   ├── sync_to_viktor.py          # Syncs core/ → viktor/vendor/
│   └── pre_commit_hook.sh         # Auto-sync before commit
│
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_core_geometry.py
│   │   ├── test_components.py
│   │   ├── test_adapters.py
│   │   └── test_exporters.py
│   ├── integration/
│   │   ├── test_section_creation.py
│   │   ├── test_export_workflow.py
│   │   └── test_viktor_vendor_sync.py
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
    ├── component_catalog.md
    └── viktor_vendoring.md       # Vendoring strategy docs
```

### Key Structure Principles

1. **`core/` is completely self-contained**
   - Only stdlib imports (math, dataclasses, typing, etc.)
   - Can be copied to VIKTOR without modification
   - All business logic and domain knowledge

2. **`adapters/` converts between core and libraries**
   - CadQuery for 3D and CAD export
   - Shapely for geometric analysis (optional)
   - VIKTOR for visualization
   - NOT copied to VIKTOR

3. **`interfaces/viktor/vendor/` is a copy of `core/`**
   - Synced via script
   - VIKTOR imports from vendor, not parent
   - Committed to git (shows what VIKTOR sees)

4. **Dependencies are optional**
   - Core: No dependencies
   - CLI: Requires Typer
   - Web: Requires FastAPI
   - Export: Requires CadQuery (DXF/STEP) or svgwrite (SVG)
   - VIKTOR: Only needs vendored core

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

### Python API (CLI/Web)
```python
from cross_section.core.domain.components import TravelLane, Shoulder, Median
from cross_section.core.domain.section import RoadSection
from cross_section.export.base import ExporterFactory

# Create section programmatically (using pure Python core)
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

# Export using adapter pattern
geometry = section.to_geometry()  # Returns abstract geometry
exporter = ExporterFactory.get_exporter('dxf')  # Uses CadQuery adapter internally
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

### VIKTOR (Uses Vendored Core)
```python
# src/cross_section/interfaces/viktor/app.py
from viktor import ViktorController
from viktor.parametrization import ViktorParametrization, NumberField
from viktor.views import GeometryView, GeometryResult
import viktor.geometry as vgeo

# Import from VENDORED core (not from parent!)
from .vendor.cross_section_core.domain.components import TravelLane, Shoulder, Median
from .vendor.cross_section_core.domain.section import RoadSection
from .viktor_adapter import ViktorAdapter

class Parametrization(ViktorParametrization):
    lane_width = NumberField("Lane Width (m)", default=3.6, min=2.5, max=5.0)
    shoulder_width = NumberField("Shoulder Width (m)", default=2.4, min=0, max=4.0)
    num_lanes = NumberField("Number of Lanes", default=2, min=1, max=4, step=1)

class RoadSectionController(ViktorController):
    parametrization = Parametrization

    @GeometryView("Cross Section View", duration_guess=1)
    def create_geometry(self, params, **kwargs):
        # Create section using vendored core (pure Python, no external deps)
        section = RoadSection(name="Parametric Section")
        section.add_component(Shoulder(width=params.shoulder_width, paved=True))

        for _ in range(int(params.num_lanes)):
            section.add_component(TravelLane(width=params.lane_width))

        section.add_component(Shoulder(width=params.shoulder_width, paved=True))

        # Convert abstract geometry to VIKTOR geometry
        abstract_geom = section.to_geometry()
        viktor_geom = ViktorAdapter.section_to_viktor(abstract_geom)

        return GeometryResult(viktor_geom)
```

**Note:** VIKTOR app imports from `vendor/cross_section_core/`, which is a copy of `core/` synced via `scripts/sync_to_viktor.py`. This allows VIKTOR to work within its project folder constraints.

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
