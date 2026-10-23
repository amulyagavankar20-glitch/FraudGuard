# Architecture

## Canonical workflow

```mermaid
flowchart TD
    A[IEEE-CIS Kaggle input] --> B[Load train_transaction.csv]
    A --> C[Load train_identity.csv]
    B --> D[Left join on TransactionID]
    C --> D
    D --> E[Sort by TransactionDT]
    E --> F[Chronological train / validation split]
    F --> G[Gaussian Naive Bayes baseline]
    F --> H[Discrete Bayesian Network]
    F --> I[LightGBM secondary benchmark]
    F --> J[GMM fitted with EM]
    G --> K[Metrics and missingness stress tests]
    H --> K
    I --> K
    J --> K
    K --> L[Export models, metadata, CSV/JSON results]
    L --> M[artifacts/]
    M --> N[FastAPI inference service]
```

## Deployment flow

```mermaid
flowchart LR
    Client -->|POST /v1/score + X-API-Key| API[FastAPI]
    API --> Auth[API key validation]
    Auth --> Prep[Schema alignment and categorical mapping]
    Prep --> Model[Notebook-trained LightGBM]
    Model --> Response[Fraud probability]
    API --> Health[GET /health]
```

## Important boundaries
- The notebook is the only training entry point. Legacy training scripts were removed to avoid pipeline drift.
- The academic progression is Gaussian Naive Bayes -> Bayesian Network. LightGBM is a secondary benchmark; the serving API currently serves LightGBM only.
- Missing BN evidence is marginalized at inference, but CPDs are estimated on complete cases; this is not EM training for the BN.
- GMM negative log likelihood is an anomaly score, not a calibrated fraud probability.

## Bayesian Network DAG

The notebook specifies these edges manually:

- `TransactionAmtBin -> Fraud`
- `TransactionDTBin -> Fraud`
- `card1Bin -> Fraud`
- `ProductCD -> Fraud`
- `card4 -> Fraud`
- `DeviceType -> Fraud`
- `P_emaildomain -> Fraud`
- `addr1Bin -> Fraud`
- `ProductCD -> addr1Bin`

CPDs use `BayesianEstimator` with a BDeu prior and equivalent sample size 10.
`VariableElimination` answers posterior queries for `Fraud`.
