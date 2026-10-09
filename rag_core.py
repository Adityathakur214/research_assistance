import os
from dotenv import load_dotenv
import chromadb
from google import genai
import uuid

# Load environment variables
load_dotenv()

# Initialize Gemini Client for Text Generation ONLY
gemini_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_key) if gemini_key else None

# Initialize Local Vector Database
db_client = chromadb.PersistentClient(path="./chroma_db")
# ChromaDB ab automatically 'sentence-transformers' use karega
collection = db_client.get_or_create_collection(name="research_assistant")

def add_to_knowledge_base(text_chunks, urls):
    """Data ko ChromaDB mein save karta hai using Local Embeddings."""
    if not text_chunks:
        return "No text provided."
        
    ids = [str(uuid.uuid4()) for _ in range(len(text_chunks))]
    metadatas = [{"url": url} for url in urls]
    
    # Humne embeddings parameter hata diya hai, Chroma khud vectors banayega
    collection.add(
        documents=text_chunks,
        metadatas=metadatas,
        ids=ids
    )
    return "Data saved to ChromaDB successfully!"

def query_assistant(user_question):
    """Local database se search karke Gemini Flash se answer nikaalta hai."""
    # Chroma automatically user question ko embed karke search karega
    results = collection.query(
        query_texts=[user_question], 
        n_results=3
    )
    
    if not results['documents'] or not results['documents'][0]:
        return "Not found in sources."
        
    # Context setup
    retrieved_chunks = results['documents'][0]
    retrieved_urls = [meta['url'] for meta in results['metadatas'][0]]
    
    context = ""
    for i in range(len(retrieved_chunks)):
        context += f"Source ({retrieved_urls[i]}): {retrieved_chunks[i]}\n\n"
        
    # Strict Prompt
    prompt = f"""You are a research assistant. Answer the user's question using ONLY the context provided below. 
    If the answer is not present in the context, explicitly say 'Not found in sources'. Do not hallucinate. 
    Append the source URL to each factual statement you make.
    
    Context:
    {context}
    
    User Question: {user_question}
    """
    
    # Gemini API for final answer generation
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt
    )
    
    return response.text