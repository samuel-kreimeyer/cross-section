"""Pixel-verified annotation overlap tests.

Uses the annotation-only debug SVG renderer (unique color per annotation)
rasterized via Inkscape, then checks for adjacent pixels of different
non-white colors — which indicates annotation overlap.
"""

import io
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from cross_section.core.domain import ControlPoint, RoadSection, TravelLane
from cross_section.core.domain.annotations import (
    AnnotationGenerator,
    default_annotation_options,
)
from cross_section.core.domain.components import Ditch, SurfaceProfile
from cross_section.core.domain.pavement import AsphaltLayer, CrushedRockLayer
from cross_section.export.svg_annotations import AnnotatedSVGExporter

# Skip entire module if inkscape is not available
HAS_INKSCAPE = shutil.which("inkscape") is not None
pytestmark = pytest.mark.skipif(not HAS_INKSCAPE, reason="inkscape not available")

try:
    import numpy as np
    from PIL import Image
    HAS_IMAGING = True
except ImportError:
    HAS_IMAGING = False

pytestmark = [
    pytest.mark.skipif(not HAS_INKSCAPE, reason="inkscape not available"),
    pytest.mark.skipif(not HAS_IMAGING, reason="numpy and/or PIL not available"),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_debug_png(geometry, annotations, tmp_dir: Path, name: str):
    """Export debug SVG, rasterize to PNG, return (pixel_array, color_list)."""
    exporter = AnnotatedSVGExporter(scale=50.0)

    svg_path = tmp_dir / f"{name}.svg"
    png_path = tmp_dir / f"{name}.png"

    with open(svg_path, "w") as f:
        exporter.export_annotations_debug(geometry, annotations, f)

    # Collect the palette of annotation colors (same logic as renderer)
    total = annotations.count()
    colors = [exporter._debug_color(i, total) for i in range(total)]

    # Rasterize via inkscape (headless)
    subprocess.run(
        ["inkscape", str(svg_path), "--export-type=png",
         f"--export-filename={png_path}", "--export-dpi=96"],
        check=True, capture_output=True,
    )

    img = Image.open(png_path).convert("RGB")
    return np.array(img), colors


def _check_pixel_overlap(
    pixels: "np.ndarray",
    annotation_colors: list[str],
    tolerance_cluster: int = 100,
) -> list[dict]:
    """Check for adjacent pixels belonging to different annotations.

    Each pixel is mapped to its *nearest* annotation colour (Euclidean
    distance in RGB space).  Only pixels whose nearest colour is within
    a reasonable distance are considered "inked" — the rest are treated
    as background.  Two adjacent inked pixels that map to *different*
    annotation colours indicate an overlap.

    Clusters of overlapping pixels smaller than *tolerance_cluster* are
    discarded as anti-aliasing noise.

    Args:
        pixels: H×W×3 uint8 numpy array (RGB).
        annotation_colors: List of hex colour strings (e.g. "#b20000")
            in annotation index order, as produced by ``_debug_color``.
        tolerance_cluster: Minimum cluster size to report.

    Returns:
        List of overlap descriptors (empty = no overlaps).
    """
    import numpy as np

    h, w, _ = pixels.shape

    # Parse annotation palette into an (N, 3) uint8 array
    palette = np.array(
        [[int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)] for c in annotation_colors],
        dtype=np.int32,
    )
    n_colors = len(palette)

    # Flatten pixels to (H*W, 3) for vectorised distance computation
    flat = pixels.reshape(-1, 3).astype(np.int32)

    # Compute squared distance from every pixel to every palette entry
    # Using broadcasting: (H*W, 1, 3) - (1, N, 3) → (H*W, N, 3)
    diff = flat[:, None, :] - palette[None, :, :]  # (H*W, N, 3)
    sq_dist = (diff * diff).sum(axis=2)  # (H*W, N)

    # Nearest annotation for each pixel
    nearest_idx = sq_dist.argmin(axis=1).reshape(h, w)  # (H, W) int
    nearest_dist = sq_dist.min(axis=1).reshape(h, w)  # (H, W) int

    # Background mask: a pixel is background if it's closer to white
    # than to its nearest annotation colour *by a margin*.  Anti-aliased
    # edge pixels are blended towards white and should be background.
    # We also require the pixel to be reasonably close to its nearest
    # palette colour (within ~80 RGB units per channel).
    white = np.array([255, 255, 255], dtype=np.int32)
    white_diff = flat - white[None, :]
    white_dist = (white_diff * white_diff).sum(axis=1).reshape(h, w)

    # A pixel is "inked" only if it's (a) closer to an annotation colour
    # than to white AND (b) within a reasonable distance from that colour.
    # Condition (b) catches stray anti-aliased pixels that are equidistant
    # from both white and an annotation colour.
    MAX_DIST_SQ = 3 * 80 * 80  # ~80 per channel
    is_inked = (nearest_dist < white_dist) & (nearest_dist < MAX_DIST_SQ)

    # Check 4 directions for adjacent inked pixels with different labels
    overlap_mask = np.zeros((h, w), dtype=bool)

    for dy, dx in [(0, 1), (1, 0), (1, 1), (1, -1)]:
        sy = slice(None, -1) if dy else slice(None)
        ey = slice(1, None) if dy else slice(None)
        if dx == 1:
            sx, ex = slice(None, -1), slice(1, None)
        elif dx == -1:
            sx, ex = slice(1, None), slice(None, -1)
        else:
            sx, ex = slice(None), slice(None)

        src_idx = nearest_idx[sy, sx]
        nbr_idx = nearest_idx[ey, ex]
        src_ink = is_inked[sy, sx]
        nbr_ink = is_inked[ey, ex]

        conflict = src_ink & nbr_ink & (src_idx != nbr_idx)
        # Mark both the source and neighbour pixels
        tmp = np.zeros((h, w), dtype=bool)
        tmp[sy, sx] |= conflict
        tmp[ey, ex] |= conflict
        overlap_mask |= tmp

    # Cluster using flood-fill
    overlap_positions = list(zip(*np.nonzero(overlap_mask)))
    if len(overlap_positions) < tolerance_cluster:
        return []

    visited: set[tuple[int, int]] = set()
    clusters: list[list[tuple[int, int]]] = []
    for pos in overlap_positions:
        if pos in visited:
            continue
        cluster: list[tuple[int, int]] = []
        queue = [pos]
        visited.add(pos)
        while queue:
            cy, cx = queue.pop()
            cluster.append((cy, cx))
            for ny, nx in [(cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)]:
                if (ny, nx) in visited:
                    continue
                if 0 <= ny < h and 0 <= nx < w and overlap_mask[ny, nx]:
                    visited.add((ny, nx))
                    queue.append((ny, nx))
        clusters.append(cluster)

    results = []
    for cluster in clusters:
        if len(cluster) < tolerance_cluster:
            continue
        y, x = cluster[0]
        a1 = int(nearest_idx[y, x])
        # Find adjacent pixel with different annotation
        a2 = None
        for ddy, ddx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            ny, nx = y + ddy, x + ddx
            if 0 <= ny < h and 0 <= nx < w and is_inked[ny, nx]:
                if nearest_idx[ny, nx] != a1:
                    a2 = int(nearest_idx[ny, nx])
                    break
        results.append({
            "x": x, "y": y,
            "color1": annotation_colors[a1] if a1 < n_colors else "?",
            "color2": annotation_colors[a2] if a2 is not None and a2 < n_colors else "unknown",
            "ann_idx1": a1,
            "ann_idx2": a2,
            "cluster_size": len(cluster),
        })

    return results


