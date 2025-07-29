# reflect_on_solution

## Purpose
Iteratively self-review the assistant’s previous response(s), identify issues, propose fixes, choose the best fix, apply it, and output the refined answer until no further problems remain.

## Context Files to Load
*(none automatically—caller passes `${PREVIOUS_RESPONSES}` and `${NUMBER_OF_PREVIOUS}` placeholders.)*

## Inputs
| Variable                | Description                                              |
|-------------------------|----------------------------------------------------------|
| `${PREVIOUS_RESPONSES}` | Concatenated previous assistant responses to be reviewed |
| `${NUMBER_OF_PREVIOUS}` | Count of previous responses                              |

## Steps
1. **Issue identification**
   - For each problem detected (mistake, inconsistency, gap, etc.), wrap description in `<issue>` tags.

2. **Generate three candidate solutions per issue**
   - Provide each inside its own `<solution>` tags.

3. **Compare solution efficiency**
   - Discuss time, impact, probability of success inside `<efficiency_comparison>` tags.

4. **Select best solution**
   - Wrap rationale in `<best_solution>` tags.

5. **Apply best solution(s)**
   - Iteratively refine the response; output full improved response inside `<refined_response>` tags.

6. **Repeat until optimized**
   - Loop Steps 1-5 until no further issues.
   - If no issues on first pass → output:
     ```
     It's Optimized! No more issues :) ⭐
     ```

7. **Optional memory update**
   - If a fix yields a rule worth remembering, append STRICT rule to `.context/scratch_pad.md`.

## Output
- Either the final `<refined_response>` block or the optimization confirmation line.

## Definition of Done
- No `<issue>` blocks remain after last iteration.
- Output follows tag format exactly.
- Scratch pad updated only when warranted.

## Follow-ups
- Caller may insert the refined response into documentation or send to user.
