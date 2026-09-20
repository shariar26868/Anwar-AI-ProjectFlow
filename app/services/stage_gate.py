from sqlalchemy.orm import Session
from app.models.stage import StageHistory, StageGateChecklist, DEFAULT_STAGE_CRITERIA
from app.models.project import Project, StageEnum

STAGE_ORDER = [s.value for s in StageEnum]


def seed_checklist_for_project(db: Session, project_id: int):
    """Called once at project creation - inserts default exit criteria for every gated stage."""
    for stage, criteria_list in DEFAULT_STAGE_CRITERIA.items():
        for text in criteria_list:
            db.add(
                StageGateChecklist(project_id=project_id, stage=stage, criteria_text=text)
            )
    db.commit()


def get_incomplete_criteria(db: Session, project_id: int, stage: str):
    return (
        db.query(StageGateChecklist)
        .filter(
            StageGateChecklist.project_id == project_id,
            StageGateChecklist.stage == stage,
            StageGateChecklist.is_completed.is_(False),
        )
        .all()
    )


def advance_stage(db: Session, project_id: int, moved_by: int, notes: str = None) -> Project:
    project = db.query(Project).get(project_id)
    if not project:
        raise ValueError(f"Project {project_id} not found")

    current_stage_value = project.current_stage.value
    incomplete = get_incomplete_criteria(db, project_id, current_stage_value)
    if incomplete:
        missing = ", ".join(c.criteria_text for c in incomplete)
        raise ValueError(
            f"Cannot advance from '{current_stage_value}'. "
            f"{len(incomplete)} checklist item(s) incomplete: {missing}"
        )

    current_idx = STAGE_ORDER.index(current_stage_value)
    if current_idx + 1 >= len(STAGE_ORDER):
        raise ValueError("Project is already at the final stage")

    next_stage = STAGE_ORDER[current_idx + 1]

    db.add(
        StageHistory(
            project_id=project_id,
            from_stage=current_stage_value,
            to_stage=next_stage,
            moved_by=moved_by,
            notes=notes,
        )
    )
    project.current_stage = next_stage
    db.commit()
    db.refresh(project)
    return project
