"""Tests for surface-only components."""

import pytest

from cross_section.core.domain import Buffer, ControlPoint, SurfaceProfile


def test_surface_profile_right():
    profile = SurfaceProfile(segments=[(2.0, 0.1), (1.0, 0.0)], surface_type="grass")
    cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

    geometry = profile.to_geometry(cp, "right")

    assert geometry.polygons == []
    assert len(geometry.polylines) == 1
    line = geometry.polylines[0]
    assert line[-1].x == pytest.approx(3.0)
    assert line[-1].y == pytest.approx(99.9)
    assert geometry.metadata["component_type"] == "SurfaceProfile"


def test_buffer_attachment():
    buffer = Buffer(width=3.0, cross_slope=0.02)
    cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

    insertion = buffer.get_insertion_point(cp, "right")
    attachment = buffer.get_attachment_point(insertion, "right")

    assert attachment.x == pytest.approx(3.0)
    assert attachment.y == pytest.approx(99.94)
