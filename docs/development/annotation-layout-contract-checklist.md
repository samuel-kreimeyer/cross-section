# Annotation Layout Contract Input Checklist

Use this checklist to provide the inputs needed to build a reliable layout-contract test harness and hybrid drawing grammar.

## 1) Reference Annotated Sections

- [ ] Provide `5-10` **good** annotated sections.
- [ ] Provide `2-3` **bad** annotated sections (optional but highly useful).
- [ ] For each section, include:
  - [ ] Source file path (SVG and, if available, scenario/generator script).
  - [ ] Short label: `good` or `bad`.
  - [ ] One-sentence reason for that label.

## 2) Constraint Type by Annotation

For each annotation type, mark whether placement is hard or soft.

- [ ] Dimension annotations: `hard` or `soft`
- [ ] Component text labels: `hard` or `soft`
- [ ] Slope text / drainage symbols: `hard` or `soft`
- [ ] Leader callout text: `hard` or `soft`
- [ ] Leader line geometry (bend count, direction): `hard` or `soft`
- [ ] Keyed notes table placement: `hard` or `soft`

## 3) Numeric Layout Requirements

Provide values and units (or “unknown” if undecided).

- [ ] Minimum text-to-text spacing:
- [ ] Minimum text-to-line clearance:
- [ ] Minimum symbol-to-text clearance:
- [ ] Preferred vertical band gap (dimension to label):
- [ ] Preferred vertical band gap (label to symbol/arrow):
- [ ] Maximum leader length:
- [ ] Preferred leader angle range(s):
- [ ] Maximum leader bends:
- [ ] Tolerance by scale (if different at 30, 50, 100, etc.):

## 4) Priority and Conflict Resolution

When rules conflict, define what can move first.

- [ ] Rank from most fixed to most movable (1..N):
- [ ] If overflow remains, preferred fallback:
- [ ] Items that must never move once placed:

## 5) Scenario-Specific Exceptions

- [ ] List scenarios with known intentional rule exceptions.
- [ ] For each exception, describe:
  - [ ] Which rule is allowed to break.
  - [ ] Acceptable limit (example: one label may leave preferred band).

## 6) Acceptance Criteria for Harness

Define what “good enough to merge” means.

- [ ] Maximum allowed overflow count per scenario:
- [ ] Maximum allowed unresolved collisions per scenario:
- [ ] Required band-order checks to enforce:
- [ ] Required deterministic behavior (same input -> same layout):
- [ ] Visual regression required (`yes/no`):

## 7) Delivery Format

- [ ] I will provide file paths in the repo.
- [ ] I will provide written rules in this document or a linked note.
- [ ] I will mark unknown items explicitly so defaults can be proposed.

## Notes

- If a value is unknown, leave it blank and mark `TBD`.
- If two standards disagree, note which standard should win.
- Partial input is fine; we can start with defaults and tighten contracts iteratively.
