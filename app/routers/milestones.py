from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.milestone import Milestone, Task
from app.schemas.milestone import (
    MilestoneCreate, MilestoneUpdate, MilestoneOut,
    TaskCreate, TaskUpdate, TaskOut,
)
from app.services.health_calculator import refresh_project_health

router = APIRouter(tags=["milestones"])


@router.post("/milestones", response_model=MilestoneOut)
def create_milestone(payload: MilestoneCreate, db: Session = Depends(get_db)):
    milestone = Milestone(**payload.model_dump())
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    refresh_project_health(db, milestone.project_id)
    return milestone


@router.get("/projects/{project_id}/milestones", response_model=list[MilestoneOut])
def list_milestones(project_id: int, db: Session = Depends(get_db)):
    return db.query(Milestone).filter(Milestone.project_id == project_id).all()


@router.patch("/milestones/{milestone_id}", response_model=MilestoneOut)
def update_milestone(milestone_id: int, payload: MilestoneUpdate, db: Session = Depends(get_db)):
    milestone = db.query(Milestone).get(milestone_id)
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(milestone, field, value)

    db.commit()
    db.refresh(milestone)
    # health status depends on milestone state -> recalculate every time it changes
    refresh_project_health(db, milestone.project_id)
    return milestone


@router.post("/tasks", response_model=TaskOut)
def create_task(payload: TaskCreate, db: Session = Depends(get_db)):
    task = Task(**payload.model_dump())
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(Task).get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task
