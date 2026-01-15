# Issue: High Complexity: Shoring

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-10T16:23:09.311093Z

## Summary
Class 'Shoring' has cyclomatic complexity 5 (rank A)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoring.py
Line: 10
Complexity: 5
Rank: A

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor 'Shoring' by:
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
  "files": ["/home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoring.py"]
  "lines": [10]
}
```