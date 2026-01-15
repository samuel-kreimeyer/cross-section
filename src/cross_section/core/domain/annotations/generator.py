"""Auto-generation of annotations for road cross-sections."""

from dataclasses import dataclass

from ...geometry.primitives import Point2D
from ..section import SectionGeometry
from .container import AnnotationCollection
from .dimension import DimensionAnnotation
from .symbol import SymbolAnnotation
from .text import TextAnnotation


@dataclass
class AnnotationGeneratorOptions:
    """Configuration options for auto-generating annotations.

    Attributes:
        add_component_labels: Add text labels for each component
        add_width_dimensions: Add dimension lines for component widths
        add_material_labels: Add labels for material types/layers
        use_keyed_notes: Use keyed notes instead of inline text
        add_traffic_symbols: Add traffic direction arrows on lanes
        add_centerpoint_mark: Add mark at control point
        symbol_library: Which symbol library to use
        text_size: Default text size for labels
        dimension_offset: Vertical offset for dimension lines
    """

    add_component_labels: bool = True
    add_width_dimensions: bool = True
    add_material_labels: bool = False
    use_keyed_notes: bool = False
    add_traffic_symbols: bool = False
    add_centerpoint_mark: bool = False
    symbol_library: str = "aashto"
    text_size: float = 0.15
    dimension_offset: float = 0.5


