# Cross-Section

A modular system for creating, validating, and exporting typical road and highway cross-sections.

## Overview

Cross-Section is a Python-based engineering tool that provides a domain model for road components (lanes, shoulders, curbs, medians, slopes) and translates them into geometric shapes for export to various CAD formats (DXF, SVG, etc.). The system supports multiple frontends including CLI, Web API, and VIKTOR integration.

## Key Features

- **Rich Component Library**: Lanes, shoulders, curbs, medians, cut/fill slopes, and more
- **Intelligent Validation**: Components enforce connection rules and geometric constraints
- **Multiple Export Formats**: DXF (AutoCAD), SVG, and extensible for others
- **Three Frontends**: Command-line interface, REST API, and VIKTOR integration
- **Type-Safe**: Full type hints with mypy validation
- **Extensible Architecture**: Clean interfaces for adding components and exporters

## Quick Example

```python
from cross_section.core.domain.components import TravelLane, Shoulder, Median
from cross_section.core.domain.section import RoadSection

# Create a highway section
section = RoadSection(
    name="Four-Lane Highway",
    control_point=ControlPoint(x=0, elevation=0)
)

section.add_component(Shoulder(width=3.0, paved=True))
section.add_component(TravelLane(width=3.6))
section.add_component(TravelLane(width=3.6))
section.add_component(Median(width=4.0, barrier=True))
section.add_component(TravelLane(width=3.6))
section.add_component(TravelLane(width=3.6))
section.add_component(Shoulder(width=3.0, paved=True))

# Validate (section validates assembly)
errors = section.validate()

# Generate geometry
geometry = section.to_geometry()

# Export using adapters
from cross_section.export.dxf_exporter import DXFExporter
exporter = DXFExporter()
exporter.export(geometry, 'highway.dxf')
```

## Architecture

The project follows clean architecture principles with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│  Interface Layer (CLI, Web, VIKTOR)     │
├─────────────────────────────────────────┤
│  Application Layer (Orchestration)      │
├─────────────────────────────────────────┤
│  Domain Layer (Components, Rules)       │
├─────────────────────────────────────────┤
│  Geometry Layer (Shape Translation)     │
├─────────────────────────────────────────┤
│  Export Layer (DXF, SVG, etc.)          │
└─────────────────────────────────────────┘
```

For detailed architecture documentation, see:

- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete architectural design with code examples
- **[ROADMAP.md](ROADMAP.md)** - Implementation phases and timeline
- **[docs/design_decisions.md](docs/design_decisions.md)** - Technology choices and rationale
- **[docs/architecture_diagram.svg](docs/architecture_diagram.svg)** - Visual architecture overview

## Project Status

🚧 **Under Development** - Architecture phase complete, implementation starting

See [ROADMAP.md](ROADMAP.md) for detailed implementation schedule.

## Technology Stack

- **Core**: Pure Python 3.11+ (stdlib only - vendorable to VIKTOR)
- **Geometry Adapters** (optional):
  - CadQuery: DXF/STEP export, 3D operations
  - Shapely: Geometric validation
- **Export**: Via adapters (DXF, SVG, STEP)
- **Web API**: FastAPI
- **CLI**: Typer
- **Testing**: pytest, hypothesis
- **Type Checking**: mypy

## Installation

*Installation instructions will be added once the package is implemented*

```bash
# Future installation
pip install cross-section
```

## Usage Examples

### Command Line

```bash
# Create from template
cross-section create --template urban_arterial --export dxf

# Custom section
cross-section create \
  --components "shoulder:2.4,lane:3.6,lane:3.6,shoulder:2.4" \
  --output rural_road.dxf
```

### Web API

```bash
# Start API server
uvicorn cross_section.interfaces.web.app:app

# Create section via API
curl -X POST http://localhost:8000/api/sections \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Section", "components": [...]}'
```

### VIKTOR

Integration with VIKTOR for interactive parametric design and visualization.

## Development

### Setup Development Environment

*Development setup instructions will be added during Phase 1*

### Running Tests

```bash
pytest
pytest --cov=cross_section --cov-report=html
```

### Code Quality

```bash
# Type checking
mypy src/cross_section

# Linting
ruff check src/cross_section

# Formatting
black src/cross_section
```

## Contributing

*Contributing guidelines will be added once the project reaches alpha stage*

## Design Principles

- **Clean Architecture**: Dependencies point inward, domain is independent
- **SOLID Principles**: Single responsibility, open/closed, dependency inversion
- **Type Safety**: Comprehensive type hints throughout
- **Testability**: High test coverage, property-based testing
- **Extensibility**: Easy to add components, exporters, frontends

## Roadmap

- **Phase 1** (Weeks 1-2): Core domain model
- **Phase 2** (Weeks 2-3): Geometry layer
- **Phase 3** (Weeks 3-4): Export layer (DXF, SVG)
- **Phase 4** (Week 4): CLI interface
- **Phase 5** (Week 5): Web API
- **Phase 6** (Week 6): VIKTOR integration
- **Phase 7** (Weeks 7-8): Extended components
- **Phase 8** (Weeks 8-9): Testing & documentation
- **Phase 9** (Weeks 9-10): Release v0.1.0

See [ROADMAP.md](ROADMAP.md) for detailed breakdown.

## License

*License to be determined*

## Contact

*Contact information to be added*

## Acknowledgments

Built with:
- [CadQuery](https://cadquery.readthedocs.io/) - CAD export and 3D operations
- [Shapely](https://shapely.readthedocs.io/) - Geometric validation
- [FastAPI](https://fastapi.tiangolo.com/) - Web API framework
- [VIKTOR](https://viktor.ai/) - Engineering application platform
