from fastapi import APIRouter
from app.schemas import TaskRequest, TaskResponse
from app.db import log_rag_query
from rag.retrieval import answer_rag_query

router = APIRouter()

@router.post("/rag", response_model=TaskResponse)
def handle_rag(req: TaskRequest):
    result = answer_rag_query(req.prompt)

    log_rag_query(req.prompt, result["sources"], result["answer"])

    return TaskResponse(
        model_used=result["model_used"] or "none",
        task_type="rag_query",
        response=result["answer"],
        sources=result["sources"],
    )