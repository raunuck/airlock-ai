from typing import Optional

def classify_task(prompt: str ,previous_task_type: Optional[str] = None) -> str:
    prompt_lower = prompt.lower()

    code_keywords = ["write code", "python", "script", "function",
                    "debug", "calculate", "compute", "program", "bug", "code"]

    rag_keywords = ["what does", "according to", "sop", "procedure",
                    "manual", "guideline", "how to", "policy"]

    doc_keywords = ["scanned", "report", "image", "approval note",
                    "inspection", "upload", "ocr", "document", "draft"]

    if any(word in prompt_lower for word in code_keywords):
        return "code"

    elif any(word in prompt_lower for word in rag_keywords):
        return "rag_query"

    elif any(word in prompt_lower for word in doc_keywords):
        return "document"

    else:
        return previous_task_type or "rag_query"  # default — most queries will be knowledge-based anyway