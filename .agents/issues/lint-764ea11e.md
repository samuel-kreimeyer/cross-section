# Issue: High Complexity: _has_leader_collision

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-24T20:23:19.349527Z

## Summary
Method '_has_leader_collision' has cyclomatic complexity 14 (rank C)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/annotations/collision.py
Line: 815
Complexity: 14
Rank: C

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor '_has_leader_collision' by:
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
  "lines": [815]
}
```