# ---------------------------------------------------------------------------
# Section builders (reuse logic from generators)
# ---------------------------------------------------------------------------

def _build_basic_section():
    """Build the basic two-lane section (same as basic_section.py generator)."""
    pavement_layers = [
        AsphaltLayer(thickness=0.05, aggregate_size=12.5,
                     binder_type="PG 64-22", binder_percentage=5.5, density=2400),
        AsphaltLayer(thickness=0.075, aggregate_size=19.0,
                     binder_type="PG 64-22", binder_percentage=5.0, density=2380),
        CrushedRockLayer(thickness=0.15, aggregate_size=37.5,
                         density=2200, material_type="crushed_stone"),
    ]

    section = RoadSection(
        name="Two-Lane Road",
        control_point=ControlPoint(x=0.0, elevation=100.0),
    )
    section.add_component_right(TravelLane(
        width=3.6, cross_slope=0.02, traffic_direction="outbound",
        pavement_layers=pavement_layers,
    ))
    section.add_component_right(TravelLane(
        width=3.6, cross_slope=0.02, traffic_direction="outbound",
        pavement_layers=list(pavement_layers),
    ))

    geometry = section.to_geometry()
    options = default_annotation_options()
    annotations = AnnotationGenerator.generate(geometry, options)
    annotations.resolve_collisions(geometry=geometry)
    return geometry, annotations


