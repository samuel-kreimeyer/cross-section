# Issue: High Complexity: Ditch

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-10T16:23:09.311062Z

## Summary
Class 'Ditch' has cyclomatic complexity 4 (rank A)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/components/ditches.py
Line: 13
Complexity: 4
Rank: A

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor 'Ditch' by:
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
  "lines": [13]
}
```