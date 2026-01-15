# Issue: High Complexity: validate

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-10T16:23:09.311112Z

## Summary
Method 'validate' has cyclomatic complexity 12 (rank C)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/components/lanes.py
Line: 169
Complexity: 12
Rank: C

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
  "files": ["/home/sam/Projects/cross-section/src/cross_section/core/domain/components/lanes.py"]
  "lines": [169]
}
```