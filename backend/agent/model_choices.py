def get_model_for_task(task_type: str) -> str:
    mapping = {
        "code": "coding",       # maps to qwen2.5-coder:7b
        "document": "general",  # maps to qwen2.5:7b
        "rag_query": "general", # maps to qwen2.5:7b
    }
    
    if task_type not in mapping:
        raise ValueError(f"Unknown task type: {task_type}")
    
    return mapping[task_type]