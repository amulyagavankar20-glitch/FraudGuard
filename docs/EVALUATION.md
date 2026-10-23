# Evaluation protocol

- Split chronologically on `TransactionDT`; don't randomly mix future transactions into training.
- Learn category vocabularies, bin edges, and any imputation/scaling parameters on training rows only.
- PR-AUC is the primary ranking metric for the imbalanced fraud target. Also report ROC-AUC, Brier score, and recall at a fixed 5% FPR.
- Missingness tests mask observed cells in selected identity/contact fields. They measure sensitivity to artificial feature loss, not naturally missing-at-random performance.
- The Bayesian Network is evaluated on a sample because exact inference per row is expensive; label this clearly and avoid comparing it as if it used every validation row.
- GMM is fitted to legitimate training transactions and ranks anomalies by negative log-likelihood. Its score is not a probability, so Brier score and probability calibration are not applicable.
- Report results actually produced by the run. Do not hard-code or promise target metrics.
