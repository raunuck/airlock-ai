from app.db import get_model_for_task as db_get_model_for_task

MODEL_KEY_MAPPING = {
    "qwen2.5-coder:7b": "coding",
    "qwen2.5:7b": "general",
}

def get_model_for_task(task_type: str) -> str:
    """
    Retrieve model for a task type from the database model registry.
    Returns the configured model name (e.g. 'qwen2.5-coder:7b' or 'qwen2.5:7b').
    """
    return db_get_model_for_task(task_type)

def get_model_key_for_task(task_type: str) -> str:
    """
    Helper to get the shorthand model key ('coding' or 'general') for a task type.
    """
    model_name = get_model_for_task(task_type)
    return MODEL_KEY_MAPPING.get(model_name, "general")