"""Tests for Curb component."""

import pytest

from cross_section.core.domain.components.curbs import Curb
from cross_section.core.domain.pavement import ConcreteLayer
from cross_section.core.domain.section import ControlPoint
from cross_section.core.geometry.primitives import Segment2D


class TestCurb:
    """Tests for Curb component."""

    def test_create_curb_defaults(self):
        """Test creating a curb with minimal parameters."""
        curb = Curb(gutter_width=0.6)
        assert curb.gutter_width == 0.6
        assert curb.gutter_thickness == 0.15
        assert curb.gutter_drop == 0.025
        assert curb.curb_height == 0.15
        assert curb.curb_width_bottom == 0.15
        assert curb.curb_width_top == 0.15
        assert curb.concrete is not None

    def test_create_curb_custom(self):
        """Test creating a curb with custom parameters."""
        concrete = ConcreteLayer(
            thickness=0.20,
            compressive_strength=35.0,
            reinforced=True,
            steel_per_cy=40.0,
        )
        curb = Curb(
            gutter_width=0.8,
            gutter_thickness=0.20,
            gutter_drop=0.03,
            curb_height=0.20,
            curb_width_bottom=0.20,
            curb_width_top=0.15,
            concrete=concrete,
        )
        assert curb.gutter_width == 0.8
        assert curb.gutter_thickness == 0.20
        assert curb.gutter_drop == 0.03
        assert curb.curb_height == 0.20
        assert curb.curb_width_bottom == 0.20
        assert curb.curb_width_top == 0.15
        assert curb.concrete == concrete

    def test_post_init_creates_default_concrete(self):
        """Test that __post_init__ creates default concrete if none provided."""
        curb = Curb(gutter_width=0.6)
        assert curb.concrete is not None
        assert isinstance(curb.concrete, ConcreteLayer)
        assert curb.concrete.thickness == 0.15
        assert curb.concrete.compressive_strength == 28.0
        assert curb.concrete.reinforced is False

    def test_insertion_point_right(self):
        """Test that curb snaps to previous attachment point (right side)."""
        curb = Curb(gutter_width=0.6)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = curb.get_insertion_point(cp, 'right')
        assert insertion.x == 0.0
        assert insertion.y == 100.0

    def test_insertion_point_left(self):
        """Test that curb snaps to previous attachment point (left side)."""
        curb = Curb(gutter_width=0.6)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = curb.get_insertion_point(cp, 'left')
        assert insertion.x == 0.0
        assert insertion.y == 100.0

    def test_attachment_point_right(self):
        """Test attachment point calculation for right side."""
        curb = Curb(
            gutter_width=0.6,
            gutter_drop=0.025,
            curb_width_bottom=0.15,
        )
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = curb.get_insertion_point(cp, 'right')
        attachment = curb.get_attachment_point(insertion, 'right')

        # Attachment is at back of curb (gutter_width + curb_width_bottom)
        expected_x = 0.0 + 0.6 + 0.15
        # Attachment Y is at insertion Y minus gutter drop
        expected_y = 100.0 - 0.025
        assert attachment.x == pytest.approx(expected_x)
        assert attachment.y == pytest.approx(expected_y)

    def test_attachment_point_left(self):
        """Test attachment point calculation for left side."""
        curb = Curb(
            gutter_width=0.6,
            gutter_drop=0.025,
            curb_width_bottom=0.15,
        )
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        insertion = curb.get_insertion_point(cp, 'left')
        attachment = curb.get_attachment_point(insertion, 'left')

        # Attachment is at back of curb (negative for left)
        expected_x = 0.0 - 0.6 - 0.15
        expected_y = 100.0 - 0.025
        assert attachment.x == pytest.approx(expected_x)
        assert attachment.y == pytest.approx(expected_y)

    def test_to_geometry_right(self):
        """Test geometry creation for right side curb."""
        curb = Curb(
            gutter_width=0.6,
            gutter_thickness=0.15,
            gutter_drop=0.025,
            curb_height=0.15,
            curb_width_bottom=0.15,
            curb_width_top=0.15,
        )
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        geometry = curb.to_geometry(cp, 'right')

        # Should have one polygon (curb and gutter combined)
        assert len(geometry.polygons) == 1
        assert len(geometry.polylines) == 0

        # Polygon should have 7 vertices
        polygon = geometry.polygons[0]
        assert len(polygon.exterior) == 7

        # Check metadata
        assert geometry.metadata['component_type'] == 'Curb'
        assert geometry.metadata['gutter_width'] == 0.6
        assert geometry.metadata['curb_height'] == 0.15
        assert geometry.metadata['assembly_direction'] == 'right'
        back_face = Segment2D(polygon.exterior[3], polygon.exterior[4])
        curb_top = Segment2D(polygon.exterior[2], polygon.exterior[3])
        assert back_face.is_perpendicular_to(curb_top)

    def test_to_geometry_left(self):
        """Test geometry creation for left side curb."""
        curb = Curb(
            gutter_width=0.6,
            gutter_thickness=0.15,
            gutter_drop=0.025,
            curb_height=0.15,
            curb_width_bottom=0.15,
            curb_width_top=0.15,
        )
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        geometry = curb.to_geometry(cp, 'left')

        # Should have one polygon
        assert len(geometry.polygons) == 1
        polygon = geometry.polygons[0]
        assert len(polygon.exterior) == 7

        # Check that vertices are on left side (negative X)
        for point in polygon.exterior:
            assert point.x <= 0.0

        assert geometry.metadata['assembly_direction'] == 'left'

    def test_battered_face_geometry(self):
        """Test curb with battered face (top narrower than bottom)."""
        curb = Curb(
            gutter_width=0.6,
            curb_width_bottom=0.20,
            curb_width_top=0.15,  # Narrower top = battered face
            curb_height=0.15,
        )
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        geometry = curb.to_geometry(cp, 'right')
        polygon = geometry.polygons[0]

        # With a battered face, the profile should be wider at bottom than top
        assert curb.curb_width_top < curb.curb_width_bottom
        assert len(polygon.exterior) == 7

    def test_gutter_only_no_curb(self):
        """Test curb with only gutter (zero curb height)."""
        curb = Curb(
            gutter_width=0.6,
            curb_height=0.0,
            curb_width_bottom=0.0,
            curb_width_top=0.0,
        )
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        geometry = curb.to_geometry(cp, 'right')
        # Should still create valid geometry
        assert len(geometry.polygons) == 1

    def test_validate_valid_curb(self):
        """Test validation passes for valid curb."""
        curb = Curb(
            gutter_width=0.6,
            gutter_thickness=0.15,
            gutter_drop=0.025,
            curb_height=0.15,
            curb_width_bottom=0.15,
            curb_width_top=0.15,
        )
        errors = curb.validate()
        assert errors == []

    def test_validate_negative_gutter_width(self):
        """Test validation catches negative gutter width."""
        curb = Curb(gutter_width=-0.1)
        errors = curb.validate()
        assert any('gutter width' in error.lower() and 'negative' in error.lower() for error in errors)

    def test_validate_excessive_gutter_width(self):
        """Test validation warns about excessive gutter width."""
        curb = Curb(gutter_width=1.5)
        errors = curb.validate()
        assert any('gutter width' in error.lower() and 'exceeds' in error.lower() for error in errors)

    def test_validate_thin_gutter(self):
        """Test validation warns about thin gutter."""
        curb = Curb(gutter_width=0.6, gutter_thickness=0.05)
        errors = curb.validate()
        assert any('gutter thickness' in error.lower() and 'minimum' in error.lower() for error in errors)

    def test_validate_excessive_gutter_drop(self):
        """Test validation warns about excessive gutter drop."""
        curb = Curb(gutter_width=0.6, gutter_drop=0.15)
        errors = curb.validate()
        assert any('gutter drop' in error.lower() and 'exceeds' in error.lower() for error in errors)

    def test_validate_negative_curb_height(self):
        """Test validation catches negative curb height."""
        curb = Curb(gutter_width=0.6, curb_height=-0.1)
        errors = curb.validate()
        assert any('curb height' in error.lower() and 'negative' in error.lower() for error in errors)

    def test_validate_excessive_curb_height(self):
        """Test validation warns about excessive curb height."""
        curb = Curb(gutter_width=0.6, curb_height=0.40)
        errors = curb.validate()
        assert any('curb height' in error.lower() and 'exceeds' in error.lower() for error in errors)

    def test_validate_top_wider_than_bottom(self):
        """Test validation catches curb top wider than bottom (overhang)."""
        curb = Curb(
            gutter_width=0.6,
            curb_width_bottom=0.15,
            curb_width_top=0.20,  # Wider top = overhang
        )
        errors = curb.validate()
        assert any('top width' in error.lower() and 'exceeds' in error.lower() for error in errors)

    def test_validate_concrete_errors_propagated(self):
        """Test that concrete validation errors are propagated."""
        concrete = ConcreteLayer(
            thickness=0.15,
            compressive_strength=-10.0,  # Invalid
            reinforced=False,
        )
        curb = Curb(gutter_width=0.6, concrete=concrete)
        errors = curb.validate()
        assert any('concrete' in error.lower() for error in errors)

    def test_geometry_metadata_includes_layers(self):
        """Test that geometry metadata includes layer information."""
        curb = Curb(gutter_width=0.6)
        cp = ControlPoint(x=0.0, elevation=100.0).to_connection_point()

        geometry = curb.to_geometry(cp, 'right')

        assert 'layers' in geometry.metadata
        assert len(geometry.metadata['layers']) == 1
        layer = geometry.metadata['layers'][0]
        assert layer['type'] == 'ConcreteLayer'
        assert layer['thickness'] == 0.15
        assert layer['compressive_strength'] == 28.0
