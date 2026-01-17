# Annotation Guides Proposal

## Observations

- Annotation intent is not encoded in the domain model. Most annotations are manually defined in scenarios, and the generator only adds a small, fixed set of labels and dimensions.
- Leaders are especially brittle: the arrow tip is a manual point and collision resolution moves the entire leader, so the arrow tip drifts away from the target.
- There is no explicit guarantee that critical geometry (for example, crown point) receives a required dimension.
- There is no way to override annotation preferences (notes vs. dimension text, agency styles) without rewriting generator logic.

## Proposed Direction

Add annotation guides to the domain model via a registry keyed to component types so objects declare what they should be annotated with, while placement is derived from geometry and profile preferences. The generator becomes a planner that interprets guides rather than ad-hoc per-scenario annotations.

## Core Model Concepts

### 1) Annotation Guide Registry

Each component declares its annotation intent via a registry keyed by component type. Multiple guides can apply to a single component (for example, a travel lane may have width dimension, travel direction arrow, and cross-slope arrow).

- `TravelLane` declares a width dimension line.
- Pavement layers declare a material label or supplemental note on a dimension line.
- Crown point declares a required dimension.

Example data model (sketch):

```python
@dataclass(frozen=True)
class AnnotationGuide:
    kind: AnnotationKind  # "dimension", "note", "symbol", "leader"
    anchor: AnchorSpec    # "left_edge", "right_edge", "crown", "centroid", etc.
    target: TargetSpec    # "width", "layer_thickness", "slope", "point"
    required: bool = False
    text: str | None = None
    preference_key: str | None = None  # For agency overrides
```

Registry sketch:

```python
registry.register(
    "TravelLane",
    [
        AnnotationGuide(kind="dimension", target="width", anchor="edges", required=True),
        AnnotationGuide(kind="symbol", target="travel_direction", anchor="centerline"),
        AnnotationGuide(kind="symbol", target="cross_slope", anchor="surface"),
    ],
)
```

### 2) Annotation Profile (Agency Overrides)

Introduce a configuration layer that maps guide `preference_key` or component types to specific behavior:

```python
@dataclass(frozen=True)
class AnnotationProfile:
    dimension_style: DimensionStyle
    note_style: NoteStyle
    leader_style: LeaderStyle
    overrides: dict[str, AnnotationOverride]
```

Overrides can:
- disable or require guides (`required` hard overrides),
- choose note vs. dimension text,
- change offsets, text size, symbols, and label format,
- provide agency-specific defaults per component type.

### 3) Geometry-Driven Anchors

Replace manual leader points with anchors computed from geometry:

- `AnchorSpec` resolves to one or more geometry points (edge, centroid, crown, interface, toe, etc.).
- Leaders should always keep the arrow tip on the anchor; only the elbow and text position can move during collision resolution.
- Elbow underlines should be short: allow text-width underlines with only 1/8-1/4" extension beyond the text.
- Dimension lines derive from anchor pairs; crown dimension uses a fixed anchor at the crown point.

### 4) Annotation Planner

Add an annotation planner that consumes:
- `RoadSection` geometry,
- component `annotation_guides`,
- `AnnotationProfile`.

The planner produces actual `Annotation` objects with consistent placement rules and can be used by generators and tests.

## Behavioral Requirements

- Every `TravelLane` generates a width dimension line by default.
- `TravelLane` may also emit travel direction arrows and cross-slope arrows (profile-driven).
- Pavement layers produce either a note or supplemental text on a dimension line (profile-driven).
- Crown point must always have a dimension (required guide with no override to disable).
- Opposing cross slopes (left vs. right) should emit a warning, not a hard error.
- Leaders remain anchored to geometry; collision resolution moves only text and elbow.

## Implementation Steps (Proposed)

1) Add `AnnotationGuide`, `AnchorSpec`, and `AnnotationProfile` models in `src/cross_section/core/domain/annotations/`.
2) Add `annotation_guides` to relevant domain components (lanes, surfaces, crown, layers).
3) Implement `AnnotationPlanner` that maps guides + geometry to `Annotation` objects.
4) Update `AnnotationGenerator` to delegate to `AnnotationPlanner`.
5) Update collision logic to support fixed anchor points for leaders.
6) Add slope checks that warn on opposing cross slopes.
7) Add tests for:
   - required crown dimension,
   - leader anchor stability under collision resolution,
   - agency override behavior (note vs. dimension text),
   - guide-to-annotation mapping for lanes and layers.

## Open Questions

- Which anchors are required to cover common agency specs (edge, centerline, crown, gutter flowline)?
- How should dimension text formatting be overridden (units, rounding, custom text)?
