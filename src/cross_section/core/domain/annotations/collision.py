"""Collision detection and resolution for annotations."""

from dataclasses import replace
from typing import TYPE_CHECKING

from ...geometry.bounds import BoundingBox
from ...geometry.primitives import Point2D, Polygon
from .base import AnnotationBase
from .dimension import DimensionAnnotation
from .leader import LeaderAnnotation
from .symbol import SymbolAnnotation
from .text import TextAnnotation

if TYPE_CHECKING:
    from ..section import SectionGeometry


def line_segment_intersection(
    p1: Point2D, p2: Point2D, p3: Point2D, p4: Point2D
) -> Point2D | None:
    """Calculate intersection point of two line segments.

    Uses parametric line intersection formula. Pure Python, no dependencies.

    Args:
        p1: First point of line segment 1
        p2: Second point of line segment 1
        p3: First point of line segment 2
        p4: Second point of line segment 2

    Returns:
        Intersection point if segments intersect, None otherwise
    """
    # Direction vectors
    d1x = p2.x - p1.x
    d1y = p2.y - p1.y
    d2x = p4.x - p3.x
    d2y = p4.y - p3.y

    # Denominator for parametric equations
    denom = d1x * d2y - d1y * d2x

    # Parallel lines (or coincident)
    if abs(denom) < 1e-10:
        return None

    # Parametric parameters
    t = ((p3.x - p1.x) * d2y - (p3.y - p1.y) * d2x) / denom
    u = ((p3.x - p1.x) * d1y - (p3.y - p1.y) * d1x) / denom

    # Check if intersection is within both segments
    if 0 <= t <= 1 and 0 <= u <= 1:
        # Calculate intersection point
        ix = p1.x + t * d1x
        iy = p1.y + t * d1y
        return Point2D(ix, iy)

    return None


