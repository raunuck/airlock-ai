import ollama
from typing import Optional

# --------------------------------------------------
# Available local models (with automatic fallback mapping)
# --------------------------------------------------

MODELS = {
    "general": "qwen2.5:7b",
    "coding": "qwen2.5-coder:7b",
}

FALLBACK_MODELS = {
    "qwen2.5:7b": "qwen2.5:3b",
    "qwen2.5-coder:7b": "qwen2.5-coder:3b",
}

DEFAULT_MODEL = "general"


# --------------------------------------------------
# Core Ollama chat wrapper
# --------------------------------------------------

def chat(
    messages: list[dict[str, str]],
    model_key: str = DEFAULT_MODEL,
    system: Optional[str] = None,
) -> dict:
    """
    Sends a chat request to Ollama with automatic fallback to 3B models 
    if a system memory / OOM error occurs.
    """

    model_name = MODELS.get(model_key)

    if model_name is None:
        raise ValueError(
            f"Invalid model_key: {model_key}."
            f" Expected one of: {list(MODELS.keys())}"
        )

    final_messages = list(messages)  # Make a copy to avoid modifying the original list

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
        
        # Check if the error is related to insufficient system memory / RAM
        if ("memory" in err_str or "system memory" in err_str or "oom" in err_str) and model_name in FALLBACK_MODELS:
            fallback_model = FALLBACK_MODELS[model_name]
            print(f"⚠️ Memory limitation hit for {model_name}. Automatically falling back to {fallback_model}...")
            
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
                    f"Failed to communicate with Ollama using fallback model {fallback_model}. "
                    f"Original error: {fallback_error}"
                ) from fallback_error

        raise RuntimeError(
            f"Failed to communicate with Ollama. "
            f"Please make sure the Ollama server is running. "
            f"Original error: {e}"
        ) from e


# --------------------------------------------------
# Convenience helper
# --------------------------------------------------

def prompt(
    text: str,
    model_key: str = DEFAULT_MODEL,
    system: Optional[str] = None,
) -> dict:
    """
    Shortcut for single user prompt.
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
    )