from fastapi import APIRouter, HTTPException
from app.schemas import TaskRequest, TaskResponse
from app.db import log_task, log_rag_query, get_model_for_task
from app.classifier import classify_task
from rag.retrieval import answer_rag_query
from llm_client import prompt as llm_prompt
from agent.agentloop import run_agent

router = APIRouter()

GENERAL_SYSTEM_PROMPT = "You are a helpful industrial assistant. Always respond in English unless the user explicitly requests another language."

TASK_TYPES_NEEDING_AGENT = {"code", "document"}

@router.post("/task", response_model=TaskResponse)
def handle_task(req: TaskRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    task_type = classify_task(req.prompt, req.previous_task_type)

    if task_type == "rag_query":
        try:
            rag_result = answer_rag_query(req.prompt)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"RAG query failed: {e}")

        response_text = rag_result["answer"]
        model_used = rag_result.get("model_used") or get_model_for_task("rag_query")
        sources = rag_result.get("sources") or []
        log_rag_query(req.prompt, sources, response_text)

    elif task_type in TASK_TYPES_NEEDING_AGENT:
        model_used = get_model_for_task(task_type)
        try:
            agent_result = run_agent(req.prompt, model_key=model_used)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Agent task failed: {e}")

        response_text = agent_result.get("answer", str(agent_result))
        sources = None
        log_task(task_type, model_used, req.prompt, response_text)

    else:
        model_used = get_model_for_task(task_type)
        try:
            result = llm_prompt(req.prompt, model_key=model_used, system=GENERAL_SYSTEM_PROMPT)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM query failed: {e}")

        response_text = result["content"]
        model_used = result.get("model", model_used)
        sources = None
        log_task(task_type, model_used, req.prompt, response_text)

    return TaskResponse(
        model_used=model_used,
        task_type=task_type,
        response=response_text,
        sources=sources,
    )