# Issue: Type Error: Right operand is of type "float | None"...

**Type:** type
**Severity:** warning
**Tool:** check-types
**Detected:** 2026-01-10T16:23:09.116067Z

## Summary
Type error detected by mypy on line 86.

## Evidence
File: src/cross_section/core/domain/components/slopes.py
Line: 86

mypy output:
```
src/cross_section/core/domain/components/slopes.py:86: note: Right operand is of type "float | None"
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
  "files": ["src/cross_section/core/domain/components/slopes.py"]
  "lines": [86]
}
```