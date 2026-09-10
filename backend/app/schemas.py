from typing import Optional
from pydantic import BaseModel

class TaskRequest(BaseModel):
    prompt: str
    previous_task_type: Optional[str] = None

class TaskResponse(BaseModel):
    model_used: str
    task_type: str
    response: str
    sources: list[str] | None = None