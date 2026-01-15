# Issue: High Complexity: _add_scale

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-10T16:23:09.311260Z

## Summary
Method '_add_scale' has cyclomatic complexity 8 (rank B)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/export/svg.py
Line: 188
Complexity: 8
Rank: B

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor '_add_scale' by:
- Breaking into smaller functions
- Reducing branching (if/else, loops)
- Simplifying logic
- Target complexity < 10

## Automation
- Detectable: yes
- Auto-fixable: no

## Metadata
```json
{
  "files": ["/home/sam/Projects/cross-section/src/cross_section/export/svg.py"]
  "lines": [188]
}
```