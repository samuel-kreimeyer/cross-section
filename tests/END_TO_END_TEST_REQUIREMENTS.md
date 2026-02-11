# End-to-End Test Requirements

All generators in `tests/generators/` and scripts invoked by
`tests/regenerate_all_svgs.py` **must** follow three rules.

## Rule 1 — No manual annotation placement

Only the annotation engine (`AnnotationGenerator.generate()`) places
annotations. Generators must never create `TextAnnotation`,
`DimensionAnnotation`, etc. by hand.

**Why:** Manual placement bypasses collision resolution and silently
diverges from the engine's output. If a generator needs a specific
annotation style, the fix belongs in the engine or in the profile, not in
generator code.

## Rule 2 — No per-test annotation configuration

Every generator must use `default_annotation_options()` (exported from
`cross_section.core.domain.annotations`). This returns the standard
"everything on" profile that exercises the full annotation engine.

**Why:** Per-test toggles hide engine bugs. If a generator disables
traffic arrows to avoid a collision, the collision bug is never caught.

## Rule 3 — No fallback / silent degradation

After calling `annotations.resolve_collisions(geometry=geometry)`, the
generator **must** inspect the returned `CollisionResult`:

```python
result = annotations.resolve_collisions(geometry=geometry)
if not result.success:
    print(f"  FAIL: {result.overflow_count} overflow, "
          f"{result.remaining_collisions} collisions")
    sys.exit(1)
```

Overflow-band placement or unresolved collisions mean the engine failed
and must be fixed — not silently tolerated.

**Why:** The overflow band exists as a last resort to produce *some*
output, but it signals a real problem. Treating it as normal makes
regressions invisible.
