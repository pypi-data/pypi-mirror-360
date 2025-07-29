# create_sprints_from_milestone

## Purpose
Transform an existing **milestone** into a sequence of well-structured sprints, each with clear scope and meta files, and update project manifests accordingly.

## Context Files to Load
1. `.context/universal_claude.md`
2. `.simone/00_PROJECT_MANIFEST.md`
3. `.simone/02_REQUIREMENTS/**`
4. `.simone/01_PROJECT_DOCS/**`
5. `.simone/05_ARCHITECTURAL_DECISIONS/**`

## Inputs
| Variable     | Description                              | Example  |
|--------------|------------------------------------------|----------|
| `$MILESTONE` | **Required** milestone ID (e.g., `M01`)  | `M02`    |
| `$DATE`      | Current UTC date                         | `2025-07-04` |

## Preconditions
1. Milestone directory `.simone/02_REQUIREMENTS/$MILESTONE/` exists.
2. Milestone meta file `M##_milestone_meta.md` present.
3. Sprint template `.simone/99_TEMPLATES/sprint_meta_template.md` exists.

## Steps
1. **Analyze milestone state**
   - Parse existing sprints under `.simone/03_SPRINTS/` matching `$MILESTONE`.
   - Read each sprint meta to capture status.
   - Build list of completed vs. pending deliverables.

2. **Assess completed work vs. requirements**
   - Read milestone meta & all linked docs (PRD, SPECS, etc.).
   - Map existing sprint deliverables to milestone DoD.
   - Produce gap analysis of remaining work.

3. **Identify remaining work & dependencies**
   - Group outstanding deliverables into 1-week, independently valuable chunks.
   - Capture natural dependencies.

4. **Design sprint boundaries**
   - For each deliverable group create a sprint focus.
   - Sprint naming: `S<nn>_$MILESTONE_$slug`.
   - Skip creation if sprint already exists & is complete.

5. **Create sprint directories & meta files**
   - For every new sprint:
     - Create dir `.simone/03_SPRINTS/$FULL_NAME/`.
     - Copy template → `$FULL_NAME/$SPRINT_meta.md`.
     - Fill sections: Goal, Key deliverables, DoD, Status: planned.

6. **Update PROJECT_MANIFEST**
   - Set `highest_sprint_in_milestone` appropriately.
   - Update sprint overview list (completed ✅, planned).
   - Update `last_updated` timestamp.

7. **Validate sprint coherence & dependencies**
   - Ensure sequence flows logically, no impossible dependencies.
   - Confirm all milestone DoD items covered.

8. **Report milestone plan**
   Output Markdown summary (see format below).

## Output Summary (console & saved to `.simone/03_SPRINTS/$MILESTONE_sprint_plan_$DATE.md`)
```markdown
## Milestone Sprint Plan – [$DATE]

**Milestone:** $MILESTONE
**Sprints completed:** <count>
**Sprints planned:** <count>
**Estimated completion (sprints):** <Sxx → Syy>

### Sprint Roadmap
- **S01_$MILESTONE_auth_core**: ✅ COMPLETED – Auth foundation
- **S02_$MILESTONE_ui_polish**: 🟡 PLANNED – UI polish & tests
…

### Validation
- All milestone DoD items mapped to sprint deliverables ✅/🔄
- Dependencies minimal & logical
- Each sprint delivers independent value

**Next step:** Detail sprint **$NEXT_SPRINT** with `/project:simone:create_sprint_tasks $NEXT_SPRINT`
```

## Definition of Done
- Gap analysis complete.
- New sprint dirs & meta files created.
- Manifest updated.
- Summary file saved and printed.

## Follow-ups
- Immediately run `/project:simone:create_sprint_tasks $NEXT_SPRINT` to generate detailed tasks.
