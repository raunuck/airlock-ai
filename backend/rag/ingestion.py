import chromadb
from pathlib import Path

client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection("sop_docs")

data_folder = Path("./data")

files = list(data_folder.glob("*.txt"))

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