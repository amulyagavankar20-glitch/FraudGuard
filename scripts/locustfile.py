"""Locust load test for the exported LightGBM API.

Run:
  FRAUDGUARD_API_KEY=... locust -f scripts/locustfile.py --headless -u 25 -r 5 -t 30s --host http://127.0.0.1:8000
"""
import os

from locust import HttpUser, between, task


class FraudUser(HttpUser):
    wait_time = between(0.05, 0.25)

    def on_start(self):
        self.headers = {"X-API-Key": os.getenv("FRAUDGUARD_API_KEY", "")}
        self.client.get("/health")

    @task
    def score(self):
        # Partial payload intentionally exercises missing-feature handling.
        self.client.post(
            "/v1/score",
            headers=self.headers,
            json={"features": {
                "TransactionAmt": 125.5,
                "TransactionDT": 86400,
                "ProductCD": "W"
            }},
            name="/v1/score"
        )
