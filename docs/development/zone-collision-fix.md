# Zone-Aware Collision Resolution Fix

**Date:** 2026-02-08
**Status:** Implemented, tested, visual results verified

## Problem

Annotations (labels, symbols, dimension lines) were being pushed to an "overflow band" far above the cross-section instead of appearing inside the dimension brackets where they belong. A two-lane road with curb and gutter was generating 10+ overflow annotations.

The root cause was a series of interacting issues in the collision resolver that prevented annotations from coexisting within dimension brackets.

## Background: Annotation Zone System

The zone system assigns vertical bands above the road surface for each annotation type:

```
Zone 4: DIMENSION     @ 0.70m  ─── horizontal dimension line + text
Zone 3: SECONDARY_SYM @ 0.45m  ─── drainage arrows, slope text (0.69m)
Zone 2: PRIMARY_SYM   @ 0.30m  ─── traffic direction arrows
Zone 1: LABEL_TEXT     @ 0.12m  ─── component labels ("Lane", "Shoulder")
Zone 0: GEOMETRY       @ 0.00m  ─── road surface (immutable)
```

Annotations are intentionally placed at different vertical offsets within the dimension brackets (the space between the dimension line at top and the road surface at bottom). The collision resolver should not fight this layout.

## Root Causes Identified

### 1. Dimension `bounds()` creates a huge bounding box

`DimensionAnnotation.bounds()` includes `self.start` and `self.end` (road surface attachment points) plus the dimension line points. This creates a bounding box spanning from the road surface all the way up to the dimension line — essentially the entire bracket area.

**Impact:** Any generic `bounds().intersects()` check against a dimension annotation will always return `True` for anything inside the brackets.

### 2. `_annotation_has_collision` used generic bounds checks for dimensions

In the final overflow check (`_collect_colliding_indices` -> `_annotation_has_collision`), text annotations were checked against dimension annotations using:

```python
if other.bounds().intersects(annotation.bounds(), buffer=self.text_buffer):
    return True
```

This always triggered for any text inside the brackets because of issue #1. The more precise `detect_line_text` was called first but only checked line segments (which correctly skipped extension lines for inside-span items). The secondary bounds check then caught everything.

**Fix:** Only use the generic bounds check for `LeaderAnnotation`, not `DimensionAnnotation`. This matches the pattern already used in `_has_collision`.

### 3. Symbol `else` catch-all also used generic bounds

For `SymbolAnnotation` checking against other annotation types, an `else` branch caught `DimensionAnnotation` and `LeaderAnnotation` with the same overly broad `bounds().intersects()` check.

**Fix:** Changed to `elif` chain so each annotation type uses its appropriate detector (`detect_symbol_dimension`, `detect_symbol_leader`).

### 4. Collision resolver was zone-unaware

`_annotation_has_collision` checked ALL annotation pairs regardless of zone. A label in LABEL_TEXT zone would "collide" with a traffic arrow in PRIMARY_SYMBOL zone simply because their bounding boxes overlapped vertically. This is expected and intentional — the zone system handles vertical separation by design.

**Fix:** Added zone-awareness to `_annotation_has_collision` — annotations in different zones skip collision checks entirely.

### 5. Traffic arrows extend below road surface (geometry collision)

The traffic arrow symbol is 0.7m tall. Centered at the PRIMARY_SYMBOL offset (0.30m above road surface), its bottom extends to -0.05m below the surface. This triggered geometry collision detection, and the resolver couldn't find a valid position.

**Fix:** Traffic arrows are now created with `allow_geometry_overlap: True` metadata in the planner.

### 6. Same-layer paired annotations collide (rotation-inflated bounds)

The drainage arrow and its associated "2%" slope text are both in the SECONDARY_SYMBOL zone. The drainage arrow is rotated, which inflates its bounding box using the diagonal formula:

```
actual shape:  0.32m x 0.16m (scale=0.8)
diagonal bbox: 0.36m x 0.36m (much larger)
```

This made the drainage arrow's bounds overlap with the slope text even though they were at different Y positions.

**Fix:** Same-layer annotations at the same X position are treated as semantically paired and skip collision detection against each other.

### 7. `BoundingBox.intersects(buffer=N)` expands BOTH boxes

The `intersects` method expands both boxes by the buffer amount, so the effective gap required is `2 * buffer`, not `buffer`. With the default `text_buffer=0.05`, annotations need 0.10m of clearance, not 0.05m.

**Fix:** Adjusted `slope_text_offset` from 0.55 to 0.69 to account for the double expansion plus the rotation-inflated drainage arrow bounds.

### 8. `_has_any_collision` fast-path not zone-aware

The fast-path check that determines whether to run the resolution loop at all was checking symbol-text collisions without zone filtering. This caused unnecessary resolution attempts that could move annotations out of position.

**Fix:** Added zone filtering to the symbol-text collision check in `_has_any_collision`.

## Files Modified

| File | Change |
|------|--------|
| `collision.py` | Zone-aware `_annotation_has_collision`, extension line fixes, paired annotation detection, fast-path zone filtering |
| `planner.py` | Traffic arrows get `allow_geometry_overlap` metadata |
| `profile.py` | `slope_text_offset` 0.55 -> 0.69 |
| `zones.py` | Zone enum reorder (LABEL_TEXT=1 closest, DIMENSION=4 furthest), offset constants updated |

## Results

| Generator | Before | After |
|-----------|--------|-------|
| curb_and_gutter | 10+ overflow | 0 overflow |
| basic_section | text overflow | 0 overflow |
| symmetric_section | text overflow | 0 overflow |

All 429 tests pass. Annotations now correctly appear inside dimension brackets with the expected stacking order.

## Remaining Work

- **Leader positioning:** Many generators warn "Could not find valid position for leader to avoid dimension". Leaders cross dimension lines because they route from pavement layers (below surface) up to callout text.
- **Non-lane label overflow:** Some generators still push labels for non-lane components (shoulders, ditches, slopes) to overflow. These labels collide with each other when components are narrow.
- **Traffic arrow scale:** The 0.7m base height is large relative to the bracket space. Consider reducing the symbol definition size or applying a default scale < 1.0 in the planner.
- **Rotated symbol bounding boxes:** The diagonal bounding box for rotated symbols is very conservative. Consider computing a tighter axis-aligned bounding box from the actual rotated corners.

## Key Lessons

1. **Never use `bounds().intersects()` against DimensionAnnotation** — its bounds span from road surface to dimension line. Always use the dedicated `detect_line_text` or `detect_symbol_dimension` methods.
2. **`BoundingBox.intersects(buffer=N)` needs gap > 2N** — both boxes expand by N.
3. **Rotated symbols have inflated bounding boxes** — a 0.16m-tall arrow becomes 0.36m when rotated, due to the diagonal bounding box formula.
4. **Zone-awareness is essential** — the collision resolver must respect the zone system rather than fighting it.
