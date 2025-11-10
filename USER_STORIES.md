# User Stories

## Purpose

This document captures user stories that guide the development and testing of the cross-section system. Each story describes a specific user need, desired behavior, and acceptance criteria.

User stories help:
- **Guide development**: Prioritize features that deliver real value
- **Drive testing**: Each story maps to test scenarios
- **Validate design**: Ensure architecture supports user needs
- **Document behavior**: Explain what the system should do

## Story Format

```
As a [role],
I want to [action],
So that [benefit].

Acceptance Criteria:
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

Priority: [High/Medium/Low]
Phase: [1-9 or Future]
Related Components: [component names]
Test Coverage: [link to test file]
```

---

## Safety & Compliance

### US-001: Automatic Barrier Placement for Steep Slopes

**As a** highway engineer,
**I want** the system to automatically add barriers when side slopes exceed maximum traversable slopes,
**So that** the design complies with safety standards without manual intervention.

**Scenario:**
A user specifies a cut slope with a 1V:1H ratio (45° slope), which exceeds the maximum traversable slope of 1V:4H (14°) per AASHTO guidelines.

**Acceptance Criteria:**
- [ ] System detects when slope ratio exceeds maximum traversable (configurable, default 1V:4H)
- [ ] Barrier component is automatically inserted at required offset from edge of traveled way
- [ ] Offset distance follows applicable standard (e.g., AASHTO minimum lateral offset)
- [ ] User is notified via message: "Barrier added: slope 1V:1H exceeds max traversable 1V:4H"
- [ ] User can override barrier placement if needed (with warning)
- [ ] Barrier type is appropriate for context (guardrail, cable barrier, or concrete barrier)
- [ ] Generated cross-section includes barrier in geometry and annotations

**Priority:** High
**Phase:** 7 (Extended Components) or earlier
**Related Components:** `CutSlope`, `FillSlope`, `Barrier`, validation rules
**Test Coverage:** `tests/unit/test_safety_validation.py`, `tests/integration/test_barrier_placement.py`

**Technical Notes:**
- Requires slope traversability validation in `core/validation/rules.py`
- Barrier offset calculation based on design speed and slope ratio
- Should reference standard: AASHTO Roadside Design Guide
- May need `BarrierPlacementRule` class

---

## Natural Language Interface

### US-002: Plain Language Cross Section Description

**As an** engineer,
**I want** to describe a cross section in plain language with only basic configuration,
**So that** I can quickly generate valid designs without specifying every detail.

**Scenario:**
User inputs: "Two-lane rural highway with 12-foot lanes, 8-foot paved shoulders, and 2:1 fill slopes. Add guardrail on outside of curves."

**Acceptance Criteria:**
- [ ] System parses plain language description
- [ ] Applies sensible defaults for unspecified parameters (cross-slopes, curb types, materials)
- [ ] Validates that configuration is constructible
- [ ] Applies exceptional conditions (e.g., guardrail on curves)
- [ ] Returns valid, complete cross-section
- [ ] User can review and modify generated section before export
- [ ] System explains what defaults were applied

**Example Input Formats:**
```
"4-lane divided highway, 11-ft lanes, 10-ft outside shoulders, 4-ft inside shoulders,
 raised median with barrier, 3:1 cut/fill"

"Urban arterial, 2 lanes each direction, bike lanes, parking, 6-ft sidewalks, curb and gutter"

"Local residential street, 10-ft lanes, 8-ft parking both sides, 5-ft sidewalks"
```

**Priority:** Medium
**Phase:** Future (post v1.0) - requires NLP
**Related Components:** All components, `SectionBuilder`, templates
**Test Coverage:** `tests/integration/test_nlp_parsing.py`

**Technical Notes:**
- May require NLP library (spaCy, NLTK) or LLM integration
- Could start with structured text format before full NLP
- Template matching as intermediate step
- See also: US-004 for error handling

**Alternative: Structured Text (Earlier Implementation)**
```yaml
# section.yaml
type: highway
lanes: 2
lane_width: 3.6
shoulders:
  width: 2.4
  paved: true
slopes:
  cut: "2:1"
  fill: "2:1"
special_conditions:
  - add_barrier_if: "slope > 4:1"
```

---

## Annotation & Visualization

### US-003: Scale-Aware Annotated Cross Sections

**As a** designer,
**I want** to produce annotated cross sections with scale-appropriate dimensions and labels,
**So that** drawings are clear, professional, and ready for plan sets.

**Scenario 1: User specifies scale**
User exports cross-section at 1:50 scale for A3 sheet. Annotations are sized appropriately.

**Scenario 2: User specifies output size**
User requests 11"×17" output with 2" margins. System calculates appropriate scale.

