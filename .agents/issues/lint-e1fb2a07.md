# Issue: High Complexity: apply_override

**Type:** lint
**Severity:** warning
**Tool:** radon
**Detected:** 2026-01-24T20:23:19.349490Z

## Summary
Method 'apply_override' has cyclomatic complexity 24 (rank D)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/annotations/profile.py
Line: 48
Complexity: 24
Rank: D

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor 'apply_override' by:
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
  "files": ["/home/sam/Projects/cross-section/src/cross_section/core/domain/annotations/profile.py"],
  "lines": [48]
}
```