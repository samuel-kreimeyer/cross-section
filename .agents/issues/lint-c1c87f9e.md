# Issue: High Complexity: _foundation_polygon

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-10T16:23:09.311241Z

## Summary
Method '_foundation_polygon' has cyclomatic complexity 2 (rank A)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/components/retaining_walls.py
Line: 396
Complexity: 2
Rank: A

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor '_foundation_polygon' by:
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
  "files": ["/home/sam/Projects/cross-section/src/cross_section/core/domain/components/retaining_walls.py"]
  "lines": [396]
}
```