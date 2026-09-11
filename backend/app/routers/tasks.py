from pathlib import Path
from fastapi import APIRouter, HTTPException, Header
from app.schemas import TaskRequest, TaskResponse
from app.db import (
    log_task, log_rag_query, get_model_for_task,
    create_session, add_message, maybe_set_title,
    get_session_history_for_llm, get_connection
)
from app.classifier import classify_task
from app.tools.ocr import BASE_DIR
from app.tools.docextract import extract_file_content
from rag.retrieval import answer_rag_query
from llm_client import chat as llm_chat
from agent.agentloop import run_agent

router = APIRouter()

GENERAL_SYSTEM_PROMPT = "You are a helpful industrial assistant. Always respond in English unless the user explicitly requests another language."
DOCUMENT_SYSTEM_PROMPT = "You are a helpful industrial assistant. You are analyzing text extracted from an uploaded document or image. Answer the user's question accurately, concisely, and directly. Always respond in English unless the user explicitly requests another language."

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif", ".gif"}

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

    raw_prompt = req.prompt.strip()
    if not raw_prompt and not req.attachment_path:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    has_attachment = bool(req.attachment_path)
    is_image = bool(
        req.attachment_path and any(req.attachment_path.lower().endswith(ext) for ext in IMAGE_EXTENSIONS)
    )

    prompt_text = raw_prompt or (
        "Extract and transcribe all text from this image." if is_image else "Summarize and analyze the contents of this attached file."
    )

    session_id = req.session_id or create_session(user_id)
    history = get_session_history_for_llm(session_id, limit=6)
    maybe_set_title(session_id, prompt_text)
    add_message(session_id, "user", prompt_text, attachment_path=req.attachment_path)

    # Determine task type
    if is_image:
        task_type = "image"
    elif has_attachment:
        task_type = "document"
    else:
        task_type = classify_task(prompt_text, req.previous_task_type)

    if has_attachment:
        # Extract content from uploaded attachment (docx, pdf, image OCR, text)
        extracted_type, file_content = extract_file_content(req.attachment_path)
        model_used = get_model_for_task(task_type)

        header_label = "Tesseract OCR Extracted Text from Image" if is_image else "Uploaded Document Content"
        augmented_prompt = (
            f"--- [{header_label}] ---\n"
            f"{file_content}\n"
            f"-----------------------------\n\n"
            f"User Request: {prompt_text}"
        )

        chat_messages = list(history) + [{"role": "user", "content": augmented_prompt}]

        try:
            result = llm_chat(
                messages=chat_messages,
                model_key=model_used,
                system=DOCUMENT_SYSTEM_PROMPT,
            )
            response_text = result["content"]
            model_used = result.get("model", model_used)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Attachment processing failed: {e}")

        sources = None
        log_task(task_type, model_used, prompt_text, response_text)

    elif task_type == "rag_query":
        try:
            rag_result = answer_rag_query(prompt_text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"RAG query failed: {e}")

        response_text = rag_result["answer"]
        model_used = rag_result.get("model_used") or get_model_for_task("rag_query")
        sources = rag_result.get("sources") or []
        log_rag_query(prompt_text, sources, response_text)

    elif task_type in {"code"}:
        model_used = get_model_for_task(task_type)
        try:
            agent_result = run_agent(
                prompt_text,
                model_key=model_used,
                conversation_history=history,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Agent task failed: {e}")

        response_text = agent_result.get("answer", str(agent_result))
        sources = None
        log_task(task_type, model_used, prompt_text, response_text)

    else:
        model_used = get_model_for_task(task_type if task_type in ["code", "document"] else "general")
        chat_messages = list(history) + [{"role": "user", "content": prompt_text}]
        try:
            result = llm_chat(
                messages=chat_messages,
                model_key=task_type if task_type in ["code", "document"] else model_used,
                system=GENERAL_SYSTEM_PROMPT,
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"LLM query failed: {e}")

        response_text = result["content"]
        model_used = result.get("model", model_used)
        sources = None
        log_task(task_type, model_used, prompt_text, response_text)

    add_message(session_id, "assistant", response_text, task_type, model_used, sources)

    return TaskResponse(
        model_used=model_used,
        task_type=task_type,
        response=response_text,
        sources=sources,
        session_id=session_id,
    )