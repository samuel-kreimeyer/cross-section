"""Tests for automatic annotation generation."""

import pytest

from cross_section.core.domain.annotations import (
    AnnotationGenerator,
    AnnotationGeneratorOptions,
    AnnotationProfile,
    DimensionAnnotation,
    LeaderAnnotation,
    SymbolAnnotation,
    TextAnnotation,
)
from cross_section.core.domain.section import SectionGeometry
from cross_section.core.geometry.primitives import ComponentGeometry, Point2D, Polygon


def _create_mock_component(
    component_type: str,
    width: float,
    min_x: float,
    max_x: float,
    min_y: float,
    max_y: float,
    direction: str = "right",
    **extra_metadata
) -> ComponentGeometry:
    """Create a mock component geometry for testing."""
    # Simple rectangular polygon
    polygon = Polygon(exterior=[
        Point2D(min_x, min_y),
        Point2D(max_x, min_y),
        Point2D(max_x, max_y),
        Point2D(min_x, max_y),
    ])

    metadata = {
        "component_type": component_type,
        "width": width,
        "assembly_direction": direction,
        **extra_metadata
    }

    return ComponentGeometry(polygons=[polygon], metadata=metadata)


class TestAnnotationGeneratorOptions:
    """Tests for AnnotationGeneratorOptions dataclass."""

    def test_default_options(self):
        """Test default options."""
        options = AnnotationGeneratorOptions()

        assert options.add_component_labels is True
        assert options.add_width_dimensions is True
        assert options.add_material_labels is False
        assert options.add_layer_callouts is True
        assert options.use_keyed_notes is False
        assert options.add_cross_slope_symbols is False
        assert options.add_cross_slope_text is False
        assert options.material_label_mode == "note"
        assert options.traffic_arrow_mode == "assembly"
        assert options.text_size == 0.15

    def test_custom_options(self):
        """Test creating custom options."""
        options = AnnotationGeneratorOptions(
            add_component_labels=False,
            use_keyed_notes=True,
            text_size=0.20
        )

        assert options.add_component_labels is False
        assert options.use_keyed_notes is True
        assert options.text_size == 0.20


