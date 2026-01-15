"""Example: Generate annotated 3-lane urban section with turn lane.

Creates a complex urban road section with:
- Two 10-ft travel lanes and one 12-ft center turn lane
- 4-layer asphalt pavement (surface, intermediate, base, cement-treated subgrade)
- 6-inch barrier curbs with 1.5-ft gutters
- 3-ft grass buffers
- 5-ft concrete sidewalks (4-inch thick)
- 6:1 fill slopes off back of sidewalks
- Crowned at center of turn lane, 2% cross slope
- Comprehensive annotations: dimensions, leaders, symbols, slope indicators
"""

from cross_section.core.domain.annotations import (
    AnnotationCollection,
    DimensionAnnotation,
    LeaderAnnotation,
    SymbolAnnotation,
    TextAnnotation,
)
from cross_section.core.geometry.primitives import ComponentGeometry, Point2D, Polygon
from cross_section.core.domain.section import SectionGeometry
from cross_section.export import AnnotatedSVGExporter


def create_3lane_urban_section() -> SectionGeometry:
    """Create a 3-lane urban section with turn lane.

    Returns:
        SectionGeometry with all components
    """
    # Convert feet/inches to meters
    ft_to_m = 0.3048
    in_to_m = 0.0254

    # Dimensions
    left_lane_width = 10.0 * ft_to_m
    center_lane_width = 12.0 * ft_to_m
    right_lane_width = 10.0 * ft_to_m

    # Pavement layer thicknesses (inches)
    surface_thickness = 2.0 * in_to_m
    intermediate_thickness = 3.0 * in_to_m
    base_thickness = 4.0 * in_to_m
    subgrade_thickness = 6.0 * in_to_m
    total_pavement = surface_thickness + intermediate_thickness + base_thickness + subgrade_thickness

    # Edge features
    curb_height = 6.0 * in_to_m
    gutter_width = 1.5 * ft_to_m
    buffer_width = 3.0 * ft_to_m
    sidewalk_width = 5.0 * ft_to_m
    sidewalk_thickness = 4.0 * in_to_m

    # Slopes
    cross_slope = 0.02  # 2%
    sidewalk_slope = 0.02  # 2% toward curb
    fill_slope = 6.0  # 6:1

    # Crown elevation at center of turn lane
    crown_elevation = 100.0  # meters

    # Calculate station positions (working outward from center of turn lane)
    # Center turn lane
    turn_lane_left = -center_lane_width / 2
    turn_lane_right = center_lane_width / 2

    # Left travel lane
    left_lane_right = turn_lane_left
    left_lane_left = left_lane_right - left_lane_width
    left_lane_left_elev = crown_elevation - (left_lane_width / 2 + center_lane_width / 2) * cross_slope
    left_lane_right_elev = crown_elevation - (center_lane_width / 2) * cross_slope

    # Right travel lane
    right_lane_left = turn_lane_right
    right_lane_right = right_lane_left + right_lane_width
    right_lane_left_elev = crown_elevation - (center_lane_width / 2) * cross_slope
    right_lane_right_elev = crown_elevation - (center_lane_width / 2 + right_lane_width / 2) * cross_slope

    # Left side features
    # Gutter: 1.5ft wide, 6" deep pan
    left_gutter_right = left_lane_left
    left_gutter_left = left_gutter_right - gutter_width
    left_gutter_top_elev = left_lane_left_elev
    left_flowline_elev = left_gutter_top_elev - curb_height  # 6" down to flowline

    # Curb: 12" thick (not 6"), rises from flowline to pavement level
    curb_thickness = 12.0 * in_to_m  # 12 inches horizontal
    left_curb_right = left_gutter_left
    left_curb_left = left_curb_right - curb_thickness

    # Buffer: connects to TOP of curb, shown as line (not filled)
    left_buffer_right = left_curb_left
    left_buffer_right_elev = left_gutter_top_elev  # At pavement level (top of curb)
    left_buffer_left = left_buffer_right - buffer_width
    left_buffer_left_elev = left_buffer_right_elev  # Level buffer

    # Sidewalk: starts at end of buffer
    left_sidewalk_right = left_buffer_left
    left_sidewalk_left = left_sidewalk_right - sidewalk_width
    left_sidewalk_right_elev = left_buffer_left_elev
    left_sidewalk_left_elev = left_sidewalk_right_elev - sidewalk_width * sidewalk_slope

    # Left fill slope
    left_slope_top = left_sidewalk_left
    left_slope_bottom = left_slope_top - (left_sidewalk_left_elev - (crown_elevation - 2.0)) * fill_slope

    # Right side features (mirror)
    # Gutter: 1.5ft wide, 6" deep pan
    right_gutter_left = right_lane_right
    right_gutter_right = right_gutter_left + gutter_width
    right_gutter_top_elev = right_lane_right_elev
    right_flowline_elev = right_gutter_top_elev - curb_height  # 6" down to flowline

    # Curb: 12" thick, rises from flowline to pavement level
    right_curb_left = right_gutter_right
    right_curb_right = right_curb_left + curb_thickness

    # Buffer: connects to TOP of curb, shown as line (not filled)
    right_buffer_left = right_curb_right
    right_buffer_left_elev = right_gutter_top_elev  # At pavement level (top of curb)
    right_buffer_right = right_buffer_left + buffer_width
    right_buffer_right_elev = right_buffer_left_elev  # Level buffer

    # Sidewalk: starts at end of buffer
    right_sidewalk_left = right_buffer_right
    right_sidewalk_right = right_sidewalk_left + sidewalk_width
    right_sidewalk_left_elev = right_buffer_right_elev
    right_sidewalk_right_elev = right_sidewalk_left_elev - sidewalk_width * sidewalk_slope

    # Right fill slope
    right_slope_top = right_sidewalk_right
    right_slope_bottom = right_slope_top + (right_sidewalk_right_elev - (crown_elevation - 2.0)) * fill_slope

    components = []

    # === PAVEMENT LAYERS ===
    # Surface course - left lane
    components.append(ComponentGeometry(
        polygons=[Polygon(exterior=[
            Point2D(left_lane_left, left_lane_left_elev),
            Point2D(left_lane_right, left_lane_right_elev),
            Point2D(left_lane_right, left_lane_right_elev - surface_thickness),
            Point2D(left_lane_left, left_lane_left_elev - surface_thickness),
        ])],
        metadata={
            "component_type": "TravelLane",
            "layer": "surface",
            "width": left_lane_width,
        }
    ))

    # Surface course - center turn lane
    components.append(ComponentGeometry(
        polygons=[Polygon(exterior=[
            Point2D(turn_lane_left, crown_elevation - (center_lane_width / 2) * cross_slope),
            Point2D(turn_lane_right, crown_elevation - (center_lane_width / 2) * cross_slope),
            Point2D(turn_lane_right, crown_elevation - (center_lane_width / 2) * cross_slope - surface_thickness),
            Point2D(turn_lane_left, crown_elevation - (center_lane_width / 2) * cross_slope - surface_thickness),
        ])],
        metadata={
            "component_type": "TurnLane",
            "layer": "surface",
            "width": center_lane_width,
        }
    ))

    # Surface course - right lane
    components.append(ComponentGeometry(
        polygons=[Polygon(exterior=[
            Point2D(right_lane_left, right_lane_left_elev),
            Point2D(right_lane_right, right_lane_right_elev),
            Point2D(right_lane_right, right_lane_right_elev - surface_thickness),
            Point2D(right_lane_left, right_lane_left_elev - surface_thickness),
        ])],
        metadata={
            "component_type": "TravelLane",
            "layer": "surface",
            "width": right_lane_width,
        }
    ))

    # Intermediate course (full width)
    total_paved_width = left_lane_width + center_lane_width + right_lane_width
    intermediate_top = crown_elevation - surface_thickness
    components.append(ComponentGeometry(
        polygons=[Polygon(exterior=[
            Point2D(left_lane_left, left_lane_left_elev - surface_thickness),
            Point2D(right_lane_right, right_lane_right_elev - surface_thickness),
            Point2D(right_lane_right, right_lane_right_elev - surface_thickness - intermediate_thickness),
            Point2D(left_lane_left, left_lane_left_elev - surface_thickness - intermediate_thickness),
        ])],
        metadata={
            "component_type": "Pavement",
            "layer": "intermediate",
        }
    ))

    # Base course (full width)
    components.append(ComponentGeometry(
        polygons=[Polygon(exterior=[
            Point2D(left_lane_left, left_lane_left_elev - surface_thickness - intermediate_thickness),
            Point2D(right_lane_right, right_lane_right_elev - surface_thickness - intermediate_thickness),
            Point2D(right_lane_right, right_lane_right_elev - surface_thickness - intermediate_thickness - base_thickness),
            Point2D(left_lane_left, left_lane_left_elev - surface_thickness - intermediate_thickness - base_thickness),
        ])],
        metadata={
            "component_type": "Pavement",
            "layer": "base",
        }
    ))

    # Cement-treated subgrade (full width)
    components.append(ComponentGeometry(
        polygons=[Polygon(exterior=[
            Point2D(left_lane_left, left_lane_left_elev - surface_thickness - intermediate_thickness - base_thickness),
            Point2D(right_lane_right, right_lane_right_elev - surface_thickness - intermediate_thickness - base_thickness),
            Point2D(right_lane_right, right_lane_right_elev - total_pavement),
            Point2D(left_lane_left, left_lane_left_elev - total_pavement),
        ])],
        metadata={
            "component_type": "Pavement",
            "layer": "subgrade",
        }
    ))

    # === LEFT SIDE ===
    # Left gutter (6" deep pan)
    components.append(ComponentGeometry(
        polygons=[Polygon(exterior=[
            Point2D(left_gutter_left, left_gutter_top_elev),
            Point2D(left_gutter_right, left_gutter_top_elev),
            Point2D(left_gutter_right, left_flowline_elev),
            Point2D(left_gutter_left, left_flowline_elev),
        ])],
        metadata={"component_type": "Gutter"}
    ))

    # Left curb (12" thick barrier, rises from flowline to pavement level)
    components.append(ComponentGeometry(
        polygons=[Polygon(exterior=[
            Point2D(left_curb_left, left_gutter_top_elev),
            Point2D(left_curb_right, left_gutter_top_elev),
            Point2D(left_curb_right, left_flowline_elev),
            Point2D(left_curb_left, left_flowline_elev),
        ])],
        metadata={"component_type": "Curb"}
    ))

    # Left buffer (grass) - shown as line, not filled
    components.append(ComponentGeometry(
        polygons=[],
        polylines=[[
            Point2D(left_buffer_right, left_buffer_right_elev),
            Point2D(left_buffer_left, left_buffer_left_elev),
        ]],
        metadata={"component_type": "Buffer"}
    ))

    # Left sidewalk
    components.append(ComponentGeometry(
        polygons=[Polygon(exterior=[
            Point2D(left_sidewalk_left, left_sidewalk_left_elev),
            Point2D(left_sidewalk_right, left_sidewalk_right_elev),
            Point2D(left_sidewalk_right, left_sidewalk_right_elev - sidewalk_thickness),
            Point2D(left_sidewalk_left, left_sidewalk_left_elev - sidewalk_thickness),
        ])],
        metadata={
            "component_type": "Sidewalk",
            "width": sidewalk_width,
        }
    ))

    # Left fill slope (as polyline)
    components.append(ComponentGeometry(
        polygons=[],
        polylines=[[
            Point2D(left_slope_top, left_sidewalk_left_elev),
            Point2D(left_slope_bottom, crown_elevation - 2.0),
        ]],
        metadata={"component_type": "Slope"}
    ))

    # === RIGHT SIDE ===
    # Right gutter (6" deep pan)
    components.append(ComponentGeometry(
        polygons=[Polygon(exterior=[
            Point2D(right_gutter_left, right_gutter_top_elev),
            Point2D(right_gutter_right, right_gutter_top_elev),
            Point2D(right_gutter_right, right_flowline_elev),
            Point2D(right_gutter_left, right_flowline_elev),
        ])],
        metadata={"component_type": "Gutter"}
    ))

    # Right curb (12" thick barrier, rises from flowline to pavement level)
    components.append(ComponentGeometry(
        polygons=[Polygon(exterior=[
            Point2D(right_curb_left, right_gutter_top_elev),
            Point2D(right_curb_right, right_gutter_top_elev),
            Point2D(right_curb_right, right_flowline_elev),
            Point2D(right_curb_left, right_flowline_elev),
        ])],
        metadata={"component_type": "Curb"}
    ))

    # Right buffer (grass) - shown as line, not filled
    components.append(ComponentGeometry(
        polygons=[],
        polylines=[[
            Point2D(right_buffer_left, right_buffer_left_elev),
            Point2D(right_buffer_right, right_buffer_right_elev),
        ]],
        metadata={"component_type": "Buffer"}
    ))

    # Right sidewalk
    components.append(ComponentGeometry(
        polygons=[Polygon(exterior=[
            Point2D(right_sidewalk_left, right_sidewalk_left_elev),
            Point2D(right_sidewalk_right, right_sidewalk_right_elev),
            Point2D(right_sidewalk_right, right_sidewalk_right_elev - sidewalk_thickness),
            Point2D(right_sidewalk_left, right_sidewalk_left_elev - sidewalk_thickness),
        ])],
        metadata={
            "component_type": "Sidewalk",
            "width": sidewalk_width,
        }
    ))

    # Right fill slope (as polyline)
    components.append(ComponentGeometry(
        polygons=[],
        polylines=[[
            Point2D(right_slope_top, right_sidewalk_right_elev),
            Point2D(right_slope_bottom, crown_elevation - 2.0),
        ]],
        metadata={"component_type": "Slope"}
    ))

    return SectionGeometry(
        components=components,
        metadata={
            "name": "3-Lane Urban Section with Turn Lane",
            "control_point": {"x": 0.0, "elevation": crown_elevation}
        }
    )


