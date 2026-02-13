# Beat Addicts - AI-Powered DAW

AI-powered music production platform with pattern generation, drum sequencing, and real-time audio processing.

## Project Structure

| Folder     | Purpose                                             |
| ---------- | --------------------------------------------------- |
| `backend/` | FastAPI backend (AI engine, API, training pipeline) |
| `src/`     | React/Vite frontend                                 |
| `dist/`    | Production frontend build                           |

## Backend (FastAPI)

The backend lives in **`/backend`** and contains:

- `app/` — FastAPI application, routers, services, schemas
- `models/` — PyTorch model definitions (DrumModel, GrooveTransformer)
- `training/` — Training pipeline, dataset loaders, evaluation
- `inference/` — Drum pattern generation from trained models
- `tests/` — pytest test suite

### Run Locally

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate      # Windows
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### API Endpoints

- `GET /health` — Health check
- `POST /generate/drums` — Generate AI drum patterns
- `POST /feedback/pattern` — Submit pattern feedback
- `POST /training/batch` — Submit training data
- `GET /learning/preferences` — Get learned preferences

## Deploying the Backend on Railway

The backend is production-ready for Railway deployment with CPU-only PyTorch (~200 MB).

### Railway Build & Start

| Setting            | Value                                              |
| ------------------ | -------------------------------------------------- |
| **Root Directory** | `backend`                                          |
| **Build Command**  | `pip install -r requirements.txt`                  |
| **Start Command**  | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

The `Procfile` in `backend/` defines: `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`

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

## Frontend (Netlify)

The frontend is a Vite + React app deployed to Netlify from the `dist/` folder.

## License

All rights reserved. Beat Addicts is a proprietary project.
