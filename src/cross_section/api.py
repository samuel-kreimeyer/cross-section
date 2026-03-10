"""Stable public API surface for cross_section."""

from .core.domain.annotations import (
    AnnotationCollector,
    Dimension,
    Label,
    SectionAnnotations,
    SlopeTag,
)
from .export.dxf import DXFExporter
from .export.svg import SVGExporter, SimpleSVGExporter
from .core.domain import (
    Buffer,
    ControlPoint,
    Curb,
    Ditch,
    Gutter,
    LaneSpec,
    RoadSection,
    SectionGeometry,
    Shoulder,
    Sidewalk,
    Slope,
    SurfaceProfile,
    TraveledWay,
    TurnLane,
    TravelLane,
)
from .core.domain.components import (
    Barrier,
    ExistingPavement,
    MillAndOverlay,
    MSEWall,
    NotchAndWidening,
    RetainingWall,
    Shoring,
)
from .core.domain.pavement import (
    AsphaltLayer,
    ConcreteLayer,
    CrushedRockLayer,
    PavementLayer,
)

__all__ = [
    # Annotations
    "AnnotationCollector",
    "Dimension",
    "Label",
    "SectionAnnotations",
    "SlopeTag",
    # Exporters
    "SVGExporter",
    "SimpleSVGExporter",
    "DXFExporter",
    # Domain
    "Buffer",
    "ControlPoint",
    "Curb",
    "Ditch",
    "Gutter",
    "LaneSpec",
    "RoadSection",
    "SectionGeometry",
    "Shoulder",
    "Sidewalk",
    "Slope",
    "SurfaceProfile",
    "TraveledWay",
    "TurnLane",
    "TravelLane",
    "Barrier",
    "ExistingPavement",
    "MillAndOverlay",
    "MSEWall",
    "NotchAndWidening",
    "RetainingWall",
    "Shoring",
    "AsphaltLayer",
    "ConcreteLayer",
    "CrushedRockLayer",
    "PavementLayer",
]
