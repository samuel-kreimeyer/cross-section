"""Scenario: 3-lane urban section with turn lane.

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
from cross_section.core.domain import (
    Buffer,
    ControlPoint,
    Gutter,
    RoadSection,
    Sidewalk,
    TurnLane,
    TravelLane,
)
from cross_section.core.domain.components import Curb
from cross_section.core.domain.components.slopes import Slope
from cross_section.core.domain.pavement import AsphaltLayer, CrushedRockLayer
from cross_section.core.domain.section import SectionGeometry
from cross_section.core.geometry.primitives import Point2D


def create_3lane_urban_section() -> SectionGeometry:
    """Create a 3-lane urban section with turn lane.

    Returns:
        SectionGeometry with all components
    """
    ft_to_m = 0.3048
    in_to_m = 0.0254

    left_lane_width = 10.0 * ft_to_m
    center_lane_width = 12.0 * ft_to_m
    right_lane_width = 10.0 * ft_to_m

    surface_thickness = 2.0 * in_to_m
    intermediate_thickness = 3.0 * in_to_m
    base_thickness = 4.0 * in_to_m
    subgrade_thickness = 6.0 * in_to_m

    curb_height = 6.0 * in_to_m
    curb_thickness = 12.0 * in_to_m
    gutter_width = 1.5 * ft_to_m
    buffer_width = 3.0 * ft_to_m
    sidewalk_width = 5.0 * ft_to_m
    sidewalk_thickness = 4.0 * in_to_m

    cross_slope = 0.02
    sidewalk_slope = 0.02
    fill_slope = 6.0

    crown_elevation = 100.0

    lane_layers = [
        AsphaltLayer(
            thickness=surface_thickness,
            aggregate_size=12.5,
            binder_type="PG 64-22",
            binder_percentage=5.5,
            density=2400,
        ),
        AsphaltLayer(
            thickness=intermediate_thickness,
            aggregate_size=19.0,
            binder_type="PG 64-22",
            binder_percentage=5.0,
            density=2350,
        ),
        CrushedRockLayer(
            thickness=base_thickness,
            aggregate_size=37.5,
            density=2200,
            material_type="aggregate_base",
        ),
        CrushedRockLayer(
            thickness=subgrade_thickness,
            aggregate_size=50.0,
            density=2100,
            material_type="cement_treated",
        ),
    ]

    turn_lane = TurnLane(
        width=center_lane_width,
        cross_slope=cross_slope,
        pavement_layers=[layer for layer in lane_layers],
    )
    left_turn, right_turn = turn_lane.split()

    section = RoadSection(
        name="3-Lane Urban Section with Turn Lane",
        control_point=ControlPoint(x=0.0, elevation=crown_elevation),
        left_components=[
            left_turn,
            TravelLane(
                width=left_lane_width,
                cross_slope=cross_slope,
                traffic_direction="inbound",
                pavement_layers=[layer for layer in lane_layers],
            ),
            Gutter(width=gutter_width, drop=curb_height, thickness=curb_height),
            Curb(
                gutter_width=0.0,
                gutter_drop=0.0,
                curb_height=curb_height,
                curb_width_bottom=curb_thickness,
                curb_width_top=curb_thickness,
            ),
            Buffer(width=buffer_width, cross_slope=0.0),
            Sidewalk(
                width=sidewalk_width,
                cross_slope=sidewalk_slope,
                thickness=sidewalk_thickness,
            ),
            Slope(
                horizontal_run=fill_slope * 2.0,
                vertical_drop=2.0,
                surface_type="grass",
                thickness=0.0,
            ),
        ],
        right_components=[
            right_turn,
            TravelLane(
                width=right_lane_width,
                cross_slope=cross_slope,
                traffic_direction="outbound",
                pavement_layers=[layer for layer in lane_layers],
            ),
            Gutter(width=gutter_width, drop=curb_height, thickness=curb_height),
            Curb(
                gutter_width=0.0,
                gutter_drop=0.0,
                curb_height=curb_height,
                curb_width_bottom=curb_thickness,
                curb_width_top=curb_thickness,
            ),
            Buffer(width=buffer_width, cross_slope=0.0),
            Sidewalk(
                width=sidewalk_width,
                cross_slope=sidewalk_slope,
                thickness=sidewalk_thickness,
            ),
            Slope(
                horizontal_run=fill_slope * 2.0,
                vertical_drop=2.0,
                surface_type="grass",
                thickness=0.0,
            ),
        ],
    )

    return section.to_geometry()


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


def build_scenario() -> tuple[SectionGeometry, AnnotationCollection]:
    """Build 3-lane urban scenario with annotations.

    Returns:
        Tuple of (SectionGeometry, AnnotationCollection)
    """
    # Create section geometry
    section = create_3lane_urban_section()

    # Create manual annotations
    annotations = create_manual_annotations(section)

    # Resolve collisions with geometry awareness
    annotations.resolve_collisions(geometry=section)

    return section, annotations
