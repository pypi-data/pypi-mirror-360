# do_task

## Purpose
Process a Simone task end-to-end: select task, set status → in_progress, perform work, run code review, and finalize status.

## Context Files to Load
1. `src/.proust/universal_claude.md`
2. `src/.simone/00_PROJECT_MANIFEST.md`
3. `src/.simone/02_REQUIREMENTS/**`
4. `src/.simone/01_PROJECT_DOCS/**`
5. `src/.proust/commands/simone/code_review.md` (when step 7 triggers)

## Inputs
| Variable    | Description                                              | Example          |
|-------------|----------------------------------------------------------|------------------|
| `$ARGUMENTS?| Task ID, Sprint ID, or blank (`select next open task`)   | `T05_S02`        |
| `$DATE`     | UTC date                                                 | `2025-07-04`     |

## Steps
1. **Analyse scope from argument**
   - If blank → choose next open task in current sprint (status: open).
   - Log chosen scope.

2. **Identify task file**
   - Search `src/.simone/03_SPRINTS/` and `src/.simone/04_GENERAL_TASKS/`.
   - If none matches → ask user how to proceed.

3. **Analyse the task**
   - Read task description & front-matter.
   - **Parallel validations:**
     1. Confirm task belongs to current sprint.
     2. Check dependencies completed.
     3. Read relevant requirements docs.
     4. Ensure task aligns with sprint objectives.
   - If unclear or blockers → prompt user.

4. **Set status to _in_progress_**
   - Timestamp `$DATE` local.
   - Update task front-matter: `status: in_progress`, `updated: $DATE`.
   - Update manifest sprint/task status accordingly.

5. **Execute task work**
   - Follow Description → Goal → Acceptance Criteria.
   - Loop subtasks: mark done & append `[YYYY-MM-DDTHH:MM:SSZ]: <message>` to **## Output Log**.
   - Consult docs as needed.

6. **Placeholder** – no-op.

7. **Execute Code Review**
   - Invoke `/project:simone:code_review $TASK_ID`.
   - If **FAIL** →
     - Add review-identified subtasks.
     - Return to Step 5.
   - If **PASS** → continue.

8. **Finalize task status**
   - Set `status: completed`.
   - Rename file `T###` → `TX###` to indicate completion.
   - Update manifest.
   - Output summary block:
     ```
     ✅ Result: success
     🔎 Scope: $TASK_ID
     💬 Summary: <one-paragraph recap>
     ⏭️ Next steps: /project:simone:commit $TASK_ID
     ```

## Definition of Done
- Task file shows `status: completed`, renamed with `TX`.
- Manifest reflects completion.
- Code review PASS.
- Summary printed.

## Follow-ups
- Recommend `/project:simone:commit $TASK_ID`.
- Suggest `/clear` to reset context.