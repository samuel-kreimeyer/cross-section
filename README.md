# Cross-Section

Cross-Section is a Python toolkit for assembling road and highway cross-sections from reusable components and exporting their geometry.

## Purpose

This library enables engineers and designers to programmatically define and generate road cross-sections using a component-based approach. It provides a flexible framework for:

- Assembling cross-sections from modular, reusable components (lanes, shoulders, slopes, barriers, etc.)
- Validating geometric and engineering constraints
- Exporting to various formats (CAD, SVG, etc.)
- Integrating with engineering platforms like VIKTOR

## Status

Active development. The core component system is functional, with ongoing work on:
- Additional component types (walls, drainage features)
- Enhanced validation and geometric checks
- Export format support
- Documentation and examples

## Quick Start

```python
from cross_section.core.domain.section import Section, ControlPoint
from cross_section.core.domain.components.lanes import Lane
from cross_section.core.domain.components.shoulders import Shoulder

# Create a section with control point at road centerline
section = Section(
    control_point=ControlPoint(x=0, elevation=100.0),
    right_components=[
        Lane(width=3.6),  # 3.6m travel lane
        Shoulder(width=2.4),  # 2.4m paved shoulder
    ]
)

# Generate geometry
geometry = section.to_geometry()

# Validate
errors = section.validate()
```

## Basics

- Python 3.11+
- Pure-Python core (stdlib only) for easy vendoring (e.g., VIKTOR)
- Active development; API and exporters are evolving

## Project Structure

```
src/cross_section/
├── core/
│   ├── domain/          # Core domain models
│   │   ├── components/  # Component implementations (lanes, shoulders, etc.)
│   │   ├── section.py   # Section assembly
│   │   └── pavement.py  # Pavement layer definitions
│   ├── geometry/        # Geometric primitives and validation
│   └── export/          # Export modules (CAD, SVG, etc.)
├── examples/            # Example cross-sections
└── tests/              # Test suite

docs/
├── development/        # Development documentation
├── reference/          # API and component reference
└── design_decisions.md # Architectural decisions
```

## Documentation

- Architecture: docs/development/architecture.md
- Component specification: docs/reference/component_spec.md
- Roadmap: docs/development/roadmap.md
- User stories: docs/development/user_stories.md
- Design decisions: docs/design_decisions.md
- VIKTOR vendoring: docs/viktor_vendoring.md
- Architecture diagram: docs/architecture_diagram.svg

## License

MIT License - see LICENSE file for details
