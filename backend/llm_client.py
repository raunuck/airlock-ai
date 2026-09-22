import os
import ollama
from typing import Optional, List

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

def chat(
    messages: list[dict[str, any]],
    model_key: str = DEFAULT_MODEL,
    system: Optional[str] = None,
    images: Optional[List[str]] = None,
) -> dict:

    # Gemini api keys are only used for demo deployment, airlock-ai when setup locally does not use any kind of api keys
    
    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    
    # If a Gemini API key is configured, use cloud-based Gemini (bypasses local Ollama entirely)
    if gemini_key:
        try:
            from google import genai
            client = genai.Client(api_key=gemini_key)
            
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
            print(f"Gemini Cloud Error: {e}")

    # Fallback to local Ollama execution (used only when running on your local laptop without a cloud key)
    model_name = MODELS.get(model_key, model_key)
    final_messages = [dict(m) for m in messages]

    if images and final_messages:
        for msg in reversed(final_messages):
            if msg["role"] == "user":
                msg["images"] = images
                break

    if system:
        final_messages.insert(0, {"role": "system", "content": system})

    try:
        response = ollama.chat(model=model_name, messages=final_messages)
        return {
            "content": response["message"]["content"],
            "model": model_name,
        }
    except Exception as e:
        fallback_model = FALLBACK_MODELS.get(model_name)
        if fallback_model:
            try:
                response = ollama.chat(model=fallback_model, messages=final_messages)
                return {
                    "content": response["message"]["content"],
                    "model": fallback_model,
                }
            except Exception as fallback_error:
                raise RuntimeError(f"Ollama local connection failed: {e} | {fallback_error}") from fallback_error

        raise RuntimeError(
            f"Failed to communicate with Ollama or Cloud API. "
            f"Please check that GEMINI_API_KEY is set on Render or Ollama is running locally. Error: {e}"
        ) from e


def prompt(
    text: str,
    model_key: str = DEFAULT_MODEL,
    system: Optional[str] = None,
    images: Optional[List[str]] = None,
) -> dict:
    return chat(
        messages=[{"role": "user", "content": text}],
        model_key=model_key,
        system=system,
        images=images,
    )