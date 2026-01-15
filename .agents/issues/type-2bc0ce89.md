# Issue: Type Error: Item "None" of "ConcreteLayer | None" has no attri...

**Type:** type
**Severity:** error
**Tool:** check-types
**Detected:** 2026-01-10T16:23:09.116105Z

## Summary
Type error detected by mypy on line 125.

## Evidence
File: src/cross_section/core/domain/components/curbs.py
Line: 125

mypy output:
```
src/cross_section/core/domain/components/curbs.py:125: error: Item "None" of "ConcreteLayer | None" has no attribute "compressive_strength"  [union-attr]
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
  "files": ["src/cross_section/core/domain/components/curbs.py"]
  "lines": [125]
}
```