"""DXF exporter for road cross-section geometry.

Requires the ``ezdxf`` package::

    pip install cross-section[dxf]

This exporter follows the CAD-first philosophy described in the redesign
discussion: geometry and metadata are decoupled, and every entity is placed
on a named layer so that CAD users (AutoCAD, Civil 3D, BricsCAD) receive a
structured, professionally layered file rather than a flat drawing.

Layer conventions
-----------------
ROAD_PAVEMENT_AC      – Asphalt layers
ROAD_PAVEMENT_PCC     – Concrete layers
ROAD_PAVEMENT_AGG     – Aggregate base / crushed rock layers
ROAD_CURB             – Curbs and gutters
ROAD_SIDEWALK         – Sidewalk concrete
ROAD_SHOULDER         – Shoulders
ROAD_SLOPE            – Cut / fill slopes
ROAD_DITCH            – Ditches and drainage features
ROAD_BARRIER          – Barriers (Jersey, guardrail, cable)
ROAD_WALL             – Retaining walls and shoring
ROAD_SURFACE          – Surface profiles and buffers
ROAD_MISC             – Any unclassified component
ANNOTATION_DIM        – Width dimension entities
ANNOTATION_TEXT       – Text labels and callouts
ANNOTATION_SLOPE      – Slope tag text
DEFPOINTS             – Dimension definition points (hidden by convention)
"""

from __future__ import annotations

from typing import TYPE_CHECKING, TextIO

from ..core.domain.section import SectionGeometry

if TYPE_CHECKING:
    from ..core.domain.annotations.types import SectionAnnotations

# ---------------------------------------------------------------------------
# Layer definitions
# ---------------------------------------------------------------------------

# Maps pavement-layer class names → DXF layer name
_PAVEMENT_LAYER_MAP: dict[str, str] = {
    "AsphaltLayer": "ROAD_PAVEMENT_AC",
    "ConcreteLayer": "ROAD_PAVEMENT_PCC",
    "CrushedRockLayer": "ROAD_PAVEMENT_AGG",
}

# Maps component_type prefix → DXF layer name
_COMPONENT_LAYER_MAP: dict[str, str] = {
    "TravelLane": "ROAD_PAVEMENT_AC",  # overridden per sub-layer below
    "TurnLane": "ROAD_PAVEMENT_AC",
    "Shoulder": "ROAD_SHOULDER",
    "Curb": "ROAD_CURB",
    "Gutter": "ROAD_CURB",
    "Sidewalk": "ROAD_SIDEWALK",
    "Slope": "ROAD_SLOPE",
    "Ditch": "ROAD_DITCH",
    "Barrier": "ROAD_BARRIER",
    "RetainingWall": "ROAD_WALL",
    "Shoring": "ROAD_WALL",
    "SurfaceProfile": "ROAD_SURFACE",
    "Buffer": "ROAD_SURFACE",
}

# ACI colour index for each layer (AutoCAD standard palette)
_LAYER_COLORS_ACI: dict[str, int] = {
    "ROAD_PAVEMENT_AC": 252,   # dark grey
    "ROAD_PAVEMENT_PCC": 8,    # grey
    "ROAD_PAVEMENT_AGG": 9,    # lighter grey
    "ROAD_SHOULDER": 31,       # brown
    "ROAD_CURB": 253,          # near-white grey
    "ROAD_SIDEWALK": 254,      # light grey
    "ROAD_SLOPE": 3,           # green
    "ROAD_DITCH": 5,           # blue
    "ROAD_BARRIER": 250,       # dark
    "ROAD_WALL": 6,            # magenta
    "ROAD_SURFACE": 2,         # yellow
    "ROAD_MISC": 7,            # white
    "ANNOTATION_DIM": 1,       # red
    "ANNOTATION_TEXT": 7,      # white
    "ANNOTATION_SLOPE": 4,     # cyan
    "DEFPOINTS": 7,
}

_ALL_LAYERS = list(_LAYER_COLORS_ACI.keys())


# ---------------------------------------------------------------------------
# DXF Exporter
# ---------------------------------------------------------------------------


