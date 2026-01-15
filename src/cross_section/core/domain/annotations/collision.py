"""Collision detection and resolution for annotations."""

from typing import TYPE_CHECKING, cast

from ...geometry.primitives import Point2D
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
            segments = [
                (line.start, dim_start),  # Extension 1
                (line.end, dim_end),      # Extension 2
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
            segments1 = [(dim_start1, dim_end1)]  # Just dimension line for simplicity
        else:
            segments1 = [
                (line1.points[i], line1.points[i + 1])
                for i in range(len(line1.points) - 1)
            ]

        # Get segments for line2
        if isinstance(line2, DimensionAnnotation):
            dim_start2, dim_end2 = line2.get_dimension_line_endpoints()
            segments2 = [(dim_start2, dim_end2)]
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

        # Check if dimension line intersects symbol box
        if CollisionDetector._segment_intersects_box(dim_start, dim_end, symbol_bounds):
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
        ann_bounds = annotation.bounds().expand(buffer)

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

                    # Also check if annotation center is inside polygon
                    # (simplified point-in-polygon test)
                    if ann_bounds.contains_point(p1):
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
        geometry: "SectionGeometry | None" = None
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

        return resolved

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
        dimensions = [
            ann for ann in annotations
            if isinstance(ann, DimensionAnnotation)
        ]

        for idx, symbol in symbol_indices:
            for dimension in dimensions:
                if CollisionDetector.detect_symbol_dimension(symbol, dimension, buffer=0.05):
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
                        for dim in dimensions:
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
                    if text1.priority >= text2.priority:
                        # Reposition text2
                        new_pos = self._find_valid_text_position(
                            text2, annotations, idx2
                        )
                        if new_pos:
                            offset = Point2D(
                                new_pos.x - text2.position.x,
                                new_pos.y - text2.position.y
                            )
                            annotations[idx2] = text2.reposition(offset)
                            changed = True
                    else:
                        # Reposition text1
                        new_pos = self._find_valid_text_position(
                            text1, annotations, idx1
                        )
                        if new_pos:
                            offset = Point2D(
                                new_pos.x - text1.position.x,
                                new_pos.y - text1.position.y
                            )
                            annotations[idx1] = text1.reposition(offset)
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
