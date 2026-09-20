"""
Demonstrates the exact prototype journey required by the assignment:
New project created -> AI analyst assigned -> Discovery completed -> Design approved ->
Development starts -> Milestone becomes delayed -> Blocker recorded -> Development completed ->
UAT approved -> Project deployed -> Project closed.

Run with: python -m app.seed
"""
from datetime import date, timedelta
from app.db import SessionLocal, Base, engine
from app.models.user import User, RoleEnum
from app.models.project import Project
from app.models.milestone import Milestone, MilestoneStatus
from app.models.blocker import Blocker, ImpactEnum, DelayReasonEnum, ResolutionStatus
from app.services import stage_gate, health_calculator

Base.metadata.create_all(bind=engine)
db = SessionLocal()

print("1. Creating users...")
analyst = User(name="Rafi", email="rafi@anwargroup.net", role=RoleEnum.ai_analyst, department="AI Team")
developer = User(name="Shaikat", email="shaikat@anwargroup.net", role=RoleEnum.developer, department="AI Team")
owner = User(name="Nusrat", email="nusrat@anwargroup.net", role=RoleEnum.business_owner, department="Operations")
db.add_all([analyst, developer, owner])
db.commit()
db.refresh(analyst); db.refresh(developer); db.refresh(owner)

print("2. Creating project (Idea stage) + assigning AI analyst...")
project = Project(
    name="Demand Forecasting Assistant",
    business_unit="Retail",
    department="Operations",
    business_problem="Manual demand forecasting is slow and error-prone.",
    expected_outcome="Automated weekly demand forecast per SKU.",
    owner_id=owner.id,
    ai_analyst_id=analyst.id,
    developer_id=developer.id,
    expected_delivery_date=date.today() + timedelta(days=30),
)
db.add(project)
db.commit()
db.refresh(project)
stage_gate.seed_checklist_for_project(db, project.id)
print(f"   Project #{project.id} created at stage: {project.current_stage.value}")

print("3. Completing Discovery checklist...")
from app.models.stage import StageGateChecklist
discovery_items = db.query(StageGateChecklist).filter_by(project_id=project.id, stage="discovery").all()
for item in discovery_items:
    item.is_completed = True
db.commit()
project = stage_gate.advance_stage(db, project.id, moved_by=analyst.id, notes="Discovery complete")
print(f"   Advanced to: {project.current_stage.value}")

print("4. Completing Design checklist -> Approval...")
design_items = db.query(StageGateChecklist).filter_by(project_id=project.id, stage="design").all()
for item in design_items:
    item.is_completed = True
db.commit()
project = stage_gate.advance_stage(db, project.id, moved_by=analyst.id, notes="Design approved")
print(f"   Advanced to: {project.current_stage.value}")

print("5. Approval -> Development starts...")
project = stage_gate.advance_stage(db, project.id, moved_by=owner.id, notes="Scope approved by business owner")
print(f"   Advanced to: {project.current_stage.value}")

print("6. Creating a milestone that becomes delayed...")
milestone = Milestone(
    project_id=project.id,
    name="Core forecasting model built",
    owner_id=developer.id,
    due_date=date.today() - timedelta(days=2),  # already overdue
    status=MilestoneStatus.in_progress,
    related_stage="development",
)
db.add(milestone)
db.commit()
health_calculator.refresh_project_health(db, project.id)
db.refresh(project)
print(f"   Health auto-recalculated -> {project.health_status.value}")

print("7. Recording a blocker...")
blocker = Blocker(
    project_id=project.id,
    description="Waiting on historical sales data export from Finance",
    responsible_person_id=developer.id,
    impact=ImpactEnum.high,
    required_action="Escalate to Finance data owner",
    delay_reason_category=DelayReasonEnum.data_unavailable,
)
db.add(blocker)
db.commit()
health_calculator.refresh_project_health(db, project.id)
db.refresh(project)
print(f"   Health auto-recalculated -> {project.health_status.value} (expected: blocked)")

print("8. Resolving blocker + completing milestone + Development checklist...")
blocker.resolution_status = ResolutionStatus.resolved
milestone.status = MilestoneStatus.completed
dev_items = db.query(StageGateChecklist).filter_by(project_id=project.id, stage="development").all()
for item in dev_items:
    item.is_completed = True
db.commit()
health_calculator.refresh_project_health(db, project.id)
project = stage_gate.advance_stage(db, project.id, moved_by=developer.id, notes="Development complete")
print(f"   Advanced to: {project.current_stage.value}")

print("9. Internal Testing -> UAT...")
project = stage_gate.advance_stage(db, project.id, moved_by=developer.id, notes="Internal testing passed")
uat_items = db.query(StageGateChecklist).filter_by(project_id=project.id, stage="uat").all()
for item in uat_items:
    item.is_completed = True
db.commit()
project = stage_gate.advance_stage(db, project.id, moved_by=owner.id, notes="UAT approved by business owner")
print(f"   Advanced to: {project.current_stage.value}")

print("10. Deployment -> Stabilization -> Completed...")
project = stage_gate.advance_stage(db, project.id, moved_by=developer.id, notes="Deployed to production")
print(f"    Advanced to: {project.current_stage.value}")
project = stage_gate.advance_stage(db, project.id, moved_by=analyst.id, notes="No major post-launch issues")
print(f"    Advanced to: {project.current_stage.value}")

print(f"\nDone. Final stage: {project.current_stage.value}, final health: {project.health_status.value}")
db.close()
