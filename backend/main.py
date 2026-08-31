from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db import init_db,seed_registry
from app.routers.tasks import router as tasks_router
from pydantic import BaseModel

app = FastAPI(title="Sovereign Workbench API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for local prototype, tighten later
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()  # creates the tables if they don't exist yet
seed_registry()
app.include_router(tasks_router)

class TaskRequest(BaseModel):
    prompt: str

@app.post("/task")
def handle_task(req: TaskRequest):
    # Placeholder — Raunak's router + Arya's model client plug in here Day 2
    return {"model_used": "placeholder-model", "response": f"Echo: {req.prompt}"}

@app.get("/health")
def health():
    return {"status": "ok"}