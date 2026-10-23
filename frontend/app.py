from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime
from typing import Any

import streamlit as st

DEFAULT_API_URL = os.getenv("FRAUDGUARD_API_URL", "http://localhost:8000")
DEFAULT_API_KEY = os.getenv("FRAUDGUARD_API_KEY", "")


st.set_page_config(
    page_title="FraudGuard",
    page_icon="🛡",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #17202a;
        --muted: #65727e;
        --line: #dfe5e9;
        --accent: #126e82;
        --accent-soft: #e7f4f5;
        --surface: #ffffff;
    }
    .stApp { background: #f7f9fa; color: var(--ink); }
    .block-container { max-width: 880px; padding-top: 3rem; }
    [data-testid="stSidebar"] { background: #eef3f4; border-right: 1px solid var(--line); }
    h1, h2, h3 { letter-spacing: -0.02em; color: var(--ink); }
    .eyebrow { color: var(--accent); font-size: .76rem; font-weight: 700;
        letter-spacing: .12em; text-transform: uppercase; margin-bottom: .4rem; }
    .subtitle { color: var(--muted); font-size: 1.02rem; margin-bottom: 1.6rem; }
    .panel { background: var(--surface); border: 1px solid var(--line);
        border-radius: 12px; padding: 1.25rem 1.35rem; margin-bottom: 1rem; }
    .result-label { color: var(--muted); font-size: .78rem; text-transform: uppercase;
        letter-spacing: .08em; }
    .result-value { color: var(--ink); font-size: 2.65rem; font-weight: 700; line-height: 1.1; }
    .stButton > button[kind="primary"] { background: var(--accent); border: 0; }
    </style>
    """,
    unsafe_allow_html=True,
)


def request_json(url: str, method: str = "GET", payload: dict[str, Any] | None = None,
                 api_key: str = "") -> tuple[int, dict[str, Any]]:
    body = None
    headers = {"Accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if api_key:
        headers["X-API-Key"] = api_key
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=8) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            detail = json.loads(exc.read().decode("utf-8"))
        except json.JSONDecodeError:
            detail = {"detail": str(exc)}
        return exc.code, detail
    except (urllib.error.URLError, TimeoutError) as exc:
        return 0, {"detail": str(exc)}


def api_base(value: str) -> str:
    return value.rstrip("/")


if "history" not in st.session_state:
    st.session_state.history = []

with st.sidebar:
    st.markdown("### Connection")
    api_url = st.text_input("API URL", value=DEFAULT_API_URL)
    api_key = st.text_input("API key", value=DEFAULT_API_KEY, type="password")
    if st.button("Check API health", use_container_width=True):
        status, payload = request_json(f"{api_base(api_url)}/health")
        if status == 200 and payload.get("status") == "ok":
            st.success("API ready")
        else:
            st.error(payload.get("detail", payload.get("status", "API unavailable")))
    st.caption("The dashboard sends requests to the existing FastAPI scoring service.")

st.markdown("### Comparative analysis")
st.caption(
    "These are the canonical validation results from the training notebook. "
    "GMM reports an anomaly score, not a calibrated probability; the Bayesian "
    "Network was evaluated on a sample."
)
if st.button("Load comparison results", use_container_width=True):
    status, payload = request_json(
        f"{api_base(api_url)}/v1/comparison",
        api_key=api_key,
    )
    if status == 200:
        st.dataframe(payload["metrics"], hide_index=True, use_container_width=True)
    else:
        st.error(payload.get("detail", f"Comparison failed with HTTP {status}."))

st.markdown('<div class="eyebrow">IEEE-CIS fraud scoring</div>', unsafe_allow_html=True)
st.title("FraudGuard")
st.markdown(
    '<div class="subtitle">A small, focused workspace for checking transaction risk '
    "with the exported LightGBM model.</div>",
    unsafe_allow_html=True,
)

left, right = st.columns(2)
with left:
    st.markdown("### Transaction")
    amount = st.number_input("Transaction amount", min_value=0.0, value=125.50, step=1.0)
    product = st.selectbox("Product code", ["W", "C", "R", "S", "H"])
with right:
    st.markdown("### Context")
    transaction_dt = st.number_input("Transaction time index", min_value=0, value=86400, step=1)
    card4 = st.text_input("Card 4", value="", placeholder="Optional")

with st.expander("Additional model features"):
    extra_json = st.text_area(
        "JSON feature values",
        value="{}",
        help="Add any other IEEE-CIS feature names here. Leave blank when unavailable.",
        height=110,
    )

try:
    extra_features = json.loads(extra_json or "{}")
    if not isinstance(extra_features, dict):
        raise TypeError("Additional features must be a JSON object.")
except (json.JSONDecodeError, TypeError) as exc:
    extra_features = {}
    st.warning(str(exc))

features: dict[str, Any] = {
    **extra_features,
    "TransactionAmt": amount,
    "ProductCD": product,
    "TransactionDT": transaction_dt,
}
if card4.strip():
    features["card4"] = card4.strip()

if st.button("Score transaction", type="primary", use_container_width=True):
    status, payload = request_json(
        f"{api_base(api_url)}/v1/score",
        method="POST",
        payload={"features": features},
        api_key=api_key,
    )
    if status == 200:
        probability = float(payload["fraud_probability"])
        st.session_state.history.insert(
            0,
            {
                "time": datetime.now().strftime("%H:%M:%S"),
                "amount": amount,
                "probability": probability,
                "product": product,
            },
        )
        st.session_state.history = st.session_state.history[:10]
        st.markdown(
            f'<div class="panel"><div class="result-label">Fraud probability</div>'
            f'<div class="result-value">{probability:.1%}</div></div>',
            unsafe_allow_html=True,
        )
        st.progress(probability, text="Model risk score")
        if probability >= 0.5:
            st.warning("Review recommended: this transaction is above the 50% risk threshold.")
        else:
            st.success("Lower predicted risk: continue normal review controls.")
    else:
        st.error(payload.get("detail", f"Scoring failed with HTTP {status}."))

if st.session_state.history:
    st.markdown("### Recent checks")
    st.dataframe(
        st.session_state.history,
        column_config={
            "time": "Time",
            "amount": st.column_config.NumberColumn("Amount", format="%.2f"),
            "probability": st.column_config.ProgressColumn(
                "Fraud probability", min_value=0, max_value=1, format="%.1%"
            ),
            "product": "Product",
        },
        hide_index=True,
        use_container_width=True,
    )
