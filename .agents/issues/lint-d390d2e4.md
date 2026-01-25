# Issue: High Complexity: Slope

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-24T20:23:19.349172Z

## Summary
Class 'Slope' has cyclomatic complexity 7 (rank B)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/components/slopes.py
Line: 10
Complexity: 7
Rank: B

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor 'Slope' by:
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
  "files": ["/home/sam/Projects/cross-section/src/cross_section/core/domain/components/slopes.py"],
  "lines": [10]
}
```