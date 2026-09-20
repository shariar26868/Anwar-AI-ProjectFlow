# Anwar AI ProjectFlow — Backend Prototype

AI-focused project governance system backend, built for the Anwar Group candidate assignment.
FastAPI + SQLAlchemy with Groq-powered status parsing, dashboard narratives, and management queries.

## 1. Setup

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Load the `.env` file (e.g. via `python-dotenv` in `main.py`, or export the variables
in your shell) before running the app.

## 2. Database connection — how it works, and what's best

**Default: SQLite, zero setup.**
`app/db.py` reads a `DATABASE_URL` environment variable. If it isn't set, it falls
back to a local SQLite file:

```python
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./projectflow.db")
```

Nothing to install or configure — the first time you run the app, `projectflow.db`
is created automatically in the project folder. This is the right choice for this
prototype: no server to manage, and SQLAlchemy's ORM means switching databases
later needs zero query-code changes.

**Switching to Postgres later (recommended for actual production use):**

1. Run a Postgres instance (local Docker, or a managed service).
2. Set `DATABASE_URL` in `.env`:
   ```
   DATABASE_URL=postgresql://<user>:<password>@<host>:5432/<database_name>
   ```
3. Install the driver: `pip install psycopg2-binary`
4. That's it — no model or query code changes needed.

**Why Postgres for production, SQLite for prototype:** SQLite handles one writer
at a time well, which is fine for a single-developer demo but not for multiple
analysts/developers updating projects concurrently. Postgres handles concurrent
writes, has better indexing for larger `milestones`/`blockers` tables, and
supports proper multi-user access control. Because SQLAlchemy abstracts the DB
layer, this migration is a config change, not a rewrite.

## 3. Run the app

```bash
uvicorn main:app --reload
```

Visit `http://127.0.0.1:8000/docs` for interactive Swagger UI — every endpoint
can be tested directly from there.

The beginner-friendly browser guide with complete request and response examples
for every endpoint is available in [`API_EXAMPLES.md`](API_EXAMPLES.md).

## 4. Run with Docker

Make sure `.env` exists in the project root. Then run:

```bash
docker compose up --build
```

Open `http://127.0.0.1:8000/docs`. The SQLite database is stored in a Docker
named volume, so it survives container restarts. Stop the container with:

```bash
docker compose down
```

## 5. Run the prototype journey demo

Demonstrates the exact journey required by the assignment end-to-end (project
creation through closure, including a delayed milestone and a recorded blocker):

```bash
python -m app.seed
```

Then inspect the result via `/docs` — check `GET /projects/{id}`,
`GET /projects/{id}/checklist`, `GET /dashboard/summary`.

## 6. Project structure

```
main.py           - root FastAPI entrypoint
app/
  db.py            - DB connection/session (SQLite by default, Postgres-ready)
  auth.py          - simple header-based role simulation (prototype scope)
  models/          - SQLAlchemy models (core schema + additive AI tables)
  schemas/         - Pydantic request/response contracts
  services/        - business logic (health calculation, stage gates,
                      dashboard aggregation, AI helper) - kept separate from
                      routers so it's independently testable
  routers/         - HTTP layer only, delegates to services
  seed.py          - demo data + full prototype journey walkthrough
```

## 6. AI layer notes

The AI layer (`services/ai_helper.py`, `routers/updates.py`, `routers/dashboard.py`
query endpoint) is a first-class part of the project. It uses Groq's free
developer tier with `openai/gpt-oss-20b`, configured through `AI_API_KEY`,
`AI_BASE_URL`, and `AI_MODEL`. The health calculations, stage gates, and
blocker rules remain deterministic so governance decisions stay predictable;
AI is used for natural-language understanding and summaries.

AI never writes directly to project records — `POST /projects/{id}/updates`
stores a suggestion (`AIUpdateSuggestion`), and a human confirms it via
`PATCH /projects/updates/{id}/apply` before applying it to the real record.
