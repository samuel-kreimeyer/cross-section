"""Plan annotations from guides and profiles."""

from dataclasses import dataclass

from ...geometry.primitives import Point2D
from ..section import SectionGeometry
from .container import AnnotationCollection
from .dimension import DimensionAnnotation
from .guides import AnnotationGuide, AnnotationGuideRegistry, DEFAULT_GUIDE_REGISTRY
from .profile import AnnotationProfile
from .symbol import SymbolAnnotation
from .text import TextAnnotation


@dataclass(frozen=True)
class _AnchorPoints:
    center: Point2D
    top_center: Point2D
    left_top: Point2D
    right_top: Point2D


class AnnotationPlanner:
    """Translate guide intent into concrete annotations."""

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

        if profile.include_component_labels:
            self._add_component_labels(section_geometry, collection, profile)

        for component in section_geometry.components:
            component_type = component.metadata.get("component_type", "Component")
            guides = self._registry.get_guides(component_type)
            if not guides:
                guides = self._fallback_guides(component)

            anchors = self._compute_anchors(component)
            for guide in guides:
                resolved = profile.apply_override(guide)
                if resolved is None:
                    continue
                self._apply_guide(
                    component,
                    anchors,
                    resolved,
                    profile,
                    collection,
                )

        if profile.require_crown_dimension:
            self._ensure_crown_dimension(section_geometry, collection, profile)

        return collection

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
        for component_geom in section_geometry.components:
            metadata = component_geom.metadata
            component_type = metadata.get("component_type", "Component")
            bounds = component_geom.bounds()
            if not bounds:
                continue

            center_x = (bounds[0] + bounds[2]) / 2
            top_y = bounds[3]
            label_y = top_y + 0.2

            if component_type == "TravelLane":
                label_text = "Lane"
            elif component_type == "TurnLane":
                label_text = "Turn Lane"
            elif component_type == "Shoulder":
                label_text = "Shoulder"
            elif component_type == "Slope":
                slope_ratio = metadata.get("slope_ratio")
                label_text = f"Slope {slope_ratio:.1f}:1" if slope_ratio else "Slope"
            else:
                label_text = component_type

            if profile.use_keyed_notes:
                key = collection.add_keyed_note(label_text)
                label_text = key

            collection.add(TextAnnotation(
                position=Point2D(center_x, label_y),
                text=label_text,
                font_size=profile.text_size,
                anchor="middle",
                layer="labels",
                is_keyed_note=profile.use_keyed_notes,
            ))

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
    ) -> None:
        if guide.target == "width" and guide.kind == "dimension":
            self._add_width_dimension(component, anchors, profile, collection)
            return
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

    def _add_width_dimension(
        self,
        component,
        anchors: _AnchorPoints | None,
        profile: AnnotationProfile,
        collection: AnnotationCollection,
    ) -> None:
        width = component.metadata.get("width")
        if not width or not anchors:
            return
        direction = component.metadata.get("assembly_direction", "right")

        if direction == "right":
            start = anchors.left_top
            end = anchors.right_top
        else:
            start = anchors.right_top
            end = anchors.left_top

        dimension_text = f"{width:.2f}m"
        if profile.material_label_mode == "dimension_suffix":
            suffix = self._format_layer_label(component)
            if suffix:
                dimension_text = f"{dimension_text} ({suffix})"

        collection.add(DimensionAnnotation(
            start=start,
            end=end,
            offset=profile.dimension_offset,
            dimension_text=dimension_text,
            layer="dimensions",
        ))

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

        collection.add(SymbolAnnotation(
            position=anchors.center,
            symbol_type="traffic_arrow",
            angle=angle,
            layer="symbols",
            priority=10,
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
            collection.add(TextAnnotation(
                position=Point2D(
                    anchors.top_center.x,
                    anchors.top_center.y + profile.slope_text_offset,
                ),
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

    def _ensure_crown_dimension(
        self,
        section_geometry: SectionGeometry,
        collection: AnnotationCollection,
        profile: AnnotationProfile,
    ) -> None:
        control_point = section_geometry.metadata.get("control_point")
        if not control_point:
            return
        crown = Point2D(control_point.get("x", 0.0), control_point.get("elevation", 0.0))

        left_index, right_index = self._crown_adjacent_indices(section_geometry)
        left_needed = left_index is not None
        right_needed = right_index is not None

        for ann in collection.get_by_type(DimensionAnnotation):
            side = self._dimension_side(ann, crown)
            if side == "left":
                left_needed = False
            elif side == "right":
                right_needed = False

        if left_needed and left_index is not None:
            self._add_crown_adjacent_dimension(
                section_geometry.components[left_index],
                profile,
                collection,
            )

        if right_needed and right_index is not None:
            self._add_crown_adjacent_dimension(
                section_geometry.components[right_index],
                profile,
                collection,
            )

    def _add_crown_adjacent_dimension(
        self,
        component,
        profile: AnnotationProfile,
        collection: AnnotationCollection,
    ) -> None:
        anchors = self._compute_anchors(component)
        if not anchors:
            return
        width = component.metadata.get("width")
        if not width:
            return
        direction = component.metadata.get("assembly_direction", "right")
        if direction == "right":
            start = anchors.left_top
            end = anchors.right_top
        else:
            start = anchors.right_top
            end = anchors.left_top
        collection.add(DimensionAnnotation(
            start=start,
            end=end,
            offset=profile.dimension_offset,
            dimension_text=f"{width:.2f}m",
            layer="dimensions",
        ))

    def _dimension_side(self, dimension: DimensionAnnotation, crown: Point2D) -> str | None:
        if not self._dimension_touches_point(dimension, crown):
            return None
        other = dimension.end if abs(dimension.start.x - crown.x) < 1e-6 else dimension.start
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

    def _dimension_touches_point(self, dimension: DimensionAnnotation, point: Point2D) -> bool:
        tol = 1e-6
        return (
            abs(dimension.start.x - point.x) < tol
            and abs(dimension.start.y - point.y) < tol
        ) or (
            abs(dimension.end.x - point.x) < tol
            and abs(dimension.end.y - point.y) < tol
        )
