from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db import Base


class StageHistory(Base):
    __tablename__ = "stage_history"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    from_stage = Column(String)
    to_stage = Column(String, nullable=False)
    moved_by = Column(Integer, ForeignKey("users.id"))
    moved_at = Column(DateTime, server_default=func.now())
    notes = Column(String)

    project = relationship("Project", back_populates="stage_history")


class StageGateChecklist(Base):
    __tablename__ = "stage_gate_checklist"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    stage = Column(String, nullable=False)
    criteria_text = Column(String, nullable=False)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="checklist_items")


# Default exit criteria per stage, seeded automatically when a project is created.
# Based directly on the assignment's "Stage Gates" section.
DEFAULT_STAGE_CRITERIA = {
    "discovery": [
        "Business problem documented",
        "Current process understood",
        "Users identified",
        "Expected outcome defined",
    ],
    "design": [
        "Requirements completed",
        "Workflow approved",
        "UI/UX or solution design completed",
        "Technical approach defined",
    ],
    "development": [
        "Required functionality developed",
        "Internal testing completed",
        "Major known bugs resolved",
    ],
    "uat": [
        "Business testing completed",
        "Feedback recorded",
        "Critical issues resolved",
        "Business approval received",
    ],
}
