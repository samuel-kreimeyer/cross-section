# Issue: Type Error: Unsupported operand types for >= ("int" and "None"...

**Type:** type
**Severity:** error
**Tool:** check-types
**Detected:** 2026-01-10T16:23:09.116080Z

## Summary
Type error detected by mypy on line 166.

## Evidence
File: src/cross_section/core/domain/components/slopes.py
Line: 166

mypy output:
```
src/cross_section/core/domain/components/slopes.py:166: error: Unsupported operand types for >= ("int" and "None")  [operator]
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
  "lines": [166]
}
```