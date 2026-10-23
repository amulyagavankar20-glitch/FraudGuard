# FraudGuard — Probabilistic Fraud Detection

**Coursework focus: Intelligent Systems II, Topic 1 — Uncertain Knowledge and Reasoning**

FraudGuard studies how a system can reason about uncertain transaction evidence. The main learning path is:

1. **Gaussian Naive Bayes baseline** — use Bayes' rule to estimate fraud probability under a conditional-independence assumption.
2. **Discrete Bayesian Network** — represent selected dependencies with a directed acyclic graph, estimate CPDs, and infer `P(Fraud = 1 | evidence)` using Variable Elimination.
3. **LightGBM benchmark (secondary)** — compare predictive performance; this is not the conceptual focus.
4. **GMM + EM (optional extension)** — model legitimate transactions and use negative log-likelihood as an anomaly score.

## What is implemented

- IEEE-CIS transaction and identity tables are joined on `TransactionID`.
- Data is sorted by `TransactionDT` and split chronologically (80% train, 20% validation).
- The Bayesian Network uses a manually specified, documented graph. It is **not** currently a structure-learning experiment.
- Numeric BN features are discretized using training-only quantile boundaries.
- Missing BN feature values are represented as explicit states; the inference step also handles missing evidence.
- CPDs are estimated with a BDeu prior (equivalent sample size 10).
- Exact BN inference is evaluated on a reproducible validation sample of up to 3,000 rows because row-wise inference is expensive.
- LightGBM is retained as a performance benchmark; the current API serves LightGBM only.
- The notebook exports models, metrics and metadata.

## Syllabus mapping

| Topic 1 concept | Project component |
|---|---|
| Quantifying uncertainty | Probability scores for fraud |
| Bayes' rule / Naive Bayes | GaussianNB baseline |
| Bayesian Network semantics | Directed graph and CPDs |
| Inference in Bayesian Networks | Variable Elimination |
| Graphical models / GMM / EM | Optional GMM anomaly baseline |

## Bayesian Network used in the notebook

The BN is a manually specified DAG, not a structure-learning experiment:

```text
TransactionAmtBin ─┐
TransactionDTBin  ─┤
card1Bin          ─┤
ProductCD         ─┤──> Fraud
card4             ──┤
DeviceType        ──┤
P_emaildomain     ──┤
addr1Bin          ───┘

ProductCD ───> addr1Bin
```

Gaussian Naive Bayes assumes the selected numeric features are conditionally
independent given `Fraud`. The BN relaxes that assumption for the explicitly
represented `ProductCD -> addr1Bin` dependency while retaining direct evidence
links into `Fraud`. Variable Elimination computes
`P(Fraud = 1 | observed evidence)`; missing evidence is omitted and therefore
marginalized by the inference algorithm.

## Repository layout

```text
fraudguard_training.ipynb   # canonical, syllabus-first training notebook
src/fraudguard/service/     # FastAPI service; currently serves LightGBM
frontend/                   # Streamlit scoring dashboard
docs/                       # setup, architecture, evaluation and security notes
model_comparison.csv        # latest metrics copied from the canonical notebook run
missingness_stress.csv      # stored LightGBM feature-masking experiment
```

## Run the notebook

1. Open Kaggle and attach **IEEE-CIS Fraud Detection** through **Add Input**.
2. Ensure the notebook environment has the packages in `requirements-notebook.txt`.
3. Run the notebook from top to bottom.
4. Download `fraudguard_artifacts.zip` from `/kaggle/working/`.

For local execution, place the permitted dataset files in `ieee-fraud-detection/` and install the notebook requirements.

## Latest regenerated evaluation

The following results were regenerated locally from the dataset in
`ieee-fraud-detection/` on the chronological 80/20 split:

| Model | PR-AUC | ROC-AUC | Brier | Recall @ 5% FPR | Rows |
|---|---:|---:|---:|---:|---:|
| LightGBM benchmark | 0.5595 | 0.9100 | 0.0210 | 0.6580 | 118,108 |
| Gaussian Naive Bayes | 0.0889 | 0.7343 | 0.6957 | 0.1784 | 118,108 |
| Bayesian Network | 0.0936 | 0.7405 | 0.0528 | 0.0515 | 3,000 |
| GMM + EM anomaly score | 0.0338 | 0.4168 | N/A | N/A | 118,108 |

The BN row is a 3,000-row reproducible sample and must not be presented as
directly comparable to full-validation rows without that qualification.

- PR-AUC is the primary ranking metric because fraud is a minority class.
- Report ROC-AUC, Brier score and recall at 5% false-positive rate as supporting metrics.
- The BN result uses a smaller validation sample than LightGBM and GaussianNB; label this every time you show the comparison.
- The GMM score is an anomaly score, not a calibrated fraud probability.
- Rerun the notebook whenever the dataset, seed, or preprocessing changes.

## Current scope and limitations

- The BN graph is manually specified to keep assumptions explainable; automatic structure learning is not implemented.
- The BN is an educational/research model. It is not the deployed scoring API model.
- LightGBM's validation set is also used for early stopping, so its reported validation result is best treated as a benchmark rather than an untouched final test score.
- This is a research/coursework prototype, not a production-certified fraud prevention service.
- Do not redistribute IEEE-CIS dataset files; follow the dataset's access terms.

See `docs/SETUP.md`, `docs/ARCHITECTURE.md`, `docs/EVALUATION.md`, and `docs/SECURITY.md`.
