"""Annotation profiles for agency-specific preferences."""

from dataclasses import dataclass, field, replace
from typing import Literal

from .guides import AnnotationGuide, AnnotationKind


MaterialLabelMode = Literal["none", "note", "dimension_suffix"]
TrafficArrowMode = Literal["assembly", "traffic_direction"]


@dataclass(frozen=True)
class AnnotationGuideOverride:
    """Override for a specific annotation guide preference key."""

    enabled: bool | None = None
    kind: AnnotationKind | None = None
    target: str | None = None
    anchor: str | None = None


@dataclass(frozen=True)
class AnnotationProfile:
    """Preferences controlling which guides render and how."""

    include_component_labels: bool = True
    include_width_dimensions: bool = True
    include_material_labels: bool = False
    include_travel_direction: bool = False
    include_cross_slope: bool = False
    include_cross_slope_text: bool = False
    include_centerpoint_mark: bool = False
    require_crown_dimension: bool = True
    use_keyed_notes: bool = False
    material_label_mode: MaterialLabelMode = "note"
    traffic_arrow_mode: TrafficArrowMode = "assembly"
    symbol_library: str = "aashto"
    text_size: float = 0.15
    dimension_offset: float = 0.5
    slope_symbol_scale: float = 0.8
    slope_symbol_offset: float = 0.65
    slope_text_offset: float = 0.80
    slope_text_size: float = 0.10
    guide_overrides: dict[str, AnnotationGuideOverride] = field(default_factory=dict)

    def apply_override(self, guide: AnnotationGuide) -> AnnotationGuide | None:
        """Apply guide-level overrides and profile filters."""
        if guide.preference_key and guide.preference_key in self.guide_overrides:
            override = self.guide_overrides[guide.preference_key]
            if override.enabled is False and not guide.required:
                return None
            return replace(
                guide,
                kind=override.kind or guide.kind,
                target=override.target or guide.target,
                anchor=override.anchor or guide.anchor,
            )

        if guide.kind == "dimension" and guide.target == "width":
            if not self.include_width_dimensions and not guide.required:
                return None
        elif guide.kind == "symbol" and guide.target == "travel_direction":
            if not self.include_travel_direction and not guide.required:
                return None
        elif guide.kind == "symbol" and guide.target == "cross_slope":
            if not self.include_cross_slope and not guide.required:
                return None
        elif guide.kind == "text" and guide.target == "material_label":
            if not self.include_material_labels and not guide.required:
                return None

        return guide
