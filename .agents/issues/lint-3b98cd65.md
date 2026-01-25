# Issue: High Complexity: export

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-24T20:23:19.349678Z

## Summary
Method 'export' has cyclomatic complexity 13 (rank C)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/export/svg.py
Line: 56
Complexity: 13
Rank: C

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor 'export' by:
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
  "lines": [56]
}
```