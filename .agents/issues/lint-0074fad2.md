# Issue: High Complexity: _ensure_crown_dimension

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-24T20:23:19.349423Z

## Summary
Method '_ensure_crown_dimension' has cyclomatic complexity 9 (rank B)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/annotations/planner.py
Line: 331
Complexity: 9
Rank: B

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor '_ensure_crown_dimension' by:
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
  "files": ["/home/sam/Projects/cross-section/src/cross_section/core/domain/annotations/planner.py"],
  "lines": [331]
}
```