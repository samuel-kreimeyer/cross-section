"""Plan annotations from guides and profiles."""

from dataclasses import dataclass

from ...geometry.primitives import ComponentGeometry, Point2D
from ..section import SectionGeometry
from .container import AnnotationCollection
from .dimension import DimensionAnnotation
from .guides import AnnotationGuide, AnnotationGuideRegistry, DEFAULT_GUIDE_REGISTRY
from .leader import LeaderAnnotation
from .profile import AnnotationProfile, format_dimension
from .symbol import SymbolAnnotation
from .text import TextAnnotation
from .zones import (
    AnnotationZone,
    ZONE_BASE_OFFSETS,
    SYMBOL_CLEARANCE_BUFFER,
    compute_dimension_offset_for_span,
)


@dataclass(frozen=True)
class _AnchorPoints:
    center: Point2D
    top_center: Point2D
    left_top: Point2D
    right_top: Point2D


@dataclass
class _SymbolPlacement:
    """Planned symbol placement before final generation."""

    component_index: int
    symbol_type: str
    position: Point2D
    angle: float
    scale: float
    layer: str
    priority: int


@dataclass
class _PlannedDimension:
    """Planned dimension before alignment computation."""

    start: Point2D
    end: Point2D
    text: str
    component_indices: frozenset[int]  # Which components this dimension covers
    base_y: float  # The y position of the component top (for offset computation)
    span_level: int = 0  # 0 = single component, 1+ = spanning dimensions
    label_text: str | None = None  # Component label to pair below dimension line


