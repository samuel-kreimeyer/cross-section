# Issue: Type Error: Returning Any from function declared to return "st...

**Type:** type
**Severity:** error
**Tool:** check-types
**Detected:** 2026-01-24T20:23:19.029555Z

## Summary
Type error detected by mypy on line 329.

## Evidence
File: src/cross_section/core/domain/annotations/planner.py
Line: 329

mypy output:
```
src/cross_section/core/domain/annotations/planner.py:329: error: Returning Any from function declared to return "str | None"  [no-any-return]
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
  "lines": [329]
}
```