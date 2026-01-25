# Issue: High Complexity: detect_text_leader_line

**Type:** lint
**Severity:** info
**Tool:** radon
**Detected:** 2026-01-24T20:23:19.349581Z

## Summary
Method 'detect_text_leader_line' has cyclomatic complexity 3 (rank A)

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/annotations/collision.py
Line: 332
Complexity: 3
Rank: A

## Impact
Complex code is harder to test, understand, and maintain. High complexity often indicates a need for refactoring.

## Recommended Action
Refactor 'detect_text_leader_line' by:
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
  "lines": [332]
}
```