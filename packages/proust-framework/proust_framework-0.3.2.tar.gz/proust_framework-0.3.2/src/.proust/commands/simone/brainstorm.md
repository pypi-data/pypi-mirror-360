# brainstorm

## Purpose
Guide the user through an **iterative Q&A session** to produce a complete, step-by-step product or feature specification that is ready for developer hand-off.

## Context Files to Load
1. `.context/universal_claude.md`
2. `.context/guardrails.yaml`
3. `.context/architecture/**` (optional, if brainstorming fits existing stacks)

## Inputs
| Variable | Description                                  | Example                              |
|----------|----------------------------------------------|--------------------------------------|
| `$IDEA`  | One-sentence idea seed provided by the user  | “Zen-mode portfolio screen”          |
| `$DATE`  | Session date (UTC)                           | `2025-07-04`                         |

## Session Protocol
1. **Ask exactly _one_ question at a time.**
   - Question #1: _“What core problem or user pain point does this idea aim to solve?”_
   - Subsequent questions must build logically on previous answers (requirements → flows → edge cases → tech notes, etc.).
2. **Record each Q & A pair** in an in-memory draft spec as the conversation progresses.
3. Continue until user says **“done”** or the agent detects that the spec is complete (all essential sections filled).

## Spec Skeleton (auto-populate)
```md
# Spec: $IDEA
**Date:** $DATE

## 1. Problem / Pain Point
…

## 2. Goal
…

## 3. Users & Personas
…

## 4. Functional Requirements
…

## 5. Non-Functional Requirements
…

## 6. User Flows & Edge Cases
…

## 7. Acceptance Criteria
…

## 8. Open Questions & Risks
…

## 9. Tech Notes & Dependencies
…
```

### After Final “Done”
1. **Render the completed spec** into `.context/planning/spec-{$DATE}-{one-liner idea}.md`.
2. Ask: **“Would you like to create a new GitHub repo for this spec?”**
   - If **yes** →
     a. Initialize git repo (if none).
     b. Commit `spec.md`.
     c. Push to new GitHub repo via CLI or API credentials.
   - If **no** → End session.

## Outputs
| File                                                 | Purpose                       |
| ---------------------------------------------------- | ----------------------------- |
| `.context/planning/spec-{$DATE}-{one-liner idea}.md` | Finalized specification draft |

## Definition of Done
- All nine sections of the spec are filled.
- User explicitly approves completion.
- Spec saved at `.context/planning/spec.md`.
- GitHub repo created & spec committed **only if** user says yes.

## Follow-ups
- Convert spec into tasks with `/project:simone:create_general_task` or `/project:simone:create_sprint_tasks` as appropriate.