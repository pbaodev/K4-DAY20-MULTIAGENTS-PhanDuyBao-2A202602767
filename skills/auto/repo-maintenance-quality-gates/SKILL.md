---
name: repo-maintenance-quality-gates
description: Use when fixing bugs or maintaining a Python package under repository-level quality checks.
---
1. Read the project instructions and identify every required code, test, and documentation change before editing.
2. Add type annotations for every parameter and return value of each public function in the package.
3. Add a regression test for each bug fixed, and meet any stated test-file or minimum-count requirements.
4. Record each fix in the required changelog section and follow the prescribed bullet format.
5. Run the relevant tests and inspect the final diff; passing existing tests alone does not confirm every check is satisfied.
