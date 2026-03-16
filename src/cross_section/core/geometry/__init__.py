"""Geometry primitives and optional validation helpers."""

from .primitives import (
    ComponentGeometry,
    ConnectionPoint,
    Point2D,
    Polygon,
    Segment2D,
    horizontal_segment,
    profile_segment,
    quad_between_segments,
    vertical_segment,
)
from .validate import (
    ShapelyNotAvailable,
    clip_hatched_polylines,
    clip_overlap_allowed_polygons,
    validate_section_geometry,
)

__all__ = [
    "Point2D",
    "Segment2D",
    "Polygon",
    "ComponentGeometry",
    "ConnectionPoint",
    "horizontal_segment",
    "profile_segment",
    "quad_between_segments",
    "vertical_segment",
    "ShapelyNotAvailable",
    "clip_hatched_polylines",
    "clip_overlap_allowed_polygons",
    "validate_section_geometry",
]
