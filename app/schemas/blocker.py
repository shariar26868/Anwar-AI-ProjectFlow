from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.blocker import ImpactEnum, ResolutionStatus, DelayReasonEnum


class BlockerCreate(BaseModel):
    project_id: int
    description: str
    responsible_person_id: Optional[int] = None
    impact: ImpactEnum = ImpactEnum.medium
    required_action: Optional[str] = None
    delay_reason_category: Optional[DelayReasonEnum] = None


class BlockerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    description: str
    responsible_person_id: Optional[int]
    date_identified: Optional[date]
    impact: ImpactEnum
    required_action: Optional[str]
    resolution_status: ResolutionStatus
    delay_reason_category: Optional[DelayReasonEnum]
    resolved_at: Optional[datetime]


class ScopeChangeCreate(BaseModel):
    project_id: int
    requested_by: int
    reason: str
    impact_on_delivery: Optional[str] = None
