"""Annotation data types for road cross-section drawings.

Annotations are pure data — they carry geometry (positions, extents) and
display text but contain no rendering logic. Exporters (SVG, DXF) handle
how each annotation type is drawn.

Design principle (from constraint-based functional geometry):
  Annotations are *decorators attached to components*, derived from known
  geometry at collection time. There is no runtime collision resolution;
  placement is deterministic based on component bounds and tier rules.
"""

from dataclasses import dataclass, field


@dataclass
class Dimension:
    """A horizontal width dimension between two X positions.

    Renders as a horizontal dimension line at a fixed Y tier above the section,
    with vertical extension lines dropping to the component surface.

    Attributes:
        x_start: Left edge X coordinate (meters)
        x_end: Right edge X coordinate (meters)
        y_surface: Y elevation of the component surface at the dimension (meters)
        text: Dimension label (e.g., "3.6m" or "11.8ft")
        tier: Vertical tier index (0 = closest to section, 1 = next, …)
        layer: DXF layer name (e.g., "ANNOTATION_DIM")
    """

    x_start: float
    x_end: float
    y_surface: float
    text: str
    tier: int = 0
    layer: str = "ANNOTATION_DIM"

    @property
    def width(self) -> float:
        return abs(self.x_end - self.x_start)

    @property
    def x_mid(self) -> float:
        return (self.x_start + self.x_end) / 2.0


@dataclass
class Label:
    """A text label placed at a specific position.

    Used for material callouts, layer descriptions, and component identifiers.

    Attributes:
        x: X position (meters)
        y: Y position (meters)
        text: Label content
        layer: DXF layer name (e.g., "ANNOTATION_TEXT")
    """

    x: float
    y: float
    text: str
    layer: str = "ANNOTATION_TEXT"


@dataclass
class SlopeTag:
    """A slope indicator showing cross-slope as a percentage.

    Attributes:
        x: X position of the tag midpoint (meters)
        y: Y position of the tag (meters, at component surface)
        text: Slope text (e.g., "2.0%" or "1:50")
        layer: DXF layer name
    """

    x: float
    y: float
    text: str
    layer: str = "ANNOTATION_SLOPE"


@dataclass
class ComponentSpan:
    """A rule for creating a dimension that spans multiple component types.

    The collector matches all components whose ``component_type`` is in
    ``types``, finds their combined X extent, and emits a single ``Dimension``
    labelled with ``label``.

    This directly models the DOT convention of annotating aggregate widths
    (traveled way, curb-to-curb, shoulder-to-shoulder, etc.) alongside
    per-component dimensions.

    Attributes:
        types: Component type names to include (e.g. ``["TravelLane", "TurnLane"]``).
        label: Text for the dimension (e.g. ``"Traveled Way"``).  If ``None``,
            the collected width is formatted in the selected unit system.
        tier: Dimension tier.  Use 1 for aggregate spans so they appear above
            the tier-0 per-component dimensions.
        layer: DXF layer name.
        sides: Which assembly sides to include: ``"both"``, ``"left"``, or ``"right"``.

    Examples::

        # Full traveled way (both lanes + turn lane, both sides)
        ComponentSpan(
            types=["TravelLane", "TurnLane"],
            label="Traveled Way",
            tier=1,
        )

        # Curb-to-curb (lanes + curbs)
        ComponentSpan(
            types=["TravelLane", "TurnLane", "Curb", "Gutter"],
            label="Curb to Curb",
            tier=2,
        )

        # Back-of-walk to back-of-walk
        ComponentSpan(
            types=["TravelLane", "TurnLane", "Curb", "Gutter", "Sidewalk"],
            label="Back of Walk to Back of Walk",
            tier=3,
        )
    """

    types: list[str]
    label: str | None = None
    tier: int = 1
    layer: str = "ANNOTATION_DIM"
    sides: str = "both"  # "both" | "left" | "right"


@dataclass
class SectionAnnotations:
    """All annotations for a complete road section.

    Attributes:
        dimensions: Width dimension annotations (above section), keyed by tier.
            Tier 0 = per-component, tier 1+ = spanning / aggregate.
        labels: Material and component labels (inside or below section)
        slope_tags: Cross-slope indicators (at component surfaces)
    """

    dimensions: list[Dimension] = field(default_factory=list)
    labels: list[Label] = field(default_factory=list)
    slope_tags: list[SlopeTag] = field(default_factory=list)
