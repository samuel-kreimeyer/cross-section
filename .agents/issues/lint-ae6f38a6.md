# Issue: High Complexity: get_insertion_point

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-24T20:23:19.349234Z

## Summary
Method 'get_insertion_point' has cyclomatic complexity 1 (rank A)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/components/sidewalks.py
Line: 28
Complexity: 1
Rank: A

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor 'get_insertion_point' by:
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
  "files": ["/home/sam/Projects/cross-section/src/cross_section/core/domain/components/sidewalks.py"],
  "lines": [28]
}
```