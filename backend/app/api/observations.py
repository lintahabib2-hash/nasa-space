"""Routes: crew observations (wraps analytics.get_observations)

Owner: Member 6 (Backend, Integration, QA & Deployment)
"""

from typing import List, Optional, Union

from fastapi import APIRouter, Query, Request

from ..contracts import Observation, ObservationList

router = APIRouter(prefix="/api", tags=["observations"])


@router.get("/observations", response_model=ObservationList)
def list_observations(request: Request, subject_id: Optional[str] = Query(None),
                      measurement: Optional[str] = Query(None), study_id: Optional[str] = Query(None)):
    rows = request.app.state.repo.list_observations(subject_id=subject_id, measurement=measurement, study_id=study_id)
    return {"count": len(rows), "observations": rows}


@router.post("/observations", status_code=201)
def add_observations(request: Request, body: Union[Observation, List[Observation]]):
    """Store one or many validated observations (idempotent per series + timestamp)."""
    items = body if isinstance(body, list) else [body]
    stored = request.app.state.repo.add_observations(items)
    return {"stored": stored}
