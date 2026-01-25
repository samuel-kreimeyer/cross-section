# Issue: High Complexity: _draw_geometry

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-24T20:23:19.349709Z

## Summary
Method '_draw_geometry' has cyclomatic complexity 12 (rank C)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/export/svg_annotations.py
Line: 131
Complexity: 12
Rank: C

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor '_draw_geometry' by:
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
  "files": ["/home/sam/Projects/cross-section/src/cross_section/export/svg_annotations.py"],
  "lines": [131]
}
```