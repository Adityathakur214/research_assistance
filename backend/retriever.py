from backend.database import collection
from backend.config import CHUNK_RESULTS

def get_relevant_context(user_question):
    """Local database se search karke context nikaalta hai."""
    results = collection.query(
        query_texts=[user_question], 
        n_results=CHUNK_RESULTS
    )
    
    if not results['documents'] or not results['documents'][0]:
        return None
        
    # Context setup
    retrieved_chunks = results['documents'][0]
    retrieved_urls = [meta['url'] for meta in results['metadatas'][0]]
    
    context = ""
    for i in range(len(retrieved_chunks)):
        context += f"Source ({retrieved_urls[i]}): {retrieved_chunks[i]}\n\n"
        
    return context