def _build_crowned_road():
    """Build crowned road section (same as crowned_road.py generator)."""
    ft_to_m = 0.3048
    pavement = AsphaltLayer(thickness=0.15, aggregate_size=12.5,
                            binder_type="PG 64-22", binder_percentage=5.5, density=2400)

    section = RoadSection(
        name="Crowned Road",
        control_point=ControlPoint(x=0.0, elevation=100.0),
        left_components=[
            TravelLane(width=12.0 * ft_to_m, cross_slope=0.02,
                       traffic_direction="inbound", pavement_layers=[pavement]),
            SurfaceProfile(
                segments=[(8.0 * ft_to_m, 8.0 * ft_to_m * 0.02)],
                surface_type="asphalt",
            ),
            Ditch(depth=1.0 * ft_to_m, foreslope_ratio=4.0,
                  backslope_ratio=4.0, bottom_width=0.0),
        ],
        right_components=[
            TravelLane(width=12.0 * ft_to_m, cross_slope=0.02,
                       traffic_direction="outbound", pavement_layers=[pavement]),
            SurfaceProfile(
                segments=[(8.0 * ft_to_m, 8.0 * ft_to_m * 0.02)],
                surface_type="asphalt",
            ),
            Ditch(depth=1.0 * ft_to_m, foreslope_ratio=4.0,
                  backslope_ratio=4.0, bottom_width=0.0),
        ],
    )

    geometry = section.to_geometry()
    options = default_annotation_options()
    annotations = AnnotationGenerator.generate(geometry, options)
    annotations.resolve_collisions(geometry=geometry)
    return geometry, annotations


def _build_symmetric_section():
    """Build a symmetric two-lane section with left and right lanes."""
    pavement_layers = [
        AsphaltLayer(thickness=0.05, aggregate_size=12.5,
                     binder_type="PG 64-22", binder_percentage=5.5, density=2400),
        CrushedRockLayer(thickness=0.15, aggregate_size=37.5,
                         density=2200, material_type="crushed_stone"),
    ]

    section = RoadSection(
        name="Symmetric Section",
        control_point=ControlPoint(x=0.0, elevation=100.0),
        left_components=[
            TravelLane(width=3.6, cross_slope=0.02,
                       traffic_direction="inbound",
                       pavement_layers=list(pavement_layers)),
        ],
        right_components=[
            TravelLane(width=3.6, cross_slope=0.02,
                       traffic_direction="outbound",
                       pavement_layers=list(pavement_layers)),
        ],
    )

    geometry = section.to_geometry()
    options = default_annotation_options()
    annotations = AnnotationGenerator.generate(geometry, options)
    annotations.resolve_collisions(geometry=geometry)
    return geometry, annotations


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestAnnotationPixelOverlap:
    """Pixel-level overlap verification for annotation layouts."""

    def _run_overlap_check(self, geometry, annotations, name: str):
        """Build debug PNG and assert no overlaps."""
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            pixels, colors = _build_debug_png(geometry, annotations, tmp_dir, name)
            overlaps = _check_pixel_overlap(pixels, colors)

            if overlaps:
                # Save the debug image for inspection
                debug_dir = Path(__file__).parent / "output"
                debug_dir.mkdir(exist_ok=True)
                debug_path = debug_dir / f"{name}_debug_overlap.png"
                Image.fromarray(pixels).save(debug_path)

                details = "\n".join(
                    f"  ({o['x']}, {o['y']}): {o['color1']} vs {o['color2']} "
                    f"(cluster={o['cluster_size']}px)"
                    for o in overlaps[:10]
                )
                pytest.fail(
                    f"{len(overlaps)} annotation overlap(s) detected in {name}.\n"
                    f"Debug image saved to {debug_path}\n"
                    f"First overlaps:\n{details}"
                )

    def test_basic_section_no_overlap(self):
        geometry, annotations = _build_basic_section()
        self._run_overlap_check(geometry, annotations, "basic_section")

    def test_crowned_road_no_overlap(self):
        geometry, annotations = _build_crowned_road()
        self._run_overlap_check(geometry, annotations, "crowned_road")

    def test_symmetric_section_no_overlap(self):
        geometry, annotations = _build_symmetric_section()
        self._run_overlap_check(geometry, annotations, "symmetric_section")
