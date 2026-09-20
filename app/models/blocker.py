import enum
from datetime import date as date_cls
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Enum, func
from sqlalchemy.orm import relationship
from app.db import Base


class ImpactEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ResolutionStatus(str, enum.Enum):
    open = "open"
    resolved = "resolved"


class DelayReasonEnum(str, enum.Enum):
    requirements_not_finalized = "requirements_not_finalized"
    resource_unavailable = "resource_unavailable"
    waiting_business_feedback = "waiting_business_feedback"
    scope_change = "scope_change"
    data_unavailable = "data_unavailable"
    testing_issue = "testing_issue"
    development_issue = "development_issue"
    approval_pending = "approval_pending"
    integration_dependency = "integration_dependency"
    other = "other"


class Blocker(Base):
    __tablename__ = "blockers"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    description = Column(String, nullable=False)
    responsible_person_id = Column(Integer, ForeignKey("users.id"))
    date_identified = Column(Date, default=date_cls.today)
    impact = Column(Enum(ImpactEnum), default=ImpactEnum.medium)
    required_action = Column(String)
    resolution_status = Column(Enum(ResolutionStatus), default=ResolutionStatus.open)
    delay_reason_category = Column(Enum(DelayReasonEnum))
    resolved_at = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="blockers")


class ScopeChange(Base):
    __tablename__ = "scope_changes"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    requested_by = Column(Integer, ForeignKey("users.id"))
    reason = Column(String, nullable=False)
    impact_on_delivery = Column(String)
    created_at = Column(DateTime, server_default=func.now())

    project = relationship("Project", back_populates="scope_changes")
