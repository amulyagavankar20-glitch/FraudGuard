# Product Requirements Document

## Purpose
FraudGuard is a coursework-aligned fraud detection research prototype using the IEEE-CIS Fraud Detection dataset. The canonical Jupyter notebook is the sole source of truth for model training and evaluation.

## Users
- Students and reviewers studying Bayesian reasoning, EM/GMM, classification, and missing-data robustness.
- Developers who want to serve the exported LightGBM benchmark through a small API.

## Functional requirements
1. Load `train_transaction.csv` and left-join `train_identity.csv` on `TransactionID`.
2. Keep competition test files out of supervised evaluation.
3. Split chronologically using `TransactionDT`.
4. Train and compare LightGBM, Gaussian Naive Bayes, a discrete Bayesian Network, and GMM-EM anomaly scoring.
5. Evaluate PR-AUC, ROC-AUC, Brier score, recall at 5% FPR, and controlled missing-field stress.
6. Export models, metrics, and metadata from the notebook.
7. Serve the exported LightGBM model with API-key protection in production.

## Non-functional requirements
- Reproducible random seed.
- Preprocessing decisions learned from training data only.
- No raw competition dataset in the repository or Docker image.
- Clear limitations for sampled BN evaluation and unsupervised GMM scores.

## Out of scope
- Production banking certification, real-time authorization integrations, automated retraining, and claims of causal explanations.
