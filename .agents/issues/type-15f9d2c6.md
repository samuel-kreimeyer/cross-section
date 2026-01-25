# Issue: Type Error: Argument 1 to "_dimension_side" of "AnnotationPlan...

**Type:** type
**Severity:** error
**Tool:** check-types
**Detected:** 2026-01-24T20:23:19.029558Z

## Summary
Type error detected by mypy on line 347.

## Evidence
File: src/cross_section/core/domain/annotations/planner.py
Line: 347

mypy output:
```
src/cross_section/core/domain/annotations/planner.py:347: error: Argument 1 to "_dimension_side" of "AnnotationPlanner" has incompatible type "AnnotationBase"; expected "DimensionAnnotation"  [arg-type]
```

## Impact
Type errors can lead to runtime failures. Static type checking helps catch these issues early.

## Recommended Action
Review the type error and fix the type annotation or adjust the code to match the expected type.

## Automation
- Detectable: yes
- Auto-fixable: no

## Metadata
```json
{
  "files": ["src/cross_section/core/domain/annotations/planner.py"],
  "lines": [347]
}
```