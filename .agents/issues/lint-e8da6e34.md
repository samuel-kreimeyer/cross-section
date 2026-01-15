# Issue: High Complexity: _structural_fill_hatch

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-10T16:23:09.311225Z

## Summary
Method '_structural_fill_hatch' has cyclomatic complexity 3 (rank A)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/components/retaining_walls.py
Line: 467
Complexity: 3
Rank: A

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor '_structural_fill_hatch' by:
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
  "lines": [467]
}
```