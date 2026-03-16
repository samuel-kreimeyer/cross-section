"""Integration tests for section-level geometric validation."""

import pytest

from cross_section.core.domain import Curb, Shoulder, Slope
from cross_section.core.domain.components import TravelLane as Lane
from cross_section.core.domain.components.barriers import Barrier, JERSEY_32
from cross_section.core.domain import RoadSection
from cross_section.core.domain.pavement import AsphaltLayer, CrushedRockLayer
from cross_section.core.domain.section import ControlPoint


def _thick_asphalt():
    """Helper to create valid thickness asphalt layer (>= 150mm)."""
    return AsphaltLayer(thickness=0.15, aggregate_size=19.0, binder_type='PG 64-22',
                       binder_percentage=5.0, density=2400)


class TestRoadSectionGeometricValidation:
    """Tests for section-level validation with shapely geometry checks."""

    def test_simple_section_validates_successfully(self):
        """Test that a simple valid section passes geometric validation."""
        section = RoadSection(
            name="Test Section",
            control_point=ControlPoint(x=0, elevation=100.0),
            right_components=[
                Lane(width=3.6, pavement_layers=[
                    AsphaltLayer(thickness=0.15, aggregate_size=19.0, binder_type='PG 64-22',
                                binder_percentage=5.0, density=2400),
                ]),
                Shoulder(width=2.4, pavement_layers=[
                    AsphaltLayer(thickness=0.15, aggregate_size=12.5, binder_type='PG 64-22',
                                binder_percentage=5.5, density=2400),
                ]),
                Slope(horizontal_run=4.0, vertical_drop=1.0),
            ],
        )

        errors = section.validate(include_geometry=True)
        assert errors == []

    def test_symmetric_section_validates_successfully(self):
        """Test that a symmetric section passes geometric validation."""
        section = RoadSection(
            name="Test Section",
            control_point=ControlPoint(x=0, elevation=100.0),
            left_components=[
                Lane(width=3.6, pavement_layers=[_thick_asphalt()]),
                Shoulder(width=2.4, pavement_layers=[_thick_asphalt()]),
                Slope(horizontal_run=6.0, vertical_drop=1.0),
            ],
            right_components=[
                Lane(width=3.6, pavement_layers=[_thick_asphalt()]),
                Shoulder(width=2.4, pavement_layers=[_thick_asphalt()]),
                Slope(horizontal_run=6.0, vertical_drop=1.0),
            ],
        )

        errors = section.validate(include_geometry=True)
        assert errors == []

    def test_complex_section_with_barriers_validates(self):
        """Test complex section with barriers passes validation (allows gaps for prepared surfaces)."""
        section = RoadSection(
            name="Test Section",
            control_point=ControlPoint(x=0, elevation=100.0),
            left_components=[
                Lane(width=3.6, pavement_layers=[_thick_asphalt()]),
                Lane(width=3.6, pavement_layers=[_thick_asphalt()]),
                Shoulder(width=2.4, pavement_layers=[_thick_asphalt()]),
                Barrier(spec=JERSEY_32, front_prepared_width=0.6, back_prepared_width=0.4),
                Slope(horizontal_run=6.0, vertical_drop=1.0),
            ],
            right_components=[
                Lane(width=3.6, pavement_layers=[_thick_asphalt()]),
                Lane(width=3.6, pavement_layers=[_thick_asphalt()]),
                Shoulder(width=2.4, pavement_layers=[_thick_asphalt()]),
                Slope(horizontal_run=6.0, vertical_drop=1.0),
            ],
        )

        errors = section.validate(include_geometry=True)
        # Prepared surfaces create gaps - these are expected
        overlap_errors = [e for e in errors if 'overlap' in e.lower()]
        assert overlap_errors == []

    def test_section_with_curb_validates(self):
        """Test section with curb and gutter passes validation."""
        section = RoadSection(
            name="Test Section",
            control_point=ControlPoint(x=0, elevation=100.0),
            right_components=[
                Lane(width=3.6, pavement_layers=[_thick_asphalt()]),
                Curb(gutter_width=0.6, curb_height=0.15),
                Slope(horizontal_run=4.0, vertical_drop=0.5),
            ],
        )

        errors = section.validate(include_geometry=True)
        assert errors == []

    def test_section_with_barrier_no_overlaps(self):
        """Test section with barrier has no overlaps."""
        section = RoadSection(
            name="Test Section",
            control_point=ControlPoint(x=0, elevation=100.0),
            right_components=[
                Lane(width=3.6, pavement_layers=[_thick_asphalt()]),
                Shoulder(width=2.4, pavement_layers=[_thick_asphalt()]),
                Barrier(spec=JERSEY_32, front_prepared_width=0.6, back_prepared_width=0.4),
                Slope(horizontal_run=6.0, vertical_drop=1.0),
            ],
        )

        # Should pass - no overlaps between components
        errors = section.validate(include_geometry=True)
        overlap_errors = [e for e in errors if 'overlap' in e.lower()]
        assert overlap_errors == []

    def test_multi_lane_highway_validates(self):
        """Test multi-lane divided highway section validates."""
        section = RoadSection(
            name="Test Section",
            control_point=ControlPoint(x=0, elevation=100.0),
            left_components=[
                Slope(horizontal_run=6.0, vertical_drop=-2.0),  # Backslope
                Shoulder(width=3.0, pavement_layers=[_thick_asphalt()]),
                Lane(width=3.6, pavement_layers=[_thick_asphalt()]),
                Lane(width=3.6, pavement_layers=[_thick_asphalt()]),
            ],
            right_components=[
                Lane(width=3.6, pavement_layers=[_thick_asphalt()]),
                Lane(width=3.6, pavement_layers=[_thick_asphalt()]),
                Shoulder(width=3.0, pavement_layers=[_thick_asphalt()]),
                Slope(horizontal_run=6.0, vertical_drop=1.5),  # Foreslope
            ],
        )

        errors = section.validate(include_geometry=True)
        assert errors == []

    def test_urban_section_with_barrier_and_curb(self):
        """Test urban section with barriers and curbs validates."""
        section = RoadSection(
            name="Test Section",
            control_point=ControlPoint(x=0, elevation=100.0),
            left_components=[
                Curb(gutter_width=0.6, curb_height=0.15),
                Lane(width=3.3, pavement_layers=[_thick_asphalt()]),
                Lane(width=3.3, pavement_layers=[_thick_asphalt()]),
            ],
            right_components=[
                Lane(width=3.3, pavement_layers=[_thick_asphalt()]),
                Lane(width=3.3, pavement_layers=[_thick_asphalt()]),
                Curb(gutter_width=0.6, curb_height=0.15),
                Slope(horizontal_run=2.0, vertical_drop=0.3),
            ],
        )

        errors = section.validate(include_geometry=True)
        assert errors == []

    def test_section_with_slumped_shoulders(self):
        """Test section with paved_top_slumped shoulders validates."""
        section = RoadSection(
            name="Test Section",
            control_point=ControlPoint(x=0, elevation=100.0),
            right_components=[
                Lane(width=3.6, pavement_layers=[_thick_asphalt()]),
                Shoulder(
                    width=2.4,
                    shoulder_type="paved_top_slumped",
                    pavement_layers=[
                        AsphaltLayer(thickness=0.10, aggregate_size=12.5, binder_type='PG 64-22',
                                    binder_percentage=5.5, density=2400),
                        CrushedRockLayer(thickness=0.20, aggregate_size=37.5, density=2200),
                    ],
                ),
                Slope(horizontal_run=6.0, vertical_drop=1.0),
            ],
        )

        errors = section.validate(include_geometry=True)
        assert errors == []

    def test_validation_without_geometry_doesnt_use_shapely(self):
        """Test that validation without include_geometry skips shapely checks."""
        section = RoadSection(
            name="Test Section",
            control_point=ControlPoint(x=0, elevation=100.0),
            right_components=[
                Lane(width=3.6, pavement_layers=[_thick_asphalt()]),
                Shoulder(width=2.4, pavement_layers=[_thick_asphalt()]),
            ],
        )

        # Should not raise ShapelyNotAvailable error
        errors = section.validate(include_geometry=False)
        # Should only have basic validation errors (if any)
        assert all('overlap' not in e.lower() and 'gap' not in e.lower() for e in errors)

    def test_section_detects_component_validation_errors(self):
        """Test that section validation detects component-level errors."""
        section = RoadSection(
            name="Test Section",
            control_point=ControlPoint(x=0, elevation=100.0),
            right_components=[
                Lane(width=-1.0),  # Invalid negative width
                Shoulder(width=2.4, pavement_layers=[_thick_asphalt()]),
            ],
        )

        errors = section.validate(include_geometry=True)
        assert len(errors) > 0
        assert any('width' in e.lower() for e in errors)

    def test_section_with_no_components_fails_validation(self):
        """Test that section with no components fails validation."""
        section = RoadSection(
            name="Test Section",
            control_point=ControlPoint(x=0, elevation=100.0),
            left_components=[],
            right_components=[],
        )

        errors = section.validate(include_geometry=True)
        assert len(errors) > 0
        assert any('at least one component' in e.lower() for e in errors)

    def test_wide_median_section_validates(self):
        """Test section with wide median (gap between left and right) validates."""
        section = RoadSection(
            name="Test Section",
            control_point=ControlPoint(x=0, elevation=100.0),
            left_components=[
                Slope(horizontal_run=4.0, vertical_drop=-1.0),
                Shoulder(width=2.4, pavement_layers=[_thick_asphalt()]),
                Lane(width=3.6, pavement_layers=[_thick_asphalt()]),
                Lane(width=3.6, pavement_layers=[_thick_asphalt()]),
            ],
            right_components=[
                Lane(width=3.6, pavement_layers=[_thick_asphalt()]),
                Lane(width=3.6, pavement_layers=[_thick_asphalt()]),
                Shoulder(width=2.4, pavement_layers=[_thick_asphalt()]),
                Slope(horizontal_run=4.0, vertical_drop=1.0),
            ],
        )

        # Left and right groups have different sequence_groups, so gap is allowed
        errors = section.validate(include_geometry=True)
        # Should not have gap errors between left and right
        gap_errors = [e for e in errors if 'gap' in e.lower()]
        # Gaps within same side would be errors, but gap between sides is OK
        assert all('left' not in e.lower() or 'right' not in e.lower() for e in gap_errors)

    def test_section_geometry_has_correct_bounds(self):
        """Test that section geometry bounds are calculated correctly."""
        section = RoadSection(
            name="Test Section",
            control_point=ControlPoint(x=0, elevation=100.0),
            left_components=[
                Lane(width=3.6, pavement_layers=[_thick_asphalt()]),
            ],
            right_components=[
                Lane(width=3.6, pavement_layers=[_thick_asphalt()]),
            ],
        )

        geometry = section.to_geometry()
        x_min, y_min, x_max, y_max = geometry.bounds()

        # Should span from -3.6 to +3.6 in X
        assert x_min == pytest.approx(-3.6, abs=0.1)
        assert x_max == pytest.approx(3.6, abs=0.1)
        # Should have some vertical extent
        assert y_min < y_max

    def test_complex_multilayer_section(self):
        """Test complex section with multiple layer types validates."""
        section = RoadSection(
            name="Test Section",
            control_point=ControlPoint(x=0, elevation=100.0),
            right_components=[
                Lane(
                    width=3.6,
                    pavement_layers=[
                        AsphaltLayer(thickness=0.05, aggregate_size=9.5, binder_type='PG 64-22',
                                    binder_percentage=5.5, density=2400),
                        AsphaltLayer(thickness=0.10, aggregate_size=19.0, binder_type='PG 64-22',
                                    binder_percentage=5.0, density=2400),
                        CrushedRockLayer(thickness=0.30, aggregate_size=50.0, density=2200),
                    ],
                ),
                Shoulder(
                    width=2.4,
                    pavement_layers=[
                        AsphaltLayer(thickness=0.05, aggregate_size=12.5, binder_type='PG 64-22',
                                    binder_percentage=5.5, density=2400),
                        CrushedRockLayer(thickness=0.20, aggregate_size=37.5, density=2200),
                    ],
                ),
                Slope(horizontal_run=6.0, vertical_drop=1.2),
            ],
        )

        errors = section.validate(include_geometry=True)
        assert errors == []

        # Verify multiple polygons created
        geometry = section.to_geometry()
        # Lane (3 layers) + Shoulder (2 layers) + Slope (1 layer) = 6 polygons minimum
        assert len(geometry.components) >= 3
        total_polygons = sum(len(comp.polygons) for comp in geometry.components)
        assert total_polygons >= 6
