# Road Cross-Section Architecture Foundation

## Overview

This PR establishes the complete architectural foundation for the cross-section project, including comprehensive design documentation, technology decisions, and user stories to guide development.

## Summary of Changes

### 📐 Architecture Documentation (ARCHITECTURE.md)
- **Layered Architecture**: Clean separation between Interface, Application, Core, Adapter, and Export layers
- **Pure Python Core**: Zero external dependencies (stdlib only) - vendorable to VIKTOR
- **Abstract Geometry**: `Point2D`, `Polygon`, `ComponentGeometry` (pure data structures)
- **Adapter Pattern**: Separate adapters for CadQuery, Shapely, and VIKTOR
- **Component Model**: Unified interface for all road components (lanes, shoulders, curbs, medians, slopes)
- **Complete code examples**: Fully implementable designs with type hints

### 🗺️ Implementation Roadmap (ROADMAP.md)
- **9 phases** spanning 9-10 weeks to v0.1.0
- Phase-by-phase breakdown with tasks, durations, and deliverables
- Risk management strategies
- Success metrics and decision log
- Resource requirements and timeline

### 🎯 Technology Decisions (docs/design_decisions.md)
- **Python over TypeScript**: VIKTOR integration, geometry libraries, CAD export
- **Pure Python Core + Adapters**: Solves VIKTOR vendoring constraint
- **CadQuery + Shapely**: Best of both worlds via adapter pattern
  - CadQuery for DXF/STEP export and 3D operations
  - Shapely for fast 2D validation and analysis
- **FastAPI for Web API**: Modern, fast, auto-documentation
- **Detailed comparisons**: Technology tradeoffs and rationale

### 📦 VIKTOR Vendoring Strategy (docs/viktor_vendoring.md)
- **Complete guide** for copying core to VIKTOR project folder
- **Sync strategy**: Manual script, pre-commit hooks, CI/CD validation
- **Development workflow**: How to maintain both source and vendored copies
- **Testing strategy**: Verify both import paths work
- **Troubleshooting**: Common issues and solutions

### 📖 User Stories (USER_STORIES.md)
- **4 initial stories** with full acceptance criteria:
  - **US-001**: Automatic barrier placement for steep slopes (safety compliance)
  - **US-002**: Plain language cross-section descriptions (NLP/LLM future)
  - **US-003**: Scale-aware annotated drawings (professional output)
  - **US-004**: Plain language error messages (developer experience)
- **Test scenarios** for test-driven development
- **Phase mapping**: Stories aligned to development roadmap
- **18 placeholder stories** for future features
- **Story template** for consistency

### 🎨 Visual Documentation (docs/architecture_diagram.svg)
- Color-coded layer visualization
- Component relationships
- Technology stack overview
- Data flow illustration

### 📝 Updated README.md
- Quick start examples
- Architecture overview
- Links to detailed documentation
- Technology stack summary
- Development roadmap

## Key Architectural Innovations

### 1. Pure Python Core (Vendorable)

**Problem**: VIKTOR projects cannot import from parent folders.

**Solution**: Core module with ZERO external dependencies (stdlib only).

```python
# Core produces abstract geometry - pure Python!
from cross_section.core.domain.components import TravelLane
lane = TravelLane(width=3.6)
geom = lane.to_geometry()  # Returns Point2D, Polygon (pure data)
```

**Benefits**:
- ✅ Can be copied to VIKTOR without dependency hell
- ✅ Works in any Python environment
- ✅ Easy to test (no mocking heavy libraries)
- ✅ Portable and reusable

### 2. Adapter Pattern (Best Library for Each Job)

```python
# CLI/Web: Use adapters as needed
from cross_section.adapters.cadquery_adapter import CadQueryAdapter
cq_geom = CadQueryAdapter.from_geometry(geom)  # For CAD export

from cross_section.adapters.shapely_adapter import ShapelyAdapter
shapely_geom = ShapelyAdapter.from_geometry(geom)  # For validation

# VIKTOR: Uses vendored core + VIKTOR API
from .vendor.cross_section_core.domain.components import TravelLane
# No heavy libraries needed!
```

