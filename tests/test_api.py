from fastapi.testclient import TestClient

from fraudguard.service import app


def test_health_without_artifacts_reports_not_ready(monkeypatch, tmp_path):
    monkeypatch.setattr(app, "ARTIFACTS", tmp_path)
    client = TestClient(app.app)
    response = client.get("/health")
    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"


def test_production_requires_api_key_when_unconfigured(monkeypatch, tmp_path):
    monkeypatch.setattr(app, "ARTIFACTS", tmp_path)
    monkeypatch.setattr(app, "API_KEY", "")
    monkeypatch.setattr(app, "APP_ENV", "production")
    client = TestClient(app.app)
    response = client.post("/v1/score", json={"features": {}})
    assert response.status_code == 503


def test_comparison_returns_recorded_metrics(monkeypatch, tmp_path):
    metrics = tmp_path / "model_comparison.csv"
    metrics.write_text("model,PR_AUC\nLightGBM,0.55\n", encoding="utf-8")
    monkeypatch.setattr(app, "COMPARISON_FILE", metrics)
    monkeypatch.setattr(app, "API_KEY", "test-key")
    client = TestClient(app.app)
    response = client.get("/v1/comparison", headers={"X-API-Key": "test-key"})
    assert response.status_code == 200
    assert response.json()["metrics"] == [{"model": "LightGBM", "PR_AUC": "0.55"}]
