# Project Specification

## Summary

Cross-Section is a library for generating dimensionally accurate cross section graphics for transportation projects (highways and trails). It provides a domain-driven API that models real-world roadway components, enabling civil engineers and CAD application developers to describe cross sections naturally and receive publication-ready output files (SVG, DXF) with automatic, aesthetically-placed annotations.

## Goals

1. **Sound domain-driven core API**: Components model real-world roadway elements (travel lanes, shoulders, curbs, ditches, retaining walls) with correct geometric relationships and assembly rules.

2. **Intuitive minimal-input API**: Users describe sections with minimal parameters; the system infers reasonable defaults and "does the right thing."

3. **Dimensionally accurate output**: Generated diagrams preserve exact geometry that can be used directly in CAD workflows without translation or scaling adjustments.

4. **Automatic annotation**: Objects self-annotate based on their type and configuration. No external input required beyond optional preference configuration.

5. **Aesthetic annotation placement**: Leaders, dimensions, notes, and symbols are placed where a CAD professional would place them. No crossing lines, overlaps, or collisions.

6. **Multiple output formats**: SVG and DXF initially, with architecture supporting future DWG, DGN, and IFC outputs.

## Non-goals

1. **Structural pavement design**: This system generates graphics, not engineering calculations for pavement layer thickness or material strength.

2. **Persistence beyond file output**: No database, project management, or design history. The system behaves as a pure function: input description → output file.

3. **Deep customization UI**: No complex configuration dialogs, menus, or per-element tweaking. Users may configure wording, symbols, units, and which elements to label, but sane defaults take priority over user input.

## Users & Use Cases

### Primary Personas

**Civil Engineer (Designer)**
- Needs to generate cross section graphics for project documentation
- Wants to describe a section in terms they understand (travel lanes, shoulders, slopes)
- Expects output they can drop directly into CAD drawings or reports

**CAD Application Developer**
- Building tools for civil engineers
- Needs a reliable library to generate cross sections programmatically
- Requires clean API that matches engineering terminology

### Key Workflows

1. **Library-based generation**: Developer imports the library, constructs a cross section using domain objects (TravelLane, Shoulder, Curb, Ditch, etc.), and exports to SVG/DXF.

2. **CLI generation**: User invokes CLI with component parameters, receives output file.

3. **Configuration-driven generation**: User provides a section description file with component specifications and preferences; system generates annotated output.

## Acceptance Criteria

### Scenario 1: Basic Two-Lane Road (Happy Path)
**Given** a section with two 12-foot travel lanes, 6-foot shoulders, and 3:1 fill slopes
**When** the user exports to SVG
**Then** the output shows geometrically accurate lanes with correct widths, slopes at exact ratios, and automatic annotations showing lane widths, slope ratios, and shoulder labels without any overlapping text or crossing leader lines.

### Scenario 2: Complex Urban Section
**Given** a section with multiple travel lanes, curb and gutter, sidewalk, and retaining wall
**When** the user exports to DXF
**Then** all components connect at coincident edges, curb geometry follows standard profiles, and annotations are arranged in zones (underground, surface, above-grade) without collisions.

### Scenario 3: Invalid Component Assembly
**Given** a section where a user attempts to attach a travel lane to three different components simultaneously
**When** the section is validated
**Then** the system raises a clear error identifying the impossible geometry before any file generation occurs.

### Scenario 4: Annotation Collision Avoidance
**Given** a narrow section with many closely-spaced components
**When** annotations are generated
**Then** the annotation engine repositions labels, adjusts leader lines, and uses stacking strategies to avoid all collisions while maintaining readability.

### Scenario 5: Minimal Input Inference
**Given** only a travel lane width and shoulder type specified
**When** the section is generated
**Then** the system applies reasonable defaults for slopes, materials, layer thicknesses, and produces a complete, annotated section.

## Architecture

### Core Components

```
cross_section/
├── core/
│   └── domain/
│       ├── components/       # Roadway elements (TravelLane, Shoulder, Curb, etc.)
│       ├── geometry/         # Coordinate systems, lines, polygons, transforms
│       ├── annotations/      # Annotation engine (leaders, dimensions, labels)
│       └── assembly/         # Component connection and validation rules
├── output/
│   ├── svg/                  # SVG renderer
│   └── dxf/                  # DXF renderer
├── config/                   # User preferences (units, symbols, label formats)
└── cli/                      # Command-line interface
```

### Design Principles

1. **Domain-driven design**: API terminology matches civil engineering concepts. A `TravelLane` is a travel lane, not a "Rectangle with properties."

2. **Composition over inheritance**: Sections are assembled from discrete components with explicit attachment points.

3. **Validation at boundaries**: Geometry soundness checks run when components are connected, not during file generation. Fail fast.

4. **Output adapters**: Renderers implement a common interface. Adding DWG support means adding a new adapter, not modifying core logic.

## Data Model

### Component (Abstract Base)
| Field | Type | Description |
|-------|------|-------------|
| id | string | Unique identifier |
| geometry | Polygon | Component boundary |
| left_attachment | Point | Connection point for left-adjacent component |
| right_attachment | Point | Connection point for right-adjacent component |
| annotation_config | AnnotationProfile | How this component self-annotates |

