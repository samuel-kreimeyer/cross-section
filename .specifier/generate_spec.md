# Task: Generate Project Specification

You are a senior software architect. Create a project specification from the interview answers below.

## Instructions

Read the interview answers carefully, then generate two files:

1. **spec.md** - The main specification document
2. **tasks.md** - Ordered implementation tasks

Write these files to the current directory.

---

## Interview Answers

# Interview Q/A

## Question 1

In 1–3 sentences, what is the project and who is it for?

### Answer

This project generates typical cross section graphics for transportation projects, specifically highways and trails. At its core is a domain-driven API for naturally describing cross sectional elements of a roadway or trail. The intended users are civil engineers and designers of applications for civil engineers.


## Question 2

What are the top 3–7 goals/outcomes?

### Answer

1. A sound domain-driven core API.
2. An intuitive API that can 'do the right thing' given minimal descriptions
3. Generate dimensionally accurate roadway cross section diagrams
4. Annotate the diagrams with no input outside of, at most, a configuration file to handle preferences. Objects 'know' how they should be annotated.
5. Annotations are not just complete, but aesthetically acceptable. Annotation lines do not cross. Symbols, dimensions, notes, and leaders are shown in the same place a CAD professional would place them.
6. Multiple outputs are supported, and outputs can be used directly by roadway designers with minimal translation or adjustment.


## Question 3

What are explicit non-goals for v0/v1?

### Answer

1. Structural design of pavements
2. Persistence of designs beyond file output
3. Deep customization. Users must be allowed to define wording, symbols, desired units, and component elements to be labeled, but complex configuration, huge menus, and tweaking of every graphical component is not desirable. Sane defaults and reasonable conventions beats user input.


## Question 4

What inputs does it consume and what outputs must it produce?

### Answer

Initially, the API should be a library and programs will 'build' the cross sections. A web front end is a desirable future enhancement when the core is proven. Outputs will be graphic files that preserve dimensional integrity. SVG, DXF, and possibly DWG, DGN, and IFC.


## Question 5

What are the key workflows/use cases?

### Answer

An engineer should be able to describe a section intuitively with calls to a library at a minimum, but through a CLI and web interface soon after the API is stable, and the description should yield a file that can immediately used by a designer or CAD professional in a project.


## Question 6

What constraints must be respected (self-hosted, simplicity, formats, platforms, etc.)?

### Answer

The core API must match real-world components of a roadway. The outputs must be geometrically sound and respect basic rules of assembly (ie, adjacent travel lanes must have a coincident edges and could not be vertically separatshould be adaptable to many different types of inputs and outputs.


## Question 7

What are the main failure modes and required fault-tolerance behaviors?

### Answer

Incomplete or impossible descriptions by users (ie, one travel lane touches 3 retaining walls, a paved open shoulder abuts another shoulder), and infeasible annotations. The annotation system must have robust self-adjustment and self-validation before generation. Geometry soundness checks must be performed at runtime. Component assembly rules must be respected (an insertion point of the next component must match the attachment point of the previous component).


## Question 8

What data needs to be stored and how should deduplication/idempotency work (if relevant)?

### Answer

Configurations would need to be stored. Overall the project should behave like a function. Provide an input. Get a consistent output.


## Question 9

What is the definition of done? (tests, docs, CLI behavior, etc.)

### Answer

The core API is complete and sound. Usage and the API is documented. A miLI is provided, and a user can select components, provide parameters, and get an SVG or DXF that looks like professional work. The annotation engine works reliably without overlaps, intersections, or missing information on realistic sections from simple to moderate complexity. Test coverage is 80% or better. Integration testing is robust and reliably detect annotation faults or failures to annotate as well as component geometry errors such as overlaps or gaps.


## Question 10

What are open questions or decisions you want documented?

### Answer

Automated annotation is a hard problem that is not solved in any ergonomic way by industry-leading software vendors. An intelligent approach is critical. Any shortcomings that require a user to manually draw or annotate part of a cross section that can be described in natural language should be documented. This should only be done for problems that are impossible, (not inconvenient) to solve.



---

## File 1: spec.md

Generate `spec.md` with the following sections. Follow these rules:

- **Respect all constraints** mentioned in the interview
- **Do not add** frameworks, libraries, or complexity unless explicitly requested
- **Be specific** - vague statements are not useful
- **Be actionable** - every section should inform implementation decisions

### Required Sections

```markdown
# Project Specification

## Summary
2-3 sentences: what it does, who it's for, core value.

## Goals
3-7 measurable outcomes aligned with interview answers.

## Non-goals
What this project will NOT do in v0/v1.

## Users & Use Cases
Primary personas and their key workflows.

## Acceptance Criteria
3-5 scenarios in Given/When/Then format covering happy path, edge cases, errors.

## Architecture
Component structure respecting stated constraints. Keep it as simple as requirements allow.

## Data Model
Entity definitions with fields, types, and constraints.

## Interfaces
How users/systems interact (CLI, API, config files, etc.)

## Error Handling
Specific behavior for invalid input, system failures, edge cases.

## Testing Plan
What tests verify, based on definition of done from interview.

## Risks & Open Questions
Assumptions made, decisions needing clarification, deferred questions.
```

---

## File 2: tasks.md

Generate `tasks.md` with an ordered list of implementation tasks.

### Requirements

- **8-15 tasks** that incrementally build the complete system
- Each task is **small** (completable in 1-4 hours)
- Each task is **independently reviewable**
- Each task **builds toward the next**
- Tasks should reference specific sections of spec.md

### Format

```markdown
# Implementation Tasks

## 1. [Task Title]
**Goal**: What this task accomplishes
**Implement**: Specific components/files to create
**Verify**: How to confirm this task is complete
**Depends on**: Previous task number (if any)

## 2. [Task Title]
...
```

---

## Constraints Reminder

Before writing, review these key constraints from the interview:

- 1. Structural design of pavements
2. Persistence of designs beyond file output
3. Deep customization. Users must be allowed to define wording, symbols, desired units, and component elements to be labeled, but complex configuration, huge menus, and tweaking of every graphical component is not desirable. Sane defaults and reasonable conventions beats user input.
- The core API must match real-world components of a roadway. The outputs must be geometrically sound and respect basic rules of assembly (ie, adjacent travel lanes must have a coincident edges and could not be vertically separatshould be adaptable to many different types of inputs and outputs.

Ensure both files respect these constraints. Do not introduce complexity or dependencies that were not requested.

---

## Begin

Generate `spec.md` and `tasks.md` now.
