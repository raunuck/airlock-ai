def classify_task(prompt: str) -> str:
    prompt_lower = prompt.lower()

    code_keywords = ["write code", "python", "script", "function",
                    "debug", "calculate", "compute", "program"]

    doc_keywords = ["scanned", "report", "image", "approval note",
                    "inspection", "upload", "ocr", "document", "draft"]

    rag_keywords = ["what does", "according to", "sop", "procedure",
                    "manual", "guideline", "how to", "policy"]

    if any(word in prompt_lower for word in code_keywords):
        return "code"

    elif any(word in prompt_lower for word in doc_keywords):
        return "document"

    elif any(word in prompt_lower for word in rag_keywords):
        return "rag_query"

    else:
        return "rag_query"