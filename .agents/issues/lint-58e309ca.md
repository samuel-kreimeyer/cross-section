# Issue: High Complexity: _resolve_line_text_collisions

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-24T20:23:19.349547Z

## Summary
Method '_resolve_line_text_collisions' has cyclomatic complexity 10 (rank B)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/annotations/collision.py
Line: 703
Complexity: 10
Rank: B

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor '_resolve_line_text_collisions' by:
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
  "files": ["/home/sam/Projects/cross-section/src/cross_section/core/domain/annotations/collision.py"],
  "lines": [703]
}
```