class AnnotationGenerator:
    """Automatically generates standard annotations for road sections."""

    @staticmethod
    def generate(
        section_geometry: SectionGeometry,
        options: AnnotationGeneratorOptions
    ) -> AnnotationCollection:
        """Generate annotations for a road section.

        Args:
            section_geometry: The section geometry to annotate
            options: Generation options

        Returns:
            AnnotationCollection with generated annotations
        """
        collection = AnnotationCollection()

        # Add centerpoint mark if requested
        if options.add_centerpoint_mark and section_geometry.metadata.get("control_point"):
            AnnotationGenerator._add_centerpoint_mark(
                section_geometry, collection, options
            )

        # Add component labels if requested
        if options.add_component_labels:
            AnnotationGenerator._add_component_labels(
                section_geometry, collection, options
            )

        # Add width dimensions if requested
        if options.add_width_dimensions:
            AnnotationGenerator._add_width_dimensions(
                section_geometry, collection, options
            )

        # Add material labels if requested
        if options.add_material_labels:
            AnnotationGenerator._add_material_labels(
                section_geometry, collection, options
            )

        # Add traffic symbols if requested
        if options.add_traffic_symbols:
            AnnotationGenerator._add_traffic_symbols(
                section_geometry, collection, options
            )

        return collection

    @staticmethod
    def _add_centerpoint_mark(
        section_geometry: SectionGeometry,
        collection: AnnotationCollection,
        options: AnnotationGeneratorOptions
    ) -> None:
        """Add centerpoint mark at control point."""
        control_point = section_geometry.metadata.get("control_point")
        if not control_point:
            return

        x = control_point.get("x", 0.0)
        elevation = control_point.get("elevation", 0.0)

        collection.add(SymbolAnnotation(
            position=Point2D(x, elevation),
            symbol_type="centerpoint",
            layer="symbols",
            priority=10  # High priority, don't move
        ))

    @staticmethod
    def _add_component_labels(
        section_geometry: SectionGeometry,
        collection: AnnotationCollection,
        options: AnnotationGeneratorOptions
    ) -> None:
        """Add text labels for each component."""
        for component_geom in section_geometry.components:
            metadata = component_geom.metadata

            # Get component type and position
            component_type = metadata.get("component_type", "Component")
            direction = metadata.get("assembly_direction", "right")

            # Calculate label position (center of component, above)
            bounds = component_geom.bounds()
            if not bounds:
                continue

            center_x = (bounds[0] + bounds[2]) / 2
            top_y = bounds[3]  # Max Y

            # Position label above component
            label_y = top_y + 0.2

            # Format label text
            if component_type == "TravelLane":
                label_text = "Lane"
            elif component_type == "Shoulder":
                label_text = "Shoulder"
            elif component_type == "Slope":
                # Include slope ratio if available
                slope_ratio = metadata.get("slope_ratio")
                if slope_ratio:
                    label_text = f"Slope {slope_ratio:.1f}:1"
                else:
                    label_text = "Slope"
            else:
                label_text = component_type

            # Add to collection
            if options.use_keyed_notes:
                key = collection.add_keyed_note(label_text)
                label_text = key

            collection.add(TextAnnotation(
                position=Point2D(center_x, label_y),
                text=label_text,
                font_size=options.text_size,
                anchor="middle",
                layer="labels",
                is_keyed_note=options.use_keyed_notes
            ))

    @staticmethod
    def _add_width_dimensions(
        section_geometry: SectionGeometry,
        collection: AnnotationCollection,
        options: AnnotationGeneratorOptions
    ) -> None:
        """Add dimension lines for component widths."""
        for component_geom in section_geometry.components:
            metadata = component_geom.metadata

            # Get width if available
            width = metadata.get("width")
            if not width:
                continue

            # Get component bounds
            bounds = component_geom.bounds()
            if not bounds:
                continue

            min_x, min_y, max_x, max_y = bounds
            direction = metadata.get("assembly_direction", "right")

            # Calculate dimension points
            if direction == "right":
                # Dimension from left edge to right edge
                start = Point2D(min_x, max_y)
                end = Point2D(max_x, max_y)
            else:  # left
                start = Point2D(max_x, max_y)
                end = Point2D(min_x, max_y)

            collection.add(DimensionAnnotation(
                start=start,
                end=end,
                offset=options.dimension_offset,
                dimension_text=f"{width:.2f}m",
                layer="dimensions"
            ))

    @staticmethod
    def _add_material_labels(
        section_geometry: SectionGeometry,
        collection: AnnotationCollection,
        options: AnnotationGeneratorOptions
    ) -> None:
        """Add labels for material types."""
        for component_geom in section_geometry.components:
            metadata = component_geom.metadata

            # Get layer information
            layers = metadata.get("layers", [])
            if not layers:
                continue

            # Get component bounds
            bounds = component_geom.bounds()
            if not bounds:
                continue

            # Add label for first (top) layer only
            if layers:
                layer_info = layers[0]
                layer_type = layer_info.get("type", "Unknown")

                # Format layer description
                if layer_type == "AsphaltLayer":
                    material_text = "Asphalt"
                elif layer_type == "ConcreteLayer":
                    material_text = "Concrete"
                elif layer_type == "CrushedRockLayer":
                    material_text = "Crushed Rock"
                else:
                    material_text = layer_type

                # Position in center of component
                center_x = (bounds[0] + bounds[2]) / 2
                center_y = (bounds[1] + bounds[3]) / 2

                # Add to collection
                if options.use_keyed_notes:
                    key = collection.add_keyed_note(material_text)
                    material_text = key

                collection.add(TextAnnotation(
                    position=Point2D(center_x, center_y),
                    text=material_text,
                    font_size=options.text_size * 0.8,  # Slightly smaller
                    anchor="middle",
                    layer="materials",
                    is_keyed_note=options.use_keyed_notes
                ))

    @staticmethod
    def _add_traffic_symbols(
        section_geometry: SectionGeometry,
        collection: AnnotationCollection,
        options: AnnotationGeneratorOptions
    ) -> None:
        """Add traffic direction arrows on lanes."""
        for component_geom in section_geometry.components:
            metadata = component_geom.metadata

            # Only add to lanes
            if metadata.get("component_type") != "TravelLane":
                continue

            # Get component bounds
            bounds = component_geom.bounds()
            if not bounds:
                continue

            # Position in center of lane
            center_x = (bounds[0] + bounds[2]) / 2
            center_y = (bounds[1] + bounds[3]) / 2

            # Determine direction
            direction = metadata.get("assembly_direction", "right")
            angle = 0 if direction == "right" else 180

            collection.add(SymbolAnnotation(
                position=Point2D(center_x, center_y),
                symbol_type="traffic_arrow",
                angle=angle,
                layer="symbols",
                priority=10  # High priority, fixed
            ))
