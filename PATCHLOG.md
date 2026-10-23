# Rebuild change log

## Notebook-first consolidation

- Made `fraudguard_training.ipynb` the single canonical training/evaluation workflow.
- Added the missing Bayesian Network feature preparation cell required by the BN fitting cell.
- Added local/Kaggle path selection for the dataset and output directory.
- Removed the duplicate legacy `train.py`, `prepare_data.py`, synthetic data generator, and old evaluation/drift scripts.
- Cleared all old model/evaluation artifacts and generated processed datasets; `artifacts/` now contains only `.gitkeep`.
- Excluded the raw IEEE-CIS competition files from this project archive.
- Added PRD, architecture, setup, evaluation, security, and validation-status documents.
- Replaced the previous legacy API with a small API that consumes the canonical notebook's LightGBM export.
- Updated Docker, Compose, requirements, Makefile, and load-test script to match the notebook-artifact flow.
- Added static notebook syntax validation and API readiness/authentication tests.

## Validation performed

- Notebook JSON and code-cell Python syntax check: passed.
- Python `compileall`: passed.
- API tests: 2 passed.
- Full notebook training was not run here because `pgmpy` is unavailable and package downloads are blocked in this environment. No fresh model metrics are claimed; the artifact folder is intentionally empty until the notebook is run successfully in Kaggle.
- Docker build and live load test were not run here.
