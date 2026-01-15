"""Annotation system for road cross-sections.

Provides text labels, dimension lines, leader callouts, and symbolic annotations
with automatic collision resolution.
"""

from .base import AnnotationBase
from .container import AnnotationCollection
from .dimension import DimensionAnnotation
from .generator import AnnotationGenerator, AnnotationGeneratorOptions
from .leader import LeaderAnnotation
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
]
