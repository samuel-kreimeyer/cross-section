# Issue: Type Error: "object" has no attribute "geom_type"  [attr-defin...

**Type:** type
**Severity:** error
**Tool:** check-types
**Detected:** 2026-01-10T16:23:09.116142Z

## Summary
Type error detected by mypy on line 64.

## Evidence
File: src/cross_section/core/geometry/validate.py
Line: 64

mypy output:
```
src/cross_section/core/geometry/validate.py:64: error: "object" has no attribute "geom_type"  [attr-defined]
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
  "files": ["src/cross_section/core/geometry/validate.py"]
  "lines": [64]
}
```