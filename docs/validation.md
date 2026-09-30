# Local reconstruction validation

Validated: 2026-10-01. Python 3.10.12, standard-library test runner.

- Tests: **19 passed** (14 behavioral + 5 repository-quality) using `python3 -m unittest discover -s tests -v`.
- Default demonstration: executed successfully without production dependencies.
- Scope: synthetic public reconstruction only, not production performance or accuracy.
- File/link/SVG and heuristic disclosure review: no flagged candidate findings at this check.
- Publication status: NEEDS USER REVIEW. IP/NDA and license choice are not validated by tests.

The separate static dashboard was tested in local Chrome: 18 scenario/view combinations,
keyboard tab navigation, desktop/mobile layouts and direct file opening passed.
No JavaScript exceptions or external page requests were observed.
Nine generic architecture SVGs passed text-bound checks. These are local render checks,
not GitHub README rendering validation. The dashboard does not execute the Python runtime.
