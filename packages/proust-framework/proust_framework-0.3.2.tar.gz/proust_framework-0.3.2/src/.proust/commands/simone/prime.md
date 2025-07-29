# prime

## Purpose
Quickly **prime the agent’s context** with high-level project information and current status before any deeper Simone commands run.

## Context Files to Load
1. `.simone/01_PROJECT_DOCS/ARCHITECTURE.md`
2. `.simone/00_PROJECT_MANIFEST.md`

## Inputs
*(none)* – this command is non-interactive.

## Steps
1. **Parallel read** architecture & manifest files.
2. Extract:
   - Project name, domain, stack from ARCHITECTURE.md.
   - Current milestone, active sprint, task and sprint counts from MANIFEST.
3. **Print concise summary** to console:
   ```
   🛠  Project: <name>  |  Stack: <tech stack>
   🚩 Milestone: <id>  |  Active Sprint: <sprint id>  |  Tasks Open: <n>
   ```
4. Set internal session variables so subsequent commands inherit these facts.

## Definition of Done
- Summary printed with project + milestone + sprint info.
- No mutations to project files.

## Follow-ups
- Usually followed by `/project:simone:do_task` or `/project:simone:create_general_task`.