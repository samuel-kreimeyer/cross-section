# Issue: High Complexity: validate

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-24T20:23:19.349656Z

## Summary
Method 'validate' has cyclomatic complexity 5 (rank A)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/annotations/text.py
Line: 169
Complexity: 5
Rank: A

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
  "files": ["/home/sam/Projects/cross-section/src/cross_section/core/domain/annotations/text.py"],
  "lines": [169]
}
```