"""Tests for Sidewalk component."""

import pytest

from cross_section.core.domain import ControlPoint, Sidewalk


def test_sidewalk_geometry_left():
    sidewalk = Sidewalk(width=1.5, cross_slope=0.02, thickness=0.1)
    cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

    geometry = sidewalk.to_geometry(cp, "left")

    assert len(geometry.polygons) == 1
    assert geometry.metadata["component_type"] == "Sidewalk"


def test_sidewalk_attachment_right():
    sidewalk = Sidewalk(width=1.5, cross_slope=0.02, thickness=0.1)
    cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

    insertion = sidewalk.get_insertion_point(cp, "right")
    attachment = sidewalk.get_attachment_point(insertion, "right")

    assert attachment.x == pytest.approx(1.5)
    assert attachment.y == pytest.approx(99.97)