class CollisionDetector:
    """Detects collisions between annotations."""

    @staticmethod
    def _point_in_polygon(point: Point2D, polygon: Polygon) -> bool:
        """Check if a point is inside a polygon using ray casting."""
        x = point.x
        y = point.y
        inside = False
        vertices = polygon.exterior
        if len(vertices) < 3:
            return False

        j = len(vertices) - 1
        for i in range(len(vertices)):
            xi = vertices[i].x
            yi = vertices[i].y
            xj = vertices[j].x
            yj = vertices[j].y

            intersects = ((yi > y) != (yj > y)) and (
                x < (xj - xi) * (y - yi) / (yj - yi + 1e-12) + xi
            )
            if intersects:
                inside = not inside
            j = i

        return inside

    @staticmethod
    def _annotation_allows_geometry_overlap(annotation: AnnotationBase) -> bool:
        if annotation.metadata.get("allow_geometry_overlap"):
            return True
        if isinstance(annotation, SymbolAnnotation) and annotation.symbol_type == "grade_point":
            return True
        return False

    @staticmethod
    def detect_text_text(
        text1: TextAnnotation,
        text2: TextAnnotation,
        buffer: float = 0.05
    ) -> bool:
        """Check if two text annotations overlap.

        Args:
            text1: First text annotation
            text2: Second text annotation
            buffer: Buffer distance to expand bounds before checking

        Returns:
            True if texts overlap (or are within buffer distance)
        """
        bounds1 = text1.bounds()
        bounds2 = text2.bounds()
        return bounds1.intersects(bounds2, buffer=buffer)

    @staticmethod
    def detect_line_text(
        line: DimensionAnnotation | LeaderAnnotation,
        text: TextAnnotation,
        buffer: float = 0.02
    ) -> bool:
        """Check if a line annotation overlaps text.

        Checks if any line segment intersects the text bounding box.

        Args:
            line: Dimension or leader annotation
            text: Text annotation
            buffer: Buffer distance around text

        Returns:
            True if line overlaps text
        """
        text_bounds = text.bounds().expand(buffer)

        # Get line segments
        if isinstance(line, DimensionAnnotation):
            # Dimension has extension lines and dimension line
            dim_start, dim_end = line.get_dimension_line_endpoints()
            ext_start, ext_end = line.get_extension_line_endpoints()
            segments = [
                (line.start, ext_start),  # Extension 1
                (line.end, ext_end),      # Extension 2
                (dim_start, dim_end),     # Dimension line
            ]
        else:  # LeaderAnnotation
            # Leader is a simple polyline
            segments = []
            for i in range(len(line.points) - 1):
                segments.append((line.points[i], line.points[i + 1]))

        # Check if any segment intersects text box
        for seg_start, seg_end in segments:
            if CollisionDetector._segment_intersects_box(seg_start, seg_end, text_bounds):
                return True

        return False

    @staticmethod
    def _segment_intersects_box(
        p1: Point2D,
        p2: Point2D,
        bounds
    ) -> bool:
        """Check if line segment intersects bounding box.

        Args:
            p1: Segment start point
            p2: Segment end point
            bounds: BoundingBox to check

        Returns:
            True if segment intersects box
        """
        # Check if either endpoint is inside box
        if bounds.contains_point(p1) or bounds.contains_point(p2):
            return True

        # Check if segment intersects any edge of the box
        box_corners = [
            Point2D(bounds.min_x, bounds.min_y),
            Point2D(bounds.max_x, bounds.min_y),
            Point2D(bounds.max_x, bounds.max_y),
            Point2D(bounds.min_x, bounds.max_y),
        ]

        # Check all four edges
        for i in range(4):
            corner1 = box_corners[i]
            corner2 = box_corners[(i + 1) % 4]
            if line_segment_intersection(p1, p2, corner1, corner2):
                return True

        return False

    @staticmethod
    def detect_line_line(
        line1: DimensionAnnotation | LeaderAnnotation,
        line2: DimensionAnnotation | LeaderAnnotation,
    ) -> Point2D | None:
        """Check if two line annotations intersect.

        Args:
            line1: First line annotation
            line2: Second line annotation

        Returns:
            Intersection point if lines intersect, None otherwise
        """
        # Get segments for line1
        if isinstance(line1, DimensionAnnotation):
            dim_start1, dim_end1 = line1.get_dimension_line_endpoints()
            ext_start1, ext_end1 = line1.get_extension_line_endpoints()
            segments1 = [
                (dim_start1, dim_end1),
                (line1.start, ext_start1),
                (line1.end, ext_end1),
            ]
        else:
            segments1 = [
                (line1.points[i], line1.points[i + 1])
                for i in range(len(line1.points) - 1)
            ]

        # Get segments for line2
        if isinstance(line2, DimensionAnnotation):
            dim_start2, dim_end2 = line2.get_dimension_line_endpoints()
            ext_start2, ext_end2 = line2.get_extension_line_endpoints()
            segments2 = [
                (dim_start2, dim_end2),
                (line2.start, ext_start2),
                (line2.end, ext_end2),
            ]
        else:
            segments2 = [
                (line2.points[i], line2.points[i + 1])
                for i in range(len(line2.points) - 1)
            ]

        # Check all segment pairs
        for seg1_start, seg1_end in segments1:
            for seg2_start, seg2_end in segments2:
                intersection = line_segment_intersection(
                    seg1_start, seg1_end, seg2_start, seg2_end
                )
                if intersection:
                    return intersection

        return None

    @staticmethod
    def detect_symbol_dimension(
        symbol: SymbolAnnotation,
        dimension: DimensionAnnotation,
        buffer: float = 0.05
    ) -> bool:
        """Check if a symbol overlaps a dimension line.

        Args:
            symbol: Symbol annotation
            dimension: Dimension annotation
            buffer: Buffer distance around symbol

        Returns:
            True if symbol overlaps dimension
        """
        symbol_bounds = symbol.bounds().expand(buffer)
        dim_start, dim_end = dimension.get_dimension_line_endpoints()
        ext_start, ext_end = dimension.get_extension_line_endpoints()

        # Check if dimension line intersects symbol box
        if CollisionDetector._segment_intersects_box(dim_start, dim_end, symbol_bounds):
            return True

        # Check if extension lines intersect symbol box
        if CollisionDetector._segment_intersects_box(dimension.start, ext_start, symbol_bounds):
            return True
        if CollisionDetector._segment_intersects_box(dimension.end, ext_end, symbol_bounds):
            return True

        # Check if symbol overlaps text
        if dimension.text_position:
            # Estimate text bounds (simplified)
            text_width = len(dimension.dimension_text or "") * 0.12 * 0.6
            text_height = 0.12
            text_bounds_min_x = dimension.text_position.x - text_width / 2
            text_bounds_max_x = dimension.text_position.x + text_width / 2
            text_bounds_min_y = dimension.text_position.y - text_height / 2
            text_bounds_max_y = dimension.text_position.y + text_height / 2

            # Check if symbol overlaps dimension text
            if not (symbol_bounds.max_x < text_bounds_min_x or
                    symbol_bounds.min_x > text_bounds_max_x or
                    symbol_bounds.max_y < text_bounds_min_y or
                    symbol_bounds.min_y > text_bounds_max_y):
                return True

        return False

    @staticmethod
    def detect_symbol_leader(
        symbol: SymbolAnnotation,
        leader: LeaderAnnotation,
        buffer: float = 0.05
    ) -> bool:
        """Check if a symbol overlaps a leader line or leader text."""
        symbol_bounds = symbol.bounds().expand(buffer)

        # Check if any leader point is inside the symbol bounds
        for point in leader.points:
            if symbol_bounds.contains_point(point):
                return True

        # Check if any leader segment intersects symbol bounds
        for i in range(len(leader.points) - 1):
            if CollisionDetector._segment_intersects_box(
                leader.points[i],
                leader.points[i + 1],
                symbol_bounds
            ):
                return True

        # Check leader text bounds against symbol bounds
        if symbol_bounds.intersects(leader.bounds(), buffer=0.0):
            return True

        return False

    @staticmethod
    def detect_text_leader_line(
        text: TextAnnotation,
        leader: LeaderAnnotation,
        buffer: float = 0.02
    ) -> bool:
        """Check if text overlaps with its own leader line.

        This prevents leader text from overlapping the leader polyline.

        Args:
            text: Text annotation
            leader: Leader annotation
            buffer: Buffer distance

        Returns:
            True if text overlaps leader line
        """
        text_bounds = text.bounds().expand(buffer)

        # Check each segment of the leader
        for i in range(len(leader.points) - 1):
            if CollisionDetector._segment_intersects_box(
                leader.points[i],
                leader.points[i + 1],
                text_bounds
            ):
                return True

        return False

    @staticmethod
    def detect_annotation_geometry(
        annotation: AnnotationBase,
        geometry: "SectionGeometry",
        buffer: float = 0.02
    ) -> bool:
        """Check if an annotation overlaps with section geometry.

        Args:
            annotation: Annotation to check
            geometry: Section geometry to check against
            buffer: Buffer distance around annotation

        Returns:
            True if annotation overlaps geometry
        """
        if CollisionDetector._annotation_allows_geometry_overlap(annotation):
            return False

        ann_bounds = annotation.bounds().expand(buffer)
        ann_center = ann_bounds.center()
        ann_corners = [
            Point2D(ann_bounds.min_x, ann_bounds.min_y),
            Point2D(ann_bounds.max_x, ann_bounds.min_y),
            Point2D(ann_bounds.max_x, ann_bounds.max_y),
            Point2D(ann_bounds.min_x, ann_bounds.max_y),
        ]

        # Check against all geometry components
        for component in geometry.components:
            # Check polygons
            for polygon in component.polygons:
                # Check if any polygon edge intersects annotation bounds
                for i in range(len(polygon.exterior)):
                    p1 = polygon.exterior[i]
                    p2 = polygon.exterior[(i + 1) % len(polygon.exterior)]

                    if CollisionDetector._segment_intersects_box(p1, p2, ann_bounds):
                        return True

                    # Also check if polygon vertices fall inside the annotation bounds
                    if ann_bounds.contains_point(p1):
                        return True

                # Check if annotation bounds are inside polygon
                if CollisionDetector._point_in_polygon(ann_center, polygon):
                    return True
                for corner in ann_corners:
                    if CollisionDetector._point_in_polygon(corner, polygon):
                        return True

            # Check polylines (surface slopes, etc.)
            for polyline in component.polylines:
                for i in range(len(polyline) - 1):
                    if CollisionDetector._segment_intersects_box(
                        polyline[i],
                        polyline[i + 1],
                        ann_bounds
                    ):
                        return True

        return False


