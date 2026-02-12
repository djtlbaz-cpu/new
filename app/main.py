from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import feedback, generation, learning, training, drums, subscriptions, payments
from .services.inference import get_inference_engine

app = FastAPI(title="Beat Addicts AI Engine", version="0.1.0", description="Local-first AI engine for Pulse")

origins = [origin.strip() for origin in settings.cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(drums.router, tags=["drums"])
app.include_router(generation.router, prefix="/generate", tags=["generation"])
app.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
app.include_router(training.router, prefix="/training", tags=["training"])
app.include_router(learning.router, prefix="/learning", tags=["learning"])
app.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])


@app.on_event("startup")
async def startup_event() -> None:
    engine = get_inference_engine()
    await engine.ensure_loaded()


@app.get("/health")
async def healthcheck() -> dict:
    from .services.database import get_database_gateway
    db = get_database_gateway()
    return {"status": "ok", "supabase": db.is_enabled()}


@app.get("/admin/db-status")
async def db_status() -> dict:
    """Check which Supabase tables exist."""
    from .services.database import get_database_gateway
    db = get_database_gateway()
    if not db.is_enabled():
        return {"connected": False, "tables": {}}

    tables = [
        "users", "subscription_tiers", "user_subscriptions",
        "generation_usage", "addons", "user_addons", "content_ownership",
    ]
    status = {}
    for t in tables:
        try:
            db.client.table(t).select("*").limit(1).execute()
            status[t] = "ok"
        except Exception:
            status[t] = "missing"

    return {"connected": True, "tables": status, "ready": all(v == "ok" for v in status.values())}


if __name__ == "__main__":
    import os
    import uvicorn

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    reload_flag = os.getenv("UVICORN_RELOAD", "false").lower() in {"1", "true", "yes"}

    try:
        uvicorn.run("app.main:app", host=host, port=port, reload=reload_flag)
    except OSError as exc:
        if getattr(exc, "errno", None) in {98, 10048}:
            print("Port is already in use. Stop the existing process or choose another port.")
        else:
            raise
