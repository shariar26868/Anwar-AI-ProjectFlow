import enum
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db import Base


class MilestoneStatus(str, enum.Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"
    delayed = "delayed"


class TaskStatus(str, enum.Enum):
    not_started = "not_started"
    in_progress = "in_progress"
    completed = "completed"


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    due_date = Column(Date, nullable=False)
    status = Column(Enum(MilestoneStatus), default=MilestoneStatus.not_started)
    related_stage = Column(String)

    project = relationship("Project", back_populates="milestones")
    tasks = relationship("Task", back_populates="milestone", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=True)
    action = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    deadline = Column(Date)
    status = Column(Enum(TaskStatus), default=TaskStatus.not_started)

    milestone = relationship("Milestone", back_populates="tasks")
