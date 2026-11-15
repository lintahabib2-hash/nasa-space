"""Routes: submit / list daily check-ins

Owner: Member 6 (Backend, Integration, QA & Deployment)

The body is Member 5's check-in record (shared/schemas/checkin.schema.json). It is stored,
its indicators become observations, and the response includes the resulting baselines so a
client can show the effect of the new entry straight away.
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Query, Request

from ..services import compute_baseline

router = APIRouter(prefix="/api", tags=["checkins"])


@router.post("/checkins", status_code=201)
def submit_checkin(request: Request, record: Dict[str, Any] = Body(...)):
    repo = request.app.state.repo
    stored = repo.add_checkin(record)  # validates against the shared schema first
    baselines = [compute_baseline(repo, record["subject_id"], m) for m in record["indicators"]]
    return {
        "record_id": record["record_id"], "subject_id": record["subject_id"],
        "observations_stored": stored, "baselines": baselines,
        "notice": "Self-reported entry. Not a diagnosis or medical assessment.",
    }


@router.get("/checkins")
def list_checkins(request: Request, subject_id: Optional[str] = Query(None)):
    rows = request.app.state.repo.list_checkins(subject_id)
    return {"count": len(rows), "checkins": rows}
