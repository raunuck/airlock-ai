import re
from typing import Optional

VALID_TASK_TYPES = {"code", "document", "rag_query", "general"}

def _contains_word_or_phrase(text: str, terms: list[str]) -> bool:
    for term in terms:
        if " " in term:
            if term in text:
                return True
        else:
            if re.search(r"\b" + re.escape(term) + r"\b", text):
                return True
    return False

def classify_task(prompt: str, previous_task_type: Optional[str] = None) -> str:
    prompt_lower = prompt.lower().strip()

    # Special case: Policy / conduct queries that contain the word 'code' (e.g. 'code of conduct')
    if "code of conduct" in prompt_lower or "code of ethics" in prompt_lower:
        return "rag_query"

    code_keywords = [
        "write code", "python", "script", "function", "debug",
        "calculate", "compute", "program", "bug", "code", "algorithm",
        "refactor", "unit test", "syntax error"
    ]

    rag_keywords = [
        "what does", "according to", "sop", "procedure", "manual",
        "guideline", "policy", "regulations", "safety standard",
        "standard operating procedure", "operating procedure"
    ]

    doc_keywords = [
        "scanned", "report", "approval note", "inspection",
        "upload", "ocr", "extract text", "draft note", "image note"
    ]

    # Explicit SOP / procedure / knowledge base query
    if _contains_word_or_phrase(prompt_lower, rag_keywords):
        return "rag_query"

    # Document or scanned image processing
    if _contains_word_or_phrase(prompt_lower, doc_keywords):
        return "document"

    # Code writing or debugging
    if _contains_word_or_phrase(prompt_lower, code_keywords):
        return "code"

    # Contextual follow-up if previous task type was valid
    if previous_task_type and previous_task_type in VALID_TASK_TYPES:
        return previous_task_type

    # Default to general for conversational / general queries (math, chat, etc.)
    return "general"