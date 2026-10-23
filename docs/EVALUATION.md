# Evaluation protocol

## Primary coursework models
- **Gaussian Naive Bayes** is the baseline for probabilistic classification.
- **Bayesian Network** is the main Topic 1 model: manually specified DAG, estimated CPDs, and Variable Elimination for posterior inference.
- **LightGBM** is a secondary predictive benchmark, not the main explanation model.
- **GMM + EM** is an optional unsupervised anomaly-detection extension.

## Split and preprocessing
- Sort by `TransactionDT`; use the first 80% for training and later 20% for validation.
- Learn BN quantile bin edges and category grouping from training rows only.
- Represent missing BN values as an explicit state.
- The BN uses a reproducible validation sample (up to 3,000 rows) because exact inference per row is expensive.

## Metrics
- PR-AUC is the primary ranking metric for an imbalanced fraud target.
- Also report ROC-AUC, Brier score and recall at a fixed 5% false-positive rate.
- GMM's negative log-likelihood is an anomaly score, not a calibrated probability; do not interpret its Brier score as applicable.

## Caveats
- The root `model_comparison.csv` and `missingness_stress.csv` are copied from
  the latest notebook export. Rerun the notebook whenever the dataset or
  preprocessing changes.
- LightGBM uses the validation set for early stopping, so its reported validation metrics are not a fully untouched final-test estimate.
- The BN graph is manually specified; structure learning is not implemented.
- Missingness stress tests mask selected LightGBM input fields artificially. They measure sensitivity to feature loss, not all real-world missingness mechanisms.

## Latest measured results

| Model | PR-AUC | ROC-AUC | Brier | Recall @ 5% FPR | Validation rows |
|---|---:|---:|---:|---:|---:|
| LightGBM | 0.559487 | 0.910000 | 0.020971 | 0.657972 | 118108 |
| GaussianNB_numeric | 0.088913 | 0.734347 | 0.695684 | 0.178395 | 118108 |
| BayesianNetwork_sample | 0.093619 | 0.740459 | 0.052849 | 0.051546 | 3000 |
| GMM_EM_anomaly_score | 0.033762 | 0.416837 | N/A | N/A | 118108 |

The BN uses a reproducible 3,000-row sample because exact row-wise Variable
Elimination is slower than vectorized classifiers. GMM produces a negative
log-likelihood anomaly score, so Brier score and probability calibration do
not apply.
