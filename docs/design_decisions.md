# Design Decisions & Rationale

## Technology Choices

### Python vs TypeScript/JavaScript

| Criterion | Python | TypeScript | Winner |
|-----------|--------|------------|--------|
| VIKTOR Integration | Native support | Difficult | **Python** |
| Geometry Libraries | CadQuery, Shapely (excellent) | turf.js, jsts (limited) | **Python** |
| CAD Export | CadQuery, ezdxf, svgwrite | dxf-writer (basic) | **Python** |
| CLI Support | Click, Typer (excellent) | Commander (good) | Tie |
| Web API | FastAPI (modern) | Express, NestJS (mature) | Tie |
| Type Safety | Type hints + mypy | Native TypeScript | TypeScript |
| Scientific Computing | NumPy, SciPy ecosystem | Limited | **Python** |
| Learning Curve | Gentle | Moderate | **Python** |

**Decision: Python**
- VIKTOR is the differentiator
- Geometry operations are core to the system
- CAD export quality is critical
- Scientific computing may be needed for analysis

---

## Core Architecture Decision: Pure Python Core + Adapters

### The Critical Constraint: VIKTOR Vendoring

**VIKTOR projects cannot import from parent folders.** This means we must **vendor (copy)** core logic into the VIKTOR project folder.

**Implication:** The core must be **pure Python with zero external dependencies**.

### Architecture Decision

```
┌─────────────────────────────────────────┐
│ CORE (Pure Python)                      │
│ • Only stdlib (math, dataclasses)      │
│ • Abstract geometry (Point2D, Polygon)  │
│ • Business logic (components, rules)    │
│ • Vendorable to VIKTOR                  │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ ADAPTERS (Library-specific)             │
│ • CadQueryAdapter → CAD export          │
│ • ShapelyAdapter → validation           │
│ • ViktorAdapter → visualization         │
│ • NOT vendored to VIKTOR                │
└─────────────────────────────────────────┘
```

**Benefits:**
1. ✅ Core is portable (works in VIKTOR, CLI, Web)
2. ✅ No dependency hell in VIKTOR
3. ✅ Easy to test (no mocking heavy libraries)
4. ✅ Clear separation of concerns
5. ✅ Can use best library for each task

**Trade-offs:**
1. ❌ More abstraction layers
2. ❌ Need to sync core to VIKTOR vendor folder
3. ❌ Must maintain discipline (keep core pure)

**Decision: Use pure Python core + adapter pattern**

See [docs/viktor_vendoring.md](viktor_vendoring.md) for complete vendoring strategy.

---

### Geometry Libraries: CadQuery + Shapely (via Adapters)

**Key Insight:** We don't have to choose! Use both via adapters.

#### CadQuery

**When to use:**
- DXF/STEP export (professional CAD formats)
- 3D operations (future: extrusion along alignment)
- Complex CAD operations

**Pros:**
- Built on OpenCASCADE (professional CAD kernel)
- Native CAD export (DXF, STEP, STL)
- 3D-ready
- Handles complex geometry

**Cons:**
- Larger dependency (~200MB)
- Steeper learning curve
- Heavier than needed for simple 2D

#### Shapely

**When to use:**
- Geometric validation (overlaps, gaps)
- Fast 2D operations
- Spatial analysis

**Pros:**
- Lightweight (~10MB)
- Very fast for 2D (GEOS backend)
- Simple API
- Industry standard

**Cons:**
- 2D only
- Separate export libraries needed

#### Decision: Use Both via Adapters

```python
# Core produces abstract geometry (pure Python)
geom = lane.to_geometry()  # Returns Point2D, Polygon

# Adapters convert as needed
cq_geom = CadQueryAdapter.from_geometry(geom)  # For export
shapely_geom = ShapelyAdapter.from_geometry(geom)  # For validation
```

**Benefits:**
- Use best tool for each job
- Core stays dependency-free
- CLI/Web can use both
- VIKTOR doesn't need either (uses vendored core + VIKTOR API)

---

### Web Framework: FastAPI

**Alternatives Considered:**
1. **FastAPI** (chosen)
2. Flask + extensions
3. Django + DRF

**Why FastAPI:**
- Automatic OpenAPI documentation
- Built-in data validation (Pydantic)
- Modern async support
- Type hints throughout
- Fast performance
- Easy to test
- Growing ecosystem

**Comparison:**

| Feature | FastAPI | Flask | Django |
|---------|---------|-------|--------|
| Performance | Very Fast | Moderate | Moderate |
| Auto Docs | ✅ Built-in | ❌ Manual | ❌ Manual |
| Type Safety | ✅ Native | ⚠️ Extensions | ⚠️ Limited |
| Learning Curve | Gentle | Very Gentle | Steep |
| Async Support | ✅ Native | ⚠️ Limited | ⚠️ Limited |
| Lightweight | ✅ Yes | ✅ Yes | ❌ Heavy |

