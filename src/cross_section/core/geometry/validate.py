"""Shapely-backed geometry validation helpers."""

from __future__ import annotations

from dataclasses import dataclass

from .primitives import ComponentGeometry, Point2D, Polygon


class ShapelyNotAvailable(RuntimeError):
    """Raised when Shapely-backed validation is requested but not installed."""


@dataclass(frozen=True)
class _ShapelyBindings:
    polygon: type
    line: type
    unary_union: object
    explain_validity: object


def _require_shapely() -> _ShapelyBindings:
    try:
        from shapely.geometry import LineString, Polygon as ShapelyPolygon
        from shapely.ops import unary_union
        from shapely.validation import explain_validity
    except ImportError as exc:
        raise ShapelyNotAvailable(
            "Shapely is not installed. Install with `pip install cross-section[validation]`."
        ) from exc

    return _ShapelyBindings(
        polygon=ShapelyPolygon,
        line=LineString,
        unary_union=unary_union,
        explain_validity=explain_validity,
    )


def _coords(points: list[Point2D]) -> list[tuple[float, float]]:
    return [(point.x, point.y) for point in points]


def _to_shapely_polygon(polygon: Polygon) -> object:
    bindings = _require_shapely()
    exterior = _coords(polygon.exterior)
    holes = [_coords(hole) for hole in polygon.holes] if polygon.holes else None
    return bindings.polygon(exterior, holes)


def _from_shapely_polygon(shapely_polygon: object) -> Polygon:
    exterior = [Point2D(x, y) for x, y in shapely_polygon.exterior.coords[:-1]]
    holes = [
        [Point2D(x, y) for x, y in interior.coords[:-1]]
        for interior in shapely_polygon.interiors
    ]
    return Polygon(exterior=exterior, holes=holes or None)


def _as_polygons(shapely_geom: object, tolerance: float) -> list[Polygon]:
    if shapely_geom.is_empty:
        return []

    geom_type = shapely_geom.geom_type
    if geom_type == "Polygon":
        if shapely_geom.area <= tolerance:
            return []
        return [_from_shapely_polygon(shapely_geom)]
    if geom_type == "MultiPolygon":
        polygons: list[Polygon] = []
        for poly in shapely_geom.geoms:
            polygons.extend(_as_polygons(poly, tolerance))
        return polygons
    if geom_type == "GeometryCollection":
        polygons = []
        for geom in shapely_geom.geoms:
            polygons.extend(_as_polygons(geom, tolerance))
        return polygons

    return []


def clip_overlap_allowed_polygons(
    components: list[ComponentGeometry],
    tolerance: float = 1e-6,
) -> list[ComponentGeometry]:
    """Clip overlap-allowed polygons against other component solids."""
    bindings = _require_shapely()
    component_polys: list[list[tuple[int, object]]] = []
    overlap_allowed: list[set[int]] = []

    for component in components:
        allowed = set(component.metadata.get("overlap_allow_polygons", []))
        overlap_allowed.append(allowed)
        shapely_polys = [
            (index, _to_shapely_polygon(polygon))
            for index, polygon in enumerate(component.polygons)
        ]
        component_polys.append(shapely_polys)

    clipped_components: list[ComponentGeometry] = []

    for index, component in enumerate(components):
        blocking_polys: list[object] = []
        for other_index, polys in enumerate(component_polys):
            if other_index == index:
                continue
            allowed = overlap_allowed[other_index]
            for poly_index, shapely_poly in polys:
                if poly_index in allowed:
                    continue
                blocking_polys.append(shapely_poly)

        blocker_union = bindings.unary_union(blocking_polys) if blocking_polys else None

        new_polygons: list[Polygon] = []
        new_allow: list[int] = []

        for poly_index, polygon in enumerate(component.polygons):
            if poly_index not in overlap_allowed[index] or blocker_union is None:
                new_polygons.append(polygon)
                continue

            shapely_poly = _to_shapely_polygon(polygon)
            clipped = shapely_poly.difference(blocker_union)
            clipped_polys = _as_polygons(clipped, tolerance)
            for clipped_poly in clipped_polys:
                new_allow.append(len(new_polygons))
                new_polygons.append(clipped_poly)

        metadata = dict(component.metadata)
        metadata["overlap_allow_polygons"] = new_allow
        clipped_components.append(
            ComponentGeometry(polygons=new_polygons, polylines=component.polylines, metadata=metadata)
        )

    return clipped_components


