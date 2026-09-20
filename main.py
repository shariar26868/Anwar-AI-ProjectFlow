from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv(override=True)

from app.db import Base, engine
from app import models  # noqa: F401 - ensures all models are registered on Base
from app.routers import projects, milestones, blockers, dashboard, updates

Base.metadata.create_all(bind=engine)

app = FastAPI(
	title="Anwar AI ProjectFlow",
	description="AI project governance system - candidate assignment prototype",
	version="0.1.0",
)

app.include_router(projects.router)
app.include_router(milestones.router)
app.include_router(blockers.router)
app.include_router(dashboard.router)
app.include_router(updates.router)


@app.get("/")
def root():
	return {"status": "ok", "service": "Anwar AI ProjectFlow API"}

__all__ = ["app"]