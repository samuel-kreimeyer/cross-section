# Graphviz: Non‑Intersecting Labels and Elements (Source Review)

This summary focuses on how Graphviz attempts to avoid overlaps among labels, nodes, and related elements, based on the code in `graphviz-14.1.2/`.

**Key Takeaways**
- Graphviz relies on two layers of logic: (1) placement heuristics for labels (notably `xlabel`), and (2) post‑layout overlap removal for nodes/labels using several algorithms selected via the `overlap` attribute.
- Overlap removal is configurable and algorithmic, not just “push apart” logic. It builds overlap graphs, applies stress‑majorization or constraint solvers, and can shrink/expand the layout to minimize overlaps.
- Some label handling (especially edge labels) is integrated into the overlap removal pipeline, notably in SFDP’s edge‑label schemes.

**1) XLabel Placement: Heuristic, Spatially Indexed**
Files:
- `graphviz-14.1.2/lib/label/xlabels.c`

Highlights:
- `placeLabels(...)` places “external labels” (`xlabel`) near their owning object, trying to avoid intersecting any objects or other labels.
- The algorithm builds an R‑tree for spatial queries (`RTreeInsert`/`RTreeSearch`) and uses Hilbert curve ordering to populate it efficiently (`hd_hil_s_from_xy`, `xlhorder`).
- For each labeled object, it tries a prioritized set of anchor positions around the object (left/mid/right × top/mid/bottom). If these intersect, it slides along the top/left/right/bottom edges in increments derived from label size (`xincr`, `yincr`).
- It tracks intersections and keeps the candidate with minimum overlap area if a zero‑overlap placement is not found (`xlintersections`, `recordointrsx`, `recordlintrsx`).
- If `params->force` is true, it accepts the best available position even if overlaps remain; otherwise it reports failure.

Implication for cross‑sections:
- The `xlabel` logic is a compact example of label placement with spatial indexing, good for “labels outside shapes” with priority order + sliding fallback.

**2) Overlap Detection Primitives**
Files:
- `graphviz-14.1.2/lib/common/utils.c`

Highlights:
- `overlap_node`, `overlap_label`, `overlap_edge` provide consistent “does this geometry intersect a box?” checks.
- Edge overlap checks handle spline segments and arrowheads (`overlap_bezier`, `overlap_arrow`) and label bounding boxes.

Implication:
- These are reusable low‑level building blocks for testing overlap of labels, nodes, and edges using bounding boxes and geometry checks.

**3) Overlap Removal Framework (neato/fdp/sfdp)**
Files:
- `graphviz-14.1.2/lib/neatogen/adjust.c`

Highlights:
- `removeOverlapWith(...)` is the main entry point after initial layout. It normalizes and scales positions, then applies a chosen algorithm based on `overlap`.
- `getAdjustMode(...)` maps the `overlap` attribute to an algorithm. Supported modes include:
  - `prism` (if built with GTS)
  - `voronoi`
  - `scale`, `scalexy`, `compress`
  - `vpsc`, `ipsep`
  - `ortho` variants
- `adjustNodes(...)` uses the graph’s `overlap` attribute directly.

Relevant attributes for overlap behavior:
- `overlap` selects algorithm and parameters.
- `overlap_scaling` affects prism scaling.
- `overlap_shrink` allows shrinking if there is unused whitespace.
- `sep` and `voro_margin` influence how boxes are grown before overlap resolution.

**4) Overlap Removal Algorithms: Stress Majorization + Overlap Graphs**
Files:
- `graphviz-14.1.2/lib/neatogen/overlap.c`

Highlights:
- Builds an “overlap graph” using sweep‑line with a red‑black tree (`get_overlap_graph`). This detects which rectangles overlap (using intervals in X and Y).
- `OverlapSmoother_new` computes ideal distances to separate overlapping items. It uses stress‑majorization to update positions (`OverlapSmoother_smooth`).
- Supports scaling the layout up or down to eliminate overlap (`overlap_scaling`), with bisection search for a minimal scaling factor.
- Iterative removal: first “neighbor‑only” overlap removal, then global. Optional shrinking if no overlap and `overlap_shrink` is enabled.
- Integrates edge‑label constraints when `edge_labeling_scheme` is active, so labels can be treated as nodes with constraints.

Implication:
- This is a mathematically grounded overlap solver, not a simple local repulsion. It’s a strong reference for non‑intersection requirements.

**5) VPSC Constraint‑Based Non‑Overlap**
Files:
- `graphviz-14.1.2/lib/neatogen/quad_prog_vpsc.c`

Highlights:
- `generateNonoverlapConstraints(...)` builds X/Y constraints from node rectangles (plus gaps) and optionally cluster bounds. It does two passes (X then Y).
- Uses a Variable‑Placement with Separation Constraints (VPSC) solver to move nodes minimally while satisfying constraints.
- Supports clusters by adding dummy variables for cluster boundaries and remapping constraints.
- `removeoverlaps(...)` solves in X, then Y, updating coordinates in place.

Implication:
- VPSC is a robust “minimal movement” constraint solver. This is a good model for “don’t overlap, but move as little as possible.”

**6) Edge‑Label‑Aware Overlap Removal (SFDP)**
Files:
- `graphviz-14.1.2/lib/sfdpgen/spring_electrical.c`

Highlights:
- For certain `edge_labeling_scheme` values, SFDP first computes a layout *without* edge‑label nodes, then attaches labels near the average of neighbors.
- It then calls `remove_overlap(...)` with label sizes, so labels are included in overlap resolution.

Implication:
- Treating edge labels as nodes during overlap removal is an effective strategy for label‑heavy diagrams.

**7) Notes on Dot/XLabel Interactions**
Files:
- `graphviz-14.1.2/cmd/dot/dot.1`

Highlights:
- `xlabel` is placed after nodes/edges are positioned; this can introduce label overlaps if no further adjustment is done.

Implication:
- If you rely on `xlabel`, you’ll often need an additional overlap‑avoidance step to keep labels non‑intersecting.

---

## Practical Insights to Reuse in the Cross‑Section Project
- For label placement, the `xlabel` algorithm is a good blueprint: generate a small ordered set of preferred positions, then slide along edges and pick the position with minimum total intersection area.
- For overlap removal, Graphviz’s two‑pass approach (neighbor‑only then full) and its scaling/shrinking logic are useful patterns for stabilizing layouts.
- VPSC constraints are a solid way to enforce non‑overlap while minimizing displacement (especially if you need stable layouts across edits).
- If labels are conceptually “nodes,” treat them as nodes in the overlap system, then map them back to visual labels.

