"""Zone-based annotation placement system.

Defines vertical zones for annotation placement to prevent collisions
and coordinate multi-layer annotations (symbols + dimensions).
"""

from enum import IntEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import AnnotationBase
    from .dimension import DimensionAnnotation
    from .leader import LeaderAnnotation
    from .symbol import SymbolAnnotation
    from .text import TextAnnotation


class AnnotationZone(IntEnum):
    """Vertical zones for annotation placement (lower = closer to geometry).

    Zone 0: Section geometry (fixed, immutable)
    Zone 1: Labels/leaders (just above surface, closest to geometry)
    Zone 2: Primary symbols (traffic direction arrows)
    Zone 3: Secondary symbols (cross-slope arrows, drainage)
    Zone 4: Dimension lines + text (topmost, offset computed per span)
    """

    GEOMETRY = 0
    LABEL_TEXT = 1
    PRIMARY_SYMBOL = 2
    SECONDARY_SYMBOL = 3
    DIMENSION = 4


# Default offsets from component top surface (in meters)
# Ordered from closest to geometry to furthest:
#   primary symbols (0.30) < secondary symbols (0.45) < labels (1.45) < dimensions (1.70)
# Labels sit just below the dimension line; symbols sit closer to road surface.
ZONE_BASE_OFFSETS: dict[AnnotationZone, float] = {
    AnnotationZone.LABEL_TEXT: 1.45,
    AnnotationZone.PRIMARY_SYMBOL: 0.85,
    AnnotationZone.SECONDARY_SYMBOL: 0.45,
    AnnotationZone.DIMENSION: 1.70,
}

# Extra clearance above symbols for dimensions (in meters)
SYMBOL_CLEARANCE_BUFFER = 0.10

# Resolver tuning constants
MAX_RESOLUTION_ITERATIONS = 15
STUCK_THRESHOLD = 3  # Iterations before random restart
BASE_PERTURBATION = 0.1  # Initial random jump scale


def get_zone_for_annotation(annotation: "AnnotationBase") -> AnnotationZone:
    """Determine which zone an annotation belongs in.

    Args:
        annotation: The annotation to classify

    Returns:
        The appropriate zone for this annotation type
    """
    # Import here to avoid circular dependency
    from .dimension import DimensionAnnotation
    from .leader import LeaderAnnotation
    from .symbol import SymbolAnnotation
    from .text import TextAnnotation

    if isinstance(annotation, DimensionAnnotation):
        return AnnotationZone.DIMENSION

    if isinstance(annotation, SymbolAnnotation):
        symbol_type = annotation.symbol_type
        # Traffic arrows are primary symbols
        if symbol_type in ("traffic_arrow", "centerpoint"):
            return AnnotationZone.PRIMARY_SYMBOL
        # Drainage/slope indicators are secondary
        return AnnotationZone.SECONDARY_SYMBOL

    if isinstance(annotation, LeaderAnnotation):
        return AnnotationZone.LABEL_TEXT

    if isinstance(annotation, TextAnnotation):
        # Component labels go in label zone
        if annotation.layer in ("labels", "materials"):
            return AnnotationZone.LABEL_TEXT
        # Slope text is secondary (associated with slope symbols)
        if annotation.layer == "slope_indicators":
            return AnnotationZone.SECONDARY_SYMBOL
        return AnnotationZone.LABEL_TEXT

    # Default to label zone for unknown types
    return AnnotationZone.LABEL_TEXT


def get_zone_y_bounds(
    zone: AnnotationZone,
    component_top_y: float,
    symbol_height: float = 0.0,
) -> tuple[float, float]:
    """Get the Y coordinate bounds for a zone.

    Args:
        zone: The zone to get bounds for
        component_top_y: Y coordinate of the component's top surface
        symbol_height: Height of symbols in this span (for dimension offset)

    Returns:
        Tuple of (min_y, max_y) for this zone
    """
    base_offset = ZONE_BASE_OFFSETS.get(zone, 0.5)

    if zone == AnnotationZone.LABEL_TEXT:
        # Labels sit just above the road surface (closest to geometry)
        min_y = component_top_y + base_offset
        max_y = min_y + 0.15
        return (min_y, max_y)

    if zone == AnnotationZone.PRIMARY_SYMBOL:
        min_y = component_top_y + base_offset
        max_y = min_y + 0.15
        return (min_y, max_y)

    if zone == AnnotationZone.SECONDARY_SYMBOL:
        min_y = component_top_y + base_offset
        max_y = min_y + 0.15
        return (min_y, max_y)

    if zone == AnnotationZone.DIMENSION:
        # Dimensions sit above all symbols (furthest from geometry)
        min_y = component_top_y + base_offset
        if symbol_height > 0:
            min_y = max(min_y, component_top_y + symbol_height + SYMBOL_CLEARANCE_BUFFER)
        max_y = float("inf")  # Dimensions can expand upward as needed
        return (min_y, max_y)

    # Default fallback
    return (component_top_y + 0.2, component_top_y + 1.0)


def compute_dimension_offset_for_span(
    component_top_y: float,
    symbols_in_span: list["SymbolAnnotation"],
    base_offset: float = 0.5,
) -> float:
    """Compute dimension offset to clear symbols in a horizontal span.

    This is the key function for proactive dimension placement - it
    computes the minimum offset needed to clear all symbols that will
    appear in the same horizontal span as the dimension line.

    Args:
        component_top_y: Y coordinate of component's top surface
        symbols_in_span: List of symbols that fall within this span
        base_offset: Default offset when no symbols present

    Returns:
        The offset value to use for the dimension annotation
    """
    if not symbols_in_span:
        return base_offset

    # Find highest symbol top relative to component top
    max_symbol_top = 0.0
    for symbol in symbols_in_span:
        symbol_bounds = symbol.bounds()
        symbol_top_relative = symbol_bounds.max_y - component_top_y
        max_symbol_top = max(max_symbol_top, symbol_top_relative)

    # Add clearance buffer
    symbol_clearance = max_symbol_top + SYMBOL_CLEARANCE_BUFFER

    return max(base_offset, symbol_clearance)
