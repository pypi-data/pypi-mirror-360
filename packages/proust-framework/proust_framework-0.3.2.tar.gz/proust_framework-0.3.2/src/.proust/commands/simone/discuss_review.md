# discuss_review

## Purpose
Facilitate a **brutally honest, John-Carmack-style** technical discussion around recent code-review findings, drive actionable decisions, and log outcomes.

## Context Files to Load
1. `.context/universal_claude.md`
2. Latest review output inside the relevant task’s **## Output Log** (if provided via `$TASK_ID`)
3. `.simone/01_PROJECT_DOCS/**` (architecture docs)
4. `.simone/02_REQUIREMENTS/**` (requirements)
5. `.simone/05_ARCHITECTURAL_DECISIONS/**` (ADRs)

## Inputs
| Variable        | Description                                     | Example          |
|-----------------|-------------------------------------------------|------------------|
| `$ARGUMENTS?`   | Free-form discussion starter text               | “Severity 8 log injection” |
| `$TASK_ID?`     | Specific task ID whose review is being discussed| `T07_S02`        |
| `$DATE`         | Current UTC date                                | `2025-07-04`     |

## Session Protocol
1. **Load review findings**
   - If `$TASK_ID?` provided, read its **## Output Log** for latest review.
   - Else prompt user to paste review excerpt.

2. **Kick-off discussion**
   - Pose an initial, focused question, using `$ARGUMENTS?` if present.
   - Maintain **one-question-at-a-time** flow.

3. **Tone & Approach**
   - Channel John Carmack: blunt, practical, shipping-focused.
   - Challenge assumptions, explore trade-offs, favour working software.

4. **Discussion Outcomes** (choose as appropriate):
   - Amend review severity / priority
   - Update docs in `.simone/01_PROJECT_DOCS/`
   - Revise requirements in `.simone/02_REQUIREMENTS/`
   - Create new tasks for tech debt
   - Adjust sprint priorities

5. **Decision Logging**
   - After consensus, append a log block to the related task’s **## Output Log** or create a new discussion log:
     ```
     [YYYY-MM-DDTHH:MM:SSZ] Discuss Review
     Key Points:
     - …
     Decisions:
     - …
     Next Actions:
     - …
     ```

6. **End Session**
   - Summarise agreed actions.
   - If new tasks required, instruct user to run `/create_general_task`.

## Definition of Done
- At least one actionable decision documented.
- Log entry written with timestamp.
- User confirms no further questions.

## Follow-ups
- If tasks arise, use `/create_general_task`.
- If docs need updates, follow `/update_context`.
