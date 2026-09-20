from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut, AdvanceStageRequest
from app.services import stage_gate, health_calculator
from app.auth import get_current_user, require_role

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectOut)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    require_role(user, ["ai_analyst", "team_lead"])

    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)

    # seed default stage-gate checklist items for the new project
    stage_gate.seed_checklist_for_project(db, project.id)
    return project


@router.get("", response_model=list[ProjectOut])
def list_projects(
    stage: str | None = None,
    health: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Project)
    if stage:
        query = query.filter(Project.current_stage == stage)
    if health:
        query = query.filter(Project.health_status == health)
    return query.all()


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db),
):
    project = db.query(Project).get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


@router.get("/{project_id}/checklist")
def get_checklist(project_id: int, db: Session = Depends(get_db)):
    project = db.query(Project).get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return [
        {"id": c.id, "stage": c.stage, "criteria_text": c.criteria_text, "is_completed": c.is_completed}
        for c in project.checklist_items
        if c.stage == project.current_stage.value
    ]


@router.patch("/checklist/{item_id}/complete")
def complete_checklist_item(item_id: int, db: Session = Depends(get_db)):
    from app.models.stage import StageGateChecklist
    from datetime import datetime

    item = db.query(StageGateChecklist).get(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Checklist item not found")
    item.is_completed = True
    item.completed_at = datetime.utcnow()
    db.commit()
    return {"id": item.id, "is_completed": True}


@router.post("/{project_id}/advance-stage", response_model=ProjectOut)
def advance_stage(
    project_id: int,
    payload: AdvanceStageRequest,
    db: Session = Depends(get_db),
):
    try:
        return stage_gate.advance_stage(db, project_id, payload.moved_by, payload.notes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{project_id}/refresh-health")
def refresh_health(project_id: int, db: Session = Depends(get_db)):
    try:
        status = health_calculator.refresh_project_health(db, project_id)
        return {"project_id": project_id, "health_status": status}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
