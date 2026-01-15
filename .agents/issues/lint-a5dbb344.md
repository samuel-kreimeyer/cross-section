# Issue: High Complexity: bounds

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-10T16:23:09.310969Z

## Summary
Method 'bounds' has cyclomatic complexity 15 (rank C)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/geometry/primitives.py
Line: 94
Complexity: 15
Rank: C

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor 'bounds' by:
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
  "lines": [94]
}
```