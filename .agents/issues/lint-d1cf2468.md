# Issue: High Complexity: add_component_right

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-10T16:23:09.311054Z

## Summary
Method 'add_component_right' has cyclomatic complexity 1 (rank A)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/section.py
Line: 98
Complexity: 1
Rank: A

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor 'add_component_right' by:
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
  "files": ["/home/sam/Projects/cross-section/src/cross_section/core/domain/section.py"]
  "lines": [98]
}
```