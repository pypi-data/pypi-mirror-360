# create_sprint_tasks

## Purpose
Break down an existing sprint into detailed, implementation-ready task files with technical guidance, and update sprint/manifest metadata.

## Context Files to Load
1. `.context/universal_claude.md`
2. `.simone/00_PROJECT_MANIFEST.md`
3. `.simone/02_REQUIREMENTS/**`
4. `.simone/01_PROJECT_DOCS/**`
5. `.simone/05_ARCHITECTURAL_DECISIONS/**`

## Inputs
| Variable  | Description                              | Example |
|-----------|------------------------------------------|---------|
| `$SPRINT` | **Required** sprint ID (e.g., `S02`)     | `S02`   |
| `$DATE`   | Current UTC date                         | `2025-07-04` |

## Preconditions
1. Sprint directory `.simone/03_SPRINTS/$SPRINT_*` exists.
2. Sprint meta file `$SPRINT_sprint_meta.md` present and status ≠ completed.
3. Task template at `.simone/99_TEMPLATES/task_template.md` exists.

## TODO (execute sequentially)

1. **Identify target sprint & verify**
   - If `$SPRINT` empty → prompt user.
   - Check directory and meta file; abort if not found.
   - If tasks already exist → ask user whether to recreate or append.

2. **Load sprint context & docs**
   - Read manifest for overall context.
   - Read sprint meta for goals/deliverables.
   - Read parent milestone requirements and architecture docs.

3. **Check ADRs & technical guidance**
   - Search `.simone/05_ARCHITECTURAL_DECISIONS/` for `ADR*_$SPRINT_*`.
   - Note decisions impacting implementation; flag conflicts.

4. **Analyze sprint deliverables for task breakdown**
   - Decompose each deliverable into coherent, self-contained tasks.
   - Map tasks to ADRs and identify dependencies.

5. **Create individual task files**
   For each task:
   - File name: `T<NN>_$SPRINT_<snake_title>.md` (sequential).
   - Copy template; fill description, goals, acceptance criteria.
   - Add **Technical Guidance** & **Implementation Notes** sections:
     - Key interfaces, modules, ADR refs, testing approach.
   - Validate task is actionable & self-contained.

6. **Link ADRs to tasks**
   - In each task’s guidance, reference relevant ADR IDs and summarize impact.

7. **Update sprint meta with task references**
   - Append task list in logical order with brief descriptions.
   - Include dependency notes where relevant.

8. **Quality check & complexity assessment**
   - Mark complexity Low/Medium/High.
   - If High → split into smaller tasks and repeat Step 5.
   - Ensure numbering sequential, no gaps.
   - Update manifest sprint section with new tasks.

## Output Summary
```markdown
## Sprint Detailed - [$DATE]

**Sprint:** $SPRINT - <Sprint Name>
**Status:** Planning Complete

**Tasks Created:** <count>
- Medium Complexity: <count>
- Low Complexity: <count>

**Task Splitting Summary:**
- <notes if any>

**Next Steps:**
- Review tasks
- Run `/do_task T01_$SPRINT` to begin implementation
```

## Definition of Done
- Task files created & validated.
- Sprint meta updated with task list.
- Manifest updated.
- Summary printed.

## Follow-ups
- Developers start with `/do_task` on first task.
- If ADR conflicts unresolved, raise to user for decision.
