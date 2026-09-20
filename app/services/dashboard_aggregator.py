from datetime import date, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.project import Project, HealthEnum, StageEnum
from app.models.milestone import Milestone, MilestoneStatus
from app.models.blocker import Blocker, ResolutionStatus


def get_summary(db: Session) -> dict:
    total_active = db.query(Project).filter(Project.current_stage != StageEnum.completed).count()

    by_stage = dict(
        db.query(Project.current_stage, func.count(Project.id))
        .group_by(Project.current_stage)
        .all()
    )
    by_stage = {k.value if hasattr(k, "value") else k: v for k, v in by_stage.items()}

    by_health = dict(
        db.query(Project.health_status, func.count(Project.id))
        .group_by(Project.health_status)
        .all()
    )
    by_health = {k.value if hasattr(k, "value") else k: v for k, v in by_health.items()}

    month_end = date.today().replace(day=28) + timedelta(days=4)
    month_end = month_end - timedelta(days=month_end.day)
    expected_this_month = (
        db.query(Project)
        .filter(
            Project.expected_delivery_date >= date.today(),
            Project.expected_delivery_date <= month_end,
        )
        .count()
    )

    overdue_milestones = (
        db.query(Milestone)
        .filter(Milestone.due_date < date.today(), Milestone.status != MilestoneStatus.completed)
        .count()
    )

    upcoming_milestones = (
        db.query(Milestone)
        .filter(
            Milestone.due_date >= date.today(),
            Milestone.due_date <= date.today() + timedelta(days=7),
            Milestone.status != MilestoneStatus.completed,
        )
        .count()
    )

    open_blockers = db.query(Blocker).filter(Blocker.resolution_status == ResolutionStatus.open).count()

    analyst_workload = dict(
        db.query(Project.ai_analyst_id, func.count(Project.id))
        .filter(Project.current_stage != StageEnum.completed)
        .group_by(Project.ai_analyst_id)
        .all()
    )

    developer_workload = dict(
        db.query(Project.developer_id, func.count(Project.id))
        .filter(Project.current_stage != StageEnum.completed)
        .group_by(Project.developer_id)
        .all()
    )

    return {
        "total_active_projects": total_active,
        "projects_by_stage": by_stage,
        "projects_by_health": by_health,
        "expected_delivery_this_month": expected_this_month,
        "overdue_milestones": overdue_milestones,
        "upcoming_milestones_7_days": upcoming_milestones,
        "open_blockers": open_blockers,
        "ai_analyst_workload": analyst_workload,
        "developer_workload": developer_workload,
    }
