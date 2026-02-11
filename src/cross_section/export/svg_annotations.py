"""SVG exporter with annotation support."""

import colorsys
import re
from typing import Callable, TextIO

from ..core.domain.annotations import (
    AnnotationCollection,
    DimensionAnnotation,
    LeaderAnnotation,
    SymbolAnnotation,
    TextAnnotation,
)
from ..core.domain.annotations.symbols.library import SymbolLibrary
from ..core.domain.section import SectionGeometry
from ..core.geometry.primitives import Point2D
from .svg import SimpleSVGExporter


class AnnotatedSVGExporter(SimpleSVGExporter):
    """SVG exporter with support for annotations.

    Extends SimpleSVGExporter to add text labels, dimensions, leaders,
    and symbols with automatic collision resolution.
    """

    KEYED_NOTES_WIDTH_PX = 250
    KEYED_NOTES_ROW_HEIGHT_PX = 20
    KEYED_NOTES_PADDING_PX = 10

    def export_with_annotations(
        self,
        geometry: SectionGeometry,
        annotations: AnnotationCollection,
        output: TextIO,
        include_keyed_notes_table: bool = True
    ) -> None:
        """Export section geometry with annotations to SVG.

        Args:
            geometry: The section geometry to export
            annotations: Collection of annotations to render
            output: File object to write SVG to
            include_keyed_notes_table: Whether to include keyed notes table
        """
        if not geometry.components:
            output.write('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">')
            output.write('<text x="10" y="50">Empty section</text>')
            output.write("</svg>")
            return

        # Calculate bounds including annotations
        geom_bounds = geometry.bounds()
        min_x, min_y, max_x, max_y = geom_bounds

        # Expand bounds to include annotations
        if annotations.count() > 0:
            ann_bounds = annotations.bounds()
            if ann_bounds:
                min_x = min(min_x, ann_bounds.min_x)
                min_y = min(min_y, ann_bounds.min_y)
                max_x = max(max_x, ann_bounds.max_x)
                max_y = max(max_y, ann_bounds.max_y)

        keyed_notes_count = len(annotations.keyed_notes) if include_keyed_notes_table else 0
        (
            view_min_x,
            view_min_y,
            view_max_x,
            view_max_y,
            scale_length_m,
            scale_label,
        ) = self._compute_view_bounds(
            min_x,
            min_y,
            max_x,
            max_y,
            geometry,
            keyed_notes_count=keyed_notes_count,
        )

        # Calculate viewport dimensions
        view_width = view_max_x - view_min_x
        view_height = (view_max_y - view_min_y) * self.vertical_exaggeration

        # SVG dimensions in pixels
        svg_width = view_width * self.scale
        svg_height = view_height * self.scale

        # Write SVG header
        output.write('<svg xmlns="http://www.w3.org/2000/svg" ')
        output.write(f'width="{svg_width:.1f}" height="{svg_height:.1f}" ')
        output.write(f'viewBox="0 0 {svg_width:.1f} {svg_height:.1f}">\n')

        # Add title
        output.write(f"  <title>{geometry.metadata.get('name', 'Road Section')}</title>\n")

        # Add white background
        output.write(f'  <rect width="{svg_width:.1f}" height="{svg_height:.1f}" fill="white"/>\n')

        # Create transformation group (flip Y axis)
        output.write('  <g transform="scale(1,-1)">\n')
        output.write(f'    <g transform="translate(0,-{svg_height:.1f})">\n')

        # Draw geometry (same as parent class)
        self._draw_geometry(output, geometry, view_min_x, view_min_y, svg_width, svg_height)

        # Create transform function for annotations
        def transform_point(point: Point2D) -> Point2D:
            """Transform real-world coordinates to SVG coordinates."""
            x = (point.x - view_min_x) * self.scale
            y = (point.y - view_min_y) * self.scale * self.vertical_exaggeration
            return Point2D(x, y)

        # Draw annotations in layers
        self._render_annotations(output, annotations, transform_point)

        output.write("    </g>\n")
        output.write("  </g>\n")

        # Add legend (not transformed)
        self._add_legend(output, geometry, svg_width, svg_height)

        # Add scale indicator
        self._add_scale(output, svg_height, scale_length_m, scale_label)

        # Add keyed notes table if requested
        if include_keyed_notes_table and annotations.keyed_notes:
            self._render_keyed_notes_table(output, annotations.keyed_notes, svg_width, svg_height)

        output.write("</svg>\n")

    def _draw_geometry(
        self,
        output: TextIO,
        geometry: SectionGeometry,
        view_min_x: float,
        view_min_y: float,
        svg_width: float,
        svg_height: float
    ) -> None:
        """Draw section geometry (same logic as SimpleSVGExporter)."""
        for comp_idx, component in enumerate(geometry.components):
            for poly_idx, polygon in enumerate(component.polygons):
                # Get layer info from metadata if available
                layer_info = None
                if "layers" in component.metadata:
                    layers = component.metadata["layers"]
                    if poly_idx < len(layers):
                        layer_info = layers[poly_idx]

                # Determine color based on layer type
                if layer_info and "type" in layer_info:
                    color = self.COLORS.get(layer_info["type"], self.COLORS["default"])
                else:
                    color = self.COLORS["default"]

                # Convert polygon vertices to SVG path
                points = []
                for point in polygon.exterior:
                    # Transform coordinates
                    x = (point.x - view_min_x) * self.scale
                    y = (point.y - view_min_y) * self.scale * self.vertical_exaggeration
                    points.append(f"{x:.2f},{y:.2f}")

                # Draw polygon
                points_str = " ".join(points)
                output.write(f'      <polygon points="{points_str}" ')
                output.write(f'fill="{color}" stroke="black" stroke-width="1"/>\n')

            # Draw component's polylines
            polyline_styles = component.metadata.get("polyline_styles", [])
            for poly_idx, polyline in enumerate(component.polylines):
                points = []
                for point in polyline:
                    x = (point.x - view_min_x) * self.scale
                    y = (point.y - view_min_y) * self.scale * self.vertical_exaggeration
                    points.append(f"{x:.2f},{y:.2f}")

                points_str = " ".join(points)
                output.write(f'      <polyline points="{points_str}" ')
                style = polyline_styles[poly_idx] if poly_idx < len(polyline_styles) else {}
                dasharray = style.get("stroke_dasharray")
                stroke_width = style.get("stroke_width", "1.5")
                if dasharray:
                    output.write(
                        f'fill="none" stroke="black" stroke-width="{stroke_width}" '
                        f'stroke-dasharray="{dasharray}"/>\n'
                    )
                else:
                    output.write(f'fill="none" stroke="black" stroke-width="{stroke_width}"/>\n')

    def _render_annotations(
        self,
        output: TextIO,
        annotations: AnnotationCollection,
        transform: Callable[[Point2D], Point2D]
    ) -> None:
        """Render all annotations in appropriate order."""
        output.write("      <!-- Annotations -->\n")

        # Render in order: dimensions, leaders, symbols, text
        # This ensures text appears on top

        for annotation in annotations.annotations:
            if isinstance(annotation, DimensionAnnotation):
                self._render_dimension(output, annotation, transform)
            elif isinstance(annotation, LeaderAnnotation):
                self._render_leader(output, annotation, transform)
            elif isinstance(annotation, SymbolAnnotation):
                self._render_symbol(output, annotation, transform)
            elif isinstance(annotation, TextAnnotation):
                self._render_text(output, annotation, transform)

    def _keyed_notes_box_px(self, keyed_notes_count: int) -> tuple[float, float]:
        if keyed_notes_count <= 0:
            return (0.0, 0.0)
        table_height = (
            (keyed_notes_count + 1) * self.KEYED_NOTES_ROW_HEIGHT_PX
            + self.KEYED_NOTES_PADDING_PX
        )
        return (self.KEYED_NOTES_WIDTH_PX, table_height + 20)

    def _render_text(
        self,
        output: TextIO,
        annotation: TextAnnotation,
        transform: Callable[[Point2D], Point2D]
    ) -> None:
        """Render text annotation to SVG."""
        pos = transform(annotation.position)

        # Convert font size from meters to pixels
        font_size_px = annotation.font_size * self.scale

        # Build text element
        # Note: Text needs to be flipped vertically because it's inside the Y-flipped coordinate system
        # We flip around the text's own position so it stays in place
        output.write(f'      <text x="{pos.x:.2f}" y="{pos.y:.2f}" ')
        output.write(f'font-family="Arial" font-size="{font_size_px:.1f}" ')
        output.write(f'text-anchor="{annotation.anchor}" ')

        # Apply transforms: flip Y around text position, then rotate if needed
        if annotation.angle != 0:
            # Flip Y around text position and rotate
            output.write(f'transform="translate(0,{2*pos.y:.2f}) scale(1,-1) rotate({annotation.angle},{pos.x:.2f},{pos.y:.2f})" ')
        else:
            # Just flip Y around text position
            output.write(f'transform="translate(0,{2*pos.y:.2f}) scale(1,-1)" ')

        output.write('fill="black">')
        output.write(annotation.text)
        output.write('</text>\n')

    def _render_dimension(
        self,
        output: TextIO,
        annotation: DimensionAnnotation,
        transform: Callable[[Point2D], Point2D]
    ) -> None:
        """Render dimension annotation to SVG."""
        start = transform(annotation.start)
        end = transform(annotation.end)

        # Calculate perpendicular offset direction
        dx = end.x - start.x
        dy = end.y - start.y
        length = (dx * dx + dy * dy) ** 0.5

        if length < 0.01:  # Avoid division by zero
            return

        # Perpendicular unit vector
        perp_x = -dy / length
        perp_y = dx / length

        # Offset in pixels
        offset_px = annotation.offset * self.scale * self.vertical_exaggeration

        # Dimension line endpoints
        dim_start_x = start.x + perp_x * offset_px
        dim_start_y = start.y + perp_y * offset_px
        dim_end_x = end.x + perp_x * offset_px
        dim_end_y = end.y + perp_y * offset_px

        output.write(f'      <g id="dimension-{annotation.id}">\n')

        # Extension lines
        output.write(f'        <line x1="{start.x:.2f}" y1="{start.y:.2f}" ')
        output.write(f'x2="{dim_start_x:.2f}" y2="{dim_start_y:.2f}" ')
        output.write('stroke="black" stroke-width="0.5"/>\n')

        output.write(f'        <line x1="{end.x:.2f}" y1="{end.y:.2f}" ')
        output.write(f'x2="{dim_end_x:.2f}" y2="{dim_end_y:.2f}" ')
        output.write('stroke="black" stroke-width="0.5"/>\n')

        # Dimension line
        output.write(f'        <line x1="{dim_start_x:.2f}" y1="{dim_start_y:.2f}" ')
        output.write(f'x2="{dim_end_x:.2f}" y2="{dim_end_y:.2f}" ')
        output.write('stroke="black" stroke-width="1"/>\n')

        # Arrow heads at dimension endpoints - always pointing outward
        if annotation.show_arrows:
            import math
            arrow_size = 5  # Pixel size of arrow head

            # Calculate angle of dimension line
            angle_rad = math.atan2(dy, dx)
            angle_deg = math.degrees(angle_rad)

            # Arrows point outward from the dimension line (away from center)
            # Start arrow points away from end (angle + 180)
            # End arrow points away from start (angle)
            start_arrow_angle = angle_deg + 180
            end_arrow_angle = angle_deg

            # Start arrow
            output.write(f'        <polygon points="{dim_start_x:.2f},{dim_start_y:.2f} ')
            output.write(f'{dim_start_x - arrow_size:.2f},{dim_start_y - arrow_size/2:.2f} ')
            output.write(f'{dim_start_x - arrow_size:.2f},{dim_start_y + arrow_size/2:.2f}" ')
            output.write(f'fill="black" transform="rotate({start_arrow_angle:.1f},{dim_start_x:.2f},{dim_start_y:.2f})"/>\n')

            # End arrow
            output.write(f'        <polygon points="{dim_end_x:.2f},{dim_end_y:.2f} ')
            output.write(f'{dim_end_x - arrow_size:.2f},{dim_end_y - arrow_size/2:.2f} ')
            output.write(f'{dim_end_x - arrow_size:.2f},{dim_end_y + arrow_size/2:.2f}" ')
            output.write(f'fill="black" transform="rotate({end_arrow_angle:.1f},{dim_end_x:.2f},{dim_end_y:.2f})"/>\n')

        # Dimension text - positioned above dimension line with small offset
        if annotation.dimension_text and annotation.text_position:
            text_pos = transform(annotation.text_position)
            font_size_px = 0.12 * self.scale  # Slightly smaller than default

            # Add small offset above dimension line (half text height in perpendicular direction)
            text_offset = font_size_px / 2
            text_x = text_pos.x + perp_x * text_offset
            text_y = text_pos.y + perp_y * text_offset

            output.write(f'        <text x="{text_x:.2f}" y="{text_y:.2f}" ')
            output.write(f'font-family="Arial" font-size="{font_size_px:.1f}" ')
            output.write(f'text-anchor="middle" transform="translate(0,{2*text_y:.2f}) scale(1,-1)" fill="black">')
            output.write(annotation.dimension_text)
            output.write('</text>\n')

        output.write('      </g>\n')

    def _render_leader(
        self,
        output: TextIO,
        annotation: LeaderAnnotation,
        transform: Callable[[Point2D], Point2D]
    ) -> None:
        """Render leader annotation to SVG."""
        output.write(f'      <g id="leader-{annotation.id}">\n')

        # Convert points to SVG coordinates
        svg_points = [transform(p) for p in annotation.points]
        points_str = " ".join(f"{p.x:.2f},{p.y:.2f}" for p in svg_points)

        # Draw polyline
        output.write(f'        <polyline points="{points_str}" ')
        output.write('fill="none" stroke="black" stroke-width="1"/>\n')

        # Arrow at start if requested
        if annotation.arrow_at_start and len(svg_points) >= 2:
            p1 = svg_points[0]  # Point at object
            p2 = svg_points[1]  # Next point away from object
            # Arrow should point FROM p2 TOWARD p1 (toward the object)
            dx = p1.x - p2.x
            dy = p1.y - p2.y
            import math
            angle_deg = math.degrees(math.atan2(dy, dx))

            arrow_size = 5
            output.write(f'        <polygon points="{p1.x:.2f},{p1.y:.2f} ')
            output.write(f'{p1.x - arrow_size:.2f},{p1.y - arrow_size/2:.2f} ')
            output.write(f'{p1.x - arrow_size:.2f},{p1.y + arrow_size/2:.2f}" ')
            output.write(f'fill="black" transform="rotate({angle_deg},{p1.x:.2f},{p1.y:.2f})"/>\n')

        # Text at end
        last_point = svg_points[-1]
        font_size_px = 0.15 * self.scale
        text_y = last_point.y

        output.write(f'        <text x="{last_point.x + 5:.2f}" y="{text_y:.2f}" ')
        output.write(f'font-family="Arial" font-size="{font_size_px:.1f}" ')
        output.write(f'text-anchor="start" transform="translate(0,{2*text_y:.2f}) scale(1,-1)" fill="black">')
        output.write(annotation.text)
        output.write('</text>\n')

        output.write('      </g>\n')

    def _render_symbol(
        self,
        output: TextIO,
        annotation: SymbolAnnotation,
        transform: Callable[[Point2D], Point2D]
    ) -> None:
        """Render symbol annotation to SVG."""
        pos = transform(annotation.position)

        # Get symbol from library
        try:
            symbol_def = SymbolLibrary.get(annotation.symbol_type)
        except KeyError:
            # Symbol not found, render placeholder
            output.write(f'      <circle cx="{pos.x:.2f}" cy="{pos.y:.2f}" r="5" ')
            output.write('fill="red" stroke="black" stroke-width="1"/>\n')
            return

        svg_path = symbol_def.get("svg_path", "")
        width = symbol_def.get("width", 0.5) * self.scale * annotation.scale
        height = symbol_def.get("height", 0.5) * self.scale * annotation.scale

        # Create group with transform
        output.write(f'      <g id="symbol-{annotation.id}" ')
        output.write(f'transform="translate({pos.x:.2f},{pos.y:.2f}) ')
        output.write(f'scale({annotation.scale}) ')
        output.write(f'rotate({-annotation.angle})">\n')

        # Render SVG markup directly (not as path data)
        output.write(f'{svg_path}\n')

        output.write('      </g>\n')

    def _render_keyed_notes_table(
        self,
        output: TextIO,
        keyed_notes: dict[str, str],
        svg_width: float,
        svg_height: float
    ) -> None:
        """Render keyed notes table in bottom-right corner."""
        output.write("  <!-- Keyed Notes Table -->\n")

        # Table parameters
        table_x = svg_width - self.KEYED_NOTES_WIDTH_PX
        table_y = (
            svg_height
            - 20
            - (len(keyed_notes) * self.KEYED_NOTES_ROW_HEIGHT_PX)
            - 30
        )
        row_height = self.KEYED_NOTES_ROW_HEIGHT_PX
        col1_width = 40
        col2_width = 200

        # Table background
        table_height = (len(keyed_notes) + 1) * row_height + self.KEYED_NOTES_PADDING_PX
        output.write(f'  <rect x="{table_x}" y="{table_y}" ')
        output.write(f'width="{self.KEYED_NOTES_WIDTH_PX}" height="{table_height}" ')
        output.write('fill="white" stroke="black" stroke-width="1"/>\n')

        # Header
        output.write(f'  <text x="{table_x + 5}" y="{table_y + 15}" ')
        output.write('font-family="Arial" font-size="12" font-weight="bold">Key</text>\n')
        output.write(f'  <text x="{table_x + col1_width + 5}" y="{table_y + 15}" ')
        output.write('font-family="Arial" font-size="12" font-weight="bold">Description</text>\n')

        # Header line
        output.write(f'  <line x1="{table_x}" y1="{table_y + row_height}" ')
        output.write(f'x2="{table_x + col1_width + col2_width}" y2="{table_y + row_height}" ')
        output.write('stroke="black" stroke-width="1"/>\n')

        # Rows
        y = table_y + row_height
        sorted_keys = sorted(keyed_notes.keys(), key=lambda k: (k.isdigit(), int(k) if k.isdigit() else 0, k))

        for key in sorted_keys:
            description = keyed_notes[key]
            y += row_height

            # Key column
            output.write(f'  <text x="{table_x + 5}" y="{y + 12}" ')
            output.write('font-family="Arial" font-size="11">')
            output.write(key)
            output.write('</text>\n')

            # Description column (truncate if too long)
            max_chars = 25
            display_text = description if len(description) <= max_chars else description[:max_chars-3] + "..."
            output.write(f'  <text x="{table_x + col1_width + 5}" y="{y + 12}" ')
            output.write('font-family="Arial" font-size="11">')
            output.write(display_text)
            output.write('</text>\n')

            # Row line
            output.write(f'  <line x1="{table_x}" y1="{y + row_height - 8}" ')
            output.write(f'x2="{table_x + col1_width + col2_width}" y2="{y + row_height - 8}" ')
            output.write('stroke="black" stroke-width="0.5"/>\n')

        # Column divider
        output.write(f'  <line x1="{table_x + col1_width}" y1="{table_y}" ')
        output.write(f'x2="{table_x + col1_width}" y2="{table_y + table_height}" ')
        output.write('stroke="black" stroke-width="1"/>\n')

    # ------------------------------------------------------------------
    # Debug annotation-only renderer
    # ------------------------------------------------------------------

    @staticmethod
    def _debug_color(index: int, total: int) -> str:
        """Generate a deterministic unique color for annotation *index*.

        Uses evenly-spaced hues on the HSV wheel with full saturation and
        full value.  Colors are quantized to 32-level steps per channel so
        that anti-aliased edge pixels (which blend toward white) remain
        distinguishable from neighbouring annotation colors after
        quantization in the pixel overlap test.
        """
        if total <= 0:
            total = 1
        hue = (index / total) % 1.0
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 0.70)
        # Quantize to 8 levels per channel (multiples of 32) so anti-aliased
        # variants of the same colour stay in the same bin.
        ri = (int(r * 255) // 32) * 32
        gi = (int(g * 255) // 32) * 32
        bi = (int(b * 255) // 32) * 32
        return f"#{ri:02x}{gi:02x}{bi:02x}"

    def export_annotations_debug(
        self,
        geometry: SectionGeometry,
        annotations: AnnotationCollection,
        output: TextIO,
    ) -> None:
        """Export annotations-only SVG with unique color per annotation.

        Same viewBox / scale / transforms as ``export_with_annotations``
        but **no geometry, legend, scale bar, or keyed-notes table**.
        Each annotation is rendered in a deterministic unique color so
        pixel overlap between different annotations can be detected.
        """
        if not geometry.components:
            output.write('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">')
            output.write('<text x="10" y="50">Empty section</text>')
            output.write("</svg>")
            return

        # Calculate bounds (same logic as export_with_annotations)
        geom_bounds = geometry.bounds()
        min_x, min_y, max_x, max_y = geom_bounds

        if annotations.count() > 0:
            ann_bounds = annotations.bounds()
            if ann_bounds:
                min_x = min(min_x, ann_bounds.min_x)
                min_y = min(min_y, ann_bounds.min_y)
                max_x = max(max_x, ann_bounds.max_x)
                max_y = max(max_y, ann_bounds.max_y)

        (
            view_min_x, view_min_y, view_max_x, view_max_y,
            _scale_length_m, _scale_label,
        ) = self._compute_view_bounds(min_x, min_y, max_x, max_y, geometry,
                                      keyed_notes_count=0)

        view_width = view_max_x - view_min_x
        view_height = (view_max_y - view_min_y) * self.vertical_exaggeration
        svg_width = view_width * self.scale
        svg_height = view_height * self.scale

        # SVG header — disable anti-aliasing for crisp pixel boundaries
        output.write('<svg xmlns="http://www.w3.org/2000/svg" ')
        output.write(f'width="{svg_width:.1f}" height="{svg_height:.1f}" ')
        output.write(f'viewBox="0 0 {svg_width:.1f} {svg_height:.1f}" ')
        output.write('shape-rendering="crispEdges" text-rendering="geometricPrecision">\n')
        output.write(f"  <title>Annotation Debug</title>\n")
        output.write(f'  <rect width="{svg_width:.1f}" height="{svg_height:.1f}" fill="white"/>\n')

        # Y-flip group (same as normal export)
        output.write('  <g transform="scale(1,-1)">\n')
        output.write(f'    <g transform="translate(0,-{svg_height:.1f})">\n')

        def transform_point(point: Point2D) -> Point2D:
            x = (point.x - view_min_x) * self.scale
            y = (point.y - view_min_y) * self.scale * self.vertical_exaggeration
            return Point2D(x, y)

        total = annotations.count()
        for ann_idx, annotation in enumerate(annotations.annotations):
            color = self._debug_color(ann_idx, total)
            if isinstance(annotation, DimensionAnnotation):
                self._render_dimension_debug(output, annotation, transform_point, color)
            elif isinstance(annotation, LeaderAnnotation):
                self._render_leader_debug(output, annotation, transform_point, color)
            elif isinstance(annotation, SymbolAnnotation):
                self._render_symbol_debug(output, annotation, transform_point, color)
            elif isinstance(annotation, TextAnnotation):
                self._render_text_debug(output, annotation, transform_point, color)

        output.write("    </g>\n")
        output.write("  </g>\n")
        output.write("</svg>\n")

    # --- Debug colour variants of each renderer ---

    def _render_text_debug(
        self, output: TextIO, annotation: TextAnnotation,
        transform: Callable[[Point2D], Point2D], color: str,
    ) -> None:
        pos = transform(annotation.position)
        font_size_px = annotation.font_size * self.scale

        output.write(f'      <text x="{pos.x:.2f}" y="{pos.y:.2f}" ')
        output.write(f'font-family="Arial" font-size="{font_size_px:.1f}" ')
        output.write(f'text-anchor="{annotation.anchor}" ')

        if annotation.angle != 0:
            output.write(f'transform="translate(0,{2*pos.y:.2f}) scale(1,-1) '
                         f'rotate({annotation.angle},{pos.x:.2f},{pos.y:.2f})" ')
        else:
            output.write(f'transform="translate(0,{2*pos.y:.2f}) scale(1,-1)" ')

        output.write(f'fill="{color}">')
        output.write(annotation.text)
        output.write('</text>\n')

    def _render_dimension_debug(
        self, output: TextIO, annotation: DimensionAnnotation,
        transform: Callable[[Point2D], Point2D], color: str,
    ) -> None:
        start = transform(annotation.start)
        end = transform(annotation.end)
        dx = end.x - start.x
        dy = end.y - start.y
        length = (dx * dx + dy * dy) ** 0.5
        if length < 0.01:
            return

        perp_x = -dy / length
        perp_y = dx / length
        offset_px = annotation.offset * self.scale * self.vertical_exaggeration

        dim_start_x = start.x + perp_x * offset_px
        dim_start_y = start.y + perp_y * offset_px
        dim_end_x = end.x + perp_x * offset_px
        dim_end_y = end.y + perp_y * offset_px

        output.write(f'      <g>\n')
        # Skip extension lines in debug mode — the collision detector exempts
        # items inside the dimension span from extension-line checks, so
        # rendering them would cause false overlap positives in pixel tests.
        # Dimension line
        output.write(f'        <line x1="{dim_start_x:.2f}" y1="{dim_start_y:.2f}" '
                     f'x2="{dim_end_x:.2f}" y2="{dim_end_y:.2f}" '
                     f'stroke="{color}" stroke-width="1"/>\n')

        # Arrows
        if annotation.show_arrows:
            import math
            arrow_size = 5
            angle_rad = math.atan2(dy, dx)
            angle_deg = math.degrees(angle_rad)

            for px, py, arrow_angle in [
                (dim_start_x, dim_start_y, angle_deg + 180),
                (dim_end_x, dim_end_y, angle_deg),
            ]:
                output.write(f'        <polygon points="{px:.2f},{py:.2f} '
                             f'{px - arrow_size:.2f},{py - arrow_size/2:.2f} '
                             f'{px - arrow_size:.2f},{py + arrow_size/2:.2f}" '
                             f'fill="{color}" transform="rotate({arrow_angle:.1f},{px:.2f},{py:.2f})"/>\n')

        # Text
        if annotation.dimension_text and annotation.text_position:
            text_pos = transform(annotation.text_position)
            font_size_px = 0.12 * self.scale
            text_offset = font_size_px / 2
            text_x = text_pos.x + perp_x * text_offset
            text_y = text_pos.y + perp_y * text_offset

            output.write(f'        <text x="{text_x:.2f}" y="{text_y:.2f}" '
                         f'font-family="Arial" font-size="{font_size_px:.1f}" '
                         f'text-anchor="middle" '
                         f'transform="translate(0,{2*text_y:.2f}) scale(1,-1)" '
                         f'fill="{color}">')
            output.write(annotation.dimension_text)
            output.write('</text>\n')

        output.write('      </g>\n')

    def _render_leader_debug(
        self, output: TextIO, annotation: LeaderAnnotation,
        transform: Callable[[Point2D], Point2D], color: str,
    ) -> None:
        svg_points = [transform(p) for p in annotation.points]
        points_str = " ".join(f"{p.x:.2f},{p.y:.2f}" for p in svg_points)

        output.write(f'      <g>\n')
        output.write(f'        <polyline points="{points_str}" '
                     f'fill="none" stroke="{color}" stroke-width="1"/>\n')

        if annotation.arrow_at_start and len(svg_points) >= 2:
            import math
            p1, p2 = svg_points[0], svg_points[1]
            angle_deg = math.degrees(math.atan2(p1.y - p2.y, p1.x - p2.x))
            arrow_size = 5
            output.write(f'        <polygon points="{p1.x:.2f},{p1.y:.2f} '
                         f'{p1.x - arrow_size:.2f},{p1.y - arrow_size/2:.2f} '
                         f'{p1.x - arrow_size:.2f},{p1.y + arrow_size/2:.2f}" '
                         f'fill="{color}" transform="rotate({angle_deg},{p1.x:.2f},{p1.y:.2f})"/>\n')

        last = svg_points[-1]
        font_size_px = 0.15 * self.scale
        output.write(f'        <text x="{last.x + 5:.2f}" y="{last.y:.2f}" '
                     f'font-family="Arial" font-size="{font_size_px:.1f}" '
                     f'text-anchor="start" '
                     f'transform="translate(0,{2*last.y:.2f}) scale(1,-1)" '
                     f'fill="{color}">')
        output.write(annotation.text)
        output.write('</text>\n')
        output.write('      </g>\n')

    def _render_symbol_debug(
        self, output: TextIO, annotation: SymbolAnnotation,
        transform: Callable[[Point2D], Point2D], color: str,
    ) -> None:
        pos = transform(annotation.position)

        try:
            symbol_def = SymbolLibrary.get(annotation.symbol_type)
        except KeyError:
            output.write(f'      <circle cx="{pos.x:.2f}" cy="{pos.y:.2f}" r="5" '
                         f'fill="{color}" stroke="{color}" stroke-width="1"/>\n')
            return

        svg_path = symbol_def.get("svg_path", "")
        # Recolour all fill/stroke attributes in the SVG markup
        recolored = re.sub(r'fill="[^"]*"', f'fill="{color}"', svg_path)
        recolored = re.sub(r'stroke="[^"]*"', f'stroke="{color}"', recolored)

        output.write(f'      <g transform="translate({pos.x:.2f},{pos.y:.2f}) ')
        output.write(f'scale({annotation.scale}) ')
        output.write(f'rotate({-annotation.angle})">\n')
        output.write(f'{recolored}\n')
        output.write('      </g>\n')
