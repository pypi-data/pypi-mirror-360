# create_general_task

## Purpose
Create a **new general task** under `.simone/04_GENERAL_TASKS/`, following project documentation standards and updating the manifest.

## Context Files to Load
1. `.context/universal_claude.md`
2. `.simone/00_PROJECT_MANIFEST.md`
3. `.simone/01_PROJECT_DOCS/**`
4. `.simone/05_ARCHITECTURAL_DECISIONS/**`
5. Latest snapshot under `.simone/10_STATE_OF_PROJECT/` (optional)

## Inputs
| Variable       | Description                                | Example                                      |
|----------------|--------------------------------------------|----------------------------------------------|
| `$TITLE?`      | Task title / description (free-text)       | `"Add logging middleware"`                   |
| `$DATE`        | Current UTC date                           | `2025-07-04`                                 |

## Preconditions
1. `.simone/04_GENERAL_TASKS/` exists.
2. Task template at `.simone/99_TEMPLATES/task_template.md` exists.
3. Git repo clean or staged as appropriate.

## Steps
1. **Parse task arguments & determine ID**
   - If `$TITLE?` empty → prompt user.
   - Scan existing tasks for highest `T###`; next ID = +1.
   - Filename pattern: `T###_${TITLE_SNAKE}.md`.
   - Ensure sequence gap-free.

2. **Load project context & docs**
   - Read manifest, architecture docs, latest state snapshot, ADRs.
   - Ensure alignment with architecture vision.

3. **Check for duplicates**
   - Search `.simone/04_GENERAL_TASKS/` and `.simone/03_SPRINTS/**/T*.md` for similar titles/keywords.
   - If duplicate found → abort & notify user.

4. **Research codebase for implementation context**
   - Parallel grep for relevant modules, interfaces, tests.
   - Record integration points, patterns, error-handling styles.

5. **Create task file from template**
   - Copy `.simone/99_TEMPLATES/task_template.md` → new file path.
   - Insert timestamp `$DATE`.

6. **Populate task details**
   - Fill Title, Context, Requirements, Acceptance Criteria, Dependencies.
   - Reference architecture docs and state snapshot URLs.

7. **Add technical guidance & codebase references**
   - List key interfaces, existing patterns, test locations.
   - No inline code; only file/function references.

8. **Update project manifest**
   - Add bullet in **## General Tasks** section:
     `- [ ] T###: $TITLE - Status: Not Started`
   - Link to task file; keep ordering intact.

9. **Validate alignment**
   - Check task meets architecture & guardrails.
   - Verify references are valid paths.
   - Confirm unique sequential ID.

10. **Final quality check & report**
    - If all good, output summary block (see below).
    - Else list issues to fix.

## Output Summary (console)
```markdown
✅ **Created**: T###_<title_snake>.md
📋 **Type**: General Task
🎯 **Purpose**: <one-line summary>
📚 **References**: <key docs>
🔧 **Key Integration Points**: <main files/modules>
🧪 **Test Approach**: <testing pattern>
⏭️ **Next Step**: run `/do_task T###`
```

## Definition of Done
- New task file exists, complete, follows template.
- Manifest updated with bullet link.
- No duplicate ID.
- Summary printed.

## Follow-ups
- User runs `/do_task T###` to begin implementation.
- If high impact, consider sprint placement via `/project:simone:create_sprint_tasks`.