**Scenario 3: Smart defaults**
User exports without specifying scale. System ensures output fits 11"×17" with legible text.

**Acceptance Criteria:**

**Scale Handling:**
- [ ] User can specify output scale (e.g., 1:50, 1:100)
- [ ] User can specify output paper size (e.g., 11×17", A3, A1)
- [ ] If neither specified, system auto-scales to fit 11×17" with 2" margins
- [ ] Minimum text size is 8pt (or 2.5mm) at output scale
- [ ] If section too wide, system suggests appropriate scale or paper size

**Annotation Styles:**
- [ ] Multiple annotation styles available: "minimal", "standard", "detailed", "construction"
- [ ] Style controls what gets annotated (widths only vs. slopes, materials, stations)
- [ ] Style controls annotation appearance (text size, leader style, dimension format)
- [ ] User can customize styles or create new ones

**Annotation Content:**
- [ ] Component widths (with dimension lines)
- [ ] Slope ratios (e.g., "2:1" or "2H:1V")
- [ ] Materials/surface types (asphalt, concrete, gravel)
- [ ] Elevations (if vertical datum provided)
- [ ] Stationing (if applicable)
- [ ] Notes (e.g., "6\" AC over 8\" aggregate base")

**Visual Quality:**
- [ ] Dimension lines don't overlap
- [ ] Text is readable at output scale
- [ ] Leaders point clearly to referenced elements
- [ ] Consistent line weights and styles
- [ ] Professional appearance suitable for construction documents

**Export Formats:**
- [ ] DXF with annotations on separate layer
- [ ] PDF with vector annotations
- [ ] SVG with styled annotations

**Priority:** High
**Phase:** 8 (Testing & Documentation) - after basic export works
**Related Components:** All components, `DXFExporter`, `SVGExporter`, new `AnnotationEngine`
**Test Coverage:** `tests/unit/test_annotations.py`, `tests/visual/test_annotation_rendering.py`

**Technical Notes:**
- Annotation engine calculates label positions to avoid overlaps
- Scale calculation: `scale = section_width / (paper_width - 2*margin)`
- Text height in model units: `text_height_mm / scale`
- May use constraint solver for optimal label placement
- DXF: annotations on layer "ANNO", dimensions on "DIM"

**Example Style Definitions:**
```python
# Annotation styles
STYLES = {
    "minimal": {
        "show_widths": True,
        "show_slopes": False,
        "show_materials": False,
        "text_height_mm": 2.5,
        "dimension_style": "simple"
    },
    "standard": {
        "show_widths": True,
        "show_slopes": True,
        "show_materials": True,
        "show_elevations": False,
        "text_height_mm": 3.0,
        "dimension_style": "detailed"
    },
    "construction": {
        "show_widths": True,
        "show_slopes": True,
        "show_materials": True,
        "show_elevations": True,
        "show_notes": True,
        "text_height_mm": 3.5,
        "dimension_style": "construction"
    }
}
```

---

## Error Handling & Validation

### US-004: Plain Language Error Messages

**As a** user,
**I want** to receive clear, actionable error messages when inputs are invalid,
**So that** I understand what's wrong and how to fix it.

**Scenario 1: Invalid connection**
User tries to place a sidewalk directly next to a travel lane (missing curb).

**Bad Error:**
```
ValidationError: Component connection invalid at index 2
```

**Good Error:**
```
❌ Invalid connection between Lane and Sidewalk at position 2

The Sidewalk component requires a raised connection (curb), but the
adjacent TravelLane provides a flush connection.

Suggestions:
  • Insert a Curb component between the lane and sidewalk
  • Use a different edge treatment (e.g., Gutter, Shoulder)

Example fix:
  section.insert_component(2, Curb(height=0.15))
```

**Scenario 2: Impossible geometry**
User specifies conflicting dimensions that cannot be resolved.

**Good Error:**
```
❌ Cannot resolve cross-section geometry

The specified components create an unsolvable configuration:
  • Total width specified: 15.0 m
  • Sum of component widths: 18.4 m
  • Difference: -3.4 m (too wide by 3.4 m)

Components:
  1. Shoulder: 2.4 m
  2. Lane: 3.6 m
  3. Lane: 3.6 m
  4. Median: 6.0 m  ← Consider reducing
  5. Lane: 3.6 m
  6. Lane: 3.6 m
  7. Shoulder: 2.4 m

Suggestions:
  • Reduce median width to 2.6 m or less
  • Remove total width constraint
  • Reduce lane or shoulder widths
```

**Scenario 3: Standards violation**
Design violates minimum standards.

**Good Error:**
```
⚠️  Design does not meet minimum standards

Lane width (3.0 m) is below minimum for design classification:
  • Specified: 3.0 m
  • Minimum for "highway": 3.6 m (AASHTO)
  • Recommended: 3.7 m

This is a WARNING. You can proceed, but the design may not be acceptable
for construction.

To fix: increase lane width to 3.6 m or greater
To suppress: add flag --allow-substandard
```

**Acceptance Criteria:**

**Error Message Quality:**
- [ ] Errors explain WHAT is wrong (not just that something failed)
- [ ] Errors explain WHY it's wrong (violated rule, constraint, or standard)
- [ ] Errors suggest HOW to fix (specific actions or alternatives)
- [ ] Errors show WHERE the problem is (component index, position, or name)
- [ ] Error severity is clear: Error (blocking) vs Warning (advisory)

**Error Categories:**
- [ ] **Validation errors**: Invalid component connections, incompatible types
- [ ] **Geometry errors**: Impossible configurations, overlaps, gaps
- [ ] **Standards violations**: Minimum widths, maximum slopes, clear zones
- [ ] **Input errors**: Missing required fields, invalid values, type mismatches

**Error Context:**
- [ ] Show relevant section configuration
- [ ] Highlight problematic components
- [ ] Display current values vs. required values
- [ ] Link to documentation or standards reference

**Developer Experience:**
- [ ] Errors include component names/types (not just indices)
- [ ] Errors suggest code fixes (for API users)
- [ ] Validation errors are collected (not just first error)
- [ ] Errors are testable (consistent format)

**Priority:** High
**Phase:** 1 (Core Domain) - validation framework from the start
**Related Components:** All components, `validation/rules.py`, `RoadSection`
**Test Coverage:** `tests/unit/test_error_messages.py`

**Technical Notes:**
- Use custom exception classes: `ValidationError`, `GeometryError`, `StandardsViolation`
- Errors should have structured data (not just strings) for programmatic access
- Consider error codes for documentation cross-reference
- Support multiple locales eventually (start with English)

**Example Error Class:**
```python
@dataclass
class ValidationError(Exception):
    """Structured validation error"""
    message: str
    component_index: Optional[int]
    component_type: Optional[str]
    violation_type: str  # "connection", "geometry", "standard"
    current_value: Optional[Any]
    required_value: Optional[Any]
    suggestions: List[str]
    severity: str = "error"  # "error" or "warning"

    def __str__(self) -> str:
        """Generate human-readable error message"""
        lines = [f"❌ {self.message}\n"]

        if self.current_value and self.required_value:
            lines.append(f"  • Current: {self.current_value}")
            lines.append(f"  • Required: {self.required_value}\n")

        if self.suggestions:
            lines.append("Suggestions:")
            for suggestion in self.suggestions:
                lines.append(f"  • {suggestion}")

        return "\n".join(lines)
```

---

## Additional User Stories (To Be Developed)

### Safety & Compliance
- [ ] **US-005**: ADA compliance checking for pedestrian facilities
- [ ] **US-006**: Clear zone verification based on design speed
- [ ] **US-007**: Sight distance validation at intersections

### Design Standards
- [ ] **US-008**: Apply state DOT standard sections
- [ ] **US-009**: AASHTO geometric design standards checking
- [ ] **US-010**: Context-sensitive design alternatives

### Workflow & Productivity
- [ ] **US-011**: Compare multiple cross-section alternatives
- [ ] **US-012**: Batch generate sections for alignment stations
- [ ] **US-013**: Import existing cross-sections from other formats

### Collaboration
- [ ] **US-014**: Version control and change tracking
- [ ] **US-015**: Share sections with team members
- [ ] **US-016**: Review and approval workflow

### Analysis & Reporting
- [ ] **US-017**: Earthwork quantity calculations
- [ ] **US-018**: Cost estimation based on unit prices
- [ ] **US-019**: Generate cross-section sheets for plan sets

### Advanced Features
- [ ] **US-020**: Superelevation transitions
- [ ] **US-021**: 3D corridor modeling along alignment
- [ ] **US-022**: Drainage design integration

---

## Story Mapping to Development

### Phase 1 (Weeks 1-2): Core Domain
**Stories:** US-004 (error handling foundation)
- Implement validation framework
- Create structured error classes
- Test error message quality

### Phase 2 (Weeks 2-3): Geometry Layer
**Stories:** (foundation for later stories)
- Pure Python geometry enables all stories
- No direct user stories, but critical for US-001, US-003

### Phase 3 (Weeks 3-4): Export Layer
**Stories:** US-003 (basic export, annotations come later)
- DXF/SVG export without annotations
- Set foundation for annotation layer

### Phase 7 (Weeks 7-8): Extended Components
**Stories:** US-001 (barrier placement)
- Implement Barrier component
- Add slope traversability validation
- Auto-placement logic

### Phase 8 (Weeks 8-9): Testing & Documentation
**Stories:** US-003 (annotations), US-004 (polish error messages)
- Annotation engine
- Scale-aware rendering
- Error message review and improvement

### Future (Post v1.0)
**Stories:** US-002 (NLP interface)
- Natural language parsing
- Template matching
- LLM integration exploration

---

## Testing Strategy for User Stories

Each user story maps to specific test scenarios:

### US-001: Barrier Placement
```python
def test_steep_slope_triggers_barrier():
    """Test that steep slope automatically adds barrier"""
    section = RoadSection()
    section.add_component(TravelLane(width=3.6))
    section.add_component(Shoulder(width=2.4))
    section.add_component(FillSlope(h_ratio=1, v_ratio=1))  # 1:1 slope

    # Validate should add barrier
    warnings = section.validate_and_fix()

    assert any("barrier added" in w.lower() for w in warnings)
    assert any(isinstance(c, Barrier) for c in section.components)

def test_gentle_slope_no_barrier():
    """Test that gentle slope does not add barrier"""
    section = RoadSection()
    section.add_component(TravelLane(width=3.6))
    section.add_component(Shoulder(width=2.4))
    section.add_component(FillSlope(h_ratio=4, v_ratio=1))  # 4:1 slope

    warnings = section.validate_and_fix()

    assert not any("barrier" in w.lower() for w in warnings)
    assert not any(isinstance(c, Barrier) for c in section.components)
```

### US-003: Annotations
```python
def test_annotation_auto_scale():
    """Test automatic scaling for 11x17 paper"""
    section = create_wide_highway_section()  # 50m wide

    annotator = AnnotationEngine(
        paper_size=(11, 17),  # inches
        margins=2.0,  # inches
        units="metric"
    )

    scale = annotator.calculate_scale(section)

    # 50m should fit in 13" (17-2*2) at scale
    expected_scale = 50 / (13 * 0.0254)  # ~1:150
    assert abs(scale - expected_scale) < 0.1 * expected_scale

def test_annotation_text_legible():
    """Test that text is legible at calculated scale"""
    section = create_wide_highway_section()

    annotator = AnnotationEngine(paper_size=(11, 17), margins=2.0)
    drawing = annotator.annotate(section, style="standard")

    # Text should be >= 8pt (2.8mm) at output scale
    for text in drawing.text_elements:
        assert text.height_mm >= 2.5
```

### US-004: Error Messages
```python
def test_connection_error_message():
    """Test error message quality for invalid connection"""
    section = RoadSection()
    section.add_component(TravelLane(width=3.6))
    section.add_component(Sidewalk(width=2.0))  # Missing curb!

    with pytest.raises(ValidationError) as exc_info:
        section.validate_connections()

    error = exc_info.value

    # Check message quality
    assert "Sidewalk" in str(error)
    assert "TravelLane" in str(error)
    assert "curb" in str(error).lower()
    assert len(error.suggestions) > 0
    assert "insert" in error.suggestions[0].lower()
```

---

## Contributing New Stories

When adding user stories:

1. **Use the standard format** (As a... I want... So that...)
2. **Include acceptance criteria** (testable conditions)
3. **Assign priority and phase** (helps roadmap planning)
4. **Link to components** (shows architecture impact)
5. **Write test scenarios** (drives TDD)
6. **Get stakeholder review** (validate user needs)

**Template for new story:**
```markdown
### US-XXX: Story Title

**As a** [role],
**I want** [action],
**So that** [benefit].

**Scenario:**
[Describe concrete example]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

**Priority:** [High/Medium/Low]
**Phase:** [1-9 or Future]
**Related Components:** [components]
**Test Coverage:** [test file]

**Technical Notes:**
[Implementation considerations]
```

---

## Story Review Checklist

Before accepting a user story:

- [ ] **User-focused**: Written from user perspective, not implementation
- [ ] **Testable**: Acceptance criteria are verifiable
- [ ] **Valuable**: Delivers clear benefit to users
- [ ] **Independent**: Can be developed separately (mostly)
- [ ] **Small enough**: Can be completed in one phase
- [ ] **Clear**: Stakeholders understand what's being built

---

## References

- **AASHTO Green Book**: Geometric Design Standards
- **AASHTO Roadside Design Guide**: Clear zones and barriers
- **State DOT Standards**: Jurisdiction-specific requirements
- **ADA Guidelines**: Pedestrian facility requirements