def create_manual_annotations(section: SectionGeometry) -> AnnotationCollection:
    """Create comprehensive annotations for the 3-lane section.

    Args:
        section: The section geometry to annotate

    Returns:
        AnnotationCollection with all annotations
    """
    ft_to_m = 0.3048
    collection = AnnotationCollection()

    # Dimensions
    left_lane_width = 10.0 * ft_to_m
    center_lane_width = 12.0 * ft_to_m
    right_lane_width = 10.0 * ft_to_m
    sidewalk_width = 5.0 * ft_to_m

    crown_elev = 100.0
    cross_slope = 0.02

    # Calculate key positions
    turn_lane_left = -center_lane_width / 2
    turn_lane_right = center_lane_width / 2
    left_lane_left = turn_lane_left - left_lane_width
    right_lane_right = turn_lane_right + right_lane_width

    # Pavement layer elevations (for leaders)
    surface_thickness = 2.0 * 0.0254
    intermediate_thickness = 3.0 * 0.0254
    base_thickness = 4.0 * 0.0254

    # Dimension offsets
    dim_offset_lower = 0.5  # For lane dimensions
    dim_offset_middle = 1.2  # For sidewalk dimensions
    dim_offset_upper = 1.9  # For overall dimension

    # === LANE DIMENSIONS ===
    # Left lane dimension
    collection.add(DimensionAnnotation(
        start=Point2D(left_lane_left, crown_elev),
        end=Point2D(turn_lane_left, crown_elev),
        offset=dim_offset_lower,
        dimension_text="10'-0\"",
        layer="dimensions"
    ))

    # Center turn lane dimension
    collection.add(DimensionAnnotation(
        start=Point2D(turn_lane_left, crown_elev),
        end=Point2D(turn_lane_right, crown_elev),
        offset=dim_offset_lower,
        dimension_text="12'-0\"",
        layer="dimensions"
    ))

    # Right lane dimension
    collection.add(DimensionAnnotation(
        start=Point2D(turn_lane_right, crown_elev),
        end=Point2D(right_lane_right, crown_elev),
        offset=dim_offset_lower,
        dimension_text="10'-0\"",
        layer="dimensions"
    ))

    # === DIRECTIONAL ARROW SYMBOLS ===
    # Left lane - arrow pointing down (180 degrees)
    collection.add(SymbolAnnotation(
        position=Point2D(left_lane_left + left_lane_width / 2, crown_elev + 0.35),
        symbol_type="traffic_arrow",
        angle=270,  # Pointing down
        scale=1.0,
        layer="symbols"
    ))

    # Right lane - arrow pointing up (0 degrees)
    collection.add(SymbolAnnotation(
        position=Point2D(turn_lane_right + right_lane_width / 2, crown_elev + 0.35),
        symbol_type="traffic_arrow",
        angle=90,  # Pointing up
        scale=1.0,
        layer="symbols"
    ))

    # === SLOPE INDICATORS ===
    # Left lane slope indicator
    left_lane_center_x = left_lane_left + left_lane_width / 2
    collection.add(SymbolAnnotation(
        position=Point2D(left_lane_center_x, crown_elev + 0.65),
        symbol_type="drainage_arrow",
        angle=180,  # Pointing left
        scale=0.8,
        layer="slope_indicators"
    ))
    collection.add(TextAnnotation(
        position=Point2D(left_lane_center_x, crown_elev + 0.80),
        text="2%",
        font_size=0.10,
        layer="slope_indicators"
    ))

    # Right lane slope indicator
    right_lane_center_x = turn_lane_right + right_lane_width / 2
    collection.add(SymbolAnnotation(
        position=Point2D(right_lane_center_x, crown_elev + 0.65),
        symbol_type="drainage_arrow",
        angle=0,  # Pointing right
        scale=0.8,
        layer="slope_indicators"
    ))
    collection.add(TextAnnotation(
        position=Point2D(right_lane_center_x, crown_elev + 0.80),
        text="2%",
        font_size=0.10,
        layer="slope_indicators"
    ))

    # === PAVEMENT LAYER LEADERS ===
    # Surface course leader (pointing to center of left lane surface)
    surface_elev = crown_elev - (left_lane_width / 2 + center_lane_width / 2) * cross_slope - surface_thickness / 2
    collection.add(LeaderAnnotation(
        points=[
            Point2D(left_lane_left + left_lane_width / 2, surface_elev),
            Point2D(left_lane_left + left_lane_width / 2 - 0.5, surface_elev - 0.2),
            Point2D(left_lane_left + left_lane_width / 2 - 1.5, surface_elev - 0.2),
        ],
        text="Surface Course (2\")",
        arrow_at_start=True,
        layer="leaders"
    ))

    # Intermediate course leader
    intermediate_elev = surface_elev - surface_thickness / 2 - intermediate_thickness / 2
    collection.add(LeaderAnnotation(
        points=[
            Point2D(turn_lane_left + center_lane_width / 3, intermediate_elev),
            Point2D(turn_lane_left + center_lane_width / 3 - 0.5, intermediate_elev - 0.3),
            Point2D(turn_lane_left + center_lane_width / 3 - 1.8, intermediate_elev - 0.3),
        ],
        text="Intermediate Course (3\")",
        arrow_at_start=True,
        layer="leaders"
    ))

    # Base course leader
    base_elev = intermediate_elev - intermediate_thickness / 2 - base_thickness / 2
    collection.add(LeaderAnnotation(
        points=[
            Point2D(turn_lane_right + right_lane_width / 3, base_elev),
            Point2D(turn_lane_right + right_lane_width / 3 + 0.5, base_elev - 0.3),
            Point2D(turn_lane_right + right_lane_width / 3 + 1.5, base_elev - 0.3),
        ],
        text="Base Course (4\")",
        arrow_at_start=True,
        layer="leaders"
    ))

    # Cement-treated subgrade leader
    subgrade_thickness = 6.0 * 0.0254
    subgrade_elev = base_elev - base_thickness / 2 - subgrade_thickness / 2
    collection.add(LeaderAnnotation(
        points=[
            Point2D(turn_lane_left / 2, subgrade_elev),
            Point2D(turn_lane_left / 2 - 0.5, subgrade_elev - 0.4),
            Point2D(turn_lane_left / 2 - 2.2, subgrade_elev - 0.4),
        ],
        text="Cement-Treated Subgrade (6\")",
        arrow_at_start=True,
        layer="leaders"
    ))

    # === SIDEWALK ANNOTATIONS ===
    # Calculate sidewalk positions
    gutter_width = 1.5 * ft_to_m
    buffer_width = 3.0 * ft_to_m
    curb_height = 6.0 * 0.0254

    left_gutter_left = left_lane_left - gutter_width
    left_curb_left = left_gutter_left - 0.15
    left_buffer_left = left_curb_left - buffer_width
    left_sidewalk_left = left_buffer_left - sidewalk_width

    right_gutter_right = right_lane_right + gutter_width
    right_curb_right = right_gutter_right + 0.15
    right_buffer_right = right_curb_right + buffer_width
    right_sidewalk_right = right_buffer_right + sidewalk_width

    # Left sidewalk dimension
    collection.add(DimensionAnnotation(
        start=Point2D(left_sidewalk_left, crown_elev),
        end=Point2D(left_buffer_left, crown_elev),
        offset=dim_offset_middle,
        dimension_text="5'-0\"",
        layer="dimensions"
    ))

    # Right sidewalk dimension
    collection.add(DimensionAnnotation(
        start=Point2D(right_buffer_right, crown_elev),
        end=Point2D(right_sidewalk_right, crown_elev),
        offset=dim_offset_middle,
        dimension_text="5'-0\"",
        layer="dimensions"
    ))

    # Left sidewalk leader
    sidewalk_elev = crown_elev - (left_lane_width / 2 + center_lane_width / 2) * cross_slope - curb_height
    collection.add(LeaderAnnotation(
        points=[
            Point2D(left_sidewalk_left + sidewalk_width / 2, sidewalk_elev - 0.02),
            Point2D(left_sidewalk_left + sidewalk_width / 2 - 0.3, sidewalk_elev - 0.25),
            Point2D(left_sidewalk_left + sidewalk_width / 2 - 1.2, sidewalk_elev - 0.25),
        ],
        text="Concrete Sidewalk (4\")",
        arrow_at_start=True,
        layer="leaders"
    ))

    # Right sidewalk leader
    collection.add(LeaderAnnotation(
        points=[
            Point2D(right_sidewalk_right - sidewalk_width / 2, sidewalk_elev - 0.02),
            Point2D(right_sidewalk_right - sidewalk_width / 2 + 0.3, sidewalk_elev - 0.25),
            Point2D(right_sidewalk_right - sidewalk_width / 2 + 1.2, sidewalk_elev - 0.25),
        ],
        text="Concrete Sidewalk (4\")",
        arrow_at_start=True,
        layer="leaders"
    ))

    # Left sidewalk slope indicator
    sidewalk_slope = 0.02
    left_sidewalk_center = left_sidewalk_left + sidewalk_width / 2
    left_sidewalk_elev_at_center = sidewalk_elev - (sidewalk_width / 2) * sidewalk_slope
    collection.add(SymbolAnnotation(
        position=Point2D(left_sidewalk_center, left_sidewalk_elev_at_center + 0.25),
        symbol_type="drainage_arrow",
        angle=0,  # Pointing toward curb (right)
        scale=0.6,
        layer="slope_indicators"
    ))
    collection.add(TextAnnotation(
        position=Point2D(left_sidewalk_center, left_sidewalk_elev_at_center + 0.35),
        text="2%",
        font_size=0.08,
        layer="slope_indicators"
    ))

    # Right sidewalk slope indicator
    right_sidewalk_center = right_buffer_right + sidewalk_width / 2
    right_sidewalk_elev_at_center = sidewalk_elev - (sidewalk_width / 2) * sidewalk_slope
    collection.add(SymbolAnnotation(
        position=Point2D(right_sidewalk_center, right_sidewalk_elev_at_center + 0.25),
        symbol_type="drainage_arrow",
        angle=180,  # Pointing toward curb (left)
        scale=0.6,
        layer="slope_indicators"
    ))
    collection.add(TextAnnotation(
        position=Point2D(right_sidewalk_center, right_sidewalk_elev_at_center + 0.35),
        text="2%",
        font_size=0.08,
        layer="slope_indicators"
    ))

    # === OVERALL DIMENSION ===
    # From back of left sidewalk to back of right sidewalk
    collection.add(DimensionAnnotation(
        start=Point2D(left_sidewalk_left, crown_elev),
        end=Point2D(right_sidewalk_right, crown_elev),
        offset=dim_offset_upper,
        dimension_text="64'-0\"",  # Approximate total width
        layer="dimensions"
    ))

    return collection


