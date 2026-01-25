# Issue: Type Error: Function is missing a type annotation for one or m...

**Type:** type
**Severity:** error
**Tool:** check-types
**Detected:** 2026-01-24T20:23:19.029541Z

## Summary
Type error detected by mypy on line 208.

## Evidence
File: src/cross_section/core/domain/annotations/planner.py
Line: 208

mypy output:
```
src/cross_section/core/domain/annotations/planner.py:208: error: Function is missing a type annotation for one or more arguments  [no-untyped-def]
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
  "lines": [208]
}
```