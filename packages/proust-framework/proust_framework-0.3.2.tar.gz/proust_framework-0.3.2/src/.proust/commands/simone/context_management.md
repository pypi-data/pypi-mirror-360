# context_management

## Purpose
Provide a suite of sub-commands to initialize, track, update, and document project context so that agents and developers share a single source of truth.

## Sub-Commands
| Command               | Description                                             |
|-----------------------|---------------------------------------------------------|
| `init_context`        | Create baseline context scaffold for a new project      |
| `analyze_context`     | Detect recent context changes & assess their impact     |
| `update_context`      | Amend context docs to reflect a specific change         |
| `generate_context_docs` | Produce comprehensive context diagrams & docs        |

---

### ✳️ `init_context`

#### Prompt Template
```
Initialize context management for this project.
Create `src/.proust/` sub-folders: assessments/, guidelines/, planning/, scrapbook/.
Create placeholders: external_docs.yml, FEATURES.md, MANIFESTO.yml.
Establish baseline understanding of project structure and components.
```

#### Outputs
- `src/.proust/guidelines/README.md` (baseline rules)
- `src/.proust/planning/context_spec.md` (auto-generated spec)

---

### ✳️ `analyze_context`

#### Prompt Template
```
Analyze the current project context.
Identify recent changes and their impact on the overall system.
Track dependency relationships and affected components.
Provide a context change impact assessment.
```

#### Outputs
- `src/.proust/assessments/$DATE/context_change_log.md`
- Impact score from 1 (low) to 10 (critical)

---

### ✳️ `update_context`

#### Prompt Template
```
Update the project context documentation.
Incorporate recent changes to $COMPONENT.
Refresh component relationships and dependencies.
Ensure documentation alignment with current implementation.
```

#### Inputs
| Var         | Description                          |
|-------------|--------------------------------------|
| `$COMPONENT`| Component or module that changed     |

#### Outputs
- Updated docs under `src/.proust/planning/` or `src/.proust/guidelines/`
- Changelog entry appended to `context_change_log.md`

---

### ✳️ `generate_context_docs`

#### Prompt Template
```
Generate context documentation for the project.
Create visual representation of component relationships.
Document key abstractions, patterns, and architectural decisions.
Include detailed component interaction flows and data models.
```

#### Outputs
- `src/.proust/planning/context_diagram.png`
- `src/.proust/planning/context_overview.md`

---

## Definition of Done (for any sub-command)
- Specified files created/updated without overwriting unrelated content
- Timestamp appended to every generated doc
- No guardrail violations in generated Markdown / diagrams

## Follow-ups
- After `analyze_context` with high impact (score ≥7), create tasks via `/project:simone:create_general_task`.
- After `generate_context_docs`, consider snapshot via `/project:simone:project_review`.