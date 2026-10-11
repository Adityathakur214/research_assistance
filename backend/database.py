import chromadb
import uuid
from backend.config import CHROMA_DB_PATH, COLLECTION_NAME

# Initialize Local Vector Database
db_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
collection = db_client.get_or_create_collection(name=COLLECTION_NAME)

def add_to_knowledge_base(text_chunks, urls):
    """Data ko ChromaDB mein save karta hai using Local Embeddings."""
    if not text_chunks:
        return "No text provided."
        
    ids = [str(uuid.uuid4()) for _ in range(len(text_chunks))]
    metadatas = [{"url": url} for url in urls]
    
    collection.add(
        documents=text_chunks,
        metadatas=metadatas,
        ids=ids
    )
    return "Data saved to ChromaDB successfully!"