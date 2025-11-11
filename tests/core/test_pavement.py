"""Tests for pavement layer classes."""

import pytest
from cross_section.core.domain.pavement import AsphaltLayer, ConcreteLayer, CrushedRockLayer


class TestAsphaltLayer:
    """Tests for AsphaltLayer."""

    def test_create_asphalt_layer(self):
        """Test creating an asphalt layer."""
        layer = AsphaltLayer(
            thickness=0.05,
            aggregate_size=12.5,
            binder_type='PG 64-22',
            binder_percentage=5.5,
            density=2400
        )
        assert layer.thickness == 0.05
        assert layer.aggregate_size == 12.5
        assert layer.binder_type == 'PG 64-22'
        assert layer.binder_percentage == 5.5
        assert layer.density == 2400

    def test_validate_valid_asphalt(self):
        """Test validation of valid asphalt layer."""
        layer = AsphaltLayer(
            thickness=0.05,
            aggregate_size=12.5,
            binder_type='PG 64-22',
            binder_percentage=5.5,
            density=2400
        )
        errors = layer.validate()
        assert errors == []

    def test_validate_negative_thickness(self):
        """Test validation catches negative thickness."""
        layer = AsphaltLayer(
            thickness=-0.05,
            aggregate_size=12.5,
            binder_type='PG 64-22',
            binder_percentage=5.5,
            density=2400
        )
        errors = layer.validate()
        assert len(errors) > 0
        assert any('positive' in error.lower() for error in errors)

    def test_validate_thin_layer(self):
        """Test validation warns about thin layers."""
        layer = AsphaltLayer(
            thickness=0.03,  # 30mm, below typical minimum
            aggregate_size=12.5,
            binder_type='PG 64-22',
            binder_percentage=5.5,
            density=2400
        )
        errors = layer.validate()
        assert len(errors) > 0
        assert any('thin' in error.lower() for error in errors)


class TestConcreteLayer:
    """Tests for ConcreteLayer."""

    def test_create_concrete_layer(self):
        """Test creating a concrete layer."""
        layer = ConcreteLayer(
            thickness=0.25,
            compressive_strength=35.0,
            reinforced=True,
            steel_per_cy=40.0
        )
        assert layer.thickness == 0.25
        assert layer.compressive_strength == 35.0
        assert layer.reinforced is True
        assert layer.steel_per_cy == 40.0

    def test_validate_valid_concrete(self):
        """Test validation of valid concrete layer."""
        layer = ConcreteLayer(
            thickness=0.25,
            compressive_strength=35.0,
            reinforced=False
        )
        errors = layer.validate()
        assert errors == []

    def test_validate_reinforced_without_steel(self):
        """Test validation catches reinforced concrete without steel specification."""
        layer = ConcreteLayer(
            thickness=0.25,
            compressive_strength=35.0,
            reinforced=True
            # Missing steel_per_cy
        )
        errors = layer.validate()
        assert len(errors) > 0
        assert any('steel_per_cy' in error.lower() for error in errors)

    def test_validate_unreinforced_with_steel(self):
        """Test validation catches unreinforced concrete with steel specification."""
        layer = ConcreteLayer(
            thickness=0.25,
            compressive_strength=35.0,
            reinforced=False,
            steel_per_cy=40.0  # Should not be specified
        )
        errors = layer.validate()
        assert len(errors) > 0
        assert any('steel_per_cy' in error.lower() for error in errors)


class TestCrushedRockLayer:
    """Tests for CrushedRockLayer."""

    def test_create_crushed_rock_layer(self):
        """Test creating a crushed rock layer."""
        layer = CrushedRockLayer(
            thickness=0.20,
            aggregate_size=37.5,
            density=2200,
            material_type='crushed_stone'
        )
        assert layer.thickness == 0.20
        assert layer.aggregate_size == 37.5
        assert layer.density == 2200
        assert layer.material_type == 'crushed_stone'

    def test_validate_valid_crushed_rock(self):
        """Test validation of valid crushed rock layer."""
        layer = CrushedRockLayer(
            thickness=0.20,
            aggregate_size=37.5,
            density=2200
        )
        errors = layer.validate()
        assert errors == []

    def test_validate_thin_base(self):
        """Test validation warns about thin base course."""
        layer = CrushedRockLayer(
            thickness=0.08,  # 80mm, below typical minimum
            aggregate_size=37.5,
            density=2200
        )
        errors = layer.validate()
        assert len(errors) > 0
        assert any('minimum' in error.lower() for error in errors)
