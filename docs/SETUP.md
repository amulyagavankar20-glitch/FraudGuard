# Setup

## Training source of truth

`fraudguard_training.ipynb` is the only training and evaluation entry point.
It implements Gaussian Naive Bayes -> manually specified discrete Bayesian
Network, then evaluates LightGBM as a secondary benchmark and GMM + EM as an
optional extension.

## Kaggle training
1. Open a Kaggle notebook and attach the **IEEE-CIS Fraud Detection** competition dataset.
2. Upload `fraudguard_training.ipynb` from this repository, or open it as a notebook.
3. Confirm the input path is `/kaggle/input/competitions/ieee-fraud-detection/`.
4. Install the versions in `requirements-notebook.txt`, then restart the kernel.
5. Run all cells. The notebook writes files under `/kaggle/working/fraudguard_artifacts/` and creates `fraudguard_artifacts.zip`.
6. Download the ZIP. It contains a `fraudguard_artifacts/` directory; copy the files *inside that directory* into this repository's `artifacts/` directory. Ensure `artifacts/metadata.json` and `artifacts/lightgbm_model.joblib` exist. Do not commit the raw dataset.

## Local setup
Python 3.10+ is recommended. Install runtime dependencies with `pip install -r requirements.txt`; install `pgmpy==0.1.24` separately if needed for the notebook. Put the dataset under `ieee-fraud-detection/` only if permitted by the competition terms. Otherwise use Kaggle.

For local notebook execution:

```powershell
conda activate ai
python -m pip install -r requirements.txt
python -m pip install -r requirements-notebook.txt
python -m jupyter nbconvert --to notebook --execute fraudguard_training.ipynb `
  --output fraudguard_training_executed.ipynb `
  --ExecutePreprocessor.timeout=-1
```

The notebook reads `ieee-fraud-detection/train_transaction.csv` and
`train_identity.csv`, then writes models and fresh metrics under `artifacts/`.

## Run static checks
```bash
python scripts/validate_training.py
pytest
```

## Run API after artifacts are exported
```bash
cp .env.example .env
# Set a strong FRAUDGUARD_API_KEY in .env
docker compose up --build
```
The API reports `not_ready` until `artifacts/metadata.json` and `artifacts/lightgbm_model.joblib` exist.
The Streamlit dashboard is available at `http://localhost:8501` and uses the
same API key. For a local dashboard, install `frontend/requirements.txt` and
run `streamlit run frontend/app.py` while the API is running.
