# Issue: Type Error: Hint: "python3 -m pip install types-shapely"...

**Type:** type
**Severity:** warning
**Tool:** check-types
**Detected:** 2026-01-10T16:23:09.116115Z

## Summary
Type error detected by mypy on line 24.

## Evidence
File: src/cross_section/core/geometry/validate.py
Line: 24

mypy output:
```
src/cross_section/core/geometry/validate.py:24: note: Hint: "python3 -m pip install types-shapely"
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
  "lines": [24]
}
```