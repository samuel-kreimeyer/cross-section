"""Tests for AnnotationCollection container."""

import pytest

from cross_section.core.domain.annotations import (
    AnnotationCollection,
    DimensionAnnotation,
    LeaderAnnotation,
    TextAnnotation,
)
from cross_section.core.geometry.primitives import Point2D


class TestAnnotationCollection:
    """Tests for AnnotationCollection class."""

    def test_create_empty_collection(self):
        """Test creating an empty annotation collection."""
        collection = AnnotationCollection()
        assert collection.count() == 0
        assert len(collection.annotations) == 0
        assert len(collection.keyed_notes) == 0

    def test_add_annotation(self):
        """Test adding annotations to collection."""
        collection = AnnotationCollection()

        text1 = TextAnnotation(position=Point2D(0, 0), text="Test 1")
        text2 = TextAnnotation(position=Point2D(5, 5), text="Test 2")

        collection.add(text1)
        assert collection.count() == 1

        collection.add(text2)
        assert collection.count() == 2

    def test_add_keyed_note_auto_key(self):
        """Test adding keyed note with auto-generated key."""
        collection = AnnotationCollection()

        key1 = collection.add_keyed_note("First note")
        assert key1 == "1"
        assert collection.keyed_notes["1"] == "First note"

        key2 = collection.add_keyed_note("Second note")
        assert key2 == "2"
        assert collection.keyed_notes["2"] == "Second note"

    def test_add_keyed_note_custom_key(self):
        """Test adding keyed note with custom key."""
        collection = AnnotationCollection()

        key = collection.add_keyed_note("Custom note", key="A")
        assert key == "A"
        assert collection.keyed_notes["A"] == "Custom note"

    def test_get_by_layer(self):
        """Test filtering annotations by layer."""
        collection = AnnotationCollection()

        dim = DimensionAnnotation(
            start=Point2D(0, 0),
            end=Point2D(5, 0),
            layer="dimensions"
        )
        text1 = TextAnnotation(
            position=Point2D(0, 1),
            text="Label 1",
            layer="labels"
        )
        text2 = TextAnnotation(
            position=Point2D(0, 2),
            text="Label 2",
            layer="labels"
        )

        collection.add(dim)
        collection.add(text1)
        collection.add(text2)

        labels = collection.get_by_layer("labels")
        assert len(labels) == 2

        dimensions = collection.get_by_layer("dimensions")
        assert len(dimensions) == 1

        nonexistent = collection.get_by_layer("nonexistent")
        assert len(nonexistent) == 0

    def test_get_by_type(self):
        """Test filtering annotations by type."""
        collection = AnnotationCollection()

        text1 = TextAnnotation(position=Point2D(0, 0), text="Text 1")
        text2 = TextAnnotation(position=Point2D(1, 1), text="Text 2")
        dim = DimensionAnnotation(start=Point2D(0, 0), end=Point2D(5, 0))
        leader = LeaderAnnotation(
            points=[Point2D(0, 0), Point2D(5, 5)],
            text="Leader"
        )

        collection.add(text1)
        collection.add(text2)
        collection.add(dim)
        collection.add(leader)

        texts = collection.get_by_type(TextAnnotation)
        assert len(texts) == 2

        dims = collection.get_by_type(DimensionAnnotation)
        assert len(dims) == 1

        leaders = collection.get_by_type(LeaderAnnotation)
        assert len(leaders) == 1

    def test_bounds_empty_collection(self):
        """Test bounds of empty collection returns None."""
        collection = AnnotationCollection()
        assert collection.bounds() is None

    def test_bounds_single_annotation(self):
        """Test bounds with single annotation."""
        collection = AnnotationCollection()

        text = TextAnnotation(position=Point2D(5.0, 10.0), text="Test")
        collection.add(text)

        bounds = collection.bounds()
        assert bounds is not None
        assert bounds.center().x == pytest.approx(5.0, abs=0.5)
        assert bounds.center().y == pytest.approx(10.0, abs=0.5)

    def test_bounds_multiple_annotations(self):
        """Test bounds encompasses all annotations."""
        collection = AnnotationCollection()

        text1 = TextAnnotation(position=Point2D(0.0, 0.0), text="A")
        text2 = TextAnnotation(position=Point2D(10.0, 20.0), text="B")

        collection.add(text1)
        collection.add(text2)

        bounds = collection.bounds()
        assert bounds is not None
        assert bounds.min_x <= 0.0
        assert bounds.max_x >= 10.0
        assert bounds.min_y <= 0.0
        assert bounds.max_y >= 20.0

    def test_count(self):
        """Test annotation count."""
        collection = AnnotationCollection()
        assert collection.count() == 0

        collection.add(TextAnnotation(position=Point2D(0, 0), text="A"))
        assert collection.count() == 1

        collection.add(TextAnnotation(position=Point2D(1, 1), text="B"))
        assert collection.count() == 2

    def test_count_by_layer(self):
        """Test counting annotations by layer."""
        collection = AnnotationCollection()

        collection.add(TextAnnotation(
            position=Point2D(0, 0),
            text="L1",
            layer="labels"
        ))
        collection.add(TextAnnotation(
            position=Point2D(1, 1),
            text="L2",
            layer="labels"
        ))
        collection.add(DimensionAnnotation(
            start=Point2D(0, 0),
            end=Point2D(5, 0),
            layer="dimensions"
        ))

        counts = collection.count_by_layer()
        assert counts["labels"] == 2
        assert counts["dimensions"] == 1

    def test_clear(self):
        """Test clearing collection."""
        collection = AnnotationCollection()

        collection.add(TextAnnotation(position=Point2D(0, 0), text="A"))
        collection.add_keyed_note("Note 1")

        assert collection.count() > 0
        assert len(collection.keyed_notes) > 0

        collection.clear()

        assert collection.count() == 0
        assert len(collection.keyed_notes) == 0

    def test_export_keyed_notes_csv_empty(self):
        """Test CSV export with no keyed notes."""
        collection = AnnotationCollection()
        csv = collection.export_keyed_notes_csv()
        assert csv == ""

    def test_export_keyed_notes_csv(self):
        """Test CSV export of keyed notes."""
        collection = AnnotationCollection()

        collection.add_keyed_note("First note")
        collection.add_keyed_note("Second note")
        collection.add_keyed_note("Custom note", key="A")

        csv = collection.export_keyed_notes_csv()

        assert "Key,Description" in csv
        assert '"1","First note"' in csv
        assert '"2","Second note"' in csv
        assert '"A","Custom note"' in csv

    def test_export_keyed_notes_csv_escapes_quotes(self):
        """Test CSV export escapes quotes in text."""
        collection = AnnotationCollection()

        collection.add_keyed_note('Note with "quotes"', key="1")

        csv = collection.export_keyed_notes_csv()

        # Should escape quotes by doubling them
        assert '""quotes""' in csv

    def test_validate_all_annotations(self):
        """Test validation of all annotations."""
        collection = AnnotationCollection()

        # Add valid annotations
        collection.add(TextAnnotation(position=Point2D(0, 0), text="Valid"))

        # Add annotation with warning (large font size)
        collection.add(TextAnnotation(
            position=Point2D(0, 0),
            text="Test",
            font_size=1.5  # Very large - triggers warning
        ))

        errors = collection.validate()
        assert len(errors) > 0
        assert any("very large" in e.lower() for e in errors)

    def test_validate_empty_collection(self):
        """Test validation of empty collection."""
        collection = AnnotationCollection()
        errors = collection.validate()
        assert errors == []

    def test_metadata(self):
        """Test collection metadata."""
        collection = AnnotationCollection()

        collection.metadata["section_name"] = "Test Section"
        collection.metadata["created_by"] = "Test User"

        assert collection.metadata["section_name"] == "Test Section"
        assert collection.metadata["created_by"] == "Test User"

    def test_mixed_annotation_types(self):
        """Test collection with mixed annotation types."""
        collection = AnnotationCollection()

        collection.add(TextAnnotation(position=Point2D(0, 0), text="Text"))
        collection.add(DimensionAnnotation(start=Point2D(0, 0), end=Point2D(5, 0)))
        collection.add(LeaderAnnotation(
            points=[Point2D(0, 0), Point2D(5, 5)],
            text="Leader"
        ))

        assert collection.count() == 3
        assert len(collection.get_by_type(TextAnnotation)) == 1
        assert len(collection.get_by_type(DimensionAnnotation)) == 1
        assert len(collection.get_by_type(LeaderAnnotation)) == 1

    def test_layer_organization(self):
        """Test organizing annotations by layer."""
        collection = AnnotationCollection()

        # Add annotations to different layers
        collection.add(TextAnnotation(
            position=Point2D(0, 0),
            text="Dim 1",
            layer="dimensions"
        ))
        collection.add(TextAnnotation(
            position=Point2D(1, 1),
            text="Label 1",
            layer="labels"
        ))
        collection.add(TextAnnotation(
            position=Point2D(2, 2),
            text="Symbol 1",
            layer="symbols"
        ))

        # Check layer counts
        counts = collection.count_by_layer()
        assert counts["dimensions"] == 1
        assert counts["labels"] == 1
        assert counts["symbols"] == 1

        # Filter by layer
        dim_annotations = collection.get_by_layer("dimensions")
        assert len(dim_annotations) == 1
        assert dim_annotations[0].text == "Dim 1"
