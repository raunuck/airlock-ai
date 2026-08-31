import ollama
from typing import Optional

# --------------------------------------------------
# Available local models
# --------------------------------------------------

MODELS = {
    "general": "qwen2.5:7b",
    "coding": "qwen2.5-coder:7b",
}

DEFAULT_MODEL = "general"


# --------------------------------------------------
# Chat with Ollama
# --------------------------------------------------

def chat(
    messages: list[dict[str, str]],
    model_key: str = DEFAULT_MODEL,
    system: Optional[str] = None,
) -> dict:
    """
    Sends a chat request to Ollama.

    Args:
        messages:
            Example:
            [
                {"role": "user", "content": "Hello"}
            ]

        model_key:
            "general" or "coding"

        system:
            Optional system prompt.

    Returns:
        {
            "content": "...",
            "model": "qwen2.5:7b"
        }
    """

    model_name = MODELS.get(model_key, MODELS[DEFAULT_MODEL])

    final_messages = messages.copy()

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
        raise RuntimeError(f"Ollama request failed: {e}") from e


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