# Issue: High Complexity: SectionGeometry

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-10T16:23:09.311039Z

## Summary
Class 'SectionGeometry' has cyclomatic complexity 8 (rank B)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/section.py
Line: 32
Complexity: 8
Rank: B

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor 'SectionGeometry' by:
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
  "lines": [32]
}
```