# Issue: High Complexity: ConcreteLayer

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-24T20:23:19.349011Z

## Summary
Class 'ConcreteLayer' has cyclomatic complexity 15 (rank C)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/pavement.py
Line: 59
Complexity: 15
Rank: C

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor 'ConcreteLayer' by:
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
  "files": ["/home/sam/Projects/cross-section/src/cross_section/core/domain/pavement.py"],
  "lines": [59]
}
```