"""Unit tests for rehabilitation components.

Tests ExistingPavement, MillAndOverlay, and NotchAndWidening components
for correct geometry generation and attachment point connectivity.
"""

import pytest

from cross_section.core.domain.components.rehabilitation import (
    ExistingPavement,
    MillAndOverlay,
    NotchAndWidening,
)
from cross_section.core.domain.pavement import AsphaltLayer, CrushedRockLayer
from cross_section.core.geometry.primitives import ConnectionPoint


class TestExistingPavement:
    """Tests for ExistingPavement component."""

    def test_insertion_point_matches_previous_attachment(self):
        """Insertion point should match the previous attachment (control point)."""
        component = ExistingPavement(
            half_width=3.0,
            total_depth=0.3,
            cross_slope=0.02,
        )
        previous = ConnectionPoint(x=0.0, y=100.0, description="control")
        insertion = component.get_insertion_point(previous, "right")

        assert insertion.x == previous.x
        assert insertion.y == previous.y

    def test_attachment_point_at_edge_right(self):
        """Right-side attachment should be at positive X edge."""
        component = ExistingPavement(
            half_width=3.0,
            total_depth=0.3,
            cross_slope=0.02,
        )
        insertion = ConnectionPoint(x=0.0, y=100.0, description="insertion")
        attachment = component.get_attachment_point(insertion, "right")

        assert attachment.x == 3.0  # half_width
        assert attachment.y == pytest.approx(100.0 - 3.0 * 0.02)  # surface drop

    def test_attachment_point_at_edge_left(self):
        """Left-side attachment should be at negative X edge."""
        component = ExistingPavement(
            half_width=3.0,
            total_depth=0.3,
            cross_slope=0.02,
        )
        insertion = ConnectionPoint(x=0.0, y=100.0, description="insertion")
        attachment = component.get_attachment_point(insertion, "left")

        assert attachment.x == -3.0  # -half_width
        assert attachment.y == pytest.approx(100.0 - 3.0 * 0.02)  # surface drop

    def test_geometry_has_single_polygon(self):
        """Should generate a single polygon for existing pavement."""
        component = ExistingPavement(
            half_width=3.0,
            total_depth=0.3,
            cross_slope=0.02,
        )
        insertion = ConnectionPoint(x=0.0, y=100.0, description="insertion")
        geometry = component.to_geometry(insertion, "right")

        assert len(geometry.polygons) == 1
        assert geometry.metadata["component_type"] == "ExistingPavement"
        assert geometry.metadata["half_width"] == 3.0
        assert geometry.metadata["total_depth"] == 0.3

    def test_geometry_bounds_correct(self):
        """Geometry bounds should match half_width and total_depth."""
        component = ExistingPavement(
            half_width=3.0,
            total_depth=0.3,
            cross_slope=0.02,
        )
        insertion = ConnectionPoint(x=0.0, y=100.0, description="insertion")
        geometry = component.to_geometry(insertion, "right")
        bounds = geometry.bounds()

        assert bounds[0] == pytest.approx(0.0)  # min_x at centerline
        assert bounds[2] == pytest.approx(3.0)  # max_x at edge
        # Y range includes cross slope and depth
        assert bounds[3] == pytest.approx(100.0)  # max_y at crown

    def test_validation_catches_invalid_parameters(self):
        """Should catch invalid parameters."""
        component = ExistingPavement(
            half_width=-1.0,  # Invalid
            total_depth=0.05,  # Below minimum warning
            cross_slope=0.10,  # Exceeds maximum
        )
        errors = component.validate()

        assert len(errors) >= 2
        assert any("Half width must be positive" in e for e in errors)
        assert any("exceeds typical maximum" in e for e in errors)


