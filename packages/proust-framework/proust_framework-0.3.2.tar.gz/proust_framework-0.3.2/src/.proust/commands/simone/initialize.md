# initialize

## Purpose
Interactively initialize the Simone PM framework for a project—detect project characteristics, optionally import existing docs, create baseline Simone structure, first milestone, and project manifest.

## Context Files to Load
1. `src/.proust/universal_claude.md`
2. Existing `src/.simone/**` directory (if any)

## Inputs
| Variable   | Description                                             | Example |
|------------|---------------------------------------------------------|---------|
| `$DATE`    | Current UTC date                                        | `2025-07-04` |

## TODO (execute sequentially)

1. **Scan & analyze project**
   - Detect language/tooling (`package.json`, `pubspec.yaml`, `requirements.txt`, etc.).
   - Determine project name from `README` or folder.
   - Identify if `.simone/` already exists.
   - Keep findings brief.

2. **Interactive confirmation**
   - Present findings:
     ```
     I found a [project type] project named “[name]”. Proceed with Simone setup? (yes/no)
     ```
   - Await user response before continuing.

3. **Check for existing Simone documents**
   - If `src/.simone/` exists, list docs (ARCHITECTURE.md, milestones, sprints).
   - Ask user whether to use, extend, or start fresh.
   - Allow cancel.

4. **Guide document creation**
   - If starting fresh / extending:
     - Run lightweight architecture analysis.
     - Draft `01_PROJECT_DOCS/ARCHITECTURE.md`; ask clarifying questions to fill gaps.
   - If importing existing docs: adapt them into Simone structure.

5. **Create first milestone**
   - Suggest milestone based on project phase.
   - Interactively confirm milestone name & focus.
   - Generate `src/.simone/02_REQUIREMENTS/$MILESTONE_ID/` with meta & initial requirements.

6. **Generate project manifest**
   - Populate `src/.simone/00_PROJECT_MANIFEST.md` with:
     - Project metadata (name, type)
     - First milestone + status
     - Initial sprint list (empty)
     - Timestamp `$DATE`.

7. **Provide next steps**
   - Print customised guidance:
     ```
     ✅ Simone initialized for “[project name]”.

     Next steps:
     - Review src/.simone/01_PROJECT_DOCS/ARCHITECTURE.md
     - Check milestone requirements: src/.simone/02_REQUIREMENTS/$MILESTONE_ID/
     - Create first task: /project:simone:create_general_task
     ```

## Definition of Done
- `src/.simone/` folder exists with required subfolders.
- `ARCHITECTURE.md`, milestone dir, and manifest created/updated.
- User confirmed completion.

## Follow-ups
- Recommend `/project:simone:create_general_task` to begin tasks.
- Suggest running `/project:simone:initialize_new_project` only if full reset required.