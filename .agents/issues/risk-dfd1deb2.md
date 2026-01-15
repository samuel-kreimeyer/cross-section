# Issue: Bandit [B101]: assert_used

**Type:** risk
**Severity:** info
**Tool:** check-risk
**Detected:** 2026-01-10T16:23:14.534431Z

## Summary
Security issue detected by bandit (confidence: HIGH).

## Evidence
File: /home/sam/Projects/cross-section/src/cross_section/core/domain/components/barriers.py
Line: 450
Test: B101 (assert_used)

Use of assert detected. The enclosed code will be removed when compiling to optimised byte code.

## Impact
Bandit detected a potential security vulnerability in Python code.

## Recommended Action
Review and fix the security issue. See: https://bandit.readthedocs.io/en/latest/plugins/b101.html

## Automation
- Detectable: yes
- Auto-fixable: no

## Metadata
```json
{
  "files": ["/home/sam/Projects/cross-section/src/cross_section/core/domain/components/barriers.py"]
  "lines": [450]
}
```