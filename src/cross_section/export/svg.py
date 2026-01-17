"""Simple SVG exporter - Pure Python, no dependencies."""

from typing import Literal, TextIO

from ..core.domain.section import SectionGeometry


class SimpleSVGExporter:
    """Export road section geometry to SVG format.

    This is a minimal pure-Python SVG exporter for visualization and testing.
    Colors are assigned to layers based on their type.
    """

    LEGEND_X = 10
    LEGEND_Y = 20
    LEGEND_LINE_HEIGHT = 20
    LEGEND_TITLE_FONT_PX = 14
    LEGEND_ITEM_FONT_PX = 12
    SCALE_X_START = 10
    SCALE_Y_OFFSET = 30
    SCALE_TICK_HALF = 5
    SCALE_LABEL_OFFSET = 20

    # Color palette for different layer types
    COLORS = {
        "AsphaltLayer": "#2C3E50",  # Dark gray-blue
        "ConcreteLayer": "#95A5A6",  # Light gray
        "CrushedRockLayer": "#7F8C8D",  # Medium gray
        "default": "#BDC3C7",  # Very light gray
    }

    def __init__(
        self,
        scale: float = 100.0,
        vertical_exaggeration: float = 1.0,
        units: Literal["imperial", "metric"] = "imperial",
        content_margin_m: float = 0.5,
        ui_padding_px: float = 10.0,
    ):
        """Initialize SVG exporter.

        Args:
            scale: Pixels per meter (default 100 = 1m = 100px)
            vertical_exaggeration: Factor to exaggerate vertical dimensions for visibility
            units: Unit system for scale labeling ('imperial' or 'metric')
            content_margin_m: Base margin around geometry in meters
            ui_padding_px: Extra padding around UI elements in pixels
        """
        self.scale = scale
        self.vertical_exaggeration = vertical_exaggeration
        self.units = units
        self.content_margin_m = content_margin_m
        self.ui_padding_px = ui_padding_px

    def export(self, geometry: SectionGeometry, output: TextIO) -> None:
        """Export section geometry to SVG.

        Args:
            geometry: The section geometry to export
            output: File object to write SVG to
        """
        if not geometry.components:
            output.write('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">')
            output.write('<text x="10" y="50">Empty section</text>')
            output.write("</svg>")
            return

        # Calculate bounds
        bounds = geometry.bounds()
        min_x, min_y, max_x, max_y = bounds

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
            keyed_notes_count=0,
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

        # Create transformation group (flip Y axis since SVG Y increases downward)
        output.write('  <g transform="scale(1,-1)">\n')
        output.write(f'    <g transform="translate(0,-{svg_height:.1f})">\n')

        # Draw each component's polygons
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

            # Draw component's polylines (e.g., ditch void boundaries)
            polyline_styles = component.metadata.get("polyline_styles", [])
            for poly_idx, polyline in enumerate(component.polylines):
                # Convert polyline vertices to SVG path
                points = []
                for point in polyline:
                    # Transform coordinates
                    x = (point.x - view_min_x) * self.scale
                    y = (point.y - view_min_y) * self.scale * self.vertical_exaggeration
                    points.append(f"{x:.2f},{y:.2f}")

                # Draw polyline (no fill, just stroke)
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
                    output.write(
                        f'fill="none" stroke="black" stroke-width="{stroke_width}"/>\n'
                    )

        output.write("    </g>\n")
        output.write("  </g>\n")

        # Add legend (not transformed)
        self._add_legend(output, geometry, svg_width, svg_height)

        # Add scale indicator
        self._add_scale(output, svg_height, scale_length_m, scale_label)

        output.write("</svg>\n")

    def _compute_view_bounds(
        self,
        min_x: float,
        min_y: float,
        max_x: float,
        max_y: float,
        geometry: SectionGeometry,
        keyed_notes_count: int,
    ) -> tuple[float, float, float, float, float, str]:
        content_width = max(max_x - min_x, 1e-6)
        scale_length_m, scale_label = self._select_scale_bar(content_width)

        left_px, right_px, top_px, bottom_px = self._ui_margins_px(
            geometry,
            scale_length_m,
            keyed_notes_count,
        )

        y_scale = self.scale * self.vertical_exaggeration
        left_m = left_px / self.scale
        right_m = right_px / self.scale
        top_m = top_px / y_scale
        bottom_m = bottom_px / y_scale

        view_min_x = min_x - self.content_margin_m - left_m
        view_max_x = max_x + self.content_margin_m + right_m
        view_min_y = min_y - self.content_margin_m - bottom_m
        view_max_y = max_y + self.content_margin_m + top_m

        return view_min_x, view_min_y, view_max_x, view_max_y, scale_length_m, scale_label

    def _ui_margins_px(
        self,
        geometry: SectionGeometry,
        scale_length_m: float,
        keyed_notes_count: int,
    ) -> tuple[float, float, float, float]:
        legend_width, legend_height = self._legend_box_px(geometry)
        scale_width, scale_height = self._scale_box_px(scale_length_m)
        notes_width, notes_height = self._keyed_notes_box_px(keyed_notes_count)

        left_px = max(legend_width, scale_width) + self.ui_padding_px
        top_px = legend_height + self.ui_padding_px
        bottom_px = max(scale_height, notes_height) + self.ui_padding_px
        right_px = (notes_width + self.ui_padding_px) if notes_width > 0 else self.ui_padding_px

        return left_px, right_px, top_px, bottom_px

    def _legend_box_px(self, geometry: SectionGeometry) -> tuple[float, float]:
        title_text = geometry.metadata.get("name", "Section")
        title_width = self._estimate_text_width(title_text, self.LEGEND_TITLE_FONT_PX)

        layer_types = self._collect_layer_types(geometry)
        item_width = 0.0
        if layer_types:
            item_width = max(
                self._estimate_text_width(layer_type, self.LEGEND_ITEM_FONT_PX)
                for layer_type in layer_types
            )

        width = max(
            self.LEGEND_X + title_width,
            self.LEGEND_X + 20 + item_width,
        )
        item_count = max(1, len(layer_types) + 1)
        height = self.LEGEND_Y + self.LEGEND_LINE_HEIGHT * item_count
        return width + self.ui_padding_px, height + self.ui_padding_px

    def _scale_box_px(self, scale_length_m: float) -> tuple[float, float]:
        scale_px = scale_length_m * self.scale
        width = self.SCALE_X_START + scale_px
        height = self.SCALE_Y_OFFSET + self.SCALE_LABEL_OFFSET
        return width + self.ui_padding_px, height + self.ui_padding_px

    def _keyed_notes_box_px(self, keyed_notes_count: int) -> tuple[float, float]:
        return (0.0, 0.0)

    def _estimate_text_width(self, text: str, font_size_px: float) -> float:
        return len(text) * font_size_px * 0.6

    def _collect_layer_types(self, geometry: SectionGeometry) -> list[str]:
        layer_types = set()
        for component in geometry.components:
            if "layers" in component.metadata:
                for layer in component.metadata["layers"]:
                    if "type" in layer:
                        layer_types.add(layer["type"])
        return sorted(layer_types)

    def _select_scale_bar(self, content_width: float) -> tuple[float, str]:
        if self.units == "imperial":
            feet_per_meter = 3.28084
            view_width_ft = content_width * feet_per_meter
            if view_width_ft < 20:
                scale_length_ft = 5.0
            elif view_width_ft < 50:
                scale_length_ft = 10.0
            elif view_width_ft < 100:
                scale_length_ft = 20.0
            else:
                scale_length_ft = 50.0
            scale_length = scale_length_ft / feet_per_meter
            scale_label = f"{scale_length_ft:.0f}ft"
        else:
            if content_width < 5:
                scale_length = 1.0
            elif content_width < 15:
                scale_length = 2.0
            elif content_width < 30:
                scale_length = 5.0
            else:
                scale_length = 10.0
            scale_label = f"{scale_length:.0f}m"

        return scale_length, scale_label

    def _add_legend(
        self, output: TextIO, geometry: SectionGeometry, svg_width: float, svg_height: float
    ) -> None:
        """Add legend showing layer types."""
        legend_x = self.LEGEND_X
        legend_y = self.LEGEND_Y
        line_height = self.LEGEND_LINE_HEIGHT

        output.write("  <!-- Legend -->\n")
        output.write(f'  <text x="{legend_x}" y="{legend_y}" font-family="Arial" ')
        output.write(f'font-size="{self.LEGEND_TITLE_FONT_PX}" font-weight="bold">')
        output.write(f"{geometry.metadata.get('name', 'Section')}</text>\n")

        # Collect unique layer types
        layer_types = set(self._collect_layer_types(geometry))

        # Draw legend items
        y = legend_y + line_height
        for layer_type in sorted(layer_types):
            color = self.COLORS.get(layer_type, self.COLORS["default"])
            output.write(
                f'  <rect x="{legend_x}" y="{y}" width="15" height="15" fill="{color}"/>\n'
            )
            output.write(
                f'  <text x="{legend_x + 20}" y="{y + 12}" font-family="Arial" '
                f'font-size="{self.LEGEND_ITEM_FONT_PX}">'
            )
            output.write(f"{layer_type}</text>\n")
            y += line_height

    def _add_scale(
        self,
        output: TextIO,
        svg_height: float,
        scale_length: float,
        scale_label: str,
    ) -> None:
        """Add scale indicator."""
        scale_px = scale_length * self.scale
        x_start = self.SCALE_X_START
        y_pos = svg_height - self.SCALE_Y_OFFSET

        output.write("  <!-- Scale -->\n")
        output.write(f'  <line x1="{x_start}" y1="{y_pos}" x2="{x_start + scale_px}" y2="{y_pos}" ')
        output.write('stroke="black" stroke-width="2"/>\n')
        output.write(
            f'  <line x1="{x_start}" y1="{y_pos - self.SCALE_TICK_HALF}" '
            f'x2="{x_start}" y2="{y_pos + self.SCALE_TICK_HALF}" '
        )
        output.write('stroke="black" stroke-width="2"/>\n')
        output.write(f'  <line x1="{x_start + scale_px}" y1="{y_pos - self.SCALE_TICK_HALF}" ')
        output.write(
            f'x2="{x_start + scale_px}" y2="{y_pos + self.SCALE_TICK_HALF}" '
            'stroke="black" stroke-width="2"/>\n'
        )
        output.write(
            f'  <text x="{x_start + scale_px / 2}" y="{y_pos + self.SCALE_LABEL_OFFSET}" '
        )
        output.write('font-family="Arial" font-size="12" text-anchor="middle">')
        output.write(f"{scale_label}</text>\n")