class TestMillAndOverlay:
    """Tests for MillAndOverlay component."""

    @pytest.fixture
    def overlay_layers(self):
        """Standard overlay layer stack."""
        return [
            AsphaltLayer(
                thickness=0.05,
                aggregate_size=12.5,
                binder_type="PG 64-22",
                binder_percentage=5.5,
                density=2400,
            )
        ]

    def test_insertion_point_matches_previous_attachment(self, overlay_layers):
        """Insertion point should match the previous attachment."""
        component = MillAndOverlay(
            width=3.0,
            mill_depth=0.0,
            overlay_layers=overlay_layers,
            cross_slope=0.02,
        )
        previous = ConnectionPoint(x=3.0, y=99.94, description="existing edge")
        insertion = component.get_insertion_point(previous, "right")

        assert insertion.x == previous.x
        assert insertion.y == previous.y

    def test_attachment_point_elevates_by_overlay_thickness(self, overlay_layers):
        """Attachment should be elevated by net overlay thickness."""
        component = MillAndOverlay(
            width=3.0,
            mill_depth=0.0,
            overlay_layers=overlay_layers,  # 0.05m thick
            cross_slope=0.02,
        )
        insertion = ConnectionPoint(x=3.0, y=99.94, description="existing edge")
        attachment = component.get_attachment_point(insertion, "right")

        # X stays the same (at existing pavement edge)
        assert attachment.x == insertion.x
        # Y elevates by overlay thickness
        assert attachment.y == pytest.approx(99.94 + 0.05)

    def test_attachment_accounts_for_milling(self, overlay_layers):
        """Net elevation should account for milling removal."""
        component = MillAndOverlay(
            width=3.0,
            mill_depth=0.025,  # Mill 25mm
            overlay_layers=overlay_layers,  # 50mm overlay
            cross_slope=0.02,
        )
        insertion = ConnectionPoint(x=3.0, y=99.94, description="existing edge")
        attachment = component.get_attachment_point(insertion, "right")

        # Net elevation: +0.05 overlay - 0.025 milling = +0.025
        assert attachment.y == pytest.approx(99.94 + 0.025)

    def test_geometry_generates_overlay_polygon(self, overlay_layers):
        """Should generate polygon(s) for overlay layers."""
        component = MillAndOverlay(
            width=3.0,
            mill_depth=0.0,
            overlay_layers=overlay_layers,
            cross_slope=0.02,
        )
        insertion = ConnectionPoint(x=3.0, y=99.94, description="existing edge")
        geometry = component.to_geometry(insertion, "right")

        assert len(geometry.polygons) == 1  # One overlay layer
        assert geometry.metadata["component_type"] == "MillAndOverlay"
        assert geometry.metadata["overlay_thickness"] == 0.05

    def test_geometry_with_leveling_course(self, overlay_layers):
        """Should generate separate polygon for leveling course."""
        component = MillAndOverlay(
            width=3.0,
            mill_depth=0.0,
            overlay_layers=overlay_layers,
            leveling_thickness=0.02,  # 20mm leveling
            cross_slope=0.02,
        )
        insertion = ConnectionPoint(x=3.0, y=99.94, description="existing edge")
        geometry = component.to_geometry(insertion, "right")

        assert len(geometry.polygons) == 2  # Leveling + overlay
        assert geometry.metadata["leveling_thickness"] == 0.02

    def test_validation_catches_invalid_parameters(self):
        """Should catch invalid parameters."""
        component = MillAndOverlay(
            width=-1.0,  # Invalid
            mill_depth=0.2,  # Exceeds typical
            overlay_layers=[],  # No layers and no milling
            cross_slope=0.02,
        )
        errors = component.validate()

        assert len(errors) >= 2
        assert any("Width must be positive" in e for e in errors)


