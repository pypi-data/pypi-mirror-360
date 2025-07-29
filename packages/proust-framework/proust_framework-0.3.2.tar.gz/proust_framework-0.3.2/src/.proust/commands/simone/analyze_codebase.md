# analyze_codebase

## Purpose
Generate a **single-session health report** for an existing codebase:
- Architecture & guardrail compliance
- Feature completeness vs. manifests
- Deployment readiness (GO / NO-GO)
- Actionable recommendations

## Context Files to Load
1. `.context/universal_claude.md`
2. `.context/guardrails.yaml`
3. `.context/architecture/**` (frontend / backend manifests)
4. `.context/external_docs.yaml`
5. Latest snapshot under `.simone/10_STATE_OF_PROJECT/` (if any)

## Inputs
| Variable          | Description                                   | Example                                                            |
|-------------------|-----------------------------------------------|--------------------------------------------------------------------|
| `$ROOT_PATH`      | Absolute path to repo root                    | `/workspace/kasanova-backend`                                      |
| `$DATE`           | Real-world date (UTC)                         | `2025-07-04`                                                       |
| `$STATUS_REPORT?` | Path to latest snapshot (optional)            | `.simone/10_STATE_OF_PROJECT/2025-06-20_14-00_snapshot`            |

## Preconditions
1. Repo is present at **`$ROOT_PATH`**.
2. Shell tools **find**, **grep**, **tree** are available.
3. Agent can write to `.context/assessments/`.

## Steps
1. **Generate directory tree**
   ```bash
   cd "$ROOT_PATH"
   find . -type f -not -path "*/node_modules/*" -not -path "*/.git/*" \
     | sort > /tmp/dir_tree.txt
   ```
2. **Diff against previous snapshot** (if `$STATUS_REPORT?` provided) and flag new/deleted files.
3. **Guardrail scan**
   - Raw colors → `grep -R "Color(" lib/ | grep -v AppColors || true`
   - Un-pinned deps → `grep -R "\^" **/pubspec.yaml || true`
4. **Load manifests & requirements**
   - Parse `.context/architecture/**/*.yaml`
   - Parse `.simone/02_REQUIREMENTS/` if present.
5. **Feature coverage**
   - If `FEATURES.md` exists, mark each feature ✅/🔄/❌.
   - Else derive feature list from code + manifests.
6. **Run tests** (if present)
   ```bash
   flutter test -q || true
   ```
7. **Produce outputs** (see table below).
8. **Save** all outputs under `.context/assessments/$DATE/`.

## Outputs  →  `.context/assessments/$DATE/`
| File                       | Purpose                                          |
|----------------------------|--------------------------------------------------|
| `overall_project_status.md`| Executive summary & completion %                 |
| `feature_checklist.md`     | Feature table with completion %                  |
| `identified_issues.md`     | Guardrail & code-quality findings                |
| `recommendations.md`       | Actionable next steps                            |
| `deployment_readiness.md`  | GO / NO-GO plus blockers                         |
| `project_structure.md`     | Directory tree (+ highlights for new files)      |
| `codebase_graph.png`       | Mermaid-generated architecture graph             |

## Definition of Done
- All output files exist in `.context/assessments/$DATE/`
- Guardrail violations documented or resolved
- Summary line **“Ready for deployment: YES/NO”** present
- Each output file ends with ISO-8601 timestamp

## Follow-ups
- Create tasks using `/project:simone:create_general_task` for each 🔴 critical issue.
- Snapshot state with `/project:simone:project_review` once blockers are fixed.
