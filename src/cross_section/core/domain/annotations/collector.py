"""Annotation collector — derives annotations from assembled section geometry.

This replaces the old annotation generator/planner/collision/solver stack.

Core philosophy (constraint-based functional geometry):
  Each component already knows its own geometry — stored in ComponentGeometry.metadata.
  Annotations are *read* from that metadata, not planned after the fact.

Placement rules (no collision resolution needed):
  - Width dimensions: all at one fixed Y tier above the section.
    Extension lines drop vertically to each component's surface.
    If a span is too narrow for in-line text the label is placed outside.
  - Slope tags: placed at the midpoint of the component surface.
  - Layer labels: placed at the vertical center of the top pavement polygon.
"""

from __future__ import annotations

from typing import Literal

from ..section import SectionGeometry
from .types import Dimension, Label, SectionAnnotations, SlopeTag

# Components whose widths are worth annotating
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

# Minimum width (meters) for a dimension span — narrower spans get labels outside
_MIN_INLINE_SPAN_M = 0.5


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

        collector = AnnotationCollector(units="imperial")
        annotations = collector.collect(geometry)

    Options:
        units: "metric" or "imperial" — affects dimension label formatting.
        include_widths: Generate width dimension annotations.
        include_slopes: Generate cross-slope tag annotations.
        include_layer_labels: Generate pavement-layer text labels.
    """

    def __init__(
        self,
        units: Literal["metric", "imperial"] = "imperial",
        include_widths: bool = True,
        include_slopes: bool = True,
        include_layer_labels: bool = True,
    ) -> None:
        self.units = units
        self.include_widths = include_widths
        self.include_slopes = include_slopes
        self.include_layer_labels = include_layer_labels

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

            # Width dimension
            if self.include_widths and comp_type in _WIDTH_COMPONENT_TYPES:
                width = meta.get("width")
                if width is not None and abs(max_x - min_x) > 1e-6:
                    text = _format_width(float(width), self.units)
                    # y_surface = top of component (max_y from bounds)
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

        return annotations


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
