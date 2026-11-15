"""FastAPI application entry point; mounts routers

Owner: Member 6 (Backend, Integration, QA & Deployment)

Run from the repository root:

    pip install -r backend/requirements.txt
    uvicorn backend.app.main:app --port 8000

then, for the frontend dev server: VITE_API_BASE=http://127.0.0.1:8000 npm run dev
Interactive docs: http://127.0.0.1:8000/docs
"""

from typing import Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api import baseline, checkins, environment, knowledge, observations
from .config import Settings
from .contracts import Health
from .services import open_repository
from .storage import Repository, RepositoryError


def create_app(settings: Optional[Settings] = None, repo: Optional[Repository] = None) -> FastAPI:
    settings = settings or Settings()
    app = FastAPI(
        title="Crew Vitals API",
        description="Decision support, not a diagnosis. Not a medical device. Demo data is simulated.",
        version="1.0.0",
    )
    app.state.settings = settings
    app.state.repo = repo or open_repository(settings)

    app.add_middleware(CORSMiddleware, allow_origins=list(settings.cors_origins),
                       allow_methods=["GET", "POST"], allow_headers=["Content-Type", "Accept"])

    @app.exception_handler(RepositoryError)
    async def _refused(_: Request, exc: RepositoryError):
        return JSONResponse(status_code=422, content={"error": "invalid_data", "detail": str(exc)})

    @app.exception_handler(ValueError)
    async def _bad_value(_: Request, exc: ValueError):
        # Analytics raises ValueError for malformed supplied fields; surface it, never guess.
        return JSONResponse(status_code=422, content={"error": "invalid_data", "detail": str(exc)})

    @app.get("/api/health", response_model=Health, tags=["meta"])
    def health(request: Request):
        counts = request.app.state.repo.counts()
        return {"status": "ok", "storage": "sqlite", **counts}

    for module in (observations, baseline, checkins, environment, knowledge):
        app.include_router(module.router)
    return app


app = create_app()
