"""Annotation guide registry keyed to component types."""

from dataclasses import dataclass
from typing import Literal


AnnotationKind = Literal["dimension", "symbol", "text", "note", "leader"]


@dataclass(frozen=True)
class AnnotationGuide:
    """Declarative description of a potential annotation."""

    kind: AnnotationKind
    target: str
    anchor: str
    required: bool = False
    preference_key: str | None = None


class AnnotationGuideRegistry:
    """Registry mapping component types to annotation guides."""

    def __init__(self) -> None:
        self._guides_by_component: dict[str, list[AnnotationGuide]] = {}

    def register(self, component_type: str, guides: list[AnnotationGuide]) -> None:
        if component_type in self._guides_by_component:
            self._guides_by_component[component_type].extend(guides)
        else:
            self._guides_by_component[component_type] = list(guides)

    def get_guides(self, component_type: str) -> list[AnnotationGuide]:
        return list(self._guides_by_component.get(component_type, []))


DEFAULT_GUIDE_REGISTRY = AnnotationGuideRegistry()

# Travel lanes: width dimension, travel direction arrow, cross-slope arrow, material note.
DEFAULT_GUIDE_REGISTRY.register(
    "TravelLane",
    [
        AnnotationGuide(
            kind="dimension",
            target="width",
            anchor="component_edges",
            preference_key="lane_width",
        ),
        AnnotationGuide(
            kind="symbol",
            target="travel_direction",
            anchor="component_center",
            preference_key="lane_travel_direction",
        ),
        AnnotationGuide(
            kind="symbol",
            target="cross_slope",
            anchor="component_top_center",
            preference_key="lane_cross_slope",
        ),
        AnnotationGuide(
            kind="text",
            target="material_label",
            anchor="component_center",
            preference_key="lane_material_label",
        ),
    ],
)

DEFAULT_GUIDE_REGISTRY.register(
    "TurnLane",
    [
        AnnotationGuide(
            kind="dimension",
            target="width",
            anchor="component_edges",
            preference_key="turn_lane_width",
        ),
        AnnotationGuide(
            kind="symbol",
            target="travel_direction",
            anchor="component_center",
            preference_key="turn_lane_travel_direction",
        ),
        AnnotationGuide(
            kind="symbol",
            target="cross_slope",
            anchor="component_top_center",
            preference_key="turn_lane_cross_slope",
        ),
        AnnotationGuide(
            kind="text",
            target="material_label",
            anchor="component_center",
            preference_key="turn_lane_material_label",
        ),
    ],
)

DEFAULT_GUIDE_REGISTRY.register(
    "Shoulder",
    [
        AnnotationGuide(
            kind="dimension",
            target="width",
            anchor="component_edges",
            preference_key="shoulder_width",
        ),
        AnnotationGuide(
            kind="symbol",
            target="cross_slope",
            anchor="component_top_center",
            preference_key="shoulder_cross_slope",
        ),
        AnnotationGuide(
            kind="text",
            target="material_label",
            anchor="component_center",
            preference_key="shoulder_material_label",
        ),
    ],
)

DEFAULT_GUIDE_REGISTRY.register(
    "Sidewalk",
    [
        AnnotationGuide(
            kind="dimension",
            target="width",
            anchor="component_edges",
            preference_key="sidewalk_width",
        ),
        AnnotationGuide(
            kind="symbol",
            target="cross_slope",
            anchor="component_top_center",
            preference_key="sidewalk_cross_slope",
        ),
    ],
)

DEFAULT_GUIDE_REGISTRY.register(
    "Buffer",
    [
        AnnotationGuide(
            kind="dimension",
            target="width",
            anchor="component_edges",
            preference_key="buffer_width",
        ),
        AnnotationGuide(
            kind="symbol",
            target="cross_slope",
            anchor="component_top_center",
            preference_key="buffer_cross_slope",
        ),
    ],
)
