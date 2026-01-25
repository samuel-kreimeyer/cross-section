# Issue: Type Error: Incompatible types in assignment (expression has t...

**Type:** type
**Severity:** error
**Tool:** check-types
**Detected:** 2026-01-24T20:23:19.029507Z

## Summary
Type error detected by mypy on line 66.

## Evidence
File: src/cross_section/core/domain/annotations/text.py
Line: 66

mypy output:
```
src/cross_section/core/domain/annotations/text.py:66: error: Incompatible types in assignment (expression has type "float", variable has type "int")  [assignment]
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
  "files": ["src/cross_section/core/domain/annotations/text.py"],
  "lines": [66]
}
```