def main():
    """Generate and export annotated 3-lane urban section."""
    print("Generating 3-lane urban section with turn lane...")

    # Create section geometry
    section = create_3lane_urban_section()
    print(f"  Created section with {len(section.components)} components")

    # Create manual annotations
    annotations = create_manual_annotations(section)
    print(f"  Created {annotations.count()} annotations")

    # Resolve collisions
    print("  Resolving annotation collisions...")
    annotations.resolve_collisions()
    print(f"  Collision resolution complete")

    # Export to SVG
    exporter = AnnotatedSVGExporter(
        scale=100.0,  # 100 pixels per meter
        vertical_exaggeration=1.0,  # No vertical exaggeration
        units="imperial"
    )

    output_path = "3lane_urban_annotated.svg"
    with open(output_path, "w") as f:
        exporter.export_with_annotations(section, annotations, f)

    print(f"  Exported to {output_path}")
    print("\nSection details:")
    print(f"  - Three lanes: 10' left, 12' center turn, 10' right")
    print(f"  - 4-layer asphalt pavement")
    print(f"  - 6\" barrier curbs with 1.5' gutters")
    print(f"  - 3' grass buffers")
    print(f"  - 5' concrete sidewalks (4\" thick)")
    print(f"  - 6:1 fill slopes")
    print(f"  - Crowned at center, 2% cross slope")
    print("\nAnnotations:")
    print(f"  - {len(annotations.get_by_type(DimensionAnnotation))} dimension lines")
    print(f"  - {len(annotations.get_by_type(LeaderAnnotation))} leader callouts")
    print(f"  - {len(annotations.get_by_type(SymbolAnnotation))} symbols")
    print(f"  - {len(annotations.get_by_type(TextAnnotation))} text labels")


if __name__ == "__main__":
    main()
