"""Routes: NASA environment series (wraps environment.get_environment_series)

Owner: Member 6 (Backend, Integration, QA & Deployment)

Historical instrument data only. It is served on its own route and never merged into a
crew response. If the adapter fails the route says so (503); it never substitutes made-up data.
"""

from fastapi import APIRouter, HTTPException

from ..services import environment_payload

router = APIRouter(prefix="/api", tags=["environment"])


@router.get("/environment")
def environment():
    try:
        return environment_payload()
    except (ValueError, OSError, KeyError) as exc:
        raise HTTPException(status_code=503, detail={
            "error": "environment_unavailable",
            "detail": str(exc),
            "fallback": "Use the cited static fallback in data/fallback/ (labelled not ingested).",
        })
