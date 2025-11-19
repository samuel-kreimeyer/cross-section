"""Simple SVG exporter - Pure Python, no dependencies."""

from typing import TextIO
from ..core.domain.section import SectionGeometry


class SimpleSVGExporter:
    """Export road section geometry to SVG format.

    This is a minimal pure-Python SVG exporter for visualization and testing.
    Colors are assigned to layers based on their type.
    """

    # Color palette for different layer types
    COLORS = {
        'AsphaltLayer': '#2C3E50',      # Dark gray-blue
        'ConcreteLayer': '#95A5A6',      # Light gray
        'CrushedRockLayer': '#7F8C8D',   # Medium gray
        'default': '#BDC3C7'             # Very light gray
    }

    def __init__(self, scale: float = 100.0, vertical_exaggeration: float = 1.0):
        """Initialize SVG exporter.

        Args:
            scale: Pixels per meter (default 100 = 1m = 100px)
            vertical_exaggeration: Factor to exaggerate vertical dimensions for visibility
        """
        self.scale = scale
        self.vertical_exaggeration = vertical_exaggeration

    def export(self, geometry: SectionGeometry, output: TextIO) -> None:
        """Export section geometry to SVG.

        Args:
            geometry: The section geometry to export
            output: File object to write SVG to
        """
        if not geometry.components:
            output.write('<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">')
            output.write('<text x="10" y="50">Empty section</text>')
            output.write('</svg>')
            return

        # Calculate bounds
        bounds = geometry.bounds()
        min_x, min_y, max_x, max_y = bounds

        # Add margins (in meters)
        margin = 0.5
        view_min_x = min_x - margin
        view_max_x = max_x + margin
        view_min_y = min_y - margin
        view_max_y = max_y + margin

        # Calculate viewport dimensions
        view_width = view_max_x - view_min_x
        view_height = (view_max_y - view_min_y) * self.vertical_exaggeration

        # SVG dimensions in pixels
        svg_width = view_width * self.scale
        svg_height = view_height * self.scale

        # Write SVG header
        output.write(f'<svg xmlns="http://www.w3.org/2000/svg" ')
        output.write(f'width="{svg_width:.1f}" height="{svg_height:.1f}" ')
        output.write(f'viewBox="0 0 {svg_width:.1f} {svg_height:.1f}">\n')

        # Add title
        output.write(f'  <title>{geometry.metadata.get("name", "Road Section")}</title>\n')

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
                if 'layers' in component.metadata:
                    layers = component.metadata['layers']
                    if poly_idx < len(layers):
                        layer_info = layers[poly_idx]

                # Determine color based on layer type
                if layer_info and 'type' in layer_info:
                    color = self.COLORS.get(layer_info['type'], self.COLORS['default'])
                else:
                    color = self.COLORS['default']

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
            for polyline in component.polylines:
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
                output.write(f'fill="none" stroke="black" stroke-width="1.5"/>\n')

        output.write('    </g>\n')
        output.write('  </g>\n')

        # Add legend (not transformed)
        self._add_legend(output, geometry, svg_width, svg_height)

        # Add scale indicator
        self._add_scale(output, svg_height, view_width)

        output.write('</svg>\n')

    def _add_legend(self, output: TextIO, geometry: SectionGeometry,
                    svg_width: float, svg_height: float) -> None:
        """Add legend showing layer types."""
        legend_x = 10
        legend_y = 20
        line_height = 20

        output.write('  <!-- Legend -->\n')
        output.write(f'  <text x="{legend_x}" y="{legend_y}" font-family="Arial" ')
        output.write(f'font-size="14" font-weight="bold">')
        output.write(f'{geometry.metadata.get("name", "Section")}</text>\n')

        # Collect unique layer types
        layer_types = set()
        for component in geometry.components:
            if 'layers' in component.metadata:
                for layer in component.metadata['layers']:
                    if 'type' in layer:
                        layer_types.add(layer['type'])

        # Draw legend items
        y = legend_y + line_height
        for layer_type in sorted(layer_types):
            color = self.COLORS.get(layer_type, self.COLORS['default'])
            output.write(f'  <rect x="{legend_x}" y="{y}" width="15" height="15" fill="{color}"/>\n')
            output.write(f'  <text x="{legend_x + 20}" y="{y + 12}" font-family="Arial" font-size="12">')
            output.write(f'{layer_type}</text>\n')
            y += line_height

    def _add_scale(self, output: TextIO, svg_height: float, view_width: float) -> None:
        """Add scale indicator."""
        # Determine scale bar length (1m, 2m, 5m, or 10m)
        if view_width < 5:
            scale_length = 1.0
        elif view_width < 15:
            scale_length = 2.0
        elif view_width < 30:
            scale_length = 5.0
        else:
            scale_length = 10.0

        scale_px = scale_length * self.scale
        x_start = 10
        y_pos = svg_height - 30

        output.write('  <!-- Scale -->\n')
        output.write(f'  <line x1="{x_start}" y1="{y_pos}" x2="{x_start + scale_px}" y2="{y_pos}" ')
        output.write('stroke="black" stroke-width="2"/>\n')
        output.write(f'  <line x1="{x_start}" y1="{y_pos - 5}" x2="{x_start}" y2="{y_pos + 5}" ')
        output.write('stroke="black" stroke-width="2"/>\n')
        output.write(f'  <line x1="{x_start + scale_px}" y1="{y_pos - 5}" ')
        output.write(f'x2="{x_start + scale_px}" y2="{y_pos + 5}" stroke="black" stroke-width="2"/>\n')
        output.write(f'  <text x="{x_start + scale_px/2}" y="{y_pos + 20}" ')
        output.write('font-family="Arial" font-size="12" text-anchor="middle">')
        output.write(f'{scale_length:.0f}m</text>\n')
