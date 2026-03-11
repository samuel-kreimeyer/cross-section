"""Annotation collector — derives annotations from assembled section geometry.

This replaces the old annotation generator/planner/collision/solver stack.

Core philosophy (constraint-based functional geometry):
  Each component already knows its own geometry — stored in ComponentGeometry.metadata.
  Annotations are *read* from that metadata, not planned after the fact.

Placement rules (no collision resolution needed):
  - Width dimensions: all at one fixed Y tier above the section.
    Extension lines drop vertically to each component's surface.
    If a span is too narrow for in-line text the label is placed outside.
  - Spanning dimensions: multiple components aggregated into one measurement
    (e.g. "Traveled Way", "Curb to Curb").  Placed at higher tiers so they
    sit above the per-component tier-0 dimensions.
  - Slope tags: placed at the midpoint of the component surface.
  - Layer labels: placed at the vertical center of the top pavement polygon.
"""

from __future__ import annotations

from typing import Literal

from ..section import SectionGeometry
from .types import ComponentSpan, Dimension, Label, SectionAnnotations, SlopeTag

# Components whose widths are worth annotating individually (tier 0)
_WIDTH_COMPONENT_TYPES = {
    "TravelLane",
    "TurnLane",
    "Shoulder",
    "Curb",
    "Sidewalk",
    "Ditch",
    "Gutter",
    "Buffer",
    "Barrier",
    "RetainingWall",
}

# Components whose cross-slope is worth tagging
_SLOPE_COMPONENT_TYPES = {
    "TravelLane",
    "TurnLane",
    "Shoulder",
    "Sidewalk",
}

# Default ComponentSpan rules that match common DOT conventions.
# Callers can pass their own list to override these completely.
DEFAULT_SPANS: list[ComponentSpan] = [
    ComponentSpan(
        types=["TravelLane", "TurnLane"],
        label="Traveled Way",
        tier=1,
    ),
]


def _format_slope(slope: float, units: Literal["metric", "imperial"]) -> str:
    """Format a cross-slope value as a readable string."""
    pct = abs(slope) * 100.0
    direction = "↓" if slope > 0 else "↑"
    return f"{pct:.1f}% {direction}"


def _format_width(width: float, units: Literal["metric", "imperial"]) -> str:
    """Format a width value in the appropriate units."""
    if units == "imperial":
        feet = width * 3.28084
        return f"{feet:.1f}'"
    return f"{width:.2f}m"


