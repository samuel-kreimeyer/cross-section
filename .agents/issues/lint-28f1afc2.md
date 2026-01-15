# Issue: High Complexity: _create_right_geometry

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-10T16:23:09.311136Z

## Summary
Method '_create_right_geometry' has cyclomatic complexity 1 (rank A)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/components/curbs.py
Line: 137
Complexity: 1
Rank: A

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor '_create_right_geometry' by:
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
  "files": ["/home/sam/Projects/cross-section/src/cross_section/core/domain/components/curbs.py"]
  "lines": [137]
}
```