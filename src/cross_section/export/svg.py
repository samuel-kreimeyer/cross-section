"""SVG exporter for road cross-section geometry.

Pure Python — no external dependencies required.

The exporter supports two modes:

1. Geometry-only (SimpleSVGExporter.export):
   Renders component polygons and polylines with layer-based colours.

2. Annotated (SVGExporter.export_annotated):
   Adds width dimensions, slope tags, and layer labels above/below
   the geometry using a *tiered*, deterministic placement strategy —
   no runtime collision resolution.

Dimension placement:
   All width dimensions share a single horizontal dimension line located
   DIMENSION_TIER_MARGIN_M above the top of the section.  Vertical
   extension lines drop from that line to each component's surface.
   Text sits centred on the span; if the span is too narrow the text
   is placed outside with a small tick.
"""

from __future__ import annotations

import html
import math
from typing import TYPE_CHECKING, Literal, TextIO

from ..core.domain.section import SectionGeometry

if TYPE_CHECKING:
    from ..core.domain.annotations.types import SectionAnnotations

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Colours keyed by pavement layer class name
_LAYER_COLORS: dict[str, str] = {
    "AsphaltLayer": "#2C3E50",
    "ConcreteLayer": "#95A5A6",
    "CrushedRockLayer": "#7F8C8D",
}
_DEFAULT_COLOR = "#BDC3C7"

# Component fill colours for non-pavement components
_COMPONENT_COLORS: dict[str, str] = {
    "Curb": "#808080",
    "Sidewalk": "#A8A8A8",
    "Barrier": "#505050",
    "RetainingWall": "#606060",
    "Ditch": "#B8D4F0",
    "Slope": "#C8E6C9",
    "Gutter": "#909090",
    "Buffer": "#8BC34A",
    "Shoring": "#607D8B",
    "Shoulder": "#546E7A",
}

# Margin above section top to the dimension tier line (meters)
_DIMENSION_TIER_MARGIN_M = 0.8
# Arrow half-length at tips of dimension lines (meters)
_ARROW_SIZE_M = 0.05
# Minimum span for in-line dimension text (meters)
_MIN_INLINE_SPAN_M = 0.4
# Font size for dimension text (meters)
_DIM_FONT_SIZE_M = 0.18
# Font size for slope tags (meters)
_SLOPE_FONT_SIZE_M = 0.16
# Font size for layer labels (meters)
_LABEL_FONT_SIZE_M = 0.14
# Extension line overshoot above dimension tier line (meters)
_EXT_LINE_OVERSHOOT_M = 0.05


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _escape(text: str) -> str:
    return html.escape(str(text))


def _fmt_pts(points: list[tuple[float, float]]) -> str:
    return " ".join(f"{x:.3f},{y:.3f}" for x, y in points)


# ---------------------------------------------------------------------------
# SVG Exporter
# ---------------------------------------------------------------------------