---

### CLI Framework: Click vs Typer

Both are excellent. **Recommendation: Typer** (built on Click)

**Why Typer:**
- Type hints for automatic validation
- Better help messages from type hints
- Less boilerplate
- Click compatibility
- Modern Python approach

```python
# Click approach
@click.command()
@click.option('--width', type=float, help='Lane width')
def create(width):
    pass

# Typer approach (cleaner)
def create(width: float = typer.Option(..., help='Lane width')):
    pass
```

---

### CAD Export: CadQuery

**Why CadQuery (via adapter):**
- Built on OpenCASCADE (professional CAD kernel)
- Native DXF, STEP, STL export
- 3D-ready for future extrusion features
- Well-maintained and actively developed
- Used via adapter pattern (not in core)

---

### Testing Framework: pytest

**Alternatives Considered:**
1. **pytest** (chosen)
2. unittest (stdlib)
3. nose (deprecated)

**Why pytest:**
- Industry standard
- Clean test syntax
- Excellent fixture system
- Rich plugin ecosystem
- Better error messages
- Parameterized tests
- Coverage integration

---

## Architectural Patterns

Key patterns used in the architecture:

- **Component Pattern**: Consistent interface for all road components
- **Builder Pattern**: Fluent API for section assembly (`section.add_component()`)
- **Strategy Pattern**: Pluggable exporters for different formats
- **Adapter Pattern**: Convert core geometry to library-specific formats

**See [ARCHITECTURE.md](../ARCHITECTURE.md) for complete pattern implementations and examples.**

---

## Design Principles Applied

### 1. Dependency Inversion (SOLID)

**Layers depend on abstractions, not concretions**

```
Interface Layer → Application Layer → Domain Layer
                       ↓                    ↓
                  (abstractions)      (interfaces)
```

Domain defines interfaces, outer layers implement them.

### 2. Open/Closed Principle

**Open for extension, closed for modification**

- New component types: Implement `RoadComponent`
- New export formats: Implement `SectionExporter`
- New frontends: Use existing application layer

No need to modify core code.

### 3. Single Responsibility

**Each class has one reason to change**

- Components: Define dimensions and connections
- Exporters: Handle format specifics
- Validators: Check rules
- Geometry: Handle shapes

### 4. Interface Segregation

**Clients depend only on methods they use**

- `RoadComponent`: Minimal interface
- `ConnectionInterface`: Separate concern
- Exporters: Format-specific options

### 5. Liskov Substitution

**Subtypes must be substitutable**

- Any `RoadComponent` can be used in `RoadSection`
- Any `SectionExporter` can export
- Consistent behavior across implementations

---

## Data Flow

```
User Input (CLI/Web/VIKTOR)
    ↓
Application Layer (validates, orchestrates)
    ↓
Domain Layer (creates RoadSection with Components)
    ↓
Geometry Layer (converts to Polygons/Polylines)
    ↓
Export Layer (writes to DXF/SVG/etc.)
    ↓
Output File
```

Each layer transforms data without knowing about layers above it.

---

## Key Tradeoffs

### Flexibility vs Simplicity

**Decision: Favor flexibility**

- More abstractions, interfaces
- Steeper learning curve
- Easier to extend later
- Better for long-term maintenance

**Rationale:** Requirements will evolve (new components, formats, analyses)

---

### Performance vs Readability

**Decision: Favor readability (optimize later)**

- Clean, clear code
- Good abstractions
- Profile before optimizing
- Most operations are not performance-critical

**Rationale:** Premature optimization is root of all evil. Export operations happen infrequently.

---

### Type Safety vs Rapid Development

**Decision: Balance with type hints**

- Type hints everywhere
- mypy in CI/CD
- Runtime validation in critical paths
- Not overly strict (no `strict` mode initially)

**Rationale:** Type hints catch bugs without significant overhead

---

### Monorepo vs Multi-repo

**Decision: Monorepo (for now)**

- All code in one repository
- Shared version
- Easier cross-cutting changes
- Simpler CI/CD

**Future:** Could split into multiple packages if needed:
- `cross-section-core`
- `cross-section-cli`
- `cross-section-web`
- `cross-section-viktor`

---

## Module Organization

### Why Layer-based (not Feature-based)?

**Layer-based:**
```
src/cross_section/
  domain/
  geometry/
  export/
  interfaces/
```

**Feature-based:**
```
src/cross_section/
  lanes/
  curbs/
  medians/
```

**Decision: Layer-based**

**Rationale:**
- Clear separation of concerns
- Dependencies flow inward
- Easier to understand architecture
- Better for library use (import specific layers)

