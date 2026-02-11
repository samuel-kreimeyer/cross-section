"""Annotation system for road cross-sections.

Provides text labels, dimension lines, leader callouts, and symbolic annotations
with automatic collision resolution.
"""

from .base import AnnotationBase
from .container import AnnotationCollection
from .dimension import DimensionAnnotation
from .collision import CollisionResult
from .generator import AnnotationGenerator, AnnotationGeneratorOptions, default_annotation_options
from .guides import AnnotationGuide, AnnotationGuideRegistry, DEFAULT_GUIDE_REGISTRY
from .leader import LeaderAnnotation
from .planner import AnnotationPlanner
from .profile import AnnotationProfile, AnnotationGuideOverride, DEFAULT_FULL_PROFILE, format_dimension, UnitSystem
from .symbol import SymbolAnnotation
from .text import TextAnnotation
from .zones import (
    AnnotationZone,
    ZONE_BASE_OFFSETS,
    SYMBOL_CLEARANCE_BUFFER,
    MAX_RESOLUTION_ITERATIONS,
    STUCK_THRESHOLD,
    BASE_PERTURBATION,
    get_zone_for_annotation,
    get_zone_y_bounds,
    compute_dimension_offset_for_span,
)

__all__ = [
    "AnnotationBase",
    "TextAnnotation",
    "DimensionAnnotation",
    "LeaderAnnotation",
    "SymbolAnnotation",
    "AnnotationCollection",
    "AnnotationGenerator",
    "AnnotationGeneratorOptions",
    "default_annotation_options",
    "CollisionResult",
    "AnnotationGuide",
    "AnnotationGuideRegistry",
    "DEFAULT_GUIDE_REGISTRY",
    "AnnotationPlanner",
    "AnnotationProfile",
    "AnnotationGuideOverride",
    "DEFAULT_FULL_PROFILE",
    "format_dimension",
    "UnitSystem",
    # Zone system
    "AnnotationZone",
    "ZONE_BASE_OFFSETS",
    "SYMBOL_CLEARANCE_BUFFER",
    "MAX_RESOLUTION_ITERATIONS",
    "STUCK_THRESHOLD",
    "BASE_PERTURBATION",
    "get_zone_for_annotation",
    "get_zone_y_bounds",
    "compute_dimension_offset_for_span",
]
