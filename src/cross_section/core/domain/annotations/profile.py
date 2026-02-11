"""Annotation profiles for agency-specific preferences."""

from dataclasses import dataclass, field, replace
from typing import Literal

from .guides import AnnotationGuide, AnnotationKind


MaterialLabelMode = Literal["none", "note", "dimension_suffix"]
TrafficArrowMode = Literal["assembly", "traffic_direction"]
UnitSystem = Literal["metric", "imperial"]


def format_dimension(value_meters: float, unit_system: UnitSystem) -> str:
    """Format a dimension value according to the unit system.

    Args:
        value_meters: Dimension value in meters
        unit_system: Unit system to use for formatting

    Returns:
        Formatted dimension string with units
    """
    if unit_system == "imperial":
        # Convert meters to feet
        value_ft = value_meters / 0.3048
        if value_ft >= 1.0:
            # Format as feet with optional inches
            feet = int(value_ft)
            inches = (value_ft - feet) * 12
            if inches < 0.5:
                return f"{feet}'"
            elif abs(inches - round(inches)) < 0.1:
                return f"{feet}'-{int(round(inches))}\""
            else:
                return f"{feet}'-{inches:.1f}\""
        else:
            # Format as inches only
            inches = value_ft * 12
            if abs(inches - round(inches)) < 0.1:
                return f"{int(round(inches))}\""
            else:
                return f"{inches:.1f}\""
    else:
        # Metric: format as meters
        if value_meters >= 1.0:
            return f"{value_meters:.2f}m"
        else:
            # Format as millimeters for small values
            mm = value_meters * 1000
            return f"{mm:.0f}mm"


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
    include_layer_callouts: bool = False
    require_crown_dimension: bool = True
    use_keyed_notes: bool = False
    material_label_mode: MaterialLabelMode = "note"
    traffic_arrow_mode: TrafficArrowMode = "assembly"
    symbol_library: str = "aashto"
    unit_system: UnitSystem = "imperial"
    text_size: float = 0.15
    dimension_offset: float = 1.70
    slope_symbol_scale: float = 0.8
    slope_symbol_offset: float = 0.45
    slope_text_offset: float = 0.15
    slope_text_size: float = 0.10
    traffic_symbol_offset: float = 0.85
    leader_text_size: float = 0.12
    leader_offset_x: float = 0.5
    leader_offset_y: float = -0.5
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


DEFAULT_FULL_PROFILE = AnnotationProfile(
    include_component_labels=True,
    include_width_dimensions=True,
    include_material_labels=True,
    include_travel_direction=True,
    include_cross_slope=True,
    include_cross_slope_text=True,
    include_layer_callouts=True,
    include_centerpoint_mark=False,
    require_crown_dimension=True,
    use_keyed_notes=False,
    unit_system="imperial",
)