---

## Configuration Management

### Environment Variables vs Config Files

**Decision: Both**

- **Environment variables:** Deployment config (API keys, URLs)
- **Config files:** User preferences, templates
- **Defaults:** Sane defaults in code

**Format:** YAML for human-edited configs

**Example:**
```yaml
# ~/.cross-section/config.yaml
defaults:
  lane_width: 3.6
  shoulder_width: 2.4
  units: metric

export:
  dxf:
    version: R2018
  svg:
    scale: 100
```

---

## Error Handling Strategy

### Validation Errors

**Philosophy:** Fail fast with clear messages

```python
def validate(self) -> List[str]:
    """Return list of errors (empty if valid)"""
    errors = []
    if self.width <= 0:
        errors.append("Width must be positive")
    return errors
```

**Benefits:**
- Collect all errors, not just first
- Clear error messages
- Easy to test
- Non-exception based (faster)

### Export Errors

**Philosophy:** Exception-based for I/O

```python
def export(self, path: str):
    try:
        # Export logic
    except IOError as e:
        raise ExportError(f"Failed to write {path}: {e}")
```

**Benefits:**
- Standard Python pattern
- Can't ignore failures
- Stack traces for debugging

---

## Testing Strategy

### Unit Tests
- Every component
- Every exporter
- Every validator
- 90%+ coverage

### Integration Tests
- Full workflow tests
- CLI command tests
- API endpoint tests

### Property Tests (Hypothesis)
- Geometric invariants
- Validation rules
- Round-trip tests (create → export → import)

### Visual Tests
- Generate outputs
- Manual inspection
- Image comparison (for SVG)

---

## Documentation Strategy

### Code Documentation
- Docstrings: Google style
- Type hints: All public APIs
- Comments: Why, not what

### User Documentation
- Getting started guide
- Tutorial with examples
- API reference (auto-generated)
- Component catalog

### Developer Documentation
- Architecture overview (this doc)
- Contributing guide
- Development setup
- Design patterns used

---

## Versioning Strategy

**Semantic Versioning (SemVer)**

- **MAJOR:** Breaking API changes
- **MINOR:** New features, backward compatible
- **PATCH:** Bug fixes

**Pre-1.0:**
- 0.1.0: Initial release (basic features)
- 0.2.0: Add web API
- 0.3.0: Add VIKTOR support
- 1.0.0: Stable API, production ready

**Compatibility:**
- Support last 2 minor versions
- Deprecation warnings for 1 version before removal

---

## Future-Proofing

### Extensibility Points

1. **New Components:** Implement `RoadComponent`
2. **New Exporters:** Implement `SectionExporter`
3. **New Validators:** Add to validation pipeline
4. **New Frontends:** Use application layer
5. **Custom Geometry:** Extend `ComponentGeometry`

### Plugin System (Future)

Could add plugin architecture:
```python
# Register custom component
ComponentRegistry.register('CustomLane', CustomLaneClass)

# Register custom exporter
ExporterFactory.register('custom', CustomExporter)
```

### API Stability

- Version API endpoints (`/api/v1/sections`)
- Deprecation policy
- Backward compatibility guarantees

---

## Lessons from Similar Projects

### What Worked Well Elsewhere

1. **OpenSCAD:** Programmatic design (we copy this)
2. **Blender:** Python API for extensions (inspiration)
3. **PostGIS:** Geometry standardization (we use similar approach)
4. **ezdxf:** Clean export API (we follow this pattern)

### What to Avoid

1. **Overly complex GUIs** → Start with code/API
2. **Proprietary formats** → Use standards (DXF, SVG)
3. **Monolithic design** → Keep modular
4. **Poor documentation** → Document from day 1

---

## Success Criteria

### Technical
- ✅ Clean architecture with clear layers
- ✅ 90%+ test coverage
- ✅ Type-safe with mypy
- ✅ Fast exports (<1s for typical sections)
- ✅ Extensible design

### User Experience
- ✅ Clear error messages
- ✅ Good documentation
- ✅ Multiple interfaces (CLI, Web, VIKTOR)
- ✅ Standard templates
- ✅ Easy to learn

### Project
- ✅ On-time delivery
- ✅ Active maintenance
- ✅ Community engagement
- ✅ Clear roadmap

---

## References

### Books
- "Clean Architecture" by Robert C. Martin
- "Design Patterns" by Gang of Four
- "Domain-Driven Design" by Eric Evans

### Articles
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Python Design Patterns](https://refactoring.guru/design-patterns/python)

### Similar Projects
- [OpenRoads Designer](https://www.bentley.com/software/openroads-designer/)
- [Civil 3D](https://www.autodesk.com/products/civil-3d/)
- [QGIS](https://qgis.org/) (for GIS inspiration)
