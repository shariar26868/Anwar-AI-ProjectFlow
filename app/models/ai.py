from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.db import Base


class AIUpdateSuggestion(Base):
    """
    Stores LLM-parsed structure from a free-text project update.
    The AI only suggests here -- it never writes directly to Project/Milestone.
    A human (analyst) reviews and confirms before `applied` is set True and
    the real record is updated.
    """
    __tablename__ = "ai_update_suggestions"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    submitted_by = Column(Integer, ForeignKey("users.id"))
    raw_text = Column(String, nullable=False)
    parsed_progress_percent = Column(String)
    parsed_blocker_detected = Column(Boolean, default=False)
    parsed_delay_reason = Column(String, nullable=True)
    parsed_risk_signal = Column(String, default="none")
    applied = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    project = relationship("Project", back_populates="ai_suggestions")


class AIQueryLog(Base):
    """Audit trail of natural-language dashboard queries and AI responses."""
    __tablename__ = "ai_query_logs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    query_text = Column(String, nullable=False)
    generated_response = Column(String)
    created_at = Column(DateTime, server_default=func.now())
