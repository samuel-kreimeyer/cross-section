"""Auto-generation of annotations for road cross-sections."""

from dataclasses import dataclass
from typing import Literal

from ..section import SectionGeometry
from .container import AnnotationCollection
from .planner import AnnotationPlanner
from .profile import AnnotationProfile


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
        add_cross_slope_symbols: Add cross-slope arrows on pavement components
        add_cross_slope_text: Add cross-slope text labels (percent)
        material_label_mode: How to render pavement material labels
        traffic_arrow_mode: How to orient traffic arrows
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
    add_cross_slope_symbols: bool = False
    add_cross_slope_text: bool = False
    material_label_mode: Literal["note", "dimension_suffix"] = "note"
    traffic_arrow_mode: Literal["assembly", "traffic_direction"] = "assembly"
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
        material_label_mode = (
            options.material_label_mode if options.add_material_labels else "none"
        )
        profile = AnnotationProfile(
            include_component_labels=options.add_component_labels,
            include_width_dimensions=options.add_width_dimensions,
            include_material_labels=options.add_material_labels,
            include_travel_direction=options.add_traffic_symbols,
            include_cross_slope=options.add_cross_slope_symbols,
            include_cross_slope_text=options.add_cross_slope_text,
            include_centerpoint_mark=options.add_centerpoint_mark,
            use_keyed_notes=options.use_keyed_notes,
            material_label_mode=material_label_mode,
            traffic_arrow_mode=options.traffic_arrow_mode,
            symbol_library=options.symbol_library,
            text_size=options.text_size,
            dimension_offset=options.dimension_offset,
        )
        planner = AnnotationPlanner()
        return planner.plan(section_geometry, profile)