class TestNotchAndWidening:
    """Tests for NotchAndWidening component."""

    @pytest.fixture
    def widening_layers(self):
        """Standard widening layer stack."""
        return [
            AsphaltLayer(
                thickness=0.10,  # 4" total surface
                aggregate_size=12.5,
                binder_type="PG 64-22",
                binder_percentage=5.5,
                density=2400,
            ),
            AsphaltLayer(
                thickness=0.075,  # 3" binder
                aggregate_size=19.0,
                binder_type="PG 64-22",
                binder_percentage=4.5,
                density=2350,
            ),
            CrushedRockLayer(
                thickness=0.15,  # 6" base
                aggregate_size=37.5,
                density=2200,
                material_type="crushed_stone",
            ),
        ]

    def test_insertion_point_matches_previous_attachment(self, widening_layers):
        """Insertion point should match the previous attachment."""
        component = NotchAndWidening(
            notch_depth=0.28,
            notch_horizontal=0.28,
            widening_width=0.3,
            widening_layers=widening_layers,
            cross_slope=0.04,
        )
        previous = ConnectionPoint(x=3.0, y=99.99, description="overlay edge")
        insertion = component.get_insertion_point(previous, "right")

        assert insertion.x == previous.x
        assert insertion.y == previous.y

    def test_attachment_point_at_widening_edge_right(self, widening_layers):
        """Right-side attachment should be at outer edge of widening."""
        component = NotchAndWidening(
            notch_depth=0.28,
            notch_horizontal=0.28,
            widening_width=0.3,
            widening_layers=widening_layers,
            cross_slope=0.04,
        )
        insertion = ConnectionPoint(x=3.0, y=99.99, description="overlay edge")
        attachment = component.get_attachment_point(insertion, "right")

        total_width = 0.28 + 0.3  # notch + widening
        expected_x = 3.0 + total_width
        expected_y = 99.99 - total_width * 0.04  # surface drop

        assert attachment.x == pytest.approx(expected_x)
        assert attachment.y == pytest.approx(expected_y)

    def test_attachment_point_at_widening_edge_left(self, widening_layers):
        """Left-side attachment should be at outer edge of widening."""
        component = NotchAndWidening(
            notch_depth=0.28,
            notch_horizontal=0.28,
            widening_width=0.3,
            widening_layers=widening_layers,
            cross_slope=0.04,
        )
        insertion = ConnectionPoint(x=-3.0, y=99.99, description="overlay edge")
        attachment = component.get_attachment_point(insertion, "left")

        total_width = 0.28 + 0.3  # notch + widening
        expected_x = -3.0 - total_width
        expected_y = 99.99 - total_width * 0.04  # surface drop

        assert attachment.x == pytest.approx(expected_x)
        assert attachment.y == pytest.approx(expected_y)

    def test_geometry_generates_layer_polygons(self, widening_layers):
        """Should generate one polygon per widening layer."""
        component = NotchAndWidening(
            notch_depth=0.28,
            notch_horizontal=0.28,
            widening_width=0.3,
            widening_layers=widening_layers,
            cross_slope=0.04,
        )
        insertion = ConnectionPoint(x=3.0, y=99.99, description="overlay edge")
        geometry = component.to_geometry(insertion, "right")

        assert len(geometry.polygons) == 3  # Three widening layers
        assert geometry.metadata["component_type"] == "NotchAndWidening"
        assert geometry.metadata["total_width"] == pytest.approx(0.58)

    def test_geometry_has_six_vertices_per_polygon(self, widening_layers):
        """Each layer polygon should have 6 vertices (notch + widening shape)."""
        component = NotchAndWidening(
            notch_depth=0.28,
            notch_horizontal=0.28,
            widening_width=0.3,
            widening_layers=widening_layers,
            cross_slope=0.04,
        )
        insertion = ConnectionPoint(x=3.0, y=99.99, description="overlay edge")
        geometry = component.to_geometry(insertion, "right")

        for polygon in geometry.polygons:
            assert len(polygon.exterior) == 6

    def test_validation_catches_invalid_parameters(self):
        """Should catch invalid parameters."""
        component = NotchAndWidening(
            notch_depth=0.3,
            notch_horizontal=-0.1,  # Invalid
            widening_width=0.0,  # Invalid
            widening_layers=[],  # No layers
            cross_slope=0.04,
        )
        errors = component.validate()

        assert len(errors) >= 3
        assert any("Notch horizontal extent must be positive" in e for e in errors)
        assert any("Widening width must be positive" in e for e in errors)
        assert any("at least one pavement layer" in e for e in errors)

    def test_validation_warns_when_layers_thinner_than_notch(self, widening_layers):
        """Should warn if total layer depth is less than notch depth."""
        # Total layer depth is 0.325m (0.1 + 0.075 + 0.15)
        component = NotchAndWidening(
            notch_depth=0.5,  # Deeper than layers
            notch_horizontal=0.28,
            widening_width=0.3,
            widening_layers=widening_layers,
            cross_slope=0.04,
        )
        errors = component.validate()

        assert any("should match or exceed notch depth" in e for e in errors)