class AnnotationPlanner:
    """Translate guide intent into concrete annotations.

    Uses two-pass planning for optimal placement:
    1. Pass 1 (Symbol pre-scan): Identify all symbols that will be placed
    2. Pass 2 (Annotation generation): Generate annotations with computed offsets
    """

    def __init__(self, registry: AnnotationGuideRegistry | None = None) -> None:
        self._registry = registry or DEFAULT_GUIDE_REGISTRY

    def plan(
        self,
        section_geometry: SectionGeometry,
        profile: AnnotationProfile,
    ) -> AnnotationCollection:
        collection = AnnotationCollection()

        if profile.include_centerpoint_mark:
            self._add_centerpoint_mark(section_geometry, collection)

        # Pass 1: Pre-scan for symbols to determine placement needs
        planned_symbols = self._prescan_symbols(section_geometry, profile)

        # Build index of symbols by component for offset computation
        symbols_by_component: dict[int, list[_SymbolPlacement]] = {}
        for ps in planned_symbols:
            symbols_by_component.setdefault(ps.component_index, []).append(ps)

        # Pass 2: Collect planned dimensions (before alignment)
        # Use section top as common reference for all dimensions
        section_bounds = section_geometry.bounds()
        section_top = section_bounds[3] if section_bounds else 0.0

        planned_dimensions: list[_PlannedDimension] = []
        for comp_idx, component in enumerate(section_geometry.components):
            component_type = component.metadata.get("component_type", "Component")
            guides = self._registry.get_guides(component_type)
            if not guides:
                guides = self._fallback_guides(component)

            anchors = self._compute_anchors(component)
            component_symbols = symbols_by_component.get(comp_idx, [])

            for guide in guides:
                resolved = profile.apply_override(guide)
                if resolved is None:
                    continue

                # Dimensions are collected, not added directly
                if resolved.target == "width" and resolved.kind == "dimension":
                    dim = self._plan_width_dimension(
                        component, anchors, profile, comp_idx, section_top,
                        collection,
                    )
                    if dim:
                        planned_dimensions.append(dim)
                else:
                    # Non-dimension guides are applied directly
                    self._apply_guide(
                        component,
                        anchors,
                        resolved,
                        profile,
                        collection,
                        component_symbols,
                    )

        # Check for crown dimensions
        if profile.require_crown_dimension:
            crown_dims = self._plan_crown_dimensions(
                section_geometry, planned_dimensions, profile, section_top,
                collection,
            )
            planned_dimensions.extend(crown_dims)

        # Pass 3: Compute aligned offsets and create dimension annotations
        self._create_aligned_dimensions(
            planned_dimensions, symbols_by_component, profile, collection
        )

        # Pass 4: Add standalone labels for non-dimensioned components
        if profile.include_component_labels:
            self._add_component_labels(
                section_geometry, collection, profile
            )

        if profile.include_layer_callouts:
            self._add_layer_callouts(section_geometry, collection, profile)

        return collection

    def _prescan_symbols(
        self,
        section_geometry: SectionGeometry,
        profile: AnnotationProfile,
    ) -> list[_SymbolPlacement]:
        """Pre-scan to identify all symbols that will be placed.

        This enables computing dimension offsets before placing dimensions.
        """
        planned: list[_SymbolPlacement] = []

        for comp_idx, component in enumerate(section_geometry.components):
            anchors = self._compute_anchors(component)
            if not anchors:
                continue

            # Check for traffic direction symbol
            if profile.include_travel_direction:
                angle = self._compute_traffic_arrow_angle(component, profile)
                planned.append(_SymbolPlacement(
                    component_index=comp_idx,
                    symbol_type="traffic_arrow",
                    position=Point2D(
                        anchors.top_center.x,
                        anchors.top_center.y + profile.traffic_symbol_offset,
                    ),
                    angle=angle,
                    scale=1.0,
                    layer="symbols",
                    priority=10,
                ))

            # Check for cross slope symbol
            if profile.include_cross_slope:
                cross_slope = component.metadata.get("cross_slope")
                if cross_slope is not None and abs(cross_slope) >= 1e-6:
                    angle = self._compute_slope_arrow_angle(component)
                    planned.append(_SymbolPlacement(
                        component_index=comp_idx,
                        symbol_type="drainage_arrow",
                        position=Point2D(
                            anchors.top_center.x,
                            anchors.top_center.y + profile.slope_symbol_offset,
                        ),
                        angle=angle,
                        scale=profile.slope_symbol_scale,
                        layer="slope_indicators",
                        priority=5,
                    ))

        return planned

    def _compute_traffic_arrow_angle(self, component, profile: AnnotationProfile) -> float:
        """Compute rotation angle for traffic direction arrow."""
        if profile.traffic_arrow_mode == "traffic_direction":
            traffic = component.metadata.get("traffic_direction")
            if traffic == "inbound":
                return 180.0
            return 0.0
        else:
            direction = component.metadata.get("assembly_direction", "right")
            return 0.0 if direction == "right" else 180.0

    def _compute_slope_arrow_angle(self, component) -> float:
        """Compute rotation angle for slope/drainage arrow."""
        cross_slope = component.metadata.get("cross_slope", 0)
        direction = component.metadata.get("assembly_direction", "right")
        slope_outward = cross_slope >= 0
        if direction == "right":
            return 0.0 if slope_outward else 180.0
        else:
            return 180.0 if slope_outward else 0.0

    def _add_centerpoint_mark(
        self,
        section_geometry: SectionGeometry,
        collection: AnnotationCollection,
    ) -> None:
        control_point = section_geometry.metadata.get("control_point")
        if not control_point:
            return
        collection.add(SymbolAnnotation(
            position=Point2D(control_point.get("x", 0.0), control_point.get("elevation", 0.0)),
            symbol_type="centerpoint",
            layer="symbols",
            priority=10,
        ))

    def _add_component_labels(
        self,
        section_geometry: SectionGeometry,
        collection: AnnotationCollection,
        profile: AnnotationProfile,
    ) -> None:
        # Find global section top for consistent label band
        section_bounds = section_geometry.bounds()
        if not section_bounds:
            return
        section_top = section_bounds[3]  # max_y of entire section

        # First pass: collect all label info
        label_info: list[tuple[float, float, str]] = []  # (center_x, comp_top_y, text)

        for component_geom in section_geometry.components:
            metadata = component_geom.metadata
            bounds = component_geom.bounds()
            if not bounds:
                continue

            # Skip components that have a width when width dimensions are
            # enabled — they get labels paired with their dimension lines instead
            if "width" in metadata and profile.include_width_dimensions:
                continue

            center_x = (bounds[0] + bounds[2]) / 2
            comp_top_y = bounds[3]

            label_text = self._get_component_label_text(metadata, profile, collection)
            if not label_text:
                continue

            label_info.append((center_x, comp_top_y, label_text))

        # Sort by x position for staggering
        label_info.sort(key=lambda x: x[0])

        # Second pass: place labels with vertical staggering
        # Labels sit inside the dimension U-shape (between extension lines),
        # just above section_top.  When labels overlap horizontally they
        # stagger *downward* so they never climb up into the dimension line.
        placed: list[tuple[float, float, float]] = []  # (x, y, text_width)
        # Place standalone labels in the same band as paired labels (just below dimension line)
        base_offset = profile.dimension_offset - 0.25
        stagger_step = 0.10  # Vertical step when staggering

        for center_x, comp_top_y, label_text in label_info:
            # Estimate label width (rough: 0.055m per character)
            est_label_width = len(label_text) * 0.055

            label_y = section_top + base_offset

            # Find a non-overlapping y position by checking against placed labels
            # Stagger downward to stay inside the dimension U-shape
            max_attempts = 8
            for _ in range(max_attempts):
                overlap = False
                for px, py, pw in placed:
                    # Check horizontal overlap
                    h_dist = abs(center_x - px)
                    combined_half_width = (est_label_width + pw) / 2 + 0.08
                    if h_dist < combined_half_width:
                        # Check if they're at same vertical level
                        if abs(label_y - py) < stagger_step * 0.9:
                            overlap = True
                            break
                if not overlap:
                    break
                label_y -= stagger_step

            placed.append((center_x, label_y, est_label_width))

            collection.add(TextAnnotation(
                position=Point2D(center_x, label_y),
                text=label_text,
                font_size=profile.text_size,
                anchor="middle",
                layer="labels",
                is_keyed_note=profile.use_keyed_notes,
            ))

    def _get_component_label_text(
        self,
        metadata: dict,
        profile: AnnotationProfile,
        collection: AnnotationCollection,
    ) -> str | None:
        """Get the label text for a component, or None if it shouldn't have one."""
        component_type = metadata.get("component_type", "Component")

        if component_type == "TravelLane":
            label_text = "Lane"
        elif component_type == "TurnLane":
            label_text = "Turn Lane"
        elif component_type == "Shoulder":
            label_text = "Shoulder"
        elif component_type == "Slope":
            slope_ratio = metadata.get("slope_ratio")
            label_text = f"Slope {slope_ratio:.1f}:1" if slope_ratio else "Slope"
        elif component_type == "Ditch":
            label_text = "Ditch"
        elif component_type == "SurfaceProfile":
            label_text = "Surface"
        else:
            label_text = component_type

        if profile.use_keyed_notes:
            key = collection.add_keyed_note(label_text)
            label_text = key

        return label_text

    def _compute_anchors(self, component_geom) -> _AnchorPoints | None:
        bounds = component_geom.bounds()
        if not bounds:
            return None
        min_x, min_y, max_x, max_y = bounds
        center = Point2D((min_x + max_x) / 2, (min_y + max_y) / 2)
        top_center = Point2D((min_x + max_x) / 2, max_y)
        left_top = Point2D(min_x, max_y)
        right_top = Point2D(max_x, max_y)
        return _AnchorPoints(
            center=center,
            top_center=top_center,
            left_top=left_top,
            right_top=right_top,
        )

    def _apply_guide(
        self,
        component,
        anchors: _AnchorPoints | None,
        guide: AnnotationGuide,
        profile: AnnotationProfile,
        collection: AnnotationCollection,
        component_symbols: list[_SymbolPlacement] | None = None,
    ) -> None:
        # Note: width dimensions are handled separately via _plan_width_dimension
        # to enable row-based alignment across components
        if guide.target == "travel_direction" and guide.kind == "symbol":
            self._add_travel_direction_symbol(component, anchors, profile, collection)
            return
        if guide.target == "cross_slope" and guide.kind == "symbol":
            self._add_cross_slope_symbol(component, anchors, profile, collection)
            return
        if guide.target == "material_label" and guide.kind == "text":
            self._add_material_label(component, anchors, profile, collection)

    def _fallback_guides(self, component) -> list[AnnotationGuide]:
        guides: list[AnnotationGuide] = []
        if "width" in component.metadata:
            guides.append(AnnotationGuide(
                kind="dimension",
                target="width",
                anchor="component_edges",
            ))
        if "layers" in component.metadata:
            guides.append(AnnotationGuide(
                kind="text",
                target="material_label",
                anchor="component_center",
            ))
        return guides

    def _plan_width_dimension(
        self,
        component,
        anchors: _AnchorPoints | None,
        profile: AnnotationProfile,
        component_index: int,
        section_top: float,
        collection: AnnotationCollection | None = None,
    ) -> _PlannedDimension | None:
        """Plan a width dimension without creating it yet.

        Returns a _PlannedDimension that will be aligned with other dimensions
        before the actual DimensionAnnotation is created.

        Args:
            section_top: The top y coordinate of the entire section, used as
                a common reference for aligning all dimensions at the same level.
            collection: If provided, used to resolve keyed notes for the label.
        """
        width = component.metadata.get("width")
        if not width or not anchors:
            return None

        # Always orient dimensions left-to-right for consistent offset direction
        # (perpendicular offset goes UP when start is left of end)
        start = anchors.left_top
        end = anchors.right_top

        dimension_text = format_dimension(width, profile.unit_system)
        if profile.material_label_mode == "dimension_suffix":
            suffix = self._format_layer_label(component)
            if suffix:
                dimension_text = f"{dimension_text} ({suffix})"

        # Look up component label text to pair with this dimension
        label_text = None
        if collection and profile.include_component_labels:
            label_text = self._get_component_label_text(
                component.metadata, profile, collection
            )

        return _PlannedDimension(
            start=start,
            end=end,
            text=dimension_text,
            component_indices=frozenset([component_index]),
            base_y=section_top,  # Use section top for alignment, not component top
            span_level=0,  # Single component = base level
            label_text=label_text,
        )

    def _create_aligned_dimensions(
        self,
        planned_dimensions: list[_PlannedDimension],
        symbols_by_component: dict[int, list[_SymbolPlacement]],
        profile: AnnotationProfile,
        collection: AnnotationCollection,
    ) -> None:
        """Create dimension annotations with aligned offsets.

        Groups dimensions by span level and computes a common target y-position
        for each level, so dimensions measuring adjacent components align
        horizontally regardless of individual component heights.
        """
        if not planned_dimensions:
            return

        # All dimensions share the same base_y (section_top)
        section_top = planned_dimensions[0].base_y

        # Group dimensions by span level
        dims_by_level: dict[int, list[_PlannedDimension]] = {}
        for dim in planned_dimensions:
            dims_by_level.setdefault(dim.span_level, []).append(dim)

        # Compute target y-position for each level (relative to section_top)
        level_target_y: dict[int, float] = {}
        sorted_levels = sorted(dims_by_level.keys())

        for level in sorted_levels:
            dims_at_level = dims_by_level[level]

            # Find the maximum offset needed by any dimension at this level
            # (computed relative to section_top, not individual component tops)
            max_offset = profile.dimension_offset
            for dim in dims_at_level:
                # Collect all symbols that fall within this dimension's span
                symbols_in_span: list[_SymbolPlacement] = []
                for comp_idx in dim.component_indices:
                    symbols_in_span.extend(symbols_by_component.get(comp_idx, []))

                # Compute offset needed (relative to section_top)
                needed_offset = self._compute_span_offset(
                    section_top, symbols_in_span, profile.dimension_offset
                )
                max_offset = max(max_offset, needed_offset)

            # For higher levels, add clearance above lower levels
            if level > 0 and (level - 1) in level_target_y:
                dimension_height = 0.25  # Height of dimension line + text
                min_target = level_target_y[level - 1] + dimension_height
                max_offset = max(max_offset, min_target - section_top)

            level_target_y[level] = section_top + max_offset

        # Create dimension annotations with per-dimension offsets
        # that align all dimensions at the same level to the same y-position
        for dim in planned_dimensions:
            target_y = level_target_y[dim.span_level]
            # The dimension line y = max(start.y, end.y) + offset
            # So offset = target_y - max(start.y, end.y)
            component_top = max(dim.start.y, dim.end.y)
            offset = target_y - component_top
            collection.add(DimensionAnnotation(
                start=dim.start,
                end=dim.end,
                offset=offset,
                dimension_text=dim.text,
                layer="dimensions",
            ))

            # Emit paired label just below the dimension line
            if dim.label_text:
                label_x = (dim.start.x + dim.end.x) / 2
                label_y = target_y - 0.25
                collection.add(TextAnnotation(
                    position=Point2D(label_x, label_y),
                    text=dim.label_text,
                    font_size=profile.text_size,
                    anchor="middle",
                    layer="labels",
                    is_keyed_note=profile.use_keyed_notes,
                ))

    def _compute_span_offset(
        self,
        component_top_y: float,
        component_symbols: list[_SymbolPlacement],
        base_offset: float,
    ) -> float:
        """Compute dimension offset to clear symbols in the horizontal span.

        Uses pre-scanned symbol positions to determine the minimum offset
        needed for the dimension line to clear all symbols.
        """
        if not component_symbols:
            return base_offset

        # Find highest symbol top relative to component top
        max_symbol_top = 0.0
        for ps in component_symbols:
            # Estimate symbol height (use default for pre-scan)
            symbol_half_height = 0.15 * ps.scale  # Approximate
            symbol_top = ps.position.y + symbol_half_height
            symbol_top_relative = symbol_top - component_top_y
            max_symbol_top = max(max_symbol_top, symbol_top_relative)

        # Add clearance buffer
        symbol_clearance = max_symbol_top + SYMBOL_CLEARANCE_BUFFER

        return max(base_offset, symbol_clearance)

    def _add_travel_direction_symbol(
        self,
        component,
        anchors: _AnchorPoints | None,
        profile: AnnotationProfile,
        collection: AnnotationCollection,
    ) -> None:
        if not anchors:
            return
        angle = 0.0
        if profile.traffic_arrow_mode == "traffic_direction":
            traffic = component.metadata.get("traffic_direction")
            if traffic == "inbound":
                angle = 180.0
            elif traffic == "outbound":
                angle = 0.0
            else:
                angle = 0.0
        else:
            direction = component.metadata.get("assembly_direction", "right")
            angle = 0.0 if direction == "right" else 180.0

        position = Point2D(
            anchors.top_center.x,
            anchors.top_center.y + profile.traffic_symbol_offset,
        )

        collection.add(SymbolAnnotation(
            position=position,
            symbol_type="traffic_arrow",
            angle=angle,
            layer="symbols",
            priority=10,
            metadata={"allow_geometry_overlap": True},
        ))

    def _add_cross_slope_symbol(
        self,
        component,
        anchors: _AnchorPoints | None,
        profile: AnnotationProfile,
        collection: AnnotationCollection,
    ) -> None:
        if not anchors:
            return
        cross_slope = component.metadata.get("cross_slope")
        if cross_slope is None:
            return
        if abs(cross_slope) < 1e-6:
            return
        direction = component.metadata.get("assembly_direction", "right")
        slope_outward = cross_slope >= 0
        if direction == "right":
            angle = 0.0 if slope_outward else 180.0
        else:
            angle = 180.0 if slope_outward else 0.0

        position = Point2D(
            anchors.top_center.x,
            anchors.top_center.y + profile.slope_symbol_offset,
        )

        collection.add(SymbolAnnotation(
            position=position,
            symbol_type="drainage_arrow",
            angle=angle,
            scale=profile.slope_symbol_scale,
            layer="slope_indicators",
        ))

        if profile.include_cross_slope_text:
            text = f"{abs(cross_slope) * 100:.0f}%"
            # Pair slope text with the slope arrow: place it just below the arrow
            # Arrow half-height (unscaled 0.20m / 2 = 0.10m) * scale, plus small gap
            arrow_half_height = 0.10 * profile.slope_symbol_scale
            text_gap = 0.04
            text_y = position.y - arrow_half_height - text_gap
            collection.add(TextAnnotation(
                position=Point2D(anchors.top_center.x, text_y),
                text=text,
                font_size=profile.slope_text_size,
                anchor="middle",
                layer="slope_indicators",
            ))

    def _add_material_label(
        self,
        component,
        anchors: _AnchorPoints | None,
        profile: AnnotationProfile,
        collection: AnnotationCollection,
    ) -> None:
        if profile.material_label_mode != "note":
            return
        if not anchors:
            return
        material_text = self._format_layer_label(component)
        if not material_text:
            return

        if profile.use_keyed_notes:
            key = collection.add_keyed_note(material_text)
            material_text = key

        collection.add(TextAnnotation(
            position=anchors.center,
            text=material_text,
            font_size=profile.text_size * 0.8,
            anchor="middle",
            layer="materials",
            is_keyed_note=profile.use_keyed_notes,
            metadata={"allow_geometry_overlap": True},
        ))

    def _format_layer_label(self, component) -> str | None:
        layers = component.metadata.get("layers", [])
        if not layers:
            return None
        layer_type = layers[0].get("type", "Unknown")
        if layer_type == "AsphaltLayer":
            return "Asphalt"
        if layer_type == "ConcreteLayer":
            return "Concrete"
        if layer_type == "CrushedRockLayer":
            return "Crushed Rock"
        return layer_type

    def _plan_crown_dimensions(
        self,
        section_geometry: SectionGeometry,
        existing_planned: list[_PlannedDimension],
        profile: AnnotationProfile,
        section_top: float,
        collection: AnnotationCollection | None = None,
    ) -> list[_PlannedDimension]:
        """Plan crown-adjacent dimensions if not already covered."""
        result: list[_PlannedDimension] = []

        control_point = section_geometry.metadata.get("control_point")
        if not control_point:
            return result
        crown = Point2D(control_point.get("x", 0.0), control_point.get("elevation", 0.0))

        left_index, right_index = self._crown_adjacent_indices(section_geometry)
        left_needed = left_index is not None
        right_needed = right_index is not None

        # Check if existing planned dimensions already cover crown-adjacent
        for dim in existing_planned:
            side = self._planned_dimension_side(dim, crown)
            if side == "left":
                left_needed = False
            elif side == "right":
                right_needed = False

        if left_needed and left_index is not None:
            dim = self._plan_crown_adjacent_dimension(
                section_geometry.components[left_index],
                left_index,
                profile,
                section_top,
                collection,
            )
            if dim:
                result.append(dim)

        if right_needed and right_index is not None:
            dim = self._plan_crown_adjacent_dimension(
                section_geometry.components[right_index],
                right_index,
                profile,
                section_top,
                collection,
            )
            if dim:
                result.append(dim)

        return result

    def _plan_crown_adjacent_dimension(
        self,
        component,
        component_index: int,
        profile: AnnotationProfile,
        section_top: float,
        collection: AnnotationCollection | None = None,
    ) -> _PlannedDimension | None:
        """Plan a crown-adjacent dimension."""
        anchors = self._compute_anchors(component)
        if not anchors:
            return None
        width = component.metadata.get("width")
        if not width:
            return None

        # Always orient dimensions left-to-right for consistent offset direction
        start = anchors.left_top
        end = anchors.right_top

        # Look up component label text to pair with this dimension
        label_text = None
        if collection and profile.include_component_labels:
            label_text = self._get_component_label_text(
                component.metadata, profile, collection
            )

        return _PlannedDimension(
            start=start,
            end=end,
            text=format_dimension(width, profile.unit_system),
            component_indices=frozenset([component_index]),
            base_y=section_top,  # Use section top for alignment
            span_level=0,
            label_text=label_text,
        )

    def _planned_dimension_side(
        self, dim: _PlannedDimension, crown: Point2D
    ) -> str | None:
        """Determine which side of crown a planned dimension is on."""
        tol = 1e-6
        touches_crown = (
            (abs(dim.start.x - crown.x) < tol and abs(dim.start.y - crown.y) < tol)
            or (abs(dim.end.x - crown.x) < tol and abs(dim.end.y - crown.y) < tol)
        )
        if not touches_crown:
            return None
        other = dim.end if abs(dim.start.x - crown.x) < tol else dim.start
        if other.x < crown.x:
            return "left"
        if other.x > crown.x:
            return "right"
        return None

    def _crown_adjacent_indices(self, section_geometry: SectionGeometry) -> tuple[int | None, int | None]:
        left_count = section_geometry.metadata.get("left_component_count")
        right_count = section_geometry.metadata.get("right_component_count")
        if left_count is not None and right_count is not None:
            left_index = 0 if left_count > 0 else None
            right_index = left_count if right_count > 0 else None
            return left_index, right_index

        left_indices = [
            idx for idx, comp in enumerate(section_geometry.components)
            if comp.metadata.get("assembly_direction") == "left"
        ]
        right_indices = [
            idx for idx, comp in enumerate(section_geometry.components)
            if comp.metadata.get("assembly_direction") == "right"
        ]

        left_index = left_indices[0] if left_indices else None
        right_index = right_indices[0] if right_indices else None
        return left_index, right_index

    def _add_layer_callouts(
        self,
        section_geometry: SectionGeometry,
        collection: AnnotationCollection,
        profile: AnnotationProfile,
    ) -> None:
        """Add leader callouts for pavement layers.

        Creates leader annotations for each unique layer type, pointing
        from the layer's visible face to a text callout.
        """
        # Collect all layers with their component info
        layer_info: list[tuple[str, int, ComponentGeometry, int, dict]] = []
        for comp_idx, component in enumerate(section_geometry.components):
            layers = component.metadata.get("layers", [])
            for layer_idx, layer in enumerate(layers):
                layer_type = layer.get("type", "Unknown")
                layer_info.append((layer_type, comp_idx, component, layer_idx, layer))

        if not layer_info:
            return

        # Group layers by type and pick the best candidate for callout
        # Prefer layers closest to centerline (x=0)
        layers_by_type: dict[str, list[tuple[int, ComponentGeometry, int, dict]]] = {}
        for layer_type, comp_idx, component, layer_idx, layer in layer_info:
            layers_by_type.setdefault(layer_type, []).append(
                (comp_idx, component, layer_idx, layer)
            )

        # Get control point for reference
        control_point = section_geometry.metadata.get("control_point", {})
        centerline_x = control_point.get("x", 0.0)

        # Place callouts below the section geometry with leaders pointing up
        section_bounds = section_geometry.bounds()
        section_bottom = section_bounds[1]  # min_y of entire section

        # Track vertical positions for stacking callouts downward
        callout_y_positions: list[float] = []

        for layer_type, candidates in layers_by_type.items():
            # Prefer right-side components (positive X from centerline)
            # This avoids leaders crossing the entire section
            right_side_candidates = [
                c for c in candidates
                if self._component_center_x(c[1]) > centerline_x
            ]

            if right_side_candidates:
                # Pick the leftmost right-side component (closest to center)
                best_candidate = min(
                    right_side_candidates,
                    key=lambda c: self._component_center_x(c[1]),
                )
            else:
                # Fall back to rightmost left-side component
                best_candidate = max(
                    candidates,
                    key=lambda c: self._component_center_x(c[1]),
                )

            comp_idx, component, layer_idx, layer = best_candidate

            # Get anchor point on the layer's visible face (right edge)
            anchor = self._compute_layer_anchor(component, layer_idx)
            if not anchor:
                continue

            # Format the layer text
            text = self._format_layer_callout_text(layer)

            # Compute text Y position below geometry, stacking downward
            # leader_offset_y is negative, so section_bottom + leader_offset_y goes below
            base_y = section_bottom + profile.leader_offset_y
            text_y = self._find_non_overlapping_y(
                base_y, callout_y_positions, profile.leader_text_size * 1.5
            )
            callout_y_positions.append(text_y)

            # Leader path: text below → elbow → anchor on layer (arrow points up at layer)
            text_x = anchor.x + profile.leader_offset_x
            text_point = Point2D(text_x, text_y)
            elbow = Point2D(text_x - 0.15, text_y)

            collection.add(LeaderAnnotation(
                points=[anchor, elbow, text_point],
                text=text,
                arrow_at_start=True,
                text_anchor="start",
                text_size=profile.leader_text_size,
                layer="leaders",
            ))

    def _component_center_x(self, component: ComponentGeometry) -> float:
        """Get the horizontal center of a component."""
        bounds = component.bounds()
        if not bounds:
            return 0.0
        return (bounds[0] + bounds[2]) / 2

    def _compute_layer_anchor(
        self, component: ComponentGeometry, layer_idx: int
    ) -> Point2D | None:
        """Compute anchor point for a layer callout.

        Returns a point on the right edge of the layer, at its vertical center.
        """
        if layer_idx >= len(component.polygons):
            return None

        polygon = component.polygons[layer_idx]
        bounds = polygon.bounds()
        if not bounds:
            return None

        # Right edge, vertical center of the layer
        right_x = bounds[2]
        center_y = (bounds[1] + bounds[3]) / 2
        return Point2D(right_x, center_y)

    def _format_layer_callout_text(self, layer: dict) -> str:
        """Format layer information into callout text."""
        layer_type = layer.get("type", "Unknown")
        thickness = layer.get("thickness")

        # Map layer types to readable names
        type_names = {
            "AsphaltLayer": "Asphalt",
            "ConcreteLayer": "Concrete",
            "CrushedRockLayer": "Aggregate Base",
            "GravelLayer": "Gravel",
            "SoilLayer": "Soil",
        }
        name = type_names.get(layer_type, layer_type)

        # Add thickness if available
        if thickness:
            # Convert to inches for display (assuming meters)
            thickness_in = thickness / 0.0254
            if thickness_in >= 1:
                return f"{name} ({thickness_in:.0f}\")"
            return f"{name} ({thickness_in:.1f}\")"

        return name

    def _find_non_overlapping_y(
        self,
        preferred_y: float,
        existing_ys: list[float],
        min_spacing: float,
    ) -> float:
        """Find a Y position that doesn't overlap with existing positions."""
        if not existing_ys:
            return preferred_y

        # Check if preferred position works
        for y in existing_ys:
            if abs(preferred_y - y) < min_spacing:
                break
        else:
            return preferred_y

        # Find a non-overlapping position (prefer moving down)
        test_y = preferred_y
        step = min_spacing
        for _ in range(10):  # Max attempts
            test_y -= step
            conflict = False
            for y in existing_ys:
                if abs(test_y - y) < min_spacing:
                    conflict = True
                    break
            if not conflict:
                return test_y

        # Fallback: stack below all existing
        return min(existing_ys) - min_spacing