**Benefits**:
- ✅ CadQuery for DXF/STEP export and future 3D
- ✅ Shapely for fast 2D geometric validation
- ✅ VIKTOR uses native geometry API
- ✅ Core stays clean and dependency-free

### 3. VIKTOR Vendoring (Solves Import Constraint)

```
src/cross_section/
  ├── core/                    # Source of truth
  │   ├── geometry/
  │   ├── domain/
  │   └── validation/
  └── interfaces/viktor/
      ├── app.py               # VIKTOR app
      ├── viktor_adapter.py
      └── vendor/              # COPY of core/
          └── cross_section_core/
```

**Sync**: `python scripts/sync_to_viktor.py`

**Benefits**:
- ✅ Works within VIKTOR's folder constraints
- ✅ Simple copy strategy (no git submodules)
- ✅ Both versions tracked in git
- ✅ CI validates sync

### 4. User-Driven Design

User stories define the "what" and "why":
- **US-001**: Automatically place barriers when slopes exceed 4:1 (safety)
- **US-003**: Generate annotated drawings that fit 11×17" with legible text (usability)
- **US-004**: "Sidewalk requires curb, but lane provides flush connection" (clear errors)

Each story includes test scenarios for TDD.

## Project Structure

```
cross-section/
├── ARCHITECTURE.md              # Complete design with code examples
├── ROADMAP.md                   # 9-phase implementation plan
├── USER_STORIES.md              # User needs and acceptance criteria
├── README.md                    # Quick start and overview
│
├── docs/
│   ├── architecture_diagram.svg       # Visual overview
│   ├── design_decisions.md            # Technology rationale
│   └── viktor_vendoring.md            # Vendoring strategy
│
└── src/cross_section/           # Future implementation
    ├── core/                    # Pure Python (vendorable)
    │   ├── geometry/            # Point2D, Polygon
    │   ├── domain/              # Components, rules
    │   └── validation/          # Connection rules
    ├── adapters/                # Library conversions
    │   ├── cadquery_adapter.py
    │   ├── shapely_adapter.py
    │   └── viktor_adapter.py
    ├── export/                  # DXF, SVG, STEP exporters
    ├── application/             # Business logic, templates
    └── interfaces/              # CLI, Web, VIKTOR
        └── viktor/
            └── vendor/          # Vendored core copy
```

## Technology Stack

- **Language**: Python 3.11+ (type hints, dataclasses)
- **Core**: Pure Python (stdlib only)
- **Geometry Libraries** (via adapters):
  - CadQuery for CAD export and 3D operations
  - Shapely for 2D validation and analysis
- **Export**: CadQuery (DXF/STEP), svgwrite (SVG)
- **Web API**: FastAPI (modern, fast, auto-docs)
- **CLI**: Typer (type-safe CLI framework)
- **Testing**: pytest, hypothesis (property-based)
- **Type Checking**: mypy (strict mode)

## Design Principles

### Clean Architecture
- Dependencies point inward (toward domain)
- Domain layer has no external dependencies
- Outer layers depend on inner layers, never vice versa

### SOLID Principles
- **Single Responsibility**: Each component, one concern
- **Open/Closed**: Easy to add components, exporters, frontends
- **Liskov Substitution**: All components interchangeable
- **Interface Segregation**: Minimal, focused interfaces
- **Dependency Inversion**: Depend on abstractions (adapters)

### Type Safety
- Comprehensive type hints throughout
- mypy validation in CI/CD
- Runtime validation in critical paths

### Testability
- High test coverage goal (>90%)
- Property-based testing (hypothesis)
- Easy to test (pure Python core)

## Implementation Timeline

- **Phase 1** (Weeks 1-2): Core domain model (pure Python)
- **Phase 2** (Weeks 2-3): Geometry layer (abstract primitives)
- **Phase 3** (Weeks 3-4): Export layer (DXF, SVG via adapters)
- **Phase 4** (Week 4): CLI interface (Typer)
- **Phase 5** (Week 5): Web API (FastAPI)
- **Phase 6** (Week 6): VIKTOR integration (vendoring)
- **Phase 7** (Weeks 7-8): Extended components (barriers, slopes)
- **Phase 8** (Weeks 8-9): Testing & documentation
- **Phase 9** (Weeks 9-10): Polish & v0.1.0 release

