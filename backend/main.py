from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.db import init_db, seed_registry
from app.routers.tasks import router as tasks_router
from app.routers.sessions import router as sessions_router

BASE_DIR = Path(__file__).resolve().parent
OUTPUTS_DIR = BASE_DIR / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

app = FastAPI(title="Sovereign Workbench API")
app.include_router(sessions_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for local prototype, tighten later
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()       # creates the tables if they don't exist yet
seed_registry()

app.include_router(tasks_router)
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")


@app.get("/health")
def health():
    return {"status": "ok"}