class AnnotationCollector:
    """Derives annotations from a SectionGeometry.

    Reads ComponentGeometry.metadata that each component already writes and
    produces a flat SectionAnnotations object ready for any exporter.

    Usage::

        # Default — per-component dims + "Traveled Way" span:
        collector = AnnotationCollector(units="imperial")
        annotations = collector.collect(geometry)

        # Custom spans for a typical urban section:
        collector = AnnotationCollector(
            units="imperial",
            spans=[
                ComponentSpan(
                    types=["TravelLane", "TurnLane"],
                    label="Traveled Way",
                    tier=1,
                ),
                ComponentSpan(
                    types=["TravelLane", "TurnLane", "Curb", "Gutter"],
                    label="Curb to Curb",
                    tier=2,
                ),
            ],
        )
        annotations = collector.collect(geometry)

        # Per-component only, no spans:
        collector = AnnotationCollector(spans=[])

    Parameters
    ----------
    units:
        ``"metric"`` or ``"imperial"`` — affects dimension label formatting.
    include_widths:
        Generate per-component (tier 0) width dimension annotations.
    include_slopes:
        Generate cross-slope tag annotations.
    include_layer_labels:
        Generate pavement-layer text labels inside polygons.
    spans:
        Rules for aggregate / spanning dimensions (tier 1+).  Pass an empty
        list to suppress all spanning dimensions.  Pass ``None`` to use the
        library defaults (``DEFAULT_SPANS``).
    """

    def __init__(
        self,
        units: Literal["metric", "imperial"] = "imperial",
        include_widths: bool = True,
        include_slopes: bool = True,
        include_layer_labels: bool = True,
        spans: list[ComponentSpan] | None = None,
    ) -> None:
        self.units = units
        self.include_widths = include_widths
        self.include_slopes = include_slopes
        self.include_layer_labels = include_layer_labels
        self.spans = DEFAULT_SPANS if spans is None else spans

    def collect(self, geometry: SectionGeometry) -> SectionAnnotations:
        """Derive all annotations from assembled section geometry.

        Args:
            geometry: The fully assembled section geometry.

        Returns:
            SectionAnnotations ready for export.
        """
        annotations = SectionAnnotations()

        for comp in geometry.components:
            meta = comp.metadata
            comp_type = meta.get("component_type", "")

            if not comp.polygons and not comp.polylines:
                continue

            bounds = comp.bounds()
            min_x, min_y, max_x, max_y = bounds
            mid_x = (min_x + max_x) / 2.0

            # Per-component width dimension (tier 0)
            if self.include_widths and comp_type in _WIDTH_COMPONENT_TYPES:
                width = meta.get("width")
                if width is not None and abs(max_x - min_x) > 1e-6:
                    text = _format_width(float(width), self.units)
                    annotations.dimensions.append(
                        Dimension(
                            x_start=min_x,
                            x_end=max_x,
                            y_surface=max_y,
                            text=text,
                            tier=0,
                            layer="ANNOTATION_DIM",
                        )
                    )

            # Cross-slope tag
            if self.include_slopes and comp_type in _SLOPE_COMPONENT_TYPES:
                slope = meta.get("cross_slope")
                if slope is not None and abs(float(slope)) > 1e-6:
                    slope_text = _format_slope(float(slope), self.units)
                    annotations.slope_tags.append(
                        SlopeTag(
                            x=mid_x,
                            y=max_y,
                            text=slope_text,
                            layer="ANNOTATION_SLOPE",
                        )
                    )

            # Pavement layer labels
            if self.include_layer_labels and comp_type in ("TravelLane", "TurnLane", "Shoulder"):
                layers_meta = meta.get("layers", [])
                for i, layer_info in enumerate(layers_meta):
                    if i >= len(comp.polygons):
                        break
                    poly = comp.polygons[i]
                    poly_bounds = poly.bounds()
                    label_x = (poly_bounds[0] + poly_bounds[2]) / 2.0
                    label_y = (poly_bounds[1] + poly_bounds[3]) / 2.0
                    label_text = _layer_label(layer_info)
                    if label_text:
                        annotations.labels.append(
                            Label(
                                x=label_x,
                                y=label_y,
                                text=label_text,
                                layer="ANNOTATION_TEXT",
                            )
                        )

        # Aggregate / spanning dimensions (tier 1+)
        if self.spans:
            self._collect_spans(geometry, annotations)

        return annotations

    # ------------------------------------------------------------------
    # Spanning dimension logic
    # ------------------------------------------------------------------

    def _collect_spans(
        self, geometry: SectionGeometry, annotations: SectionAnnotations
    ) -> None:
        """Generate spanning dimensions from ComponentSpan rules.

        For each rule the collector:
        1. Finds all components whose type is in ``rule.types``, filtered by
           ``rule.sides``.
        2. Computes their combined X extent (min of all x_start, max of all x_end).
        3. Uses the maximum y_surface across matched components so the
           dimension line extension always reaches the highest surface point.
        4. Emits one Dimension per rule (if at least one matching component is found).

        The resulting dimensions are placed at ``rule.tier``, which should be
        >= 1 so they render above the tier-0 per-component dimensions.
        """
        for rule in self.spans:
            matching: list[tuple[float, float, float]] = []  # (x_start, x_end, y_surface)

            for comp in geometry.components:
                meta = comp.metadata
                comp_type = meta.get("component_type", "")
                direction = meta.get("assembly_direction", "")

                if comp_type not in rule.types:
                    continue
                if rule.sides != "both" and direction != rule.sides:
                    continue
                if not comp.polygons and not comp.polylines:
                    continue

                bounds = comp.bounds()
                min_x, _, max_x, max_y = bounds
                if abs(max_x - min_x) < 1e-6:
                    continue
                matching.append((min_x, max_x, max_y))

            if not matching:
                continue

            span_x_start = min(m[0] for m in matching)
            span_x_end = max(m[1] for m in matching)
            span_y_surface = max(m[2] for m in matching)
            span_width = abs(span_x_end - span_x_start)

            if rule.label is not None:
                width_str = _format_width(span_width, self.units)
                text = f"{rule.label} = {width_str}"
            else:
                text = _format_width(span_width, self.units)

            annotations.dimensions.append(
                Dimension(
                    x_start=span_x_start,
                    x_end=span_x_end,
                    y_surface=span_y_surface,
                    text=text,
                    tier=rule.tier,
                    layer=rule.layer,
                )
            )


def _layer_label(layer_info: dict) -> str:
    """Build a short label string from a layer metadata dict."""
    layer_type = layer_info.get("type", "")
    thickness_m = layer_info.get("thickness")
    thickness_str = ""
    if thickness_m is not None:
        thickness_mm = float(thickness_m) * 1000
        thickness_str = f"{thickness_mm:.0f}mm "

    if layer_type == "AsphaltLayer":
        binder = layer_info.get("binder_type", "")
        return f"{thickness_str}AC {binder}".strip()
    if layer_type == "ConcreteLayer":
        strength = layer_info.get("compressive_strength", "")
        reinforced = layer_info.get("reinforced", False)
        rebar = " (reinf.)" if reinforced else ""
        return f"{thickness_str}PCC {strength}{rebar}".strip()
    if layer_type == "CrushedRockLayer":
        material = layer_info.get("material_type", "Agg. Base")
        return f"{thickness_str}{material}".strip()
    return f"{thickness_str}{layer_type}".strip()
