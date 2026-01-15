# Issue: High Complexity: _create_left_geometry

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-10T16:23:09.311069Z

## Summary
Method '_create_left_geometry' has cyclomatic complexity 2 (rank A)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/components/ditches.py
Line: 198
Complexity: 2
Rank: A

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor '_create_left_geometry' by:
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
  "files": ["/home/sam/Projects/cross-section/src/cross_section/core/domain/components/ditches.py"]
  "lines": [198]
}
```