class TestAnnotationGenerator:
    """Tests for AnnotationGenerator class."""

    def test_generate_empty_section(self):
        """Test generating annotations for empty section."""
        section = SectionGeometry(components=[], metadata={})
        options = AnnotationGeneratorOptions()

        collection = AnnotationGenerator.generate(section, options)

        assert collection.count() == 0

    def test_generate_component_labels(self):
        """Test generating component labels."""
        # Create section with two components
        lane = _create_mock_component(
            "TravelLane", width=3.6, min_x=0, max_x=3.6, min_y=99.5, max_y=100.0
        )
        shoulder = _create_mock_component(
            "Shoulder", width=2.4, min_x=3.6, max_x=6.0, min_y=99.5, max_y=100.0
        )

        section = SectionGeometry(components=[lane, shoulder], metadata={})
        options = AnnotationGeneratorOptions(
            add_component_labels=True,
            add_width_dimensions=False
        )

        collection = AnnotationGenerator.generate(section, options)

        # Should have labels for both components
        labels = collection.get_by_type(TextAnnotation)
        assert len(labels) == 2

        # Check label texts
        label_texts = [label.text for label in labels]
        assert "Lane" in label_texts
        assert "Shoulder" in label_texts

    def test_generate_width_dimensions(self):
        """Test generating width dimensions."""
        lane = _create_mock_component(
            "TravelLane", width=3.6, min_x=0, max_x=3.6, min_y=99.5, max_y=100.0
        )

        section = SectionGeometry(components=[lane], metadata={})
        options = AnnotationGeneratorOptions(
            add_component_labels=False,
            add_width_dimensions=True,
            unit_system="metric"
        )

        collection = AnnotationGenerator.generate(section, options)

        # Should have one dimension
        dimensions = collection.get_by_type(DimensionAnnotation)
        assert len(dimensions) == 1

        dim = dimensions[0]
        assert "3.60m" in dim.dimension_text

    def test_generate_slope_label_with_ratio(self):
        """Test generating slope label includes ratio."""
        slope = _create_mock_component(
            "Slope",
            width=6.0,
            min_x=6.0,
            max_x=12.0,
            min_y=98.5,
            max_y=100.0,
            slope_ratio=4.0
        )

        section = SectionGeometry(components=[slope], metadata={})
        options = AnnotationGeneratorOptions(
            add_component_labels=True,
            add_width_dimensions=False
        )

        collection = AnnotationGenerator.generate(section, options)

        labels = collection.get_by_type(TextAnnotation)
        assert len(labels) == 1
        assert "4.0:1" in labels[0].text

    def test_generate_keyed_notes(self):
        """Test generating keyed notes instead of inline text."""
        lane = _create_mock_component(
            "TravelLane", width=3.6, min_x=0, max_x=3.6, min_y=99.5, max_y=100.0
        )

        section = SectionGeometry(components=[lane], metadata={})
        options = AnnotationGeneratorOptions(
            add_component_labels=True,
            add_width_dimensions=False,
            use_keyed_notes=True
        )

        collection = AnnotationGenerator.generate(section, options)

        # Should have keyed note
        assert len(collection.keyed_notes) > 0

        # Label should reference key
        labels = collection.get_by_type(TextAnnotation)
        assert len(labels) == 1
        assert labels[0].is_keyed_note is True
        assert labels[0].text in collection.keyed_notes

    def test_generate_material_labels(self):
        """Test generating material labels."""
        lane = _create_mock_component(
            "TravelLane",
            width=3.6,
            min_x=0,
            max_x=3.6,
            min_y=99.5,
            max_y=100.0,
            layers=[
                {"type": "AsphaltLayer", "thickness": 0.15},
            ]
        )

        section = SectionGeometry(components=[lane], metadata={})
        options = AnnotationGeneratorOptions(
            add_component_labels=False,
            add_width_dimensions=False,
            add_material_labels=True
        )

        collection = AnnotationGenerator.generate(section, options)

        # Should have material label
        labels = collection.get_by_type(TextAnnotation)
        assert len(labels) == 1
        assert "Asphalt" in labels[0].text

    def test_generate_centerpoint_mark(self):
        """Test generating centerpoint mark."""
        section = SectionGeometry(
            components=[],
            metadata={
                "control_point": {"x": 0.0, "elevation": 100.0}
            }
        )
        options = AnnotationGeneratorOptions(
            add_component_labels=False,
            add_width_dimensions=False,
            add_centerpoint_mark=True
        )

        collection = AnnotationGenerator.generate(section, options)

        # Should have centerpoint symbol
        symbols = collection.get_by_type(SymbolAnnotation)
        assert len(symbols) == 1
        assert symbols[0].symbol_type == "centerpoint"
        assert symbols[0].position.x == pytest.approx(0.0)
        assert symbols[0].position.y == pytest.approx(100.0)

    def test_generate_traffic_symbols(self):
        """Test generating traffic direction symbols."""
        lane1 = _create_mock_component(
            "TravelLane", width=3.6, min_x=0, max_x=3.6, min_y=99.5, max_y=100.0, direction="right"
        )
        lane2 = _create_mock_component(
            "TravelLane", width=3.6, min_x=-3.6, max_x=0, min_y=99.5, max_y=100.0, direction="left"
        )

        section = SectionGeometry(components=[lane1, lane2], metadata={})
        options = AnnotationGeneratorOptions(
            add_component_labels=False,
            add_width_dimensions=False,
            add_traffic_symbols=True
        )

        collection = AnnotationGenerator.generate(section, options)

        # Should have traffic arrows for both lanes
        symbols = collection.get_by_type(SymbolAnnotation)
        assert len(symbols) == 2

        # Check angles (right=0, left=180)
        angles = sorted([s.angle for s in symbols])
        assert angles[0] == pytest.approx(0.0)
        assert angles[1] == pytest.approx(180.0)

    def test_generate_cross_slope_symbols(self):
        """Test generating cross-slope symbols."""
        lane = _create_mock_component(
            "TravelLane",
            width=3.6,
            min_x=0,
            max_x=3.6,
            min_y=99.5,
            max_y=100.0,
            direction="right",
            cross_slope=0.02,
        )

        section = SectionGeometry(components=[lane], metadata={})
        options = AnnotationGeneratorOptions(
            add_component_labels=False,
            add_width_dimensions=False,
            add_cross_slope_symbols=True,
        )

        collection = AnnotationGenerator.generate(section, options)

        symbols = collection.get_by_type(SymbolAnnotation)
        assert len(symbols) == 1
        assert symbols[0].symbol_type == "drainage_arrow"
        assert symbols[0].angle == pytest.approx(0.0)

    def test_crown_dimension_required(self):
        """Test crown point always receives a dimension."""
        lane = _create_mock_component(
            "TravelLane",
            width=3.6,
            min_x=0,
            max_x=3.6,
            min_y=99.5,
            max_y=100.0,
            direction="right",
        )
        section = SectionGeometry(
            components=[lane],
            metadata={"control_point": {"x": 0.0, "elevation": 100.0}},
        )
        options = AnnotationGeneratorOptions(
            add_component_labels=False,
            add_width_dimensions=False,
        )

        collection = AnnotationGenerator.generate(section, options)

        dimensions = collection.get_by_type(DimensionAnnotation)
        assert len(dimensions) == 1
        assert (
            dimensions[0].start.x == pytest.approx(0.0)
            or dimensions[0].end.x == pytest.approx(0.0)
        )

    def test_generate_all_annotations(self):
        """Test generating all annotation types together."""
        lane = _create_mock_component(
            "TravelLane",
            width=3.6,
            min_x=0,
            max_x=3.6,
            min_y=99.5,
            max_y=100.0,
            layers=[{"type": "AsphaltLayer", "thickness": 0.15}]
        )

        section = SectionGeometry(
            components=[lane],
            metadata={"control_point": {"x": 0.0, "elevation": 100.0}}
        )
        options = AnnotationGeneratorOptions(
            add_component_labels=True,
            add_width_dimensions=True,
            add_material_labels=True,
            add_traffic_symbols=True,
            add_centerpoint_mark=True
        )

        collection = AnnotationGenerator.generate(section, options)

        # Should have multiple annotations
        assert collection.count() > 0

        # Check each type
        assert len(collection.get_by_type(TextAnnotation)) >= 2  # Label + material
        assert len(collection.get_by_type(DimensionAnnotation)) == 1
        assert len(collection.get_by_type(SymbolAnnotation)) >= 2  # Traffic + centerpoint

    def test_generate_respects_layers(self):
        """Test that generated annotations are on correct layers."""
        lane = _create_mock_component(
            "TravelLane", width=3.6, min_x=0, max_x=3.6, min_y=99.5, max_y=100.0
        )

        section = SectionGeometry(components=[lane], metadata={})
        options = AnnotationGeneratorOptions(
            add_component_labels=True,
            add_width_dimensions=True
        )

        collection = AnnotationGenerator.generate(section, options)

        # Check layer assignment
        labels = collection.get_by_layer("labels")
        assert len(labels) == 1

        dimensions = collection.get_by_layer("dimensions")
        assert len(dimensions) == 1

    def test_generate_multiple_components(self):
        """Test generating annotations for multiple components."""
        components = [
            _create_mock_component(
                "TravelLane", width=3.6, min_x=i*3.6, max_x=(i+1)*3.6, min_y=99.5, max_y=100.0
            )
            for i in range(3)
        ]

        section = SectionGeometry(components=components, metadata={})
        options = AnnotationGeneratorOptions(
            add_component_labels=True,
            add_width_dimensions=True
        )

        collection = AnnotationGenerator.generate(section, options)

        # Should have 3 labels + 3 dimensions
        assert len(collection.get_by_type(TextAnnotation)) == 3
        assert len(collection.get_by_type(DimensionAnnotation)) == 3

    def test_generate_component_without_width(self):
        """Test that components without width don't get dimensions."""
        # Component with no width metadata
        comp = ComponentGeometry(
            polygons=[Polygon(exterior=[
                Point2D(0, 0), Point2D(1, 0), Point2D(1, 1), Point2D(0, 1)
            ])],
            metadata={"component_type": "Unknown"}  # No width
        )

        section = SectionGeometry(components=[comp], metadata={})
        options = AnnotationGeneratorOptions(
            add_component_labels=False,
            add_width_dimensions=True
        )

        collection = AnnotationGenerator.generate(section, options)

        # Should not have dimensions
        assert len(collection.get_by_type(DimensionAnnotation)) == 0

    def test_generate_layer_callouts(self):
        """Test generating leader callouts for pavement layers."""
        # Create lane with multiple layers
        lane = _create_mock_component(
            "TravelLane",
            width=3.6,
            min_x=0,
            max_x=3.6,
            min_y=99.5,
            max_y=100.0,
            layers=[
                {"type": "AsphaltLayer", "thickness": 0.05},  # 2" surface
                {"type": "CrushedRockLayer", "thickness": 0.15},  # 6" base
            ]
        )
        # Add a second polygon for the second layer
        lane.polygons.append(Polygon(exterior=[
            Point2D(0, 99.3), Point2D(3.6, 99.3),
            Point2D(3.6, 99.5), Point2D(0, 99.5),
        ]))

        section = SectionGeometry(
            components=[lane],
            metadata={"control_point": {"x": 0.0, "elevation": 100.0}}
        )
        options = AnnotationGeneratorOptions(
            add_component_labels=False,
            add_width_dimensions=False,
            add_layer_callouts=True
        )

        collection = AnnotationGenerator.generate(section, options)

        # Should have leaders for both layer types
        leaders = collection.get_by_type(LeaderAnnotation)
        assert len(leaders) == 2

        # Check leader texts include material names
        texts = [l.text for l in leaders]
        assert any("Asphalt" in t for t in texts)
        assert any("Aggregate" in t for t in texts)

    def test_generate_layer_callouts_groups_same_type(self):
        """Test that same layer types across components are grouped."""
        # Two lanes with same layer type
        lane1 = _create_mock_component(
            "TravelLane",
            width=3.6,
            min_x=0,
            max_x=3.6,
            min_y=99.5,
            max_y=100.0,
            direction="right",
            layers=[{"type": "AsphaltLayer", "thickness": 0.05}]
        )
        lane2 = _create_mock_component(
            "TravelLane",
            width=3.6,
            min_x=-3.6,
            max_x=0,
            min_y=99.5,
            max_y=100.0,
            direction="left",
            layers=[{"type": "AsphaltLayer", "thickness": 0.05}]
        )

        section = SectionGeometry(
            components=[lane1, lane2],
            metadata={"control_point": {"x": 0.0, "elevation": 100.0}}
        )
        options = AnnotationGeneratorOptions(
            add_component_labels=False,
            add_width_dimensions=False,
            add_layer_callouts=True
        )

        collection = AnnotationGenerator.generate(section, options)

        # Should have only ONE leader for Asphalt (deduplicated)
        leaders = collection.get_by_type(LeaderAnnotation)
        assert len(leaders) == 1
        assert "Asphalt" in leaders[0].text

    def test_layer_callout_includes_thickness(self):
        """Test that layer callouts include thickness in inches."""
        lane = _create_mock_component(
            "TravelLane",
            width=3.6,
            min_x=0,
            max_x=3.6,
            min_y=99.5,
            max_y=100.0,
            layers=[{"type": "AsphaltLayer", "thickness": 0.0508}]  # 2 inches
        )

        section = SectionGeometry(
            components=[lane],
            metadata={"control_point": {"x": 0.0, "elevation": 100.0}}
        )
        options = AnnotationGeneratorOptions(
            add_component_labels=False,
            add_width_dimensions=False,
            add_layer_callouts=True
        )

        collection = AnnotationGenerator.generate(section, options)

        leaders = collection.get_by_type(LeaderAnnotation)
        assert len(leaders) == 1
        # Should include thickness (approximately 2")
        assert '2"' in leaders[0].text or "Asphalt" in leaders[0].text
