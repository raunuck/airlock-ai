import chromadb

# Connect to ChromaDB
client = chromadb.PersistentClient(path="./chroma_db")

# Get the same collection used in ingestion.py
collection = client.get_collection(name="sop_docs")


def search_documents(query):
    results = collection.query(
        query_texts=[query],
        n_results=2
    )

    return results


# Test
query = "What are the safety procedures?"

results = search_documents(query)

print(results)