class SVGExporter:
    """Export road section geometry (and optional annotations) to SVG.

    Parameters
    ----------
    scale:
        Pixels per metre.  Default 100 → 1 m = 100 px.
    vertical_exaggeration:
        Multiply vertical distances by this factor so thin layers are
        visible.  Default 1.0 (no exaggeration).
    units:
        ``"imperial"`` or ``"metric"`` — used for the scale bar label.
    content_margin_m:
        White-space margin around the section content, in metres.
    """

    def __init__(
        self,
        scale: float = 100.0,
        vertical_exaggeration: float = 1.0,
        units: Literal["imperial", "metric"] = "imperial",
        content_margin_m: float = 0.5,
    ) -> None:
        self.scale = scale
        self.ve = vertical_exaggeration  # vertical exaggeration factor
        self.units = units
        self.content_margin_m = content_margin_m

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def export(self, geometry: SectionGeometry, output: TextIO) -> None:
        """Export geometry without annotations."""
        self._write_svg(geometry, output, annotations=None)

    def export_annotated(
        self,
        geometry: SectionGeometry,
        annotations: "SectionAnnotations",
        output: TextIO,
    ) -> None:
        """Export geometry with annotations overlaid."""
        self._write_svg(geometry, output, annotations=annotations)

    # ------------------------------------------------------------------
    # Core rendering
    # ------------------------------------------------------------------

    def _write_svg(
        self,
        geometry: SectionGeometry,
        output: TextIO,
        annotations: "SectionAnnotations | None",
    ) -> None:
        if not geometry.components:
            output.write('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">')
            output.write('<text x="10" y="50">Empty section</text>')
            output.write("</svg>")
            return

        # Geometry bounds in model space (metres)
        g_min_x, g_min_y, g_max_x, g_max_y = geometry.bounds()

        # Annotation bounds — extend view upward for dimension tier
        ann_top_m = 0.0
        if annotations and annotations.dimensions:
            # Tier margin + arrow + text height above top of section
            ann_top_m = _DIMENSION_TIER_MARGIN_M + _DIM_FONT_SIZE_M + _EXT_LINE_OVERSHOOT_M

        # View bounds in model space (metres)
        m = self.content_margin_m
        view_min_x = g_min_x - m
        view_min_y = g_min_y - m
        view_max_x = g_max_x + m
        view_max_y = g_max_y + m + ann_top_m

        view_w_m = view_max_x - view_min_x
        view_h_m = (view_max_y - view_min_y) * self.ve

        svg_w = view_w_m * self.scale
        svg_h = view_h_m * self.scale

        # Reserve left margin for legend
        legend_items = self._collect_legend_items(geometry)
        legend_w_px = self._legend_width_px(geometry.metadata.get("name", ""), legend_items)
        legend_h_px = 20 + (len(legend_items) + 1) * 20

        total_w = svg_w + legend_w_px + 10
        total_h = max(svg_h, legend_h_px) + 50  # bottom margin for scale bar

        # Scale bar
        scale_len_m, scale_label = self._choose_scale_bar(view_w_m)

        output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        output.write('<svg xmlns="http://www.w3.org/2000/svg" ')
        output.write(f'width="{total_w:.1f}" height="{total_h:.1f}" ')
        output.write(f'viewBox="0 0 {total_w:.1f} {total_h:.1f}">\n')
        output.write(f'  <title>{_escape(geometry.metadata.get("name", "Road Section"))}</title>\n')
        output.write(f'  <rect width="{total_w:.1f}" height="{total_h:.1f}" fill="white"/>\n')

        # Geometry group — translated & Y-flipped
        # We render into a sub-SVG offset by legend_w_px horizontally
        content_x = legend_w_px + 10

        # Transform: flip Y (SVG Y↓, model Y↑)
        # After translate(0, svg_h) scale(1,-1):
        #   SVG_y = svg_h - (model_y - view_min_y) * scale * ve
        #   SVG_x = (model_x - view_min_x) * scale + content_x
        output.write(f'  <g id="geometry" transform="translate({content_x:.1f},0)">\n')
        output.write(f'    <g transform="translate(0,{svg_h:.3f}) scale(1,-1)">\n')
        output.write(f'      <g transform="translate({-view_min_x * self.scale:.3f},'
                     f'{view_min_y * self.scale * self.ve:.3f})">\n')

        for comp in geometry.components:
            self._render_component(output, comp)

        output.write("      </g>\n")
        output.write("    </g>\n")

        # Annotations (rendered in the same horizontal space but NOT y-flipped;
        # we compute SVG coords directly)
        if annotations:
            self._render_annotations(
                output, annotations, view_min_x, view_min_y, view_max_y, svg_h
            )

        output.write("  </g>\n")

        # Legend (top-left, outside geometry group)
        self._render_legend(output, geometry, legend_items, 10, 10)

        # Scale bar (bottom-left of entire SVG)
        self._render_scale_bar(output, scale_len_m, scale_label, 10, total_h - 30)

        output.write("</svg>\n")

    # ------------------------------------------------------------------
    # Coordinate helpers
    # ------------------------------------------------------------------

    def _to_svg_x(self, model_x: float, view_min_x: float) -> float:
        """Model X → SVG X within the geometry group (no content_x offset applied)."""
        return (model_x - view_min_x) * self.scale

    def _to_svg_y(self, model_y: float, view_min_y: float, view_max_y: float, svg_h: float) -> float:
        """Model Y → SVG Y (Y-axis flipped)."""
        # view_max_y in model space maps to SVG y=0 (top of content)
        # view_min_y in model space maps to SVG y=svg_h (bottom of content)
        return svg_h - (model_y - view_min_y) * self.scale * self.ve

    # ------------------------------------------------------------------
    # Component rendering
    # ------------------------------------------------------------------

    def _render_component(self, output: TextIO, comp: "SectionGeometry.components[0]") -> None:  # type: ignore[name-defined]
        meta = comp.metadata
        comp_type = meta.get("component_type", "")

        for poly_idx, polygon in enumerate(comp.polygons):
            color = self._polygon_color(meta, poly_idx, comp_type)
            pts = [(p.x * self.scale, p.y * self.scale * self.ve) for p in polygon.exterior]
            pts_str = _fmt_pts(pts)
            output.write(f'        <polygon points="{pts_str}" ')
            output.write(f'fill="{color}" stroke="#333333" stroke-width="0.8"/>\n')

            # Polygon holes (e.g., cable barrier post void)
            if polygon.holes:
                for hole in polygon.holes:
                    hole_pts = [(p.x * self.scale, p.y * self.scale * self.ve) for p in hole]
                    hole_str = _fmt_pts(hole_pts)
                    # Render holes by clipping: draw hole as white polygon on top
                    output.write(f'        <polygon points="{hole_str}" ')
                    output.write('fill="white" stroke="#333333" stroke-width="0.8"/>\n')

        # Polylines (ditch void outlines, surface profiles, etc.)
        polyline_styles = meta.get("polyline_styles", [])
        for pl_idx, polyline in enumerate(comp.polylines):
            pts = [(p.x * self.scale, p.y * self.scale * self.ve) for p in polyline]
            pts_str = _fmt_pts(pts)
            style = polyline_styles[pl_idx] if pl_idx < len(polyline_styles) else {}
            dasharray = style.get("stroke_dasharray", "")
            sw = style.get("stroke_width", "1.5")
            dash_attr = f'stroke-dasharray="{dasharray}" ' if dasharray else ""
            output.write(f'        <polyline points="{pts_str}" fill="none" '
                         f'stroke="#333333" stroke-width="{sw}" {dash_attr}/>\n')

    def _polygon_color(self, meta: dict, poly_idx: int, comp_type: str) -> str:
        """Determine fill colour for a polygon."""
        layers = meta.get("layers", [])
        if poly_idx < len(layers):
            layer_type = layers[poly_idx].get("type", "")
            if layer_type in _LAYER_COLORS:
                return _LAYER_COLORS[layer_type]
        for key in _COMPONENT_COLORS:
            if comp_type.startswith(key):
                return _COMPONENT_COLORS[key]
        return _DEFAULT_COLOR

    # ------------------------------------------------------------------
    # Annotation rendering
    # ------------------------------------------------------------------

    def _render_annotations(
        self,
        output: TextIO,
        annotations: "SectionAnnotations",
        view_min_x: float,
        view_min_y: float,
        view_max_y: float,
        svg_h: float,
    ) -> None:
        output.write('    <!-- Annotations -->\n')

        # Slope tags — rendered near the surface (small italic text)
        for tag in annotations.slope_tags:
            sx = self._to_svg_x(tag.x, view_min_x)
            sy = self._to_svg_y(tag.y, view_min_y, view_max_y, svg_h)
            fs = _SLOPE_FONT_SIZE_M * self.scale
            output.write(f'    <text x="{sx:.2f}" y="{sy - 4:.2f}" '
                         f'font-family="Arial" font-size="{fs:.1f}" '
                         f'font-style="italic" text-anchor="middle" '
                         f'fill="#444">{_escape(tag.text)}</text>\n')

        # Layer labels — rendered inside polygon centroids
        for label in annotations.labels:
            lx = self._to_svg_x(label.x, view_min_x)
            ly = self._to_svg_y(label.y, view_min_y, view_max_y, svg_h)
            fs = _LABEL_FONT_SIZE_M * self.scale
            output.write(f'    <text x="{lx:.2f}" y="{ly:.2f}" '
                         f'font-family="Arial" font-size="{fs:.1f}" '
                         f'text-anchor="middle" dominant-baseline="middle" '
                         f'fill="white" opacity="0.85">{_escape(label.text)}</text>\n')

        # Width dimensions — horizontal line above section
        if annotations.dimensions:
            self._render_dimensions(
                output, annotations.dimensions, view_min_x, view_min_y, view_max_y, svg_h
            )

    def _render_dimensions(
        self,
        output: TextIO,
        dimensions: list["Dimension"],  # type: ignore[name-defined]
        view_min_x: float,
        view_min_y: float,
        view_max_y: float,
        svg_h: float,
    ) -> None:
        """Render all width dimensions.

        Dimension line is a horizontal line _DIMENSION_TIER_MARGIN_M above
        the top of section geometry.  Extension lines drop from that line
        to each component's surface.
        """
        # Y position of the dimension tier line (model space → SVG)
        tier_y_model = view_max_y - self.content_margin_m + _EXT_LINE_OVERSHOOT_M
        tier_svg_y = self._to_svg_y(tier_y_model, view_min_y, view_max_y, svg_h)

        dim_line_color = "#222"
        dim_stroke = max(0.8, self.scale * 0.008)
        text_fs = _DIM_FONT_SIZE_M * self.scale
        arrow_px = _ARROW_SIZE_M * self.scale
        min_inline_px = _MIN_INLINE_SPAN_M * self.scale

        output.write('    <!-- Width dimensions -->\n')
        output.write(f'    <g stroke="{dim_line_color}" stroke-width="{dim_stroke:.2f}" '
                     f'font-family="Arial" font-size="{text_fs:.1f}" fill="{dim_line_color}">\n')

        for dim in dimensions:
            x1 = self._to_svg_x(dim.x_start, view_min_x)
            x2 = self._to_svg_x(dim.x_end, view_min_x)
            # Ensure x1 < x2 for rendering
            if x1 > x2:
                x1, x2 = x2, x1

            surf_svg_y = self._to_svg_y(dim.y_surface, view_min_y, view_max_y, svg_h)

            # Extension lines
            overshoot_px = _EXT_LINE_OVERSHOOT_M * self.scale
            ext_top = tier_svg_y - overshoot_px
            output.write(f'      <line x1="{x1:.2f}" y1="{ext_top:.2f}" '
                         f'x2="{x1:.2f}" y2="{surf_svg_y:.2f}" '
                         f'stroke-dasharray="3,2"/>\n')
            output.write(f'      <line x1="{x2:.2f}" y1="{ext_top:.2f}" '
                         f'x2="{x2:.2f}" y2="{surf_svg_y:.2f}" '
                         f'stroke-dasharray="3,2"/>\n')

            # Horizontal dimension line with arrowheads
            output.write(f'      <line x1="{x1:.2f}" y1="{tier_svg_y:.2f}" '
                         f'x2="{x2:.2f}" y2="{tier_svg_y:.2f}"/>\n')
            # Left arrowhead (pointing right, i.e. →)
            self._write_arrowhead(output, x1, tier_svg_y, arrow_px, direction="right")
            # Right arrowhead (pointing left, i.e. ←)
            self._write_arrowhead(output, x2, tier_svg_y, arrow_px, direction="left")

            # Dimension text
            span_px = x2 - x1
            mid_x = (x1 + x2) / 2.0
            text = _escape(dim.text)
            if span_px >= min_inline_px:
                # Text centred on span
                output.write(f'      <text x="{mid_x:.2f}" y="{tier_svg_y - 4:.2f}" '
                              f'text-anchor="middle" dominant-baseline="auto">'
                              f'{text}</text>\n')
            else:
                # Text placed to the right of the span
                output.write(f'      <text x="{x2 + 4:.2f}" y="{tier_svg_y + text_fs * 0.35:.2f}" '
                              f'text-anchor="start">{text}</text>\n')

        output.write('    </g>\n')

    def _write_arrowhead(
        self,
        output: TextIO,
        tip_x: float,
        tip_y: float,
        arrow_px: float,
        direction: Literal["left", "right"],
    ) -> None:
        """Draw a small filled triangle arrowhead on the dimension line."""
        if direction == "right":
            # Arrow pointing right: tip at (tip_x, tip_y), tail to the right
            pts = [
                (tip_x, tip_y),
                (tip_x + arrow_px, tip_y - arrow_px * 0.35),
                (tip_x + arrow_px, tip_y + arrow_px * 0.35),
            ]
        else:
            pts = [
                (tip_x, tip_y),
                (tip_x - arrow_px, tip_y - arrow_px * 0.35),
                (tip_x - arrow_px, tip_y + arrow_px * 0.35),
            ]
        pts_str = _fmt_pts(pts)
        output.write(f'      <polygon points="{pts_str}" fill="currentColor" stroke="none"/>\n')

    # ------------------------------------------------------------------
    # Legend
    # ------------------------------------------------------------------

    def _collect_legend_items(self, geometry: SectionGeometry) -> list[tuple[str, str]]:
        """Return (label, color) pairs for each unique layer type."""
        seen: dict[str, str] = {}
        for comp in geometry.components:
            meta = comp.metadata
            comp_type = meta.get("component_type", "")
            layers = meta.get("layers", [])
            if layers:
                for i, layer_info in enumerate(layers):
                    lt = layer_info.get("type", "")
                    if lt and lt not in seen:
                        seen[lt] = _LAYER_COLORS.get(lt, _DEFAULT_COLOR)
            else:
                for key in _COMPONENT_COLORS:
                    if comp_type.startswith(key) and comp_type not in seen:
                        seen[comp_type] = _COMPONENT_COLORS[key]
                        break
        return list(seen.items())

    def _legend_width_px(self, title: str, items: list[tuple[str, str]]) -> float:
        longest = max((len(label) for label, _ in items), default=0)
        title_len = len(title)
        chars = max(longest, title_len)
        return max(120.0, chars * 7.5 + 30)

    def _render_legend(
        self,
        output: TextIO,
        geometry: SectionGeometry,
        items: list[tuple[str, str]],
        x: float,
        y: float,
    ) -> None:
        title = _escape(geometry.metadata.get("name", "Section"))
        output.write(f'  <text x="{x}" y="{y + 14}" font-family="Arial" font-size="13" '
                     f'font-weight="bold">{title}</text>\n')
        for i, (label, color) in enumerate(items):
            iy = y + 24 + i * 20
            output.write(f'  <rect x="{x}" y="{iy}" width="14" height="14" '
                         f'fill="{color}" stroke="#333" stroke-width="0.5"/>\n')
            output.write(f'  <text x="{x + 20}" y="{iy + 11}" font-family="Arial" '
                         f'font-size="11">{_escape(label)}</text>\n')

    # ------------------------------------------------------------------
    # Scale bar
    # ------------------------------------------------------------------

    def _choose_scale_bar(self, content_width_m: float) -> tuple[float, str]:
        if self.units == "imperial":
            ft = content_width_m * 3.28084
            for threshold, size_ft in [(20, 5), (50, 10), (100, 20), (float("inf"), 50)]:
                if ft < threshold:
                    return size_ft / 3.28084, f"{size_ft:.0f} ft"
        else:
            for threshold, size_m in [(5, 1), (15, 2), (30, 5), (float("inf"), 10)]:
                if content_width_m < threshold:
                    return float(size_m), f"{size_m} m"
        return 1.0, "1 m"

    def _render_scale_bar(
        self,
        output: TextIO,
        scale_len_m: float,
        label: str,
        x: float,
        y: float,
    ) -> None:
        bar_px = scale_len_m * self.scale
        tick = 5
        output.write(f'  <line x1="{x}" y1="{y}" x2="{x + bar_px:.1f}" y2="{y}" '
                     f'stroke="black" stroke-width="2"/>\n')
        for tx in (x, x + bar_px):
            output.write(f'  <line x1="{tx:.1f}" y1="{y - tick}" x2="{tx:.1f}" y2="{y + tick}" '
                         f'stroke="black" stroke-width="2"/>\n')
        mid = x + bar_px / 2
        output.write(f'  <text x="{mid:.1f}" y="{y + 18}" font-family="Arial" '
                     f'font-size="11" text-anchor="middle">{_escape(label)}</text>\n')


# ---------------------------------------------------------------------------
# Backwards-compatible alias used by older code / tests
# ---------------------------------------------------------------------------

class SimpleSVGExporter(SVGExporter):
    """Alias for SVGExporter (backwards compatibility)."""

    def __init__(
        self,
        scale: float = 100.0,
        vertical_exaggeration: float = 1.0,
        units: Literal["imperial", "metric"] = "imperial",
        content_margin_m: float = 0.5,
        ui_padding_px: float = 10.0,  # kept for API compat, ignored
    ) -> None:
        super().__init__(
            scale=scale,
            vertical_exaggeration=vertical_exaggeration,
            units=units,
            content_margin_m=content_margin_m,
        )
