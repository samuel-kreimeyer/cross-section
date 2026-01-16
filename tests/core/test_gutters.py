"""Tests for Gutter component."""

import pytest

from cross_section.core.domain import ControlPoint
from cross_section.core.domain.components.gutters import Gutter


def test_gutter_geometry_right():
    gutter = Gutter(width=0.6, drop=0.03, thickness=0.15)
    cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

    geometry = gutter.to_geometry(cp, "right")

    assert len(geometry.polygons) == 1
    assert geometry.metadata["component_type"] == "Gutter"


def test_gutter_attachment_left():
    gutter = Gutter(width=0.6, drop=0.03, thickness=0.15)
    cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

    insertion = gutter.get_insertion_point(cp, "left")
    attachment = gutter.get_attachment_point(insertion, "left")

    assert attachment.x == pytest.approx(-0.6)
    assert attachment.y == pytest.approx(99.97)
