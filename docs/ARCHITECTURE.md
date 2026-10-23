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
    F --> G[LightGBM baseline]
    F --> H[Gaussian Naive Bayes]
    F --> I[Discrete Bayesian Network]
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
- The Bayesian Network and GMM are research comparisons. The serving API currently serves LightGBM only.
- Missing BN evidence is marginalized at inference, but CPDs are estimated on complete cases; this is not EM training for the BN.
- GMM negative log likelihood is an anomaly score, not a calibrated fraud probability.
