"""Tests for TraveledWay helpers."""

from cross_section.core.domain.components.lanes import TurnLane, TravelLane
from cross_section.core.domain.components.traveled_way import LaneSpec, TraveledWay
from cross_section.core.domain.pavement import AsphaltLayer


def test_traveled_way_build_components():
    layers = [
        AsphaltLayer(
            thickness=0.05,
            aggregate_size=12.5,
            binder_type="PG 64-22",
            binder_percentage=5.5,
            density=2400,
        )
    ]
    traveled_way = TraveledWay(
        lane_specs=[
            LaneSpec(width=3.0, lane_type="travel", traffic_direction="outbound"),
            LaneSpec(width=3.3, lane_type="turn", traffic_direction="center"),
        ],
        cross_slope=0.02,
        pavement_layers=layers,
    )

    components = traveled_way.build_components()

    assert len(components) == 2
    assert isinstance(components[0], TravelLane)
    assert isinstance(components[1], TurnLane)
