from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.milestone import Milestone, MilestoneStatus
from app.models.blocker import Blocker, ImpactEnum, ResolutionStatus
from app.models.project import Project, HealthEnum


def calculate_health(db: Session, project_id: int) -> HealthEnum:
    """
    Rule-based, deterministic health calculation - no manual override.
    Priority: blocked > delayed > at_risk > on_track.
    """
    open_high_blockers = (
        db.query(Blocker)
        .filter(
            Blocker.project_id == project_id,
            Blocker.resolution_status == ResolutionStatus.open,
            Blocker.impact == ImpactEnum.high,
        )
        .count()
    )
    if open_high_blockers > 0:
        return HealthEnum.blocked

    overdue_milestones = (
        db.query(Milestone)
        .filter(
            Milestone.project_id == project_id,
            Milestone.due_date < date.today(),
            Milestone.status != MilestoneStatus.completed,
        )
        .count()
    )
    if overdue_milestones > 0:
        return HealthEnum.delayed

    upcoming_risky = (
        db.query(Milestone)
        .filter(
            Milestone.project_id == project_id,
            Milestone.status == MilestoneStatus.in_progress,
            Milestone.due_date <= date.today() + timedelta(days=3),
        )
        .count()
    )
    if upcoming_risky > 0:
        return HealthEnum.at_risk

    return HealthEnum.on_track


def refresh_project_health(db: Session, project_id: int) -> HealthEnum:
    project = db.query(Project).get(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")
    project.health_status = calculate_health(db, project_id)
    db.commit()
    db.refresh(project)
    return project.health_status
