"""Notebook-artifact inference API.

This service consumes the canonical artifacts produced by fraudguard_training.ipynb.
It intentionally exposes a feature-dictionary contract instead of reusing the
legacy handcrafted feature pipeline.
"""
from __future__ import annotations

import hmac
import json
import os
import csv
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

ARTIFACTS = Path(os.getenv("FRAUDGUARD_ARTIFACTS_DIR", "/app/artifacts"))
COMPARISON_FILE = Path(os.getenv("FRAUDGUARD_COMPARISON_FILE", "/app/model_comparison.csv"))
API_KEY = os.getenv("FRAUDGUARD_API_KEY", "")
APP_ENV = os.getenv("FRAUDGUARD_ENV", "production")


class ScoreRequest(BaseModel):
    features: dict[str, Any] = Field(..., description="Feature names/values from the trained IEEE-CIS schema")


def auth(x_api_key: str = Header(default="")) -> None:
    if not API_KEY:
        if APP_ENV.lower() in {"prod", "production"}:
            raise HTTPException(status_code=503, detail="API authentication is not configured")
        return
    if not hmac.compare_digest(x_api_key, API_KEY):
        raise HTTPException(status_code=401, detail="invalid or missing X-API-Key")


_METADATA: dict | None = None
_MODEL: Any = None


def load_metadata() -> dict:
    global _METADATA
    if _METADATA is None:
        p = ARTIFACTS / "metadata.json"
        if not p.is_file():
            raise RuntimeError(f"Model metadata not found at {p}. Run the canonical notebook first.")
        _METADATA = json.loads(p.read_text())
    return _METADATA


def load_model():
    global _MODEL
    if _MODEL is None:
        p = ARTIFACTS / "lightgbm_model.joblib"
        if not p.is_file():
            raise RuntimeError(f"Model not found at {p}. Run the canonical notebook first.")
        _MODEL = joblib.load(p)
    return _MODEL


def model_schema(metadata: dict, model: Any) -> tuple[list[str], list[str], list[str], dict[str, list[str]]]:
    feature_columns = metadata.get("feature_columns")
    categorical_columns = metadata.get("categorical_columns")
    numeric_columns = metadata.get("numeric_columns")
    category_levels = metadata.get("category_levels")
    if feature_columns and categorical_columns and numeric_columns and category_levels:
        return feature_columns, categorical_columns, numeric_columns, category_levels

    feature_columns = list(model.feature_name_)
    categorical_indices = model.booster_.params.get("categorical_column", [])
    categorical_columns = [feature_columns[i] for i in categorical_indices]
    category_levels = dict(zip(categorical_columns, model.booster_.pandas_categorical))
    numeric_columns = [c for c in feature_columns if c not in categorical_columns]
    return feature_columns, categorical_columns, numeric_columns, category_levels


app = FastAPI(title="FraudGuard", version="1.0.0", description="IEEE-CIS fraud scoring using the exported LightGBM benchmark.")


@app.get("/health")
def health():
    ready = (ARTIFACTS / "metadata.json").is_file() and (ARTIFACTS / "lightgbm_model.joblib").is_file()
    payload = {"status": "ok" if ready else "not_ready", "model_loaded": ready}
    return payload if ready else JSONResponse(status_code=503, content=payload)


@app.get("/v1/comparison", dependencies=[Depends(auth)])
def comparison():
    if not COMPARISON_FILE.is_file():
        raise HTTPException(status_code=503, detail="Comparison metrics are not installed.")
    with COMPARISON_FILE.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise HTTPException(status_code=503, detail="Comparison metrics are empty.")
    return {"metrics": rows}


@app.post("/v1/score", dependencies=[Depends(auth)])
def score(request: ScoreRequest):
    if not (ARTIFACTS / "metadata.json").is_file() or not (ARTIFACTS / "lightgbm_model.joblib").is_file():
        raise HTTPException(status_code=503, detail="Model artifacts are not installed; run the canonical notebook and install its exports.")
    try:
        meta = load_metadata()
        model = load_model()
        feature_columns, categorical_columns, numeric_columns, category_levels = model_schema(meta, model)
        frame = pd.DataFrame([request.features]).reindex(columns=feature_columns)
        for c in categorical_columns:
            vals = frame[c].astype("string").fillna("__MISSING__").astype(str)
            levels = category_levels[c]
            vals = vals.where(vals.isin(set(levels)), "__UNKNOWN__")
            frame[c] = pd.Categorical(vals, categories=levels)
        for c in numeric_columns:
            frame[c] = pd.to_numeric(frame[c], errors="coerce")
        frame.replace([np.inf, -np.inf], np.nan, inplace=True)
        probability = float(model.predict_proba(frame)[0, 1])
        if not np.isfinite(probability):
            raise ValueError("Model produced a non-finite probability")
        return {"model": "lightgbm", "fraud_probability": probability}
    except (ValueError, KeyError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc