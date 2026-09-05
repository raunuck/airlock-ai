from fastapi import APIRouter, HTTPException
from app.schemas import TaskRequest, TaskResponse
from app.db import log_task
from app.classifier import classify_task
from rag.retrieval import answer_rag_query
from llm_client import prompt as llm_prompt

router = APIRouter()

TASK_TO_MODEL_KEY = {
    "code": "coding",
    "document": "general",
    "rag_query": "general",
}

@router.post("/task", response_model=TaskResponse)
def handle_task(req: TaskRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    task_type = classify_task(req.prompt)

    if task_type == "rag_query":
        try:
            rag_result = answer_rag_query(req.prompt)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"RAG query failed: {e}")

        response_text = rag_result["answer"]
        model_used = rag_result.get("model_used") or "rag-pipeline"   # fixed key
        sources = rag_result.get("sources") or []                    # no longer dropped
    else:
        model_key = TASK_TO_MODEL_KEY.get(task_type, "general")
        try:
            result = llm_prompt(req.prompt, model_key=model_key)
        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

        response_text = result["content"]
        model_used = result["model"]
        sources = None

    log_task(task_type, model_used, req.prompt, response_text)

    return TaskResponse(
        model_used=model_used,
        task_type=task_type,
        response=response_text,
        sources=sources,
    )