"""Geometry primitives and optional validation helpers."""

from .primitives import ComponentGeometry, ConnectionPoint, Point2D, Polygon
from .validate import (
    ShapelyNotAvailable,
    clip_hatched_polylines,
    clip_overlap_allowed_polygons,
    validate_section_geometry,
)

__all__ = [
    "Point2D",
    "Polygon",
    "ComponentGeometry",
    "ConnectionPoint",
    "ShapelyNotAvailable",
    "clip_hatched_polylines",
    "clip_overlap_allowed_polygons",
    "validate_section_geometry",
]
