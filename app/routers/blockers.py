from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.blocker import Blocker, ScopeChange, ResolutionStatus
from app.schemas.blocker import BlockerCreate, BlockerOut, ScopeChangeCreate
from app.services.health_calculator import refresh_project_health

router = APIRouter(tags=["blockers"])


@router.post("/blockers", response_model=BlockerOut)
def create_blocker(payload: BlockerCreate, db: Session = Depends(get_db)):
    blocker = Blocker(**payload.model_dump())
    db.add(blocker)
    db.commit()
    db.refresh(blocker)
    refresh_project_health(db, blocker.project_id)
    return blocker


@router.get("/projects/{project_id}/blockers", response_model=list[BlockerOut])
def list_blockers(project_id: int, db: Session = Depends(get_db)):
    return db.query(Blocker).filter(Blocker.project_id == project_id).all()


@router.patch("/blockers/{blocker_id}/resolve", response_model=BlockerOut)
def resolve_blocker(blocker_id: int, db: Session = Depends(get_db)):
    blocker = db.query(Blocker).get(blocker_id)
    if not blocker:
        raise HTTPException(status_code=404, detail="Blocker not found")

    blocker.resolution_status = ResolutionStatus.resolved
    blocker.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(blocker)
    refresh_project_health(db, blocker.project_id)
    return blocker


@router.post("/scope-changes")
def create_scope_change(payload: ScopeChangeCreate, db: Session = Depends(get_db)):
    scope_change = ScopeChange(**payload.model_dump())
    db.add(scope_change)
    db.commit()
    db.refresh(scope_change)
    return {
        "id": scope_change.id,
        "project_id": scope_change.project_id,
        "reason": scope_change.reason,
        "impact_on_delivery": scope_change.impact_on_delivery,
    }
