from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.project import StageEnum, HealthEnum


class ProjectCreate(BaseModel):
    name: str
    business_unit: Optional[str] = None
    department: Optional[str] = None
    business_problem: Optional[str] = None
    expected_outcome: Optional[str] = None
    owner_id: Optional[int] = None
    ai_analyst_id: Optional[int] = None
    developer_id: Optional[int] = None
    expected_delivery_date: Optional[date] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    business_problem: Optional[str] = None
    expected_outcome: Optional[str] = None
    owner_id: Optional[int] = None
    ai_analyst_id: Optional[int] = None
    developer_id: Optional[int] = None
    expected_delivery_date: Optional[date] = None
    overall_progress: Optional[float] = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    business_unit: Optional[str]
    department: Optional[str]
    business_problem: Optional[str]
    expected_outcome: Optional[str]
    owner_id: Optional[int]
    ai_analyst_id: Optional[int]
    developer_id: Optional[int]
    current_stage: StageEnum
    health_status: HealthEnum
    expected_delivery_date: Optional[date]
    overall_progress: float
    created_at: Optional[datetime]
    updated_at: Optional[datetime]


class AdvanceStageRequest(BaseModel):
    moved_by: int
    notes: Optional[str] = None