def _line_segments_from_geom(shapely_geom: object) -> list[list[Point2D]]:
    if shapely_geom.is_empty:
        return []

    geom_type = shapely_geom.geom_type
    if geom_type == "LineString":
        return [[Point2D(x, y) for x, y in shapely_geom.coords]]
    if geom_type == "MultiLineString":
        segments: list[list[Point2D]] = []
        for geom in shapely_geom.geoms:
            segments.extend(_line_segments_from_geom(geom))
        return segments
    if geom_type == "GeometryCollection":
        segments: list[list[Point2D]] = []
        for geom in shapely_geom.geoms:
            segments.extend(_line_segments_from_geom(geom))
        return segments

    return []


def _hatch_lines_for_polygon(
    shapely_polygon: object,
    spacing: float,
    tolerance: float,
) -> list[list[Point2D]]:
    bindings = _require_shapely()
    minx, miny, maxx, maxy = shapely_polygon.bounds
    if spacing <= 0:
        return []

    hatch_lines: list[list[Point2D]] = []
    y = miny
    maxy_with_tol = maxy + tolerance
    while y <= maxy_with_tol:
        line = bindings.line([(minx - 1.0, y), (maxx + 1.0, y)])
        intersection = shapely_polygon.intersection(line)
        hatch_lines.extend(_line_segments_from_geom(intersection))
        y += spacing

    return hatch_lines


def clip_hatched_polylines(
    components: list[ComponentGeometry],
    tolerance: float = 1e-6,
) -> list[ComponentGeometry]:
    """Clip hatched polylines (boundary + hatch) against other components."""
    bindings = _require_shapely()

    component_polys: list[list[tuple[int, object]]] = []
    overlap_allowed: list[set[int]] = []

    for component in components:
        allowed = set(component.metadata.get("overlap_allow_polygons", []))
        overlap_allowed.append(allowed)
        shapely_polys = [
            (index, _to_shapely_polygon(polygon))
            for index, polygon in enumerate(component.polygons)
        ]
        component_polys.append(shapely_polys)

    clipped_components: list[ComponentGeometry] = []

    for index, component in enumerate(components):
        boundary_index = component.metadata.get("hatch_boundary_index")
        spacing = component.metadata.get("hatch_spacing")
        orientation = component.metadata.get("hatch_orientation", "horizontal")

        if boundary_index is None or spacing is None or orientation != "horizontal":
            clipped_components.append(component)
            continue

        if boundary_index >= len(component.polylines):
            clipped_components.append(component)
            continue

        boundary_line = component.polylines[boundary_index]
        if not boundary_line:
            clipped_components.append(component)
            continue

        boundary_coords = boundary_line[:]
        if boundary_coords[0] != boundary_coords[-1]:
            boundary_coords = boundary_coords + [boundary_coords[0]]

        boundary_polygon = bindings.polygon(_coords(boundary_coords))

        blocking_polys: list[object] = []
        for other_index, polys in enumerate(component_polys):
            if other_index == index:
                continue
            allowed = overlap_allowed[other_index]
            for poly_index, shapely_poly in polys:
                if poly_index in allowed:
                    continue
                blocking_polys.append(shapely_poly)

        blocker_union = bindings.unary_union(blocking_polys) if blocking_polys else None
        clipped = (
            boundary_polygon
            if blocker_union is None
            else boundary_polygon.difference(blocker_union)
        )

        clipped_polygons = _as_polygons(clipped, tolerance)
        new_polylines: list[list[Point2D]] = []
        new_styles: list[dict[str, str]] = []

        for poly in clipped_polygons:
            boundary = poly.exterior + [poly.exterior[0]]
            new_polylines.append(boundary)
            new_styles.append({"stroke_dasharray": "6,4"})

            shapely_poly = _to_shapely_polygon(poly)
            hatch_lines = _hatch_lines_for_polygon(shapely_poly, spacing, tolerance)
            for hatch in hatch_lines:
                new_polylines.append(hatch)
                new_styles.append({"stroke_width": "1"})

        metadata = dict(component.metadata)
        metadata["polyline_styles"] = new_styles
        metadata["hatch_boundary_index"] = 0 if new_polylines else None

        clipped_components.append(
            ComponentGeometry(
                polygons=component.polygons,
                polylines=new_polylines,
                metadata=metadata,
            )
        )

    return clipped_components


