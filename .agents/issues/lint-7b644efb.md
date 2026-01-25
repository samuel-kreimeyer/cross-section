# Issue: High Complexity: get_attachment_point

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-24T20:23:19.349148Z

## Summary
Method 'get_attachment_point' has cyclomatic complexity 6 (rank B)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoulders.py
Line: 73
Complexity: 6
Rank: B

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor 'get_attachment_point' by:
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
  "files": ["/home/sam/Projects/cross-section/src/cross_section/core/domain/components/shoulders.py"],
  "lines": [73]
}
```