import os
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
    "image": "qwen2.5:7b"
}

FALLBACK_MODELS = {
    "qwen2.5:7b": "qwen2.5:3b",
    "qwen2.5-coder:7b": "qwen2.5-coder:3b",
}

DEFAULT_MODEL = "general"

# Check if running in production on Render
# Gemini api keys are only used for demo deployment, airlock-ai when setup locally does not use any kind of api keys
IS_PRODUCTION = os.environ.get("RENDER", False) or os.environ.get("PORT", None) is not None
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# --------------------------------------------------
# Core Chat Wrapper (Cloud API vs Local Ollama)
# --------------------------------------------------

def chat(
    messages: list[dict[str, any]],
    model_key: str = DEFAULT_MODEL,
    system: Optional[str] = None,
    images: Optional[List[str]] = None,
) -> dict:
    """
    Routes requests to Gemini API when live on Render, or local Ollama when running on-premise.
    """

    # If running live on Render, use the Gemini API for instant, real responses
    if IS_PRODUCTION and GEMINI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            
            # Format history/messages for Gemini
            contents = []
            if system:
                contents.append(f"System Instructions: {system}")
                
            for m in messages:
                role = "user" if m.get("role") == "user" else "model"
                contents.append(f"{role.capitalize()}: {m.get('content', '')}")
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents="\n".join(contents),
            )
            
            return {
                "content": response.text + "\n\n*(Note: Cloud evaluation node powered by Gemini API)*",
                "model": "gemini-2.5-flash-cloud",
            }
        except Exception as e:
            print(f"Gemini API Error: {e}")

    # ---- Your original local Ollama logic (runs locally on your laptop) ----
    model_name = MODELS.get(model_key, model_key)
    if model_name not in MODELS.values() and model_name not in FALLBACK_MODELS.values() and model_name not in FALLBACK_MODELS:
        pass

    final_messages = [dict(m) for m in messages]

    if images and final_messages:
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