# Issue: Type Error: "object" has no attribute "geoms"  [attr-defined]...

**Type:** type
**Severity:** error
**Tool:** check-types
**Detected:** 2026-01-10T16:23:09.116151Z

## Summary
Type error detected by mypy on line 76.

## Evidence
File: src/cross_section/core/geometry/validate.py
Line: 76

mypy output:
```
src/cross_section/core/geometry/validate.py:76: error: "object" has no attribute "geoms"  [attr-defined]
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
  "lines": [76]
}
```