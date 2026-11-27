# verboX Backend Deployment & Maintenance Guide

Production deployment reference for the **verboX FastAPI backend** running on **Azure Container Apps** with automated CI/CD via **GitHub Actions** and **GitHub Container Registry (`ghcr.io`)**.

---

## Production Overview

| Item | Value |
| :--- | :--- |
| **Live Base URL** | `https://verbox-backend.blackpond-d6fc90cf.eastus.azurecontainerapps.io` |
| **API Prefix** | `https://verbox-backend.blackpond-d6fc90cf.eastus.azurecontainerapps.io/api/v1` |
| **Swagger UI** | `https://verbox-backend.blackpond-d6fc90cf.eastus.azurecontainerapps.io/docs` |
| **OpenAPI JSON** | `https://verbox-backend.blackpond-d6fc90cf.eastus.azurecontainerapps.io/openapi.json` |
| **Health Endpoint** | `https://verbox-backend.blackpond-d6fc90cf.eastus.azurecontainerapps.io/health` |
| **Azure Resource Group** | `AI-900-lab` (`eastus`) |
| **Container Apps Env** | `verbox-env` (`--logs-destination none`) |
| **Container App** | `verbox-backend` (`0.5 vCPU`, `1.0Gi`, `min-replicas: 0`, `max-replicas: 1`, port `8000`) |
| **Container Registry** | `ghcr.io/pranavja1n/verbox-backend` |
| **CI/CD Workflow** | `../.github/workflows/deploy-backend.yml` |

---

## How CI/CD Works

Pushing to `main` automatically deploys when changes touch `backend/**` or `.github/workflows/deploy-backend.yml`:

1. **`verify` job:** Installs `uv`, runs `uv sync --frozen --no-dev`, installs `en_core_web_sm`, and smoke-tests `GET /health` using `fastapi.testclient.TestClient`. If this fails, deployment is aborted.
2. **`build-and-deploy` job:** Builds `backend/Dockerfile`, pushes `ghcr.io/pranavja1n/verbox-backend:sha-<commit>` (and `:latest`), logs into Azure using the `AZURE_CREDENTIALS` GitHub secret, and runs `az containerapp update` with the immutable `:sha-<commit>` tag so Azure always rolls out a fresh revision.

> **Note:** Commits touching only `pixos/`, `sdk/`, or `frontend/` do **not** trigger a backend redeploy. You can still trigger a deploy manually from **GitHub → Actions → Deploy Backend to Azure Container Apps → Run workflow**.

---

## Developer Guide for Future Backend Updates

### 1. Adding or Updating a Python Library

Both `backend/Dockerfile` and the CI workflow run `uv sync --frozen --no-dev`. If `backend/pyproject.toml` and `backend/uv.lock` are out of sync—or if you import a library without adding it to `backend/pyproject.toml`—CI will fail before deploying.

1. **Edit dependencies** in `backend/pyproject.toml` under `[project].dependencies` (avoid adding `dotenv-python`, which conflicts with `python-dotenv`).
2. **Regenerate `backend/uv.lock`** from the **repo root (`verboX/`)** — **no `.venv` activation needed**:
   ```bash
   # Run from: verboX/ (repo root) | venv activation: NOT required
   uv lock --directory backend
   ```
3. **Install into the shared root `.venv`** so your local environment stays in sync — **no `.venv` activation needed**:
   ```bash
   # Run from: verboX/ (repo root) | venv activation: NOT required
   uv pip install --python .venv/bin/python -e ./backend
   ```
4. **If the library requires OS packages or non-PyPI models** (for example, another spaCy language model or a C library):
   - Add the `apt-get` or wheel install step to `backend/Dockerfile`.
   - If it is loaded during app import/startup, also add the install step to the `verify` job in `.github/workflows/deploy-backend.yml`.

---

### 2. Adding New Environment Variables or Secrets

The root `.env` file is gitignored and excluded from Docker builds via `backend/.dockerignore`, so new variables added locally will **not** exist in production automatically.

