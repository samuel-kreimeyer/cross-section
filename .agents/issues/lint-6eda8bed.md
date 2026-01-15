# Issue: High Complexity: validate

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-10T16:23:09.311091Z

## Summary
Method 'validate' has cyclomatic complexity 8 (rank B)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoring.py
Line: 175
Complexity: 8
Rank: B

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor 'validate' by:
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
  "lines": [175]
}
```