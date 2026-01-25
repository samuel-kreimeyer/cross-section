# Issue: High Complexity: build_components

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-24T20:23:19.349125Z

## Summary
Method 'build_components' has cyclomatic complexity 6 (rank B)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/components/traveled_way.py
Line: 31
Complexity: 6
Rank: B

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor 'build_components' by:
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
  "files": ["/home/sam/Projects/cross-section/src/cross_section/core/domain/components/traveled_way.py"],
  "lines": [31]
}
```