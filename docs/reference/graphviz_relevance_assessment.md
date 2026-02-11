# Graphviz Label Non-Intersection: Relevance Assessment

**Date:** 2026-02-08
**Input:** `graphviz_non_intersecting_notes.md` (researcher report on Graphviz 14.1.2)

## Summary

Reviewed Graphviz's label placement and overlap removal approaches for applicability to our annotation collision resolver. The most relevant technique is the VPSC (Variable Placement with Separation Constraints) solver — a 1D constraint-based approach that minimizes displacement while enforcing non-overlap.

## Relevance by Technique

### VPSC Constraint Solver — HIGH relevance
- Solves overlap globally: "move everything the minimum distance so nothing overlaps"
- Two-pass (X then Y) maps well to our layout: annotations distributed along X with zone-constrained Y
- Directly addresses non-lane label overflow (narrow components where labels crowd)
- Our current iterative nudge-and-overflow approach is a local search that gets stuck; VPSC finds optimal solutions
- **Decision: Implement a 1D constraint solver for same-zone horizontal label separation**

### XLabel Placement — MODERATE relevance
- R-tree spatial index for O(n log n) queries vs our O(n²) pairwise checks
- "Sliding along edges" fallback is cleaner than overflow band ejection
- Not needed at current annotation counts (20-40 per section), but good to know for scaling
- **Decision: Defer; current scale doesn't warrant spatial indexing**

### Overlap Graph + Stress Majorization — LOW relevance
- Designed for unconstrained 2D node layouts with free movement
- Our annotations are heavily constrained: X by component, Y by zone
- Overkill for our problem structure
- **Decision: Skip**

### Edge-Label-as-Node — NOT applicable
- No equivalent concept in cross-section annotations
- **Decision: Skip**

### Overlap Removal Framework Modes (voronoi/prism/scale) — NOT applicable
- For spreading unconstrained 2D layouts
- Our problem is 1D (horizontal) within fixed vertical zones
- **Decision: Skip**

## Implementation Plan

Replace the iterative nudge-and-check collision resolver with a 1D VPSC-style constraint solver:

1. Group annotations by zone
2. Within each zone, sort by X position
3. Generate separation constraints: "right edge of A + gap <= left edge of B"
4. Solve the 1D constraint satisfaction to find minimum-displacement positions
5. Apply solved positions, eliminating the overflow band for within-zone conflicts

This is a significant but well-scoped change — the constraint problem reduces to 1D (X-axis only) since Y positions are fixed by zone assignment.