class TestRehabilitationChaining:
    """Tests for chaining rehabilitation components together."""

    @pytest.fixture
    def overlay_layers(self):
        """Standard overlay layer stack."""
        return [
            AsphaltLayer(
                thickness=0.05,
                aggregate_size=12.5,
                binder_type="PG 64-22",
                binder_percentage=5.5,
                density=2400,
            )
        ]

    @pytest.fixture
    def widening_layers(self):
        """Standard widening layer stack."""
        return [
            AsphaltLayer(
                thickness=0.10,
                aggregate_size=12.5,
                binder_type="PG 64-22",
                binder_percentage=5.5,
                density=2400,
            ),
            AsphaltLayer(
                thickness=0.075,
                aggregate_size=19.0,
                binder_type="PG 64-22",
                binder_percentage=4.5,
                density=2350,
            ),
            CrushedRockLayer(
                thickness=0.15,
                aggregate_size=37.5,
                density=2200,
                material_type="crushed_stone",
            ),
        ]

    def test_components_chain_correctly(self, overlay_layers, widening_layers):
        """Components should chain together with zero gap."""
        # Start from control point
        control = ConnectionPoint(x=0.0, y=100.0, description="control")

        # ExistingPavement
        existing = ExistingPavement(
            half_width=3.0,
            total_depth=0.3,
            cross_slope=0.02,
        )
        existing_insertion = existing.get_insertion_point(control, "right")
        existing_attachment = existing.get_attachment_point(existing_insertion, "right")

        # MillAndOverlay chains from ExistingPavement
        overlay = MillAndOverlay(
            width=3.0,
            mill_depth=0.0,
            overlay_layers=overlay_layers,
            cross_slope=0.02,
        )
        overlay_insertion = overlay.get_insertion_point(existing_attachment, "right")
        overlay_attachment = overlay.get_attachment_point(overlay_insertion, "right")

        # Verify overlay insertion matches existing attachment
        assert overlay_insertion.x == existing_attachment.x
        assert overlay_insertion.y == existing_attachment.y

        # NotchAndWidening chains from MillAndOverlay
        notch = NotchAndWidening(
            notch_depth=0.28,
            notch_horizontal=0.28,
            widening_width=0.3,
            widening_layers=widening_layers,
            cross_slope=0.04,
        )
        notch_insertion = notch.get_insertion_point(overlay_attachment, "right")
        notch_attachment = notch.get_attachment_point(notch_insertion, "right")

        # Verify notch insertion matches overlay attachment
        assert notch_insertion.x == overlay_attachment.x
        assert notch_insertion.y == overlay_attachment.y

        # Verify the chain progresses outward
        assert existing_attachment.x > control.x  # Existing extends right
        assert overlay_attachment.x == existing_attachment.x  # Overlay at same X, elevated
        assert overlay_attachment.y > existing_attachment.y  # Overlay is elevated
        assert notch_attachment.x > overlay_attachment.x  # Notch extends further right
