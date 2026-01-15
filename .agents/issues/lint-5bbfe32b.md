# Issue: High Complexity: validate_section_geometry

**Type:** lint
**Severity:** warning
**Tool:** radon
**Detected:** 2026-01-10T16:23:09.310993Z

## Summary
Function 'validate_section_geometry' has cyclomatic complexity 29 (rank D)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/geometry/validate.py
Line: 291
Complexity: 29
Rank: D

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor 'validate_section_geometry' by:
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
  "files": ["/home/sam/Projects/cross-section/src/cross_section/core/geometry/validate.py"]
  "lines": [291]
}
```