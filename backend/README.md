# Beat Addicts Local AI Engine

This backend powers the Pulse agent inside the Beat Addicts browser DAW. It is optimized for local training and inference, and can later be deployed to a production GPU server without code changes.

## Features

- **FastAPI** service with dedicated endpoints for each creative stage (`/generate/drums`, `/generate/bassline`, `/generate/melody`, `/generate/chords`, `/generate/arrangement`).
- **Phase 0 legal enforcement**: every request carries user consent metadata; training is only enabled when opt-in is true.
- **Supabase logging**: accepted/rejected generations, genre preferences, MIDI uploads, and training batches are stored for evaluation.
- **Model registry**: all checkpoints live in `models/` so the inference server always boots with the latest weights.
- **Local-first training**: GPU-accelerated PyTorch scripts under `training/` let you fine-tune on your laptop, then hot-load the weights into `models/checkpoints/`.

## Getting Started

```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Configure environment variables in a `.env` file:

```env
SUPABASE_URL="https://<your-project>.supabase.co"
SUPABASE_SERVICE_KEY="service-role-key"
CORS_ORIGINS="http://localhost:5173,https://beat-addicts.app"
MODEL_DIR="models"
LEGAL_GENERATION_LIMIT=64
```

## Local Training Workflow

1. Drop curated MIDI or rendered stems into `training/data/` (see `training/data_pipeline.py`).
2. Run `python -m training.run_training --config training/configs/local.json` (sample arguments are inline in the script docstring).
3. Checkpoints are saved to `models/checkpoints/` with semantic versioning; the inference service automatically loads the latest on restart.
4. Use the `/training/batch` endpoint (already called by the frontend) to log any user-approved material that is compliant with Phase 0 rules.

## Deployment Notes

- Switch the `VITE_AI_API_BASE_URL` environment variable on the frontend to point to your deployed API.
- Use `uvicorn app.main:app --host 0.0.0.0 --port 8000` behind nginx for production.
- When moving to the cloud, mount `models/` as a persistent volume so new checkpoints propagate across releases.

## Deploying the Backend on Railway

Production-ready with CPU-only PyTorch (~200 MB).

| Setting            | Value                                              |
| ------------------ | -------------------------------------------------- |
| **Root Directory** | `backend`                                          |
| **Build Command**  | `pip install -r requirements.txt`                  |
| **Start Command**  | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

The `Procfile` defines: `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Environment Variables

| Variable       | Value                                                     |
| -------------- | --------------------------------------------------------- |
| `CORS_ORIGINS` | `https://your-frontend.netlify.app,http://localhost:5173` |
| `MODEL_DIR`    | `models`                                                  |
| `PORT`         | _(set automatically by Railway)_                          |

### Deploy Steps

1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click **New Project** → **Deploy from GitHub repo**
3. Select the `djtlbaz-cpu/new` repository
4. Set **Root Directory** to `backend`
5. Add the environment variables above
6. Railway will auto-detect the `Procfile` and deploy
7. Verify health at `https://<your-app>.up.railway.app/health`

For more detail on each module see inline docstrings within `app/services` and `training/`.
