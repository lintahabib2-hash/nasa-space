"""Routes: baseline results (wraps analytics.get_baseline_result)

Owner: Member 6 (Backend, Integration, QA & Deployment)
"""

from typing import List, Optional

from fastapi import APIRouter, Query, Request

from ..contracts import BaselineResponse
from ..services import baselines_for_subject, compute_baseline

router = APIRouter(prefix="/api", tags=["baseline"])


@router.get("/baseline", response_model=BaselineResponse)
def baseline(request: Request, subject_id: str = Query(..., min_length=1),
             measurement: str = Query(..., min_length=1), study_id: Optional[str] = Query(None)):
    """Latest reading of one series vs. its own prior history (never other sources)."""
    return compute_baseline(request.app.state.repo, subject_id, measurement, study_id)


@router.get("/baseline/all", response_model=List[BaselineResponse])
def baseline_all(request: Request, subject_id: str = Query(..., min_length=1)):
    return baselines_for_subject(request.app.state.repo, subject_id)
