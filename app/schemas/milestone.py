from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.milestone import MilestoneStatus, TaskStatus


class MilestoneCreate(BaseModel):
    project_id: int
    name: str
    owner_id: Optional[int] = None
    due_date: date
    related_stage: Optional[str] = None


class MilestoneUpdate(BaseModel):
    name: Optional[str] = None
    owner_id: Optional[int] = None
    due_date: Optional[date] = None
    status: Optional[MilestoneStatus] = None


class MilestoneOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    name: str
    owner_id: Optional[int]
    due_date: date
    status: MilestoneStatus
    related_stage: Optional[str]


class TaskCreate(BaseModel):
    project_id: int
    milestone_id: Optional[int] = None
    action: str
    owner_id: Optional[int] = None
    deadline: Optional[date] = None


class TaskUpdate(BaseModel):
    action: Optional[str] = None
    owner_id: Optional[int] = None
    deadline: Optional[date] = None
    status: Optional[TaskStatus] = None


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    project_id: int
    milestone_id: Optional[int]
    action: str
    owner_id: Optional[int]
    deadline: Optional[date]
    status: TaskStatus
