# Issue: High Complexity: BoundingBox

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-24T20:23:19.348938Z

## Summary
Class 'BoundingBox' has cyclomatic complexity 4 (rank A)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/geometry/bounds.py
Line: 9
Complexity: 4
Rank: A

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor 'BoundingBox' by:
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
  "files": ["/home/sam/Projects/cross-section/src/cross_section/core/geometry/bounds.py"],
  "lines": [9]
}
```