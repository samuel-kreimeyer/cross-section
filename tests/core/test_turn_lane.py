"""Tests for TurnLane component."""

import pytest

from cross_section.core.domain import ControlPoint
from cross_section.core.domain.components.lanes import TurnLane


def test_turn_lane_metadata():
    lane = TurnLane(width=3.0, cross_slope=0.02)
    cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

    geometry = lane.to_geometry(cp, "right")

    assert geometry.metadata["component_type"] == "TurnLane"
    assert geometry.metadata["lane_type"] == "turn"


def test_turn_lane_split():
    lane = TurnLane(width=3.2, cross_slope=0.02)
    left, right = lane.split()

    assert left.width == pytest.approx(1.6)
    assert right.width == pytest.approx(1.6)
    assert left.segment == "left"
    assert right.segment == "right"
