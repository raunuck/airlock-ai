from pathlib import Path
import chromadb
from backend.llm_client import prompt as llm_prompt

# Connect to ChromaDB
# Resolve the database path relative to the backend directory
BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "chroma_db"

client = chromadb.PersistentClient(path=str(CHROMA_DIR))

# Get the same collection used in ingestion.py
collection = client.get_collection(name="sop_docs")


def search_documents(query):
    results = collection.query(
        query_texts=[query],
        n_results=2
    )

    return results

def unpack_results(results: dict) -> list[dict]:
    """
    Convert ChromaDB's nested response into a simple list of dictionaries.
    """

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    return [
        {
            "text": document,
            "source": metadata["source"],
            "distance": distance,
        }
        for document, metadata, distance in zip(
            documents,
            metadatas,
            distances,
        )
    ]

def get_relevant_chunks(query: str, max_distance: float = 1.0) -> list[dict]:
    """
    Retrieve only the chunks that are similar enough to the query.
    """

    raw_results = search_documents(query)
    chunks = unpack_results(raw_results)

    return [
        chunk
        for chunk in chunks
        if chunk["distance"] < max_distance
    ]

def build_rag_prompt(question: str, chunks: list[dict]) -> tuple[str, str]:
    """
    Build a system prompt + user prompt from retrieved context.
    Returns (system_prompt, user_prompt) — pass system_prompt via
    llm_client's `system` param rather than concatenating it into one string.
    """
    system_prompt = (
        "You are an assistant answering questions using the organization's "
        "Standard Operating Procedures (SOPs). Use ONLY the information in "
        "the provided context — never rely on prior knowledge. If the answer "
        "isn't in the context, say so directly instead of guessing. When you "
        "do answer, name which source(s) you used."
    )

    if not chunks:
        user_prompt = (
            f"No relevant SOP content was found for this question.\n\n"
            f"Question: {question}\n\n"
            f"Tell the user this information isn't available in the knowledge base."
        )
        return system_prompt, user_prompt

    sources_seen = []
    context_parts = []
    for chunk in chunks:
        context_parts.append(f"[Source: {chunk['source']}]\n{chunk['text']}")
        if chunk["source"] not in sources_seen:
            sources_seen.append(chunk["source"])

    context = "\n\n".join(context_parts)
    user_prompt = (
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        f"Answer using only the context above. End your answer with "
        f"'Source(s): {', '.join(sources_seen)}'."
    )
    return system_prompt, user_prompt

def answer_rag_query(question: str) -> dict:
    """
    Retrieve relevant SOPs and generate an answer using the local LLM.

    Returns:
        {
            "answer": str,
            "sources": list[str],   # in relevance order, not alphabetical
            "model_used": str,
            "context_found": bool,       # False if no relevant chunks were found
        }
    """
    chunks = get_relevant_chunks(question)
    system_prompt, user_prompt = build_rag_prompt(question, chunks)

    if not chunks:
        return {
            "answer": "I don't have this information in the provided SOP documents.",
            "sources": [],
            "model_used": None,
            "context_found": False,
        }

    try:
        response = llm_prompt(
            text=user_prompt,
            system=system_prompt,
            model_key="general",
        )
    except RuntimeError:
        return {
            "answer": "The language model is currently unavailable. Please try again later.",
            "sources": [],
            "model_used": None,
            "context_found": bool(chunks),
        }

    # dict.fromkeys preserves first-seen order while deduplicating
    seen_sources = list(dict.fromkeys(chunk["source"] for chunk in chunks))

    return {
        "answer": response["content"],
        "sources": seen_sources,
        "model_used": response["model"],
        "context_found": True,
    }

# Test
if __name__ == "__main__":
    query = "What are the safety procedures?"

    response = answer_rag_query(query)

    print("\n===== ANSWER =====\n")
    print(response["answer"])

    print("\n===== SOURCES =====")
    print(response["sources"])

    print("\n===== MODEL USED =====")
    print(response["model_used"])

    print("\n===== CONTEXT FOUND =====")
    print(response["context_found"])