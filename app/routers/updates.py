from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.ai import AIUpdateSuggestion
from app.services.ai_helper import parse_status_update

router = APIRouter(prefix="/projects", tags=["ai-updates"])


@router.post("/{project_id}/updates")
def submit_status_update(project_id: int, update_text: str, submitted_by: int, db: Session = Depends(get_db)):
    """
    Accepts a free-text update, asks the LLM to structure it, and stores the
    result as a SUGGESTION only. Nothing is written to Project/Milestone here -
    a human must review and call /suggestions/{id}/apply to confirm it.
    """
    parsed = parse_status_update(update_text)

    suggestion = AIUpdateSuggestion(
        project_id=project_id,
        submitted_by=submitted_by,
        raw_text=update_text,
        parsed_progress_percent=str(parsed.get("progress_percent")),
        parsed_blocker_detected=parsed.get("blocker_detected", False),
        parsed_delay_reason=parsed.get("suggested_delay_reason"),
        parsed_risk_signal=parsed.get("risk_signal", "none"),
    )
    db.add(suggestion)
    db.commit()
    db.refresh(suggestion)

    return {
        "suggestion_id": suggestion.id,
        "parsed": parsed,
        "note": "Suggestion stored. Review and confirm before it affects the project record.",
    }


@router.get("/{project_id}/updates")
def list_suggestions(project_id: int, db: Session = Depends(get_db)):
    return (
        db.query(AIUpdateSuggestion)
        .filter(AIUpdateSuggestion.project_id == project_id)
        .order_by(AIUpdateSuggestion.created_at.desc())
        .all()
    )


@router.patch("/updates/{suggestion_id}/apply")
def apply_suggestion(suggestion_id: int, db: Session = Depends(get_db)):
    """
    Human-confirmed step: marks the suggestion applied. Actual field updates
    to Project/Milestone should be done explicitly via their own PATCH
    endpoints by the analyst reviewing this suggestion - keeps AI advisory,
    not autonomous.
    """
    suggestion = db.query(AIUpdateSuggestion).get(suggestion_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    suggestion.applied = True
    db.commit()
    return {"id": suggestion.id, "applied": True}