class CollisionResolver:
    """Resolves annotation collisions following strict rules.

    Rules (in priority order):
    1. Annotations NEVER overlap section geometry → reposition annotations
    2. Text NEVER overlaps text → reposition lower priority text
    3. Lines NEVER overlap text → reposition text (not lines)
    4. Lines can overlap lines → add gap at intersection
    5. Symbols are fixed → text repositions around them
    """

    def __init__(
        self,
        max_iterations: int = 10,
        text_buffer: float = 0.05,
        geometry: "SectionGeometry | None" = None,
        overflow_band_offset: float = 0.5,
        overflow_band_padding: float = 0.5,
        overflow_band_gap: float = 0.1,
    ):
        """Initialize collision resolver.

        Args:
            max_iterations: Maximum iterations for repositioning
            text_buffer: Buffer distance around text for collision detection
            geometry: Optional section geometry to avoid during placement
        """
        self.max_iterations = max_iterations
        self.text_buffer = text_buffer
        self.geometry = geometry
        self.overflow_band_offset = overflow_band_offset
        self.overflow_band_padding = overflow_band_padding
        self.overflow_band_gap = overflow_band_gap

    def resolve_all(self, annotations: list[AnnotationBase]) -> list[AnnotationBase]:
        """Resolve all collisions in annotation list.

        Args:
            annotations: List of annotations to resolve

        Returns:
            New list with collisions resolved
        """
        resolved = list(annotations)  # Copy list

        # Iteration counter to prevent infinite loops
        for iteration in range(self.max_iterations):
            changed = False

            # Rule 0: Geometry collisions (reposition annotations away from geometry)
            if self.geometry:
                changed |= self._resolve_geometry_collisions(resolved)

            # Rule 1: Symbol-dimension collisions (reposition symbol vertically)
            changed |= self._resolve_symbol_dimension_collisions(resolved)

            # Rule 1b: Leader-leader collisions (reposition leader text)
            changed |= self._resolve_leader_leader_collisions(resolved)

            # Rule 2: Text-text collisions (reposition lower priority)
            changed |= self._resolve_text_text_collisions(resolved)

            # Rule 3: Line-text collisions (reposition text)
            changed |= self._resolve_line_text_collisions(resolved)

            # Rule 4: Line-line collisions (add gaps - not implemented in this pass)
            # This would require modifying line geometry, which is complex
            # For now, we detect but don't resolve line-line collisions

            if not changed:
                # No changes in this iteration, we're done
                break

        # Final pass: move any remaining collisions into overflow band
        self._force_overflow_band(resolved)

        return resolved

    def _is_fixed(self, annotation: AnnotationBase) -> bool:
        return bool(annotation.metadata.get("fixed"))

    def _resolve_geometry_collisions(
        self,
        annotations: list[AnnotationBase]
    ) -> bool:
        """Resolve annotation-geometry collisions by repositioning annotations.

        Args:
            annotations: List of annotations (modified in place)

        Returns:
            True if any changes were made
        """
        if not self.geometry:
            return False

        changed = False

        for idx, annotation in enumerate(annotations):
            if self._is_fixed(annotation):
                continue
            # Check if annotation overlaps geometry
            if CollisionDetector.detect_annotation_geometry(
                annotation, self.geometry, buffer=0.02
            ):
                # Try to reposition the annotation
                # For text annotations, use the existing positioning logic
                if isinstance(annotation, TextAnnotation):
                    new_pos = self._find_valid_text_position(
                        annotation, annotations, idx
                    )
                    if new_pos:
                        offset = Point2D(
                            new_pos.x - annotation.position.x,
                            new_pos.y - annotation.position.y
                        )
                        annotations[idx] = annotation.reposition(offset)
                        changed = True
                elif isinstance(annotation, SymbolAnnotation):
                    new_pos = self._find_valid_symbol_position(
                        annotation, annotations, idx
                    )
                    if new_pos:
                        offset = Point2D(
                            new_pos.x - annotation.position.x,
                            new_pos.y - annotation.position.y
                        )
                        annotations[idx] = annotation.reposition(offset)
                        changed = True
                # For other annotation types, try simple vertical repositioning
                elif hasattr(annotation, 'reposition'):
                    offset_options = [
                        Point2D(0, 0.15),   # Move up
                        Point2D(0, -0.15),  # Move down
                        Point2D(0.15, 0),   # Move right
                        Point2D(-0.15, 0),  # Move left
                        Point2D(0, 0.30),   # Move further up
                        Point2D(0, -0.30),  # Move further down
                    ]

                    for offset in offset_options:
                        new_annotation = annotation.reposition(offset)
                        # Check if new position still collides with geometry
                        if not CollisionDetector.detect_annotation_geometry(
                            new_annotation, self.geometry, buffer=0.02
                        ):
                            annotations[idx] = new_annotation
                            changed = True
                            break

        return changed

    def _resolve_symbol_dimension_collisions(
        self,
        annotations: list[AnnotationBase]
    ) -> bool:
        """Resolve symbol-dimension collisions by repositioning symbols.

        Symbols that overlap dimensions are moved vertically to avoid the conflict.

        Args:
            annotations: List of annotations (modified in place)

        Returns:
            True if any changes were made
        """
        changed = False

        # Get symbols and dimensions
        symbol_indices = [
            (i, ann) for i, ann in enumerate(annotations)
            if isinstance(ann, SymbolAnnotation)
        ]
        dimension_indices = [
            (i, ann) for i, ann in enumerate(annotations)
            if isinstance(ann, DimensionAnnotation)
        ]

        for idx, symbol in symbol_indices:
            if self._is_fixed(symbol):
                continue
            for dim_idx, dimension in dimension_indices:
                if CollisionDetector.detect_symbol_dimension(symbol, dimension, buffer=0.05):
                    if not self._is_fixed(dimension):
                        candidate_dimension = self._find_valid_dimension_offset(
                            dimension, annotations, dim_idx
                        )
                        if candidate_dimension:
                            annotations[dim_idx] = candidate_dimension
                            dimension = candidate_dimension
                            for di, (stored_idx, _stored_dim) in enumerate(dimension_indices):
                                if stored_idx == dim_idx:
                                    dimension_indices[di] = (dim_idx, candidate_dimension)
                                    break
                            changed = True
                            if not CollisionDetector.detect_symbol_dimension(
                                symbol, dimension, buffer=0.05
                            ):
                                continue

                    # Collision detected - move symbol down by small amount
                    # Try moving down first (away from dimension text which is usually above)
                    offset_options = [
                        Point2D(0, -0.15),  # Move down
                        Point2D(0, -0.30),  # Move further down
                        Point2D(0, 0.15),   # Move up (if down doesn't work)
                    ]

                    for offset in offset_options:
                        new_symbol = symbol.reposition(offset)

                        # Check if new position still collides
                        still_collides = False
                        for _, dim in dimension_indices:
                            if CollisionDetector.detect_symbol_dimension(new_symbol, dim, buffer=0.05):
                                still_collides = True
                                break

                        if not still_collides:
                            annotations[idx] = new_symbol
                            changed = True
                            break  # Found valid position

        return changed

    def _resolve_text_text_collisions(
        self,
        annotations: list[AnnotationBase]
    ) -> bool:
        """Resolve text-text collisions by repositioning lower priority text.

        Args:
            annotations: List of annotations (modified in place)

        Returns:
            True if any changes were made
        """
        text_annotations = [
            (i, ann) for i, ann in enumerate(annotations)
            if isinstance(ann, TextAnnotation)
        ]

        changed = False

        # Check all pairs
        for i, (idx1, text1) in enumerate(text_annotations):
            for idx2, text2 in text_annotations[i + 1:]:
                if CollisionDetector.detect_text_text(
                    text1, text2, buffer=self.text_buffer
                ):
                    # Collision detected - reposition lower priority text
                    if self._is_fixed(text1) and self._is_fixed(text2):
                        continue
                    if self._is_fixed(text1):
                        move_idx, move_text = idx2, text2
                    elif self._is_fixed(text2):
                        move_idx, move_text = idx1, text1
                    elif text1.priority >= text2.priority:
                        move_idx, move_text = idx2, text2
                    else:
                        move_idx, move_text = idx1, text1

                    if move_idx == idx2:
                        # Reposition text2
                        new_pos = self._find_valid_text_position(
                            move_text, annotations, move_idx
                        )
                        if new_pos:
                            offset = Point2D(
                                new_pos.x - move_text.position.x,
                                new_pos.y - move_text.position.y
                            )
                            annotations[move_idx] = move_text.reposition(offset)
                            changed = True

        return changed

    def _resolve_line_text_collisions(
        self,
        annotations: list[AnnotationBase]
    ) -> bool:
        """Resolve line-text collisions by repositioning text.

        Args:
            annotations: List of annotations (modified in place)

        Returns:
            True if any changes were made
        """
        changed = False

        # Get line and text annotations
        lines = [
            ann for ann in annotations
            if isinstance(ann, (DimensionAnnotation, LeaderAnnotation))
        ]
        text_indices = [
            (i, ann) for i, ann in enumerate(annotations)
            if isinstance(ann, TextAnnotation)
        ]

        for line in lines:
            for idx, text in text_indices:
                if self._is_fixed(text):
                    continue
                if CollisionDetector.detect_line_text(line, text, buffer=0.02):
                    # Collision detected - reposition text
                    new_pos = self._find_valid_text_position(
                        text, annotations, idx
                    )
                    if new_pos:
                        offset = Point2D(
                            new_pos.x - text.position.x,
                            new_pos.y - text.position.y
                        )
                        annotations[idx] = text.reposition(offset)
                        changed = True

        return changed

    def _resolve_leader_leader_collisions(
        self,
        annotations: list[AnnotationBase]
    ) -> bool:
        """Resolve leader-leader collisions by repositioning the lower priority leader."""
        leaders = [
            (i, ann) for i, ann in enumerate(annotations)
            if isinstance(ann, LeaderAnnotation)
        ]
        changed = False

        for i, (idx1, leader1) in enumerate(leaders):
            for idx2, leader2 in leaders[i + 1:]:
                if not CollisionDetector.detect_line_line(leader1, leader2):
                    continue
                if self._is_fixed(leader1) and self._is_fixed(leader2):
                    continue

                if self._is_fixed(leader1):
                    move_idx, move_leader = idx2, leader2
                elif self._is_fixed(leader2):
                    move_idx, move_leader = idx1, leader1
                elif leader1.priority >= leader2.priority:
                    move_idx, move_leader = idx2, leader2
                else:
                    move_idx, move_leader = idx1, leader1

                new_pos = self._find_valid_leader_position(
                    move_leader, annotations, move_idx
                )
                if new_pos:
                    text_pos = move_leader.get_text_position()
                    offset = Point2D(
                        new_pos.x - text_pos.x,
                        new_pos.y - text_pos.y
                    )
                    annotations[move_idx] = move_leader.reposition(offset)
                    changed = True

        return changed

    def _find_valid_leader_position(
        self,
        leader: LeaderAnnotation,
        all_annotations: list[AnnotationBase],
        leader_index: int
    ) -> Point2D | None:
        """Find a valid text position for a leader without overlaps."""
        text_pos = leader.get_text_position()
        probe_text = TextAnnotation(
            position=text_pos,
            text=leader.text,
            font_size=leader.text_size,
            anchor=leader.text_anchor,
        )
        candidates = self._generate_text_candidates(probe_text)

        for candidate_pos in candidates:
            offset = Point2D(
                candidate_pos.x - text_pos.x,
                candidate_pos.y - text_pos.y
            )
            candidate = leader.reposition(offset)
            if self._has_leader_collision(candidate, all_annotations, leader_index):
                continue
            return candidate_pos

        return None

    def _has_leader_collision(
        self,
        candidate: LeaderAnnotation,
        all_annotations: list[AnnotationBase],
        leader_index: int
    ) -> bool:
        if self.geometry:
            if CollisionDetector.detect_annotation_geometry(candidate, self.geometry, buffer=0.02):
                return True

        for i, other in enumerate(all_annotations):
            if i == leader_index:
                continue

            if isinstance(other, LeaderAnnotation):
                if CollisionDetector.detect_line_line(candidate, other):
                    return True

            if isinstance(other, DimensionAnnotation):
                if CollisionDetector.detect_line_line(candidate, other):
                    return True

            if isinstance(other, TextAnnotation):
                if CollisionDetector.detect_line_text(candidate, other, buffer=0.02):
                    return True
                if candidate.bounds().intersects(other.bounds(), buffer=self.text_buffer):
                    return True

            if isinstance(other, SymbolAnnotation):
                if candidate.bounds().intersects(other.bounds(), buffer=self.text_buffer):
                    return True

        return False

    def _find_valid_text_position(
        self,
        text: TextAnnotation,
        all_annotations: list[AnnotationBase],
        text_index: int
    ) -> Point2D | None:
        """Find optimal position for text using candidate scoring.

        Generates multiple candidate positions and scores each based on:
        - Distance from obstacles (higher score = further from obstacles)
        - Distance from original position (lower score = closer to original)
        - Readability preference (horizontal directions preferred)

        Inspired by bin packing heuristics - evaluate all candidates and pick best.

        Args:
            text: Text annotation to reposition
            all_annotations: All annotations (for collision checking)
            text_index: Index of text in all_annotations

        Returns:
            Best valid position, or None if no valid position found
        """
        # Generate candidate positions
        candidates = self._generate_text_candidates(text)

        # Score each candidate
        scored_candidates = []
        for candidate_pos in candidates:
            candidate = text.reposition(Point2D(
                candidate_pos.x - text.position.x,
                candidate_pos.y - text.position.y
            ))

            # Check for hard collisions
            if self._has_collision(candidate, all_annotations, text_index):
                continue  # Skip invalid candidates

            # Score this candidate
            score = self._score_text_position(
                candidate,
                text.position,  # Original position
                all_annotations,
                text_index
            )
            scored_candidates.append((score, candidate_pos))

        if not scored_candidates:
            return None  # No valid positions

        # Return best candidate (highest score)
        scored_candidates.sort(key=lambda x: x[0], reverse=True)
        return scored_candidates[0][1]

    def _find_valid_symbol_position(
        self,
        symbol: SymbolAnnotation,
        all_annotations: list[AnnotationBase],
        symbol_index: int
    ) -> Point2D | None:
        """Find a valid position for a symbol using candidate offsets."""
        candidates = self._generate_symbol_candidates(symbol)

        for candidate_pos in candidates:
            candidate = symbol.reposition(Point2D(
                candidate_pos.x - symbol.position.x,
                candidate_pos.y - symbol.position.y
            ))
            if self._has_symbol_collision(candidate, all_annotations, symbol_index):
                continue
            return candidate_pos

        return None

    def _find_valid_dimension_offset(
        self,
        dimension: DimensionAnnotation,
        all_annotations: list[AnnotationBase],
        dimension_index: int
    ) -> DimensionAnnotation | None:
        """Increase dimension offset to create clearance for symbols."""
        offset_increments = [0.15, 0.30, 0.45, 0.60, 0.80]

        for inc in offset_increments:
            new_offset = dimension.offset + inc
            candidate = replace(dimension, offset=new_offset, text_position=None)
            if not self._has_dimension_collision(candidate, all_annotations, dimension_index):
                return candidate

        return None

    def _has_dimension_collision(
        self,
        candidate: DimensionAnnotation,
        all_annotations: list[AnnotationBase],
        dimension_index: int
    ) -> bool:
        if self.geometry:
            if CollisionDetector.detect_annotation_geometry(candidate, self.geometry, buffer=0.02):
                return True

        candidate_text_bounds = self._dimension_text_bounds(candidate)

        for i, other in enumerate(all_annotations):
            if i == dimension_index:
                continue

            if isinstance(other, TextAnnotation):
                if CollisionDetector.detect_line_text(candidate, other, buffer=0.02):
                    return True
                if candidate_text_bounds and candidate_text_bounds.intersects(
                    other.bounds(), buffer=self.text_buffer
                ):
                    return True

            if isinstance(other, SymbolAnnotation):
                if CollisionDetector.detect_symbol_dimension(other, candidate, buffer=0.02):
                    return True

            if isinstance(other, LeaderAnnotation):
                if CollisionDetector.detect_line_line(candidate, other):
                    return True
                if candidate_text_bounds and candidate_text_bounds.intersects(
                    other.bounds(), buffer=self.text_buffer
                ):
                    return True

            if isinstance(other, DimensionAnnotation):
                if CollisionDetector.detect_line_line(candidate, other):
                    return True

        return False

    def _generate_symbol_candidates(self, symbol: SymbolAnnotation) -> list[Point2D]:
        """Generate candidate positions for symbol placement."""
        candidates = [symbol.position]
        offset_increments = [0.10, 0.20, 0.30, 0.45, 0.60, 0.80]

        for inc in offset_increments:
            candidates.extend([
                Point2D(symbol.position.x, symbol.position.y + inc),
                Point2D(symbol.position.x, symbol.position.y - inc),
                Point2D(symbol.position.x + inc, symbol.position.y),
                Point2D(symbol.position.x - inc, symbol.position.y),
                Point2D(symbol.position.x + inc, symbol.position.y + inc),
                Point2D(symbol.position.x + inc, symbol.position.y - inc),
                Point2D(symbol.position.x - inc, symbol.position.y + inc),
                Point2D(symbol.position.x - inc, symbol.position.y - inc),
            ])

        return candidates

    def _has_symbol_collision(
        self,
        candidate: SymbolAnnotation,
        all_annotations: list[AnnotationBase],
        symbol_index: int
    ) -> bool:
        if self.geometry:
            if CollisionDetector.detect_annotation_geometry(candidate, self.geometry, buffer=0.02):
                return True

        candidate_bounds = candidate.bounds()

        for i, other in enumerate(all_annotations):
            if i == symbol_index:
                continue

            if isinstance(other, SymbolAnnotation):
                if candidate_bounds.intersects(other.bounds(), buffer=self.text_buffer):
                    return True

            if isinstance(other, TextAnnotation):
                if candidate_bounds.intersects(other.bounds(), buffer=self.text_buffer):
                    return True

            if isinstance(other, DimensionAnnotation):
                if CollisionDetector.detect_symbol_dimension(candidate, other, buffer=0.02):
                    return True

            if isinstance(other, LeaderAnnotation):
                if CollisionDetector.detect_symbol_leader(candidate, other, buffer=0.02):
                    return True

        return False

    def _generate_text_candidates(self, text: TextAnnotation) -> list[Point2D]:
        """Generate candidate positions for text placement.

        Uses multiple offset distances and directions to create a grid
        of potential positions.

        Args:
            text: Text annotation

        Returns:
            List of candidate positions
        """
        candidates = [text.position]  # Include original position

        # Multiple offset distances (inspired by bin packing - try multiple "bins")
        offset_increments = [0.08, 0.15, 0.25, 0.40, 0.60]

        for inc in offset_increments:
            # Cardinal directions (preferred for readability)
            candidates.extend([
                Point2D(text.position.x, text.position.y + inc),      # Up
                Point2D(text.position.x, text.position.y - inc),      # Down
                Point2D(text.position.x + inc, text.position.y),      # Right
                Point2D(text.position.x - inc, text.position.y),      # Left
            ])

            # Diagonals (secondary options)
            candidates.extend([
                Point2D(text.position.x + inc, text.position.y + inc),
                Point2D(text.position.x + inc, text.position.y - inc),
                Point2D(text.position.x - inc, text.position.y + inc),
                Point2D(text.position.x - inc, text.position.y - inc),
            ])

        return candidates

    def _has_collision(
        self,
        candidate: TextAnnotation,
        all_annotations: list[AnnotationBase],
        text_index: int
    ) -> bool:
        """Check if candidate position has any collisions.

        Args:
            candidate: Candidate text annotation
            all_annotations: All annotations
            text_index: Index of original text

        Returns:
            True if candidate has collision
        """
        # Check for geometry collision first (highest priority)
        if self.geometry:
            if CollisionDetector.detect_annotation_geometry(
                candidate,
                self.geometry,
                buffer=0.02
            ):
                return True

        for i, other in enumerate(all_annotations):
            if i == text_index:
                continue  # Skip self

            # Text-text collision
            if isinstance(other, TextAnnotation):
                if CollisionDetector.detect_text_text(
                    candidate,
                    other,
                    buffer=self.text_buffer
                ):
                    return True

            # Line-text collision
            if isinstance(other, (DimensionAnnotation, LeaderAnnotation)):
                if CollisionDetector.detect_line_text(
                    other,
                    candidate,
                    buffer=0.02
                ):
                    return True
                if isinstance(other, LeaderAnnotation):
                    if other.bounds().intersects(candidate.bounds(), buffer=self.text_buffer):
                        return True

            # Symbol-text collision (symbols are fixed)
            if isinstance(other, SymbolAnnotation):
                symbol_bounds = other.bounds()
                text_bounds = candidate.bounds()
                if symbol_bounds.intersects(text_bounds, buffer=self.text_buffer):
                    return True

        return False

    def _score_text_position(
        self,
        candidate: TextAnnotation,
        original_pos: Point2D,
        all_annotations: list[AnnotationBase],
        text_index: int
    ) -> float:
        """Score a candidate text position.

        Higher score is better. Scoring factors:
        - Proximity to original position (closer is better)
        - Distance from obstacles (further is better)
        - Direction preference (up/right preferred over down/left)

        Args:
            candidate: Candidate text annotation
            original_pos: Original text position
            all_annotations: All annotations
            text_index: Index of original text

        Returns:
            Score (higher is better)
        """
        score = 100.0  # Base score

        # Factor 1: Distance from original position (penalize large moves)
        dx = candidate.position.x - original_pos.x
        dy = candidate.position.y - original_pos.y
        distance_from_original = (dx * dx + dy * dy) ** 0.5
        score -= distance_from_original * 10.0  # Penalty for moving far

        # Factor 2: Direction preference (prefer up and right for readability)
        if dy > 0:  # Moving up
            score += 5.0
        if dx > 0:  # Moving right
            score += 3.0

        # Factor 3: Clearance from other annotations (bonus for extra space)
        min_clearance = float('inf')
        candidate_bounds = candidate.bounds()

        for i, other in enumerate(all_annotations):
            if i == text_index:
                continue

            other_bounds = other.bounds()

            # Calculate distance between bounds (simplified)
            # Distance is 0 if overlapping, positive otherwise
            dx_bounds = max(0, max(
                other_bounds.min_x - candidate_bounds.max_x,
                candidate_bounds.min_x - other_bounds.max_x
            ))
            dy_bounds = max(0, max(
                other_bounds.min_y - candidate_bounds.max_y,
                candidate_bounds.min_y - other_bounds.max_y
            ))
            clearance = (dx_bounds * dx_bounds + dy_bounds * dy_bounds) ** 0.5

            min_clearance = min(min_clearance, clearance)

        # Bonus for having good clearance
        score += min(min_clearance * 20.0, 30.0)

        return score

    def _dimension_text_bounds(self, dimension: DimensionAnnotation):
        if not dimension.text_position or not dimension.dimension_text:
            return None
        text_width = len(dimension.dimension_text) * dimension.text_size * 0.6
        text_height = dimension.text_size
        return BoundingBox(
            min_x=dimension.text_position.x - text_width / 2,
            min_y=dimension.text_position.y - text_height / 2,
            max_x=dimension.text_position.x + text_width / 2,
            max_y=dimension.text_position.y + text_height / 2,
        )

    def _force_overflow_band(self, annotations: list[AnnotationBase]) -> None:
        colliding_indices = self._collect_colliding_indices(annotations)
        if not colliding_indices:
            return

        band_min_x, band_max_x, band_base_y = self._overflow_band_bounds(annotations)
        self._pack_in_band(annotations, colliding_indices, band_min_x, band_max_x, band_base_y)

    def _collect_colliding_indices(
        self, annotations: list[AnnotationBase]
    ) -> list[int]:
        colliding: list[int] = []
        for idx, annotation in enumerate(annotations):
            if self._is_fixed(annotation):
                continue
            if not isinstance(annotation, (TextAnnotation, SymbolAnnotation)):
                continue
            if self._annotation_has_collision(annotation, annotations, idx):
                colliding.append(idx)
        return colliding

    def _annotation_has_collision(
        self,
        annotation: AnnotationBase,
        annotations: list[AnnotationBase],
        annotation_index: int
    ) -> bool:
        if self.geometry:
            if CollisionDetector.detect_annotation_geometry(
                annotation, self.geometry, buffer=0.02
            ):
                return True

        for i, other in enumerate(annotations):
            if i == annotation_index:
                continue

            if isinstance(annotation, TextAnnotation):
                if isinstance(other, TextAnnotation):
                    if CollisionDetector.detect_text_text(annotation, other, buffer=self.text_buffer):
                        return True
                if isinstance(other, (DimensionAnnotation, LeaderAnnotation)):
                    if CollisionDetector.detect_line_text(other, annotation, buffer=0.02):
                        return True
                    if other.bounds().intersects(annotation.bounds(), buffer=self.text_buffer):
                        return True
                if isinstance(other, SymbolAnnotation):
                    if annotation.bounds().intersects(other.bounds(), buffer=self.text_buffer):
                        return True
            elif isinstance(annotation, SymbolAnnotation):
                if isinstance(other, DimensionAnnotation):
                    if CollisionDetector.detect_symbol_dimension(annotation, other, buffer=0.02):
                        return True
                if isinstance(other, LeaderAnnotation):
                    if CollisionDetector.detect_symbol_leader(annotation, other, buffer=0.02):
                        return True
                if isinstance(other, (TextAnnotation, SymbolAnnotation)):
                    if annotation.bounds().intersects(other.bounds(), buffer=self.text_buffer):
                        return True
                else:
                    if annotation.bounds().intersects(other.bounds(), buffer=self.text_buffer):
                        return True

        return False

    def _overflow_band_bounds(
        self, annotations: list[AnnotationBase]
    ) -> tuple[float, float, float]:
        bounds = [ann.bounds() for ann in annotations]
        min_x = min(b.min_x for b in bounds)
        max_x = max(b.max_x for b in bounds)
        max_y = max(b.max_y for b in bounds)

        if self.geometry:
            geom_min_x, _geom_min_y, geom_max_x, geom_max_y = self.geometry.bounds()
            min_x = min(min_x, geom_min_x)
            max_x = max(max_x, geom_max_x)
            max_y = max(max_y, geom_max_y)

        band_min_x = min_x - self.overflow_band_padding
        band_max_x = max_x + self.overflow_band_padding
        band_base_y = max_y + self.overflow_band_offset

        return band_min_x, band_max_x, band_base_y

    def _pack_in_band(
        self,
        annotations: list[AnnotationBase],
        indices: list[int],
        band_min_x: float,
        band_max_x: float,
        band_base_y: float
    ) -> None:
        indices_sorted = sorted(indices, key=lambda i: annotations[i].priority)
        cursor_x = band_min_x
        row_y = band_base_y
        row_height = 0.0
        band_width = max(band_max_x - band_min_x, 0.01)

        for idx in indices_sorted:
            annotation = annotations[idx]
            bounds = annotation.bounds()
            width = bounds.width()
            height = bounds.height()

            if cursor_x > band_min_x and cursor_x + width > band_max_x:
                row_y += row_height + self.overflow_band_gap
                cursor_x = band_min_x
                row_height = 0.0

            if width > band_width:
                cursor_x = band_min_x

            desired_center = Point2D(
                cursor_x + width / 2,
                row_y + height / 2
            )
            current_center = bounds.center()
            offset = Point2D(
                desired_center.x - current_center.x,
                desired_center.y - current_center.y
            )
            annotations[idx] = annotation.reposition(offset)

            cursor_x += width + self.overflow_band_gap
            row_height = max(row_height, height)
