# Issue: High Complexity: __post_init__

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-10T16:23:09.311101Z

## Summary
Method '__post_init__' has cyclomatic complexity 7 (rank B)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/components/slopes.py
Line: 31
Complexity: 7
Rank: B

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor '__post_init__' by:
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
  "files": ["/home/sam/Projects/cross-section/src/cross_section/core/domain/components/slopes.py"]
  "lines": [31]
}
```