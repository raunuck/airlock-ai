from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db, seed_registry
from app.routers.tasks import router as tasks_router

app = FastAPI(title="Sovereign Workbench API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for local prototype, tighten later
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()       # creates the tables if they don't exist yet
seed_registry()

app.include_router(tasks_router)


@app.get("/health")
def health():
    return {"status": "ok"}