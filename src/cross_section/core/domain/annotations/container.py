"""Container for managing collections of annotations."""

from dataclasses import dataclass, field
from typing import Any

from ...geometry.bounds import BoundingBox
from .base import AnnotationBase


@dataclass
class AnnotationCollection:
    """Container for all annotations on a cross-section.

    Manages annotations, keyed notes, and provides query/export methods.

    Attributes:
        annotations: List of all annotations
        keyed_notes: Map of keyed note IDs to full text descriptions
        metadata: Collection-level metadata
    """

    annotations: list[AnnotationBase] = field(default_factory=list)
    keyed_notes: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def add(self, annotation: AnnotationBase) -> None:
        """Add an annotation to the collection.

        Args:
            annotation: The annotation to add
        """
        self.annotations.append(annotation)

    def add_keyed_note(self, text: str, key: str | None = None) -> str:
        """Add a keyed note and return its reference key.

        Args:
            text: The full text description
            key: Optional specific key (auto-generated if None)

        Returns:
            The key for this keyed note (e.g., "1", "2", "A", "B")
        """
        if key is None:
            # Auto-generate next numeric key
            existing_keys = self.keyed_notes.keys()
            numeric_keys = [int(k) for k in existing_keys if k.isdigit()]
            next_key = max(numeric_keys, default=0) + 1
            key = str(next_key)

        self.keyed_notes[key] = text
        return key

    def get_by_layer(self, layer: str) -> list[AnnotationBase]:
        """Get all annotations on a specific layer.

        Args:
            layer: Layer name to filter by

        Returns:
            List of annotations on the specified layer
        """
        return [ann for ann in self.annotations if ann.layer == layer]

    def get_by_type(self, annotation_type: type) -> list[AnnotationBase]:
        """Get all annotations of a specific type.

        Args:
            annotation_type: The annotation class to filter by

        Returns:
            List of annotations of the specified type
        """
        return [ann for ann in self.annotations if isinstance(ann, annotation_type)]

    def bounds(self) -> BoundingBox | None:
        """Calculate bounding box containing all annotations.

        Returns:
            Bounding box containing all annotations, or None if empty
        """
        if not self.annotations:
            return None

        annotation_bounds = [ann.bounds() for ann in self.annotations]
        return BoundingBox.union(annotation_bounds)

    def count(self) -> int:
        """Get total number of annotations.

        Returns:
            Number of annotations in collection
        """
        return len(self.annotations)

    def count_by_layer(self) -> dict[str, int]:
        """Count annotations by layer.

        Returns:
            Dictionary mapping layer names to counts
        """
        counts: dict[str, int] = {}
        for ann in self.annotations:
            counts[ann.layer] = counts.get(ann.layer, 0) + 1
        return counts

    def clear(self) -> None:
        """Remove all annotations and keyed notes."""
        self.annotations.clear()
        self.keyed_notes.clear()

    def export_keyed_notes_csv(self) -> str:
        """Export keyed notes as CSV string.

        Returns:
            CSV formatted string with keyed notes
        """
        if not self.keyed_notes:
            return ""

        lines = ["Key,Description"]
        # Sort keys for consistent output
        for key in sorted(self.keyed_notes.keys(), key=lambda k: (k.isdigit(), int(k) if k.isdigit() else 0, k)):
            text = self.keyed_notes[key]
            # Escape quotes in CSV
            escaped_text = text.replace('"', '""')
            lines.append(f'"{key}","{escaped_text}"')

        return "\n".join(lines)

    def resolve_collisions(
        self,
        max_iterations: int = 10,
        text_buffer: float = 0.05,
        geometry: "Any | None" = None
    ) -> None:
        """Resolve collisions between annotations.

        Applies strict collision rules:
        1. Annotations NEVER overlap section geometry
        2. Text NEVER overlaps text
        3. Lines NEVER overlap text
        4. Symbols are fixed, text moves around them

        Modifies annotations in place.

        Args:
            max_iterations: Maximum iterations for repositioning
            text_buffer: Buffer distance around text
            geometry: Optional section geometry to avoid during placement
        """
        from .collision import CollisionResolver

        resolver = CollisionResolver(
            max_iterations=max_iterations,
            text_buffer=text_buffer,
            geometry=geometry
        )

        self.annotations = resolver.resolve_all(self.annotations)

    def validate(self) -> list[str]:
        """Validate all annotations in the collection.

        Returns:
            List of all validation errors from all annotations
        """
        all_errors = []

        for i, annotation in enumerate(self.annotations):
            errors = annotation.validate()
            if errors:
                # Prefix with annotation index
                for error in errors:
                    all_errors.append(f"Annotation {i} ({annotation.id}): {error}")

        return all_errors
