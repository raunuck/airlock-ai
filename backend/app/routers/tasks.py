from fastapi import APIRouter
from app.schemas import TaskRequest, TaskResponse
from app.db import log_task

router = APIRouter()

@router.post("/task", response_model=TaskResponse)
def handle_task(req: TaskRequest):
    # TODO: replace with real classifier + model call
    task_type = "document"
    model_used = "qwen2.5:7b"
    response_text = f"(placeholder) received: {req.prompt}"

    log_task(task_type, model_used, req.prompt, response_text)

    return TaskResponse(model_used=model_used, task_type=task_type, response=response_text)