# Issue: High Complexity: ComponentGeometry

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-10T16:23:09.310962Z

## Summary
Class 'ComponentGeometry' has cyclomatic complexity 16 (rank C)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/geometry/primitives.py
Line: 87
Complexity: 16
Rank: C

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor 'ComponentGeometry' by:
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
  "files": ["/home/sam/Projects/cross-section/src/cross_section/core/geometry/primitives.py"]
  "lines": [87]
}
```