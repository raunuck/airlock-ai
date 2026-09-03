import chromadb
from pathlib import Path

# Resolve the project root so ingestion works regardless of the current working directory.
BASE_DIR = Path(__file__).resolve().parent.parent

CHROMA_DIR = BASE_DIR / "chroma_db"
DATA_DIR = BASE_DIR / "data"


client = chromadb.PersistentClient(path=str(CHROMA_DIR))

collection = client.get_or_create_collection("sop_docs")


files = list(DATA_DIR.glob("*.txt"))

documents = []
metadatas = []
ids = []

for i, file in enumerate(files):
    text = file.read_text(encoding="utf-8")

    documents.append(text)
    metadatas.append({"source": file.name})
    ids.append(f"doc-{i+1}")

collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids
)

print(f"{len(files)} documents added to ChromaDB successfully!")