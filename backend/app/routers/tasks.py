from fastapi import APIRouter, HTTPException
from backend.app.schemas import TaskRequest, TaskResponse
from backend.app.db import log_task
from backend.app.classifier import classify_task
from backend.llm_client import prompt as llm_prompt

router = APIRouter()

TASK_TO_MODEL_KEY = {
    "code": "coding",
    "document": "general",
    "rag_query": "general",  # TODO Day 3: route to real RAG pipeline instead of plain chat

}

@router.post("/task", response_model=TaskResponse)
def handle_task(req: TaskRequest):
    task_type = classify_task(req.prompt)
    model_key = TASK_TO_MODEL_KEY.get(task_type, "general")

    try:
        result = llm_prompt(req.prompt, model_key=model_key)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    response_text = result["content"]
    model_used = result["model"]  # real model name, e.g. "qwen2.5-coder:7b"

    log_task(task_type, model_used, req.prompt, response_text)

    return TaskResponse(model_used=model_used, task_type=task_type, response=response_text)