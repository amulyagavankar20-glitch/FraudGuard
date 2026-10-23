# Security and operational notes

- Set `FRAUDGUARD_ENV=production` and a strong `FRAUDGUARD_API_KEY`; production requests without a configured key fail closed.
- Never commit `.env`, dataset files, or trained artifacts containing sensitive data.
- `/health` reports readiness; scoring requires model artifacts.
- Use TLS at the reverse proxy, restrict network exposure, rotate keys, and avoid logging raw transaction payloads.
- This is an educational prototype and is not certified for financial authorization decisions.
