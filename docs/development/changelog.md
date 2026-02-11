# Development Changelog

All notable development changes recorded for internal tracking.

## Status: Annotation System

**Little progress has been made on annotation placement quality since the
basic implementation.** The zone system, collision resolver, overflow band,
and 1D constraint solver were all attempts to fix crowding/overlap, but none
have produced output that matches hand-annotated reference drawings. All
features implemented in the annotation module since the initial planner
should be regarded with skepticism — the fundamental layout strategy needs
rethinking, not incremental fixes to collision resolution.

The reference layout (see `tests/output/basic_section_annotated.svg`)
differs from the generated output in several key ways:

- Dimensions should be at the top of the drawing with extension lines
  reaching down to the geometry.
- Component labels should sit just below the dimension text, centered over
  each component.
- Slope/drainage arrows sit between labels and the road surface.
- Pavement layer leaders should point upward from below the geometry, not
  extend horizontally to the right margin.

## 2026-02-09

### 1D constraint solver for text-text collisions
- Added `solver.py` with `sweep_compact_1d()` — forward+backward sweep
  algorithm for minimum-displacement horizontal placement.
- Integrated into `CollisionResolver.resolve_all()` as primary text-text
  resolution method, replacing the iterative greedy loop.
- Legacy `_resolve_text_text_collisions` kept as fallback (max 3 iterations).
- Pre-existing overflow from drainage arrow diagonal bounding boxes remains.

## 2026-02-08

### Zone-aware collision resolution ([docs](zone-collision-fix.md))
- Fixed annotation overflow caused by collision resolver fighting the zone placement system.
- Made `_annotation_has_collision` zone-aware: different-zone annotations no longer collide.
- Removed overly broad `bounds().intersects()` checks against DimensionAnnotation (whose bounds span the entire bracket area from road surface to dimension line).
- Added paired-annotation detection: same-layer items at the same X position skip collision checks.
- Extension lines in `detect_line_text` and `detect_symbol_dimension` now exempt annotations horizontally inside the dimension span.
- Traffic arrows get `allow_geometry_overlap` metadata (their 0.7m height extends below road surface).
- Adjusted `slope_text_offset` (0.55 -> 0.69) to account for rotation-inflated bounding boxes and double-expanded buffer.
- Result: curb_and_gutter went from 10+ overflow annotations to 0.

### PNG output for generators
- Added `tests/generators/_svg_to_png.py` helper using Inkscape CLI.
- All 14 generator scripts now produce PNG alongside SVG.
- `regenerate_all_svgs.py` reports PNG file sizes.

## 2026-01-16

- Switched scenario builders and annotated generator scripts to automated annotations.
- Removed manual annotation helpers in scenarios/generators to keep outputs aligned with generator quality.
- Updated integration tests to assert automated annotation presence instead of manual label text.