def validate_component_geometry(component: ComponentGeometry, index: int | None = None) -> list[str]:
    """Validate polygon self-intersection and construction issues."""
    bindings = _require_shapely()
    errors: list[str] = []
    component_type = component.metadata.get("component_type", "Component")
    label = f"{component_type} ({index})" if index is not None else component_type

    for poly_index, polygon in enumerate(component.polygons):
        shapely_poly = _to_shapely_polygon(polygon)
        if not shapely_poly.is_valid:
            reason = bindings.explain_validity(shapely_poly)
            errors.append(f"{label} polygon {poly_index} invalid: {reason}")

    return errors


def validate_section_geometry(
    components: list[ComponentGeometry],
    tolerance: float = 1e-6,
) -> list[str]:
    """Validate component geometry and detect overlaps between components."""
    bindings = _require_shapely()
    errors: list[str] = []

    components = clip_overlap_allowed_polygons(components, tolerance=tolerance)
    components = clip_hatched_polylines(components, tolerance=tolerance)

    for index, component in enumerate(components):
        errors.extend(validate_component_geometry(component, index=index))

    unions: list[object | None] = []
    for component in components:
        if not component.polygons:
            unions.append(None)
            continue
        allowed = set(component.metadata.get("overlap_allow_polygons", []))
        shapely_polys = [
            _to_shapely_polygon(polygon)
            for index, polygon in enumerate(component.polygons)
            if index not in allowed
        ]
        unions.append(bindings.unary_union(shapely_polys) if shapely_polys else None)

    for i, geom_i in enumerate(unions):
        if geom_i is None:
            continue
        for j in range(i + 1, len(unions)):
            geom_j = unions[j]
            if geom_j is None:
                continue
            if not geom_i.intersects(geom_j):
                continue
            overlap = geom_i.intersection(geom_j)
            if overlap.area > tolerance:
                type_i = components[i].metadata.get("component_type", f"Component {i}")
                type_j = components[j].metadata.get("component_type", f"Component {j}")
                errors.append(
                    f"{type_i} (index {i}) overlaps {type_j} (index {j}) "
                    f"by {overlap.area:.6f} square units"
                )

    for i in range(len(unions) - 1):
        group_i = components[i].metadata.get("sequence_group")
        group_j = components[i + 1].metadata.get("sequence_group")
        if group_i is not None and group_j is not None and group_i != group_j:
            continue

        geom_i = unions[i]
        geom_j = unions[i + 1]
        if geom_i is None or geom_j is None:
            continue

        distance = geom_i.distance(geom_j)
        if distance > tolerance:
            type_i = components[i].metadata.get("component_type", f"Component {i}")
            type_j = components[i + 1].metadata.get("component_type", f"Component {i + 1}")
            errors.append(
                f"{type_i} (index {i}) has a gap of {distance:.6f} to "
                f"{type_j} (index {i + 1})"
            )

    lines: list[tuple[int, int, object]] = []
    for comp_index, component in enumerate(components):
        for poly_index, polyline in enumerate(component.polylines):
            if len(polyline) < 2:
                continue
            lines.append((comp_index, poly_index, bindings.line(_coords(polyline))))

    for i, (comp_i, line_i_idx, line_i) in enumerate(lines):
        for comp_j, line_j_idx, line_j in lines[i + 1 :]:
            if line_i.crosses(line_j) or line_i.overlaps(line_j):
                errors.append(
                    f"Polyline {line_i_idx} (component {comp_i}) crosses polyline "
                    f"{line_j_idx} (component {comp_j})"
                )
            elif line_i.intersects(line_j) and not line_i.touches(line_j):
                errors.append(
                    f"Polyline {line_i_idx} (component {comp_i}) intersects polyline "
                    f"{line_j_idx} (component {comp_j})"
                )

    return errors
