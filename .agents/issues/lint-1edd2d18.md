# Issue: High Complexity: _legend_box_px

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-24T20:23:19.349685Z

## Summary
Method '_legend_box_px' has cyclomatic complexity 3 (rank A)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/export/svg.py
Line: 227
Complexity: 3
Rank: A

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor '_legend_box_px' by:
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
  "files": ["/home/sam/Projects/cross-section/src/cross_section/export/svg.py"],
  "lines": [227]
}
```