import ollama
from typing import Optional, List

# --------------------------------------------------
# Available local models (with automatic fallback mapping)
# --------------------------------------------------

MODELS = {
    "general": "qwen2.5:7b",
    "document": "qwen2.5:7b",
    "code": "qwen2.5-coder:7b",
    "coding": "qwen2.5-coder:7b",
    "rag_query": "qwen2.5:7b",
    "image": "llava:7b"
}

FALLBACK_MODELS = {
    "qwen2.5:7b": "qwen2.5:3b",
    "qwen2.5-coder:7b": "qwen2.5-coder:3b",
    "llava:7b": "llava:3b"
}

DEFAULT_MODEL = "general"

# --------------------------------------------------
# Core Ollama chat wrapper
# --------------------------------------------------

def chat(
    messages: list[dict[str, any]],
    model_key: str = DEFAULT_MODEL,
    system: Optional[str] = None,
    images: Optional[List[str]] = None,
) -> dict:
    """
    Sends a chat request to Ollama with automatic fallback to 3B models 
    if a system memory / OOM error occurs, supporting image attachments.
    """

    model_name = MODELS.get(model_key, model_key)
    if model_name not in MODELS.values() and model_name not in FALLBACK_MODELS.values() and model_name not in FALLBACK_MODELS:
        # Allow raw model names directly if passed
        pass

    final_messages = [dict(m) for m in messages]  # Copy to avoid mutation

    if images and final_messages:
        # Attach images to the last user message for multimodal processing (e.g. llava)
        for msg in reversed(final_messages):
            if msg["role"] == "user":
                msg["images"] = images
                break

    if system:
        final_messages.insert(
            0,
            {
                "role": "system",
                "content": system,
            },
        )

    try:
        response = ollama.chat(
            model=model_name,
            messages=final_messages,
        )

        return {
            "content": response["message"]["content"],
            "model": model_name,
        }

    except Exception as e:
        err_str = str(e).lower()
        print(f"DEBUG - Ollama error with model '{model_name}': {err_str}")
        
        # Automatic fallback recovery for memory or execution errors
        fallback_model = FALLBACK_MODELS.get(model_name)
        if fallback_model:
            print(f"[FALLBACK] Primary model '{model_name}' failed ({e}). Automatically falling back to '{fallback_model}'...")
            
            try:
                response = ollama.chat(
                    model=fallback_model,
                    messages=final_messages,
                )
                return {
                    "content": response["message"]["content"],
                    "model": fallback_model,
                }
            except Exception as fallback_error:
                raise RuntimeError(
                    f"Failed to communicate with Ollama using primary model '{model_name}' and fallback model '{fallback_model}'. "
                    f"Primary error: {e} | Fallback error: {fallback_error}"
                ) from fallback_error

        raise RuntimeError(
            f"Failed to communicate with Ollama for model '{model_name}'. "
            f"Please make sure the Ollama server is running. "
            f"Original error: {e}"
        ) from e


def prompt(
    text: str,
    model_key: str = DEFAULT_MODEL,
    system: Optional[str] = None,
    images: Optional[List[str]] = None,
) -> dict:
    """
    Shortcut for single user prompt with optional image attachments.
    """
    return chat(
        messages=[
            {
                "role": "user",
                "content": text,
            }
        ],
        model_key=model_key,
        system=system,
        images=images,
    )