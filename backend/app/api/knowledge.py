"""Routes: knowledge cards and source registry

Owner: Member 6 (Backend, Integration, QA & Deployment)

Serves Member 1's reviewed files unchanged.
"""

from fastapi import APIRouter, Request

from ..services import read_json

router = APIRouter(prefix="/api", tags=["knowledge"])


@router.get("/knowledge")
def knowledge(request: Request):
    return read_json(request.app.state.settings.knowledge_path)


@router.get("/sources")
def sources(request: Request):
    return read_json(request.app.state.settings.sources_path)
