# Issue: High Complexity: validate_component_geometry

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-10T16:23:09.311004Z

## Summary
Function 'validate_component_geometry' has cyclomatic complexity 4 (rank A)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/geometry/validate.py
Line: 275
Complexity: 4
Rank: A

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor 'validate_component_geometry' by:
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
  "lines": [275]
}
```