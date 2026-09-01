# Task Classifier

When the user sends a message, we need to figure out what kind of task it is before routing it to the right model/path. Here's the logic I'm going with for now:

## 3 task types

| Type | Example | Goes to |
|------|---------|---------|
| `code` | "write a script to calculate flow rate" | qwen2.5-coder → sandbox → pass/fail |
| `document` | "read this scanned report and draft an approval note" | OCR → agent → .docx |
| `rag_query` | "what does the SOP say about valve inspection?" | Chroma → answer + citation |

## Classifier (keyword-based for now)

```python
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
        return "rag_query"  # default — most queries will be knowledge-based anyway
```

## How this connects to the backend

```
POST /task
    → classify_task(prompt) → task_type
    → router picks model + path
    → response includes: answer + model_used + task_type
                                              ↑
                                    shown as a badge in the UI
```

## Note
Keyword matching is simple but good enough for the demo. 
The "proper" version would use a small LLM call to classify — more robust, handles edge cases better. Flagging this as a known improvement for the presentation.
