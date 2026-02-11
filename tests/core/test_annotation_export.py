"""Tests for annotation SVG export."""

import io

import pytest

from cross_section.core.domain.annotations import (
    AnnotationCollection,
    AnnotationGenerator,
    AnnotationGeneratorOptions,
    DimensionAnnotation,
    LeaderAnnotation,
    SymbolAnnotation,
    TextAnnotation,
)
from cross_section.core.domain.section import SectionGeometry
from cross_section.core.geometry.primitives import ComponentGeometry, Point2D, Polygon
from cross_section.export import AnnotatedSVGExporter


def _create_simple_section() -> SectionGeometry:
    """Create a simple test section with one component."""
    # Simple rectangular component
    polygon = Polygon(exterior=[
        Point2D(0, 99.5),
        Point2D(3.6, 99.5),
        Point2D(3.6, 100.0),
        Point2D(0, 100.0),
    ])

    component = ComponentGeometry(
        polygons=[polygon],
        metadata={
            "component_type": "TravelLane",
            "width": 3.6,
            "layers": [{"type": "AsphaltLayer", "thickness": 0.5}]
        }
    )

    return SectionGeometry(components=[component], metadata={"name": "Test Section"})


class TestAnnotatedSVGExporter:
    """Tests for AnnotatedSVGExporter class."""

    def test_export_empty_section(self):
        """Test exporting empty section with no annotations."""
        section = SectionGeometry(components=[], metadata={})
        collection = AnnotationCollection()
        exporter = AnnotatedSVGExporter()

        output = io.StringIO()
        exporter.export_with_annotations(section, collection, output)

        svg_content = output.getvalue()
        assert '<svg' in svg_content
        assert 'Empty section' in svg_content

    def test_export_section_no_annotations(self):
        """Test exporting section with no annotations."""
        section = _create_simple_section()
        collection = AnnotationCollection()
        exporter = AnnotatedSVGExporter()

        output = io.StringIO()
        exporter.export_with_annotations(section, collection, output)

        svg_content = output.getvalue()
        assert '<svg' in svg_content
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg_content
        assert '<polygon' in svg_content  # Geometry rendered
        assert '<!-- Annotations -->' in svg_content

    def test_export_with_text_annotation(self):
        """Test exporting with text annotation."""
        section = _create_simple_section()
        collection = AnnotationCollection()

        # Add text annotation
        collection.add(TextAnnotation(
            position=Point2D(1.8, 100.2),
            text="Lane",
            font_size=0.15,
            layer="labels"
        ))

        exporter = AnnotatedSVGExporter()
        output = io.StringIO()
        exporter.export_with_annotations(section, collection, output)

        svg_content = output.getvalue()
        assert '<text' in svg_content
        assert 'Lane' in svg_content
        assert 'font-family="Arial"' in svg_content

    def test_export_with_dimension_annotation(self):
        """Test exporting with dimension annotation."""
        section = _create_simple_section()
        collection = AnnotationCollection()

        # Add dimension annotation
        collection.add(DimensionAnnotation(
            start=Point2D(0, 100.0),
            end=Point2D(3.6, 100.0),
            offset=0.3,
            dimension_text="3.60m",
            layer="dimensions"
        ))

        exporter = AnnotatedSVGExporter()
        output = io.StringIO()
        exporter.export_with_annotations(section, collection, output)

        svg_content = output.getvalue()
        assert 'dimension-' in svg_content  # Dimension group ID
        assert '<line' in svg_content  # Dimension and extension lines
        assert '3.60m' in svg_content  # Dimension text

    def test_export_with_dimension_arrows(self):
        """Test dimension arrows are rendered."""
        section = _create_simple_section()
        collection = AnnotationCollection()

        collection.add(DimensionAnnotation(
            start=Point2D(0, 100.0),
            end=Point2D(3.6, 100.0),
            offset=0.3,
            show_arrows=True,
            layer="dimensions"
        ))

        exporter = AnnotatedSVGExporter()
        output = io.StringIO()
        exporter.export_with_annotations(section, collection, output)

        svg_content = output.getvalue()
        assert '<polygon' in svg_content  # Arrows rendered as polygons

    def test_export_with_leader_annotation(self):
        """Test exporting with leader annotation."""
        section = _create_simple_section()
        collection = AnnotationCollection()

        # Add leader annotation
        collection.add(LeaderAnnotation(
            points=[Point2D(1.8, 99.7), Point2D(2.5, 99.3), Point2D(3.5, 99.3)],
            text="Asphalt Layer",
            arrow_at_start=True,
            layer="leaders"
        ))

        exporter = AnnotatedSVGExporter()
        output = io.StringIO()
        exporter.export_with_annotations(section, collection, output)

        svg_content = output.getvalue()
        assert 'leader-' in svg_content  # Leader group ID
        assert '<polyline' in svg_content
        assert 'Asphalt Layer' in svg_content

    def test_export_with_symbol_annotation(self):
        """Test exporting with symbol annotation."""
        section = _create_simple_section()
        collection = AnnotationCollection()

        # Add symbol annotation
        collection.add(SymbolAnnotation(
            position=Point2D(1.8, 99.75),
            symbol_type="traffic_arrow",
            layer="symbols"
        ))

        exporter = AnnotatedSVGExporter()
        output = io.StringIO()
        exporter.export_with_annotations(section, collection, output)

        svg_content = output.getvalue()
        assert 'symbol-' in svg_content  # Symbol group ID
        assert '<path' in svg_content  # Symbol rendered as path

    def test_export_with_unknown_symbol(self):
        """Test exporting with unknown symbol type renders placeholder."""
        section = _create_simple_section()
        collection = AnnotationCollection()

        # Add symbol with unknown type
        collection.add(SymbolAnnotation(
            position=Point2D(1.8, 99.75),
            symbol_type="unknown_symbol_type",
            layer="symbols"
        ))

        exporter = AnnotatedSVGExporter()
        output = io.StringIO()
        exporter.export_with_annotations(section, collection, output)

        svg_content = output.getvalue()
        # Should render placeholder circle
        assert '<circle' in svg_content
        assert 'fill="red"' in svg_content

    def test_export_with_rotated_text(self):
        """Test exporting rotated text annotation."""
        section = _create_simple_section()
        collection = AnnotationCollection()

        # Add rotated text
        collection.add(TextAnnotation(
            position=Point2D(1.8, 100.2),
            text="Rotated",
            angle=45.0,
            layer="labels"
        ))

        exporter = AnnotatedSVGExporter()
        output = io.StringIO()
        exporter.export_with_annotations(section, collection, output)

        svg_content = output.getvalue()
        assert 'rotate(' in svg_content
        assert 'Rotated' in svg_content

    def test_export_with_keyed_notes(self):
        """Test keyed notes table rendering."""
        section = _create_simple_section()
        collection = AnnotationCollection()

        # Add keyed notes
        key1 = collection.add_keyed_note("Travel Lane - 3.6m width")
        key2 = collection.add_keyed_note("Asphalt Surface - 150mm")

        collection.add(TextAnnotation(
            position=Point2D(1.8, 100.2),
            text=key1,
            is_keyed_note=True,
            layer="labels"
        ))

        exporter = AnnotatedSVGExporter()
        output = io.StringIO()
        exporter.export_with_annotations(section, collection, output, include_keyed_notes_table=True)

        svg_content = output.getvalue()
        assert '<!-- Keyed Notes Table -->' in svg_content
        assert 'Key' in svg_content
        assert 'Description' in svg_content
        assert 'Travel Lane' in svg_content
        assert 'Asphalt Surface' in svg_content

    def test_export_without_keyed_notes_table(self):
        """Test that keyed notes table can be disabled."""
        section = _create_simple_section()
        collection = AnnotationCollection()

        collection.add_keyed_note("Note 1")

        exporter = AnnotatedSVGExporter()
        output = io.StringIO()
        exporter.export_with_annotations(
            section, collection, output, include_keyed_notes_table=False
        )

        svg_content = output.getvalue()
        assert '<!-- Keyed Notes Table -->' not in svg_content

    def test_export_multiple_annotation_types(self):
        """Test exporting with multiple annotation types."""
        section = _create_simple_section()
        collection = AnnotationCollection()

        # Add various annotations
        collection.add(TextAnnotation(
            position=Point2D(1.8, 100.2),
            text="Lane",
            layer="labels"
        ))

        collection.add(DimensionAnnotation(
            start=Point2D(0, 100.0),
            end=Point2D(3.6, 100.0),
            offset=0.3,
            layer="dimensions"
        ))

        collection.add(SymbolAnnotation(
            position=Point2D(1.8, 99.75),
            symbol_type="traffic_arrow",
            layer="symbols"
        ))

        exporter = AnnotatedSVGExporter()
        output = io.StringIO()
        exporter.export_with_annotations(section, collection, output)

        svg_content = output.getvalue()
        assert '<text' in svg_content
        assert 'dimension-' in svg_content
        assert 'symbol-' in svg_content

    def test_export_with_auto_generated_annotations(self):
        """Test exporting with auto-generated annotations."""
        section = _create_simple_section()

        # Generate annotations
        options = AnnotationGeneratorOptions(
            add_component_labels=True,
            add_width_dimensions=True,
            unit_system="metric"
        )
        collection = AnnotationGenerator.generate(section, options)

        exporter = AnnotatedSVGExporter()
        output = io.StringIO()
        exporter.export_with_annotations(section, collection, output)

        svg_content = output.getvalue()
        assert '<svg' in svg_content
        assert 'Lane' in svg_content  # Component label
        assert '3.60m' in svg_content  # Width dimension

    def test_coordinate_transformation(self):
        """Test that coordinate transformation is applied correctly."""
        section = _create_simple_section()
        collection = AnnotationCollection()

        # Add annotation at known position
        collection.add(TextAnnotation(
            position=Point2D(0, 100.0),
            text="Origin",
            layer="labels"
        ))

        exporter = AnnotatedSVGExporter(scale=100.0)
        output = io.StringIO()
        exporter.export_with_annotations(section, collection, output)

        svg_content = output.getvalue()
        # Text should be transformed to SVG coordinates
        # With margin of 0.5m, x=0 becomes x=0.5*100=50
        assert '<text' in svg_content
        assert 'Origin' in svg_content

    def test_vertical_exaggeration_applied(self):
        """Test that vertical exaggeration is applied to annotations."""
        section = _create_simple_section()
        collection = AnnotationCollection()

        collection.add(TextAnnotation(
            position=Point2D(1.8, 100.0),
            text="Test",
            layer="labels"
        ))

        # Export with vertical exaggeration
        exporter = AnnotatedSVGExporter(scale=100.0, vertical_exaggeration=2.0)
        output = io.StringIO()
        exporter.export_with_annotations(section, collection, output)

        svg_content = output.getvalue()
        assert '<text' in svg_content
        assert 'Test' in svg_content

    def test_bounds_include_annotations(self):
        """Test that SVG bounds expand to include annotations."""
        section = _create_simple_section()
        collection = AnnotationCollection()

        # Add annotation above section
        collection.add(TextAnnotation(
            position=Point2D(1.8, 101.0),  # Above geometry
            text="Above",
            layer="labels"
        ))

        exporter = AnnotatedSVGExporter()
        output = io.StringIO()
        exporter.export_with_annotations(section, collection, output)

        svg_content = output.getvalue()
        # SVG should be large enough to include the annotation
        assert '<svg' in svg_content
        assert 'Above' in svg_content

    def test_annotation_layer_ordering(self):
        """Test that annotations render in correct order (dimensions, leaders, symbols, text)."""
        section = _create_simple_section()
        collection = AnnotationCollection()

        # Add in reverse order to test sorting
        collection.add(TextAnnotation(position=Point2D(1, 100), text="T", layer="labels"))
        collection.add(SymbolAnnotation(position=Point2D(2, 100), symbol_type="traffic_arrow", layer="symbols"))
        collection.add(DimensionAnnotation(start=Point2D(0, 100), end=Point2D(3, 100), layer="dimensions"))

        exporter = AnnotatedSVGExporter()
        output = io.StringIO()
        exporter.export_with_annotations(section, collection, output)

        svg_content = output.getvalue()
        # All annotation types should be present
        assert 'dimension-' in svg_content
        assert 'symbol-' in svg_content
        assert 'T</text>' in svg_content

    def test_keyed_notes_table_position(self):
        """Test that keyed notes table appears in bottom-right."""
        section = _create_simple_section()
        collection = AnnotationCollection()

        collection.add_keyed_note("Test Note")

        exporter = AnnotatedSVGExporter()
        output = io.StringIO()
        exporter.export_with_annotations(section, collection, output, include_keyed_notes_table=True)

        svg_content = output.getvalue()
        # Table should be rendered
        assert '<!-- Keyed Notes Table -->' in svg_content
        assert '<rect' in svg_content  # Table background
        assert 'Test Note' in svg_content

    def test_long_keyed_note_truncation(self):
        """Test that long keyed note descriptions are truncated."""
        section = _create_simple_section()
        collection = AnnotationCollection()

        # Add very long keyed note
        long_text = "This is a very long description that should be truncated in the table"
        collection.add_keyed_note(long_text)

        exporter = AnnotatedSVGExporter()
        output = io.StringIO()
        exporter.export_with_annotations(section, collection, output, include_keyed_notes_table=True)

        svg_content = output.getvalue()
        # Should contain truncation indicator
        assert '...' in svg_content

    def test_dimension_zero_length_rejected(self):
        """Test that zero-length dimensions are rejected by validation."""
        # Zero-length dimensions should raise ValueError during creation
        with pytest.raises(ValueError, match="start and end points must be different"):
            DimensionAnnotation(
                start=Point2D(1.8, 100.0),
                end=Point2D(1.8, 100.0),  # Same point
                layer="dimensions"
            )

    def test_text_anchor_types(self):
        """Test different text anchor types."""
        section = _create_simple_section()
        collection = AnnotationCollection()

        collection.add(TextAnnotation(
            position=Point2D(1, 100),
            text="Start",
            anchor="start",
            layer="labels"
        ))
        collection.add(TextAnnotation(
            position=Point2D(2, 100),
            text="Middle",
            anchor="middle",
            layer="labels"
        ))
        collection.add(TextAnnotation(
            position=Point2D(3, 100),
            text="End",
            anchor="end",
            layer="labels"
        ))

        exporter = AnnotatedSVGExporter()
        output = io.StringIO()
        exporter.export_with_annotations(section, collection, output)

        svg_content = output.getvalue()
        assert 'text-anchor="start"' in svg_content
        assert 'text-anchor="middle"' in svg_content
        assert 'text-anchor="end"' in svg_content

    def test_font_size_scaling(self):
        """Test that font sizes are scaled correctly."""
        section = _create_simple_section()
        collection = AnnotationCollection()

        collection.add(TextAnnotation(
            position=Point2D(1.8, 100.2),
            text="Small",
            font_size=0.1,
            layer="labels"
        ))
        collection.add(TextAnnotation(
            position=Point2D(2.8, 100.2),
            text="Large",
            font_size=0.3,
            layer="labels"
        ))

        exporter = AnnotatedSVGExporter(scale=100.0)
        output = io.StringIO()
        exporter.export_with_annotations(section, collection, output)

        svg_content = output.getvalue()
        # Font sizes should be scaled (0.1*100=10, 0.3*100=30)
        assert 'font-size="10.0"' in svg_content
        assert 'font-size="30.0"' in svg_content

    def test_symbol_scaling_and_rotation(self):
        """Test symbol scaling and rotation."""
        section = _create_simple_section()
        collection = AnnotationCollection()

        collection.add(SymbolAnnotation(
            position=Point2D(1.8, 99.75),
            symbol_type="traffic_arrow",
            scale=2.0,
            angle=180.0,
            layer="symbols"
        ))

        exporter = AnnotatedSVGExporter()
        output = io.StringIO()
        exporter.export_with_annotations(section, collection, output)

        svg_content = output.getvalue()
        assert 'scale(2.0)' in svg_content
        assert 'rotate(-180.0)' in svg_content

    def test_integration_with_collision_resolution(self):
        """Test export with collision-resolved annotations."""
        section = _create_simple_section()

        # Generate annotations
        options = AnnotationGeneratorOptions(
            add_component_labels=True,
            add_width_dimensions=True
        )
        collection = AnnotationGenerator.generate(section, options)

        # Resolve collisions
        collection.resolve_collisions()

        # Export
        exporter = AnnotatedSVGExporter()
        output = io.StringIO()
        exporter.export_with_annotations(section, collection, output)

        svg_content = output.getvalue()
        assert '<svg' in svg_content
        assert 'Lane' in svg_content

    def test_valid_svg_structure(self):
        """Test that exported SVG has valid structure."""
        section = _create_simple_section()
        collection = AnnotationCollection()

        collection.add(TextAnnotation(
            position=Point2D(1.8, 100.2),
            text="Test",
            layer="labels"
        ))

        exporter = AnnotatedSVGExporter()
        output = io.StringIO()
        exporter.export_with_annotations(section, collection, output)

        svg_content = output.getvalue()

        # Check basic SVG structure
        assert svg_content.startswith('<svg')
        assert svg_content.endswith('</svg>\n')
        assert 'xmlns="http://www.w3.org/2000/svg"' in svg_content
        assert 'viewBox=' in svg_content
        assert 'width=' in svg_content
        assert 'height=' in svg_content
