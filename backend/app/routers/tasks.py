from fastapi import APIRouter, HTTPException, Header
from app.schemas import TaskRequest, TaskResponse
from app.db import (
    log_task, log_rag_query, get_model_for_task,
    create_session, add_message, maybe_set_title,
    get_connection
)
from app.classifier import classify_task
from rag.retrieval import answer_rag_query
from llm_client import prompt as llm_prompt
from agent.agentloop import run_agent

router = APIRouter()

GENERAL_SYSTEM_PROMPT = "You are a helpful industrial assistant. Always respond in English unless the user explicitly requests another language."

TASK_TYPES_NEEDING_AGENT = {"code", "document"}

@router.post("/task", response_model=TaskResponse)
def handle_task(req: TaskRequest, user_id: str | None = Header(None)):
    if not user_id or user_id == "undefined":
        conn = get_connection()
        default_user = conn.execute("SELECT id FROM users LIMIT 1").fetchone()
        if default_user:
            user_id = default_user["id"]
        else:
            conn.close()
            raise HTTPException(status_code=400, detail="No user found. Please register or log in.")
        conn.close()

    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    session_id = req.session_id or create_session(user_id)
    maybe_set_title(session_id, req.prompt)
    add_message(session_id, "user", req.prompt, attachment_path=req.attachment_path)

    # Force image task classification if an image file attachment is provided
    task_type = req.previous_task_type
    if req.attachment_path and any(req.attachment_path.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".webp"]):
        task_type = "image"
    else:
        task_type = classify_task(req.prompt, req.previous_task_type)

    images_list = [req.attachment_path] if req.attachment_path else None

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
        model_used = get_model_for_task(task_type if task_type in ["image", "code", "document"] else "general")
        try:
            result = llm_prompt(
                text=req.prompt,
                model_key=task_type if task_type in ["image", "code", "document"] else model_used,
                system=GENERAL_SYSTEM_PROMPT,
                images=images_list
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM query failed: {e}")

        response_text = result["content"]
        model_used = result.get("model", model_used)
        sources = None
        log_task(task_type, model_used, req.prompt, response_text)

    add_message(session_id, "assistant", response_text, task_type, model_used, sources)

    return TaskResponse(
        model_used=model_used,
        task_type=task_type,
        response=response_text,
        sources=sources,
        session_id=session_id,
    )