1. **Add the variable locally** to `verboX/.env` (the central `.env` used by `backend`, `pixos`, and `sdk`).
2. **Add it to Azure Container Apps** from **any directory** (`az` CLI logged in) — **no `.venv` activation needed**:
   - For **sensitive values** (API keys, passwords, connection strings):
     ```bash
     # Run from: any directory | venv activation: NOT required
     az containerapp secret set \
       --name verbox-backend \
       --resource-group AI-900-lab \
       --secrets my-new-secret="YOUR_SECRET_VALUE"

     az containerapp update \
       --name verbox-backend \
       --resource-group AI-900-lab \
       --set-env-vars MY_NEW_ENV_VAR=secretref:my-new-secret
     ```
   - For **non-secret config values** (flags, ports, URLs):
     ```bash
     # Run from: any directory | venv activation: NOT required
     az containerapp update \
       --name verbox-backend \
       --resource-group AI-900-lab \
       --set-env-vars MY_CONFIG_VAR="some-value"
     ```
   > **Important:** Do **not** set `VERBOX_RULES_DIR` on Azure unless overriding the built-in rules folder—omitting it lets `backend/src/backend/core/config.py` use `_DEFAULT_RULES_DIR` inside the container.
3. **If the variable is required at module import time** (similar to `AZURE_OPENAI_API_KEY_JD` in `backend/src/backend/judge/llm_client.py`), add a dummy placeholder under `env:` in the `Smoke test FastAPI app & /health endpoint` step of `.github/workflows/deploy-backend.yml` so CI can import `backend.main`.

---

### 3. Adding Routes, YAML Policy Rules, or CORS

- **New API routes:** Register routers in `backend/src/backend/api/router.py`; FastAPI automatically exposes them in `/docs` and `/openapi.json`.
- **New YAML rules:** Add `.yaml` / `.yml` files under `backend/src/backend/api/routes/rules/`. They are copied into the image (`COPY src ./src`) and loaded once per container worker via `@lru_cache` in `backend/src/backend/api/dependencies.py`.
- **CORS for deployed frontend:** `backend/src/backend/main.py` does not currently include `CORSMiddleware`. If a browser-hosted Next.js frontend calls the Azure backend URL directly, add `CORSMiddleware` with your frontend origin(s).
- **Stateless execution (`min-replicas: 0`):** The app scales to zero when idle and spins up on the next request (expect a short cold start). Never rely on local container memory or container disk for persistent state—use Redis (`backend/dedup/`) or MongoDB/Cosmos DB (`backend/mongo_util/`).

---

### 4. Testing Locally Before Pushing

Run these from the **repo root (`verboX/`)** — you can call `.venv/bin/python` directly (**no `.venv` activation needed**) or activate first with `source .venv/bin/activate`.

```bash
# Run from: verboX/ (repo root) | venv activation: NOT required

# 1. Verify dependency compatibility
uv pip check --python .venv/bin/python

# 2. Smoke-test FastAPI app & /health (same check CI runs)
.venv/bin/python -c "
from fastapi.testclient import TestClient
from backend.main import app
r = TestClient(app).get('/health')
assert r.status_code == 200 and r.json() == {'status': 'ok'}, r.text
print('OK:', r.json())
"

# 3. Run the backend locally with auto-reload (reads central verboX/.env)
.venv/bin/uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

If you prefer activating the virtual environment first:

```bash
# Run from: verboX/ (repo root) | venv activation: YES
source .venv/bin/activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

---

### 5. Deploying, Checking Logs & Troubleshooting on Azure

All commands below can be run from **any directory** (except `git`, which must run inside `verboX/`) — **no `.venv` activation needed**:

- **Deploy new backend changes:**
  ```bash
  # Run from: verboX/ (repo root) | venv activation: NOT required
  git add backend/
  git commit -m "feat(backend): describe your change"
  git push origin main
  ```
- **Watch the GitHub Actions deployment:**
  ```bash
  # Run from: verboX/ (repo root) | venv activation: NOT required
  gh run list -L 5
  gh run watch
  ```
- **Check live Container App logs (stdout/stderr):**
  ```bash
  # Run from: any directory | venv activation: NOT required
  az containerapp logs show --name verbox-backend --resource-group AI-900-lab --follow
  ```
- **Check active revisions & deployed image SHA:**
  ```bash
  # Run from: any directory | venv activation: NOT required
  az containerapp revision list \
    --name verbox-backend \
    --resource-group AI-900-lab \
    --query "[].{name:name,active:properties.active,image:properties.template.containers[0].image,traffic:properties.trafficWeight}" \
    -o table
  ```
- **Verify the live endpoint:**
  ```bash
  # Run from: any directory | venv activation: NOT required
  curl -i https://verbox-backend.blackpond-d6fc90cf.eastus.azurecontainerapps.io/health
  ```
- **Rollback to a previous commit image:**
  ```bash
  # Run from: any directory | venv activation: NOT required
  az containerapp update \
    --name verbox-backend \
    --resource-group AI-900-lab \
    --image ghcr.io/pranavja1n/verbox-backend:sha-<7-char-commit-sha>
  ```
