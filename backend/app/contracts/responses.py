"""Common API response (status, severity_basis, reasons, ...).

Owner: Member 6 (Backend, Integration, QA & Deployment)

Every analytics answer the API returns is a `BaselineResponse`. Extra analytics fields
(reference_count, reference_band, ...) pass through untouched so a Member 2 change never
needs a contract change here. Mirrors shared/schemas/api-response.schema.json.
"""

from typing import Any, List, Literal, Optional

from pydantic import BaseModel, ConfigDict


class BaselineResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    subject_id: str
    measurement: str
    source_id: Optional[str] = None
    study_id: Optional[str] = None
    provenance_kind: Optional[str] = None
    units: Optional[str] = None
    status: str
    quality_state: str
    reasons: List[str]
    severity_basis: str
    not_medical_diagnosis: Literal[True]
    current_value: Optional[float] = None
    baseline_value: Optional[float] = None
    robust_z: Optional[float] = None
    history_count: int = 0
    rejected_history_count: int = 0


class ObservationList(BaseModel):
    count: int
    observations: List[dict]


class CheckinStored(BaseModel):
    record_id: str
    subject_id: str
    observations_stored: int
    baselines: List[BaselineResponse]
    notice: str = "Self-reported entry. Not a diagnosis or medical assessment."


class Health(BaseModel):
    status: Literal["ok"]
    storage: str
    observations: int
    checkins: int
    contains_real_astronaut_data: Literal[False] = False


class ErrorBody(BaseModel):
    error: str
    detail: Any = None
