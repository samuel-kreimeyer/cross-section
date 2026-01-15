# Issue: Type Error: Incompatible types in assignment (expression has t...

**Type:** type
**Severity:** error
**Tool:** check-types
**Detected:** 2026-01-10T16:23:09.116102Z

## Summary
Type error detected by mypy on line 294.

## Evidence
File: src/cross_section/core/domain/components/shoulders.py
Line: 294

mypy output:
```
src/cross_section/core/domain/components/shoulders.py:294: error: Incompatible types in assignment (expression has type "CrushedRockLayer", variable has type "AsphaltLayer")  [assignment]
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
  "files": ["src/cross_section/core/domain/components/shoulders.py"]
  "lines": [294]
}
```