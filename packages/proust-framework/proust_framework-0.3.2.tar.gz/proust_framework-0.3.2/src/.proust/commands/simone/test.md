# test

## Purpose
Run the project’s test suite, auto-fix straightforward infrastructure issues, and output a concise summary of results.

## Context Files to Load
*(none automatically—test runner detects project files)*

## Inputs
| Variable | Description            |
|----------|------------------------|
| *(none)* | Non-interactive command |

## Steps
1. **Execute test suite**
   - Detect project type & test command:
     - *Python* → `poetry run pytest` ➜ `pytest` ➜ `python -m pytest` ➜ custom `run_tests.py`.
     - *Node/TS* → `npm test` ➜ `yarn test` ➜ framework script (`jest`, `vitest`).
     - *Rust* `cargo test`, *Go* `go test ./...`, etc.
   - Run command, capture output, execution time, totals.

2. **Analyze results & identify issues**
   - Parse failures for common infrastructure causes:
     - Import/module resolution, missing dependencies, env vars, missing `__init__.py`, etc.

3. **Auto-fix common problems** (if safe)
   - Python: create empty `__init__.py`, fix sys.path, add test dir to PYTHONPATH.
   - JS/TS: run `npm install` if `node_modules` absent, fix simple Jest path in `jest.config.js`.
   - General: create missing test dirs, adjust permissions.
   - **Do not** fix business logic test failures.

4. **Provide test summary**
   ```markdown
   Test Results:
   - Total: X
   - Passed: Y (Z%)
   - Failed: A
   - Skipped: B
   - Time: C s

   Issues Fixed:
   - …

   Issues Requiring Manual Action:
   - …

   Status: PASSING | FAILING | BLOCKED
   ```

## Definition of Done
- Test command executed.
- Quick infrastructure fixes applied.
- Summary printed (concise).

## Follow-ups
- If status ≠ PASSING, create tasks via `/create_general_task` or tag failing tasks.
- Suggest running `/commit` to capture fixes.
