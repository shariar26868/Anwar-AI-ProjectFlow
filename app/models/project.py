import enum
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
from app.db import Base


class StageEnum(str, enum.Enum):
    idea = "idea"
    discovery = "discovery"
    design = "design"
    approval = "approval"
    development = "development"
    internal_testing = "internal_testing"
    uat = "uat"
    deployment = "deployment"
    stabilization = "stabilization"
    completed = "completed"


class HealthEnum(str, enum.Enum):
    on_track = "on_track"
    at_risk = "at_risk"
    delayed = "delayed"
    blocked = "blocked"


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    business_unit = Column(String)
    department = Column(String)
    business_problem = Column(String)
    expected_outcome = Column(String)

    owner_id = Column(Integer, ForeignKey("users.id"))
    ai_analyst_id = Column(Integer, ForeignKey("users.id"))
    developer_id = Column(Integer, ForeignKey("users.id"))

    current_stage = Column(Enum(StageEnum), default=StageEnum.idea, nullable=False)
    health_status = Column(Enum(HealthEnum), default=HealthEnum.on_track, nullable=False)
    expected_delivery_date = Column(Date)
    overall_progress = Column(Float, default=0.0)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    milestones = relationship("Milestone", back_populates="project", cascade="all, delete-orphan")
    blockers = relationship("Blocker", back_populates="project", cascade="all, delete-orphan")
    checklist_items = relationship("StageGateChecklist", back_populates="project", cascade="all, delete-orphan")
    stage_history = relationship("StageHistory", back_populates="project", cascade="all, delete-orphan")
    scope_changes = relationship("ScopeChange", back_populates="project", cascade="all, delete-orphan")
    ai_suggestions = relationship("AIUpdateSuggestion", back_populates="project", cascade="all, delete-orphan")
