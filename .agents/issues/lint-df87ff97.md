# Issue: High Complexity: _build_geometry

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-10T16:23:09.311084Z

## Summary
Method '_build_geometry' has cyclomatic complexity 6 (rank B)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoulders.py
Line: 358
Complexity: 6
Rank: B

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor '_build_geometry' by:
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
  "files": ["/home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoulders.py"]
  "lines": [358]
}
```