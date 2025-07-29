# Initialize **NEW** Project Context
Use this command the very first time you drop Simone (or any other PM workflow) into a fresh codebase.
It scaffolds the entire `.context/` ecosystem, seeds core docs, and prepares the first milestone.

---

## Create a TODO with **EXACTLY** these 9 items
1. Detect project basics & tech stack
2. Confirm project metadata with the user
3. Scaffold baseline `.context/` folder structure
4. Generate starter documentation templates
5. Create initial **brand**, **ethos**, & **guardrails** stubs
6. Draft `PROJECT_MANIFEST.md` (version 0.1)
7. Create **Milestone 01** + empty requirements set
8. Commit scaffold (optional)
9. Provide next‑steps summary

---

### 1 · Detect project basics & tech stack
Run in parallel:
- `find . -maxdepth 2 -type f` → detect languages & frameworks
- Identify: package.json, pyproject.toml, pubspec.yaml, Cargo.toml, go.mod, etc.
- Guess project **name**, **primary language**, **framework**, current **git remote**.
*Keep the findings concise* – one short table.

### 2 · Confirm metadata with the user
Interactive prompt:
```
I detected → Name: **$NAME**, Language: **$LANG**, Framework: **$FW**.
Is this correct? (yes / no → override)
```
If user overrides, respect their input.

### 3 · Scaffold `.context/`

Create (if absent):
```
.context/
  ├── assessments/
  ├── commands/
  │   └── simone/          # command files live here
  ├── manifesto/
  ├── brand.yml
  ├── ethos.md
  ├── external_docs.yml
  ├── guardrails.yml
  └── universal_claude.md
```
_Do **not** overwrite existing files; only create missing ones._

### 4 · Generate starter docs
Copy template stubs into:
- `.context/templates/universal_claude.md`
- `.context/templates/guardrails.yml`
- `.context/templates/brand.yml`
- `.context/templates/ethos.md`
(Only if they don’t already exist)

### 5 · Brand / Ethos / Guardrails stubs
If `/brand.yml`, `/ethos.md`, or `/guardrails.yml` are missing in root `.context/`,
create them from the templates and mark key TODO sections with `📝 TODO:` comments so the team can fill.

### 6 · Draft `PROJECT_MANIFEST.md`
Location: `.simone/00_PROJECT_MANIFEST.md`
Front‑matter fields:
```yaml
name: "<fill‑me>"
version: "1.0.0"
last_updated: "<auto‑date>"
current_milestone: "M01_initial_setup"
current_sprint: null
```
Sections:
- Overview
- Repo structure snapshot
- Rules of engagement (link to guardrails)
- Placeholders for future sprint / milestone tracking.

### 7 · Milestone 01
Create folder `.simone/02_REQUIREMENTS/M01_initial_setup/`
Seed files:
- `M01_milestone_meta.md` (template)
- `README.md` (why this milestone)
- Leave requirements list empty – user fills after scaffold.

### 8 · Optional initial commit
Ask user:
```
Shall I commit this scaffold to git? (yes/no)
```
If **yes** → stage all new files, commit `chore(context): scaffold Simone project context`, push if remote exists.

### 9 · Next‑steps summary
Console output:
- Created/updated paths list
- Any user TODO markers
- Suggested next command (`/project:simone:create_general_task` or `/analyze_codebase`).

---

**Notes for Agents Implementing this Command**
- Use **parallel subagents** for file‑system scans to stay fast.
- Never overwrite user content without confirmation.
- Treat this as idempotent: subsequent runs should be safe and only add missing pieces.