### TravelLane
| Field | Type | Constraint |
|-------|------|------------|
| width | float | > 0, typically 10-14 ft |
| cross_slope | float | percentage, typically 1.5-2% |
| surface_type | enum | ASPHALT, CONCRETE, GRAVEL |

### Shoulder
| Field | Type | Constraint |
|-------|------|------------|
| width | float | > 0 |
| surface_type | enum | PAVED, GRAVEL, GRASS |
| slope | float | percentage |

### Slope (Cut/Fill)
| Field | Type | Constraint |
|-------|------|------------|
| ratio | tuple(h, v) | e.g., (3, 1) for 3:1 |
| height | float | vertical extent |
| type | enum | CUT, FILL |

### AnnotationProfile
| Field | Type | Description |
|-------|------|-------------|
| label_template | string | Text format (e.g., "{width}' {surface_type}") |
| dimension_style | enum | ABOVE, BELOW, INLINE |
| leader_zone | enum | TOP, BOTTOM, INLINE |
| priority | int | Collision resolution priority |

### Section (Root Aggregate)
| Field | Type | Description |
|-------|------|-------------|
| components | List[Component] | Ordered left-to-right |
| centerline_offset | float | Station offset if applicable |
| annotation_settings | dict | Global annotation preferences |

## Interfaces

### Python Library API
```python
from cross_section import Section, TravelLane, Shoulder, Slope

section = Section()
section.add(TravelLane(width=12, cross_slope=0.02))
section.add(Shoulder(width=6, surface_type="PAVED"))
section.add(Slope(ratio=(3, 1), type="FILL"))

section.validate()  # Raises if geometry invalid
section.export("output.svg", annotate=True)
```

### CLI
```bash
cross-section generate \
  --lane 12ft --lane 12ft \
  --shoulder 6ft paved \
  --slope 3:1 fill \
  --output section.svg
```

### Configuration File (YAML)
```yaml
units: imperial
annotation:
  font_size: 10
  leader_style: angled
  dimension_precision: 2
components:
  travel_lane:
    default_width: 12
    label_format: "{width}' LANE"
```

## Error Handling

### Invalid Geometry
- **Detection**: At component attachment time
- **Behavior**: Raise `GeometryError` with specific message ("Shoulder cannot attach to TravelLane: edge coordinates do not match")
- **Recovery**: User must correct component parameters

### Impossible Assembly
- **Detection**: During `section.validate()` or at attachment
- **Behavior**: Raise `AssemblyError` identifying conflicting components
- **Examples**: Component attached to multiple parents, circular dependencies, gaps between components

### Annotation Collisions (Unresolvable)
- **Detection**: During annotation planning
- **Behavior**: Log warning with specific collision details. Generate output with best-effort placement. Return collision report to caller.
- **Recovery**: User may adjust section or annotation configuration

### Unsupported Output Format
- **Detection**: At export time
- **Behavior**: Raise `UnsupportedFormatError` listing available formats

## Testing Plan

### Unit Tests (Target: 80%+ coverage)
- Component geometry calculations
- Attachment point validation
- Annotation collision detection algorithms
- Profile and dimension formatting

### Integration Tests
- End-to-end section generation with multiple component types
- Annotation engine produces zero collisions on reference sections
- SVG and DXF outputs are valid and parseable
- CLI produces expected files from reference inputs

### Visual Regression Tests
- Reference SVG outputs compared pixel-by-pixel or structurally
- Annotation positions stable across runs
- Font rendering and leader line placement consistent

### Validation Tests
- Invalid geometry rejected with clear errors
- Edge cases: zero-width components, extreme slopes, empty sections
- Annotation edge cases: very narrow sections, overlapping component labels

## Risks & Open Questions

### Automated Annotation Complexity
Automated annotation placement is an unsolved problem in industry-leading CAD software. The annotation engine must handle:
- Variable section complexity (simple 2-lane to complex urban interchanges)
- Dense component spacing
- Multiple annotation zones (underground utilities, surface features, overhead clearances)

**Mitigation**: Implement zone-based annotation with priority hierarchies. Document any scenarios that cannot be automatically resolved. Only mark something as "impossible" if no algorithmic solution exists—not merely inconvenient to implement.

### DXF/DWG Compatibility
DXF is a complex format with version-specific features. CAD software (AutoCAD, MicroStation) may render elements differently.

**Mitigation**: Target DXF R2010+ format. Test outputs in multiple CAD applications. Provide format-specific configuration options.

### Performance with Complex Sections
Sections with many components and annotations may have slow collision detection.

**Mitigation**: Profile annotation engine. Implement spatial indexing if needed. Set reasonable limits on component count.

### Open Decisions
1. **Layer naming convention for DXF**: Should layer names match component types or be user-configurable?
2. **Annotation stacking strategy**: When labels must stack, should priority be left-to-right or by component importance?
3. **Multi-page sections**: How to handle sections too wide for a single output page?