class DXFExporter:
    """Export road section geometry (and optional annotations) to DXF.

    The output is an ASCII DXF R2010 file compatible with AutoCAD,
    BricsCAD, Civil 3D, and most other CAD applications.

    Parameters
    ----------
    precision:
        Number of decimal places for coordinate output.  Default 6.
    """

    def __init__(self, precision: int = 6) -> None:
        self.precision = precision
        self._fmt = f"{{:.{precision}f}}"

    def _f(self, v: float) -> str:
        return self._fmt.format(v)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def export(self, geometry: SectionGeometry, output: TextIO) -> None:
        """Export geometry without annotations."""
        self._write_dxf(geometry, output, annotations=None)

    def export_annotated(
        self,
        geometry: SectionGeometry,
        annotations: "SectionAnnotations",
        output: TextIO,
    ) -> None:
        """Export geometry with annotations on separate DXF layers."""
        self._write_dxf(geometry, output, annotations=annotations)

    # ------------------------------------------------------------------
    # DXF structure
    # ------------------------------------------------------------------

    def _write_dxf(
        self,
        geometry: SectionGeometry,
        output: TextIO,
        annotations: "SectionAnnotations | None",
    ) -> None:
        try:
            import ezdxf
            from ezdxf import enums
        except ImportError as exc:
            raise ImportError(
                "ezdxf is required for DXF export. "
                "Install it with: pip install cross-section[dxf]"
            ) from exc

        doc = ezdxf.new("R2010")
        doc.header["$INSUNITS"] = 6  # metres

        # Create all layers
        for layer_name in _ALL_LAYERS:
            aci = _LAYER_COLORS_ACI.get(layer_name, 7)
            doc.layers.add(layer_name, color=aci)

        msp = doc.modelspace()

        # Draw geometry
        for comp in geometry.components:
            self._add_component(msp, comp)

        # Draw annotations
        if annotations:
            self._add_annotations(msp, annotations, geometry)

        doc.write(output)

    def _add_component(self, msp: object, comp: object) -> None:  # type: ignore[type-arg]
        from ezdxf.entities import Hatch
        meta = comp.metadata  # type: ignore[attr-defined]
        comp_type = meta.get("component_type", "")
        pavement_layers = meta.get("layers", [])

        for poly_idx, polygon in enumerate(comp.polygons):  # type: ignore[attr-defined]
            # Determine DXF layer
            if poly_idx < len(pavement_layers):
                pl_type = pavement_layers[poly_idx].get("type", "")
                dxf_layer = _PAVEMENT_LAYER_MAP.get(pl_type, "ROAD_MISC")
            else:
                dxf_layer = self._component_layer(comp_type)

            # Convert exterior vertices to 2D tuples
            pts = [(p.x, p.y) for p in polygon.exterior]  # type: ignore[attr-defined]
            if pts and pts[0] != pts[-1]:
                pts.append(pts[0])  # close the ring

            # Lightweight polyline for outline
            msp.add_lwpolyline(  # type: ignore[attr-defined]
                pts,
                format="xy",
                close=True,
                dxfattribs={"layer": dxf_layer},
            )

            # Solid hatch fill
            hatch = msp.add_hatch(dxfattribs={"layer": dxf_layer})  # type: ignore[attr-defined]
            aci = _LAYER_COLORS_ACI.get(dxf_layer, 7)
            hatch.set_solid_fill(color=aci)
            hatch.paths.add_polyline_path(  # type: ignore[attr-defined]
                [(p.x, p.y) for p in polygon.exterior],  # type: ignore[attr-defined]
                is_closed=True,
            )

        # Polylines (ditch voids, surface profiles)
        for polyline in comp.polylines:  # type: ignore[attr-defined]
            dxf_layer = self._component_layer(comp_type)
            pts = [(p.x, p.y) for p in polyline]  # type: ignore[attr-defined]
            msp.add_lwpolyline(pts, format="xy", dxfattribs={"layer": dxf_layer})  # type: ignore[attr-defined]

    def _add_annotations(
        self,
        msp: object,
        annotations: "SectionAnnotations",
        geometry: SectionGeometry,
    ) -> None:
        from ezdxf.enums import TextEntityAlignment

        _, _, _, section_max_y = geometry.bounds()
        dim_y = section_max_y + 0.8  # 0.8 m above top of section

        # Width dimensions
        for dim in annotations.dimensions:
            # DXF QDIM-style: use aligned dimension entity
            # Place dimension line at dim_y, measure between x_start and x_end
            x1, x2 = sorted([dim.x_start, dim.x_end])
            mid_x = (x1 + x2) / 2.0

            try:
                dimstyle = self._ensure_dimstyle(msp)
                msp.add_linear_dim(  # type: ignore[attr-defined]
                    base=(mid_x, dim_y),
                    p1=(x1, dim.y_surface),
                    p2=(x2, dim.y_surface),
                    dimstyle=dimstyle,
                    override={"dimtxt": 0.15, "dimasz": 0.1},
                    dxfattribs={"layer": "ANNOTATION_DIM"},
                ).render()
            except Exception:
                # Fallback: plain text if dimension fails
                msp.add_text(  # type: ignore[attr-defined]
                    dim.text,
                    dxfattribs={
                        "layer": "ANNOTATION_DIM",
                        "height": 0.15,
                        "insert": (mid_x, dim_y + 0.1),
                        "halign": 1,  # center
                    },
                )

        # Slope tags
        for tag in annotations.slope_tags:
            msp.add_text(  # type: ignore[attr-defined]
                tag.text,
                dxfattribs={
                    "layer": "ANNOTATION_SLOPE",
                    "height": 0.12,
                    "insert": (tag.x, tag.y + 0.1),
                },
            )

        # Labels
        for label in annotations.labels:
            msp.add_text(  # type: ignore[attr-defined]
                label.text,
                dxfattribs={
                    "layer": "ANNOTATION_TEXT",
                    "height": 0.10,
                    "insert": (label.x, label.y),
                },
            )

    def _component_layer(self, comp_type: str) -> str:
        for prefix, layer in _COMPONENT_LAYER_MAP.items():
            if comp_type.startswith(prefix):
                return layer
        return "ROAD_MISC"

    def _ensure_dimstyle(self, msp: object) -> str:  # type: ignore[type-arg]
        """Return a metric dimstyle name, creating it if needed."""
        try:
            doc = msp.doc  # type: ignore[attr-defined]
            if "CS_METRIC" not in doc.dimstyles:
                doc.dimstyles.new(
                    "CS_METRIC",
                    dxfattribs={
                        "dimtxt": 0.15,
                        "dimasz": 0.10,
                        "dimexo": 0.05,
                        "dimexe": 0.05,
                        "dimlunit": 2,  # decimal
                        "dimrnd": 0.01,
                    },
                )
            return "CS_METRIC"
        except Exception:
            return "Standard"
