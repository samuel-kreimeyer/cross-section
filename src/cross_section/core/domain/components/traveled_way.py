"""Traveled way definitions (lane grouping helpers)."""

from dataclasses import dataclass, field
from typing import Literal

from ..base import RoadComponent
from ..pavement import PavementLayer
from .lanes import TurnLane, TravelLane

LaneType = Literal["travel", "turn"]


@dataclass(frozen=True)
class LaneSpec:
    """Definition for a lane within a traveled way."""

    width: float
    lane_type: LaneType = "travel"
    traffic_direction: Literal["inbound", "outbound", "center"] = "outbound"
    pavement_layers: list[PavementLayer] | None = None


@dataclass
class TraveledWay:
    """Helper container for a group of adjacent lanes on one side of a section."""

    lane_specs: list[LaneSpec]
    cross_slope: float = 0.02
    pavement_layers: list[PavementLayer] = field(default_factory=list)

    def build_components(self) -> list[RoadComponent]:
        """Create lane components from the lane specs."""
        components: list[RoadComponent] = []
        for spec in self.lane_specs:
            layers = spec.pavement_layers or self.pavement_layers
            if spec.lane_type == "turn":
                components.append(
                    TurnLane(
                        width=spec.width,
                        cross_slope=self.cross_slope,
                        traffic_direction=spec.traffic_direction,
                        pavement_layers=[layer for layer in layers],
                    )
                )
            else:
                components.append(
                    TravelLane(
                        width=spec.width,
                        cross_slope=self.cross_slope,
                        traffic_direction=spec.traffic_direction,
                        pavement_layers=[layer for layer in layers],
                    )
                )
        return components