## What's Next

### Ready to Start: Phase 1 Implementation
1. **Project setup**: `pyproject.toml`, dependencies, CI/CD
2. **Core geometry**: `Point2D`, `Polygon`, `ComponentGeometry`
3. **Domain model**: `RoadComponent`, `TravelLane`, `Shoulder`
4. **Validation framework**: Connection rules, error handling
5. **Tests**: Unit tests for core (>90% coverage)

### Acceptance Criteria for Phase 1
- [ ] Pure Python core with zero dependencies
- [ ] Basic components implemented (Lane, Shoulder, Curb)
- [ ] Connection validation works
- [ ] Structured error messages (US-004)
- [ ] Unit tests with >90% coverage
- [ ] Type hints pass mypy strict mode

## Files Changed

### New Files
- ✅ `ARCHITECTURE.md` (2,138 lines) - Complete architectural design
- ✅ `ROADMAP.md` (897 lines) - Implementation plan
- ✅ `USER_STORIES.md` (581 lines) - User requirements
- ✅ `docs/architecture_diagram.svg` - Visual overview
- ✅ `docs/design_decisions.md` (450+ lines) - Technology rationale
- ✅ `docs/viktor_vendoring.md` (400+ lines) - Vendoring strategy

### Modified Files
- ✅ `README.md` - Updated with architecture overview and links

### Total Lines Added: ~4,500+ lines of documentation

## Breaking Changes

None - this is the initial architecture.

## Testing Plan

Each user story includes test scenarios:

```python
# US-001: Barrier placement
def test_steep_slope_triggers_barrier():
    section = RoadSection()
    section.add_component(FillSlope(h_ratio=1, v_ratio=1))  # 1:1 slope
    warnings = section.validate_and_fix()
    assert any("barrier added" in w.lower() for w in warnings)

# US-003: Annotations
def test_annotation_auto_scale():
    annotator = AnnotationEngine(paper_size=(11, 17), margins=2.0)
    scale = annotator.calculate_scale(wide_section)
    assert text_is_legible(scale)

# US-004: Error messages
def test_connection_error_message():
    with pytest.raises(ValidationError) as exc:
        section.validate_connections()
    error = exc.value
    assert "Sidewalk" in str(error)
    assert "curb" in str(error).lower()
    assert len(error.suggestions) > 0
```

## Documentation Quality

All documents include:
- ✅ Clear code examples with syntax highlighting
- ✅ Architecture diagrams (text and SVG)
- ✅ Technology comparisons (tables with pros/cons)
- ✅ Implementation notes and rationale
- ✅ Test scenarios for TDD
- ✅ Links between related documents
- ✅ Professional structure and formatting

## Checklist

- [x] Architecture documented
- [x] Technology stack decided
- [x] Pure Python core designed
- [x] Adapter pattern specified
- [x] VIKTOR vendoring strategy documented
- [x] User stories written
- [x] Implementation roadmap created
- [x] Project structure defined
- [x] Design principles articulated
- [x] Test strategy outlined
- [x] README updated
- [x] Visual diagrams created

## Review Notes

This PR establishes the foundation for a professional, maintainable, and extensible road cross-section design system. Key innovations:

1. **Pure Python core** solves VIKTOR's import constraint elegantly
2. **Adapter pattern** allows using best library for each task
3. **User stories** drive test-driven development
4. **Comprehensive documentation** enables confident implementation

The architecture is ready for Phase 1 implementation to begin.

---

## Related Issues

N/A - Initial architecture

## References

- [AASHTO Green Book](https://www.aashto.org/) - Geometric Design Standards
- [CadQuery Documentation](https://cadquery.readthedocs.io/)
- [Shapely Documentation](https://shapely.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [VIKTOR Documentation](https://docs.viktor.ai/)
