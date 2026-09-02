from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from llm_client import prompt as call_model
from agent.task_classifier import classify_task
from agent.model_choices import get_model_for_task

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskRequest(BaseModel):
    prompt: str

@app.post("/task")
def handle_task(req: TaskRequest):
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    try:
        task_type = classify_task(req.prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {e}")

    try:
        model_key = get_model_for_task(task_type)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No model mapped for task type: {e}")

    try:
        result = call_model(text=req.prompt, model_key=model_key)
        response_text = result["content"]
        model_name = result["model"]
    except ConnectionError:
        raise HTTPException(status_code=503, detail="Ollama isn't running — start it with `ollama serve`")
    except Exception as e:
        # Catch connection refusals from the ollama library as well
        if "connection" in str(e).lower() or "connrefused" in str(e).lower():
            raise HTTPException(status_code=503, detail="Ollama isn't running — start it with `ollama serve`")
        raise HTTPException(status_code=500, detail=f"Model call failed: {e}")

    return {
        "task_type": task_type,
        "model_used": model_name,
        "response": response_text,
    }

@app.get("/health")
def health():
    return {"status": "ok"}