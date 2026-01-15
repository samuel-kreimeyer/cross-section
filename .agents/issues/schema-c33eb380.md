# Issue: Missing README Section: License

**Type:** schema
**Severity:** warning
**Tool:** check-schema
**Detected:** 2026-01-10T16:23:08.756286Z

## Summary
README.md is missing required section: `## License`

## Evidence
Expected section header: `## License`
Section not found in README.md.

## Impact
The `## License` section is required by the WorkBench schema. This section provides important context for understanding the project.

## Recommended Action
Add the missing section to README.md:

```markdown
## License

[Content here]
```

## Automation
- Detectable: yes
- Auto-fixable: no

## Metadata
```json
{
  "files": ["/home/sam/Projects/cross-section/README.md"]
}
```