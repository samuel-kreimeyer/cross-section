# Issue: High Complexity: to_geometry

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-24T20:23:19.349134Z

## Summary
Method 'to_geometry' has cyclomatic complexity 3 (rank A)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/components/gutters.py
Line: 47
Complexity: 3
Rank: A

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor 'to_geometry' by:
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
  "files": ["/home/sam/Projects/cross-section/src/cross_section/core/domain/components/gutters.py"],
  "lines": [47]
}
```