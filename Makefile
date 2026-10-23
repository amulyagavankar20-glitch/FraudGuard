PYTHON ?= python
.PHONY: help test lint validate serve docker-build loadtest

help:
	@echo "make validate      - validate training JSON and Python syntax"
	@echo "make test           - run API and unit tests"
	@echo "make lint           - run ruff"
	@echo "make serve          - run artifact API"
	@echo "make docker-build   - build deployment image (requires artifacts)"

validate:
	$(PYTHON) scripts/validate_training.py

test:
	$(PYTHON) -m pytest

lint:
	$(PYTHON) -m ruff check src tests scripts

serve:
	$(PYTHON) -m uvicorn fraudguard.service.app:app --host 0.0.0.0 --port 8000

docker-build:
	docker build -t fraudguard:latest .

loadtest:
	locust -f scripts/locustfile.py --headless -u 25 -r 5 -t 30s --host http://127.0.0.1:8000 --only-summary
