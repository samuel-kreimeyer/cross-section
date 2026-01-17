"""Annotation system for road cross-sections.

Provides text labels, dimension lines, leader callouts, and symbolic annotations
with automatic collision resolution.
"""

from .base import AnnotationBase
from .container import AnnotationCollection
from .dimension import DimensionAnnotation
from .generator import AnnotationGenerator, AnnotationGeneratorOptions
from .guides import AnnotationGuide, AnnotationGuideRegistry, DEFAULT_GUIDE_REGISTRY
from .leader import LeaderAnnotation
from .planner import AnnotationPlanner
from .profile import AnnotationProfile, AnnotationGuideOverride
from .symbol import SymbolAnnotation
from .text import TextAnnotation

__all__ = [
    "AnnotationBase",
    "TextAnnotation",
    "DimensionAnnotation",
    "LeaderAnnotation",
    "SymbolAnnotation",
    "AnnotationCollection",
    "AnnotationGenerator",
    "AnnotationGeneratorOptions",
    "AnnotationGuide",
    "AnnotationGuideRegistry",
    "DEFAULT_GUIDE_REGISTRY",
    "AnnotationPlanner",
    "AnnotationProfile",
    "AnnotationGuideOverride",
]
