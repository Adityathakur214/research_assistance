import os
from dotenv import load_dotenv
import chromadb
from google import genai
import uuid

# Load environment variables
load_dotenv()

# Configure Google Gemini API using the NEW SDK
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    client = genai.Client(api_key=gemini_key)
else:
    print("Gemini API key not found in .env file.")

# Initialize Local Vector Database
db_client = chromadb.PersistentClient(path="./chroma_db")
collection = db_client.get_or_create_collection(name="research_assistant")

def get_embedding(text):
    """Text ko naye Gemini SDK se embeddings (vectors) mein convert karta hai."""
    response = client.models.embed_content(
        model="text-embedding-004",
        contents=text
    )
    return response.embeddings[0].values

def add_to_knowledge_base(text_chunks, urls):
    """Data ko ChromaDB mein save karta hai."""
    if not text_chunks:
        return "No text provided."
        
    embeddings = [get_embedding(chunk) for chunk in text_chunks]
    ids = [str(uuid.uuid4()) for _ in range(len(text_chunks))]
    metadatas = [{"url": url} for url in urls]
    
    collection.add(
        documents=text_chunks,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )
    return "Data saved to ChromaDB successfully!"

def query_assistant(user_question):
    """Gemini Flash model ka use karke accurate, cited answer nikaalta hai."""
    # 1. Question ko vector banana
    question_embedding = get_embedding(user_question)
    
    # 2. Database se similar text nikaalna
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=3
    )
    
    if not results['documents'] or not results['documents'][0]:
        return "Not found in sources."
        
    # 3. Context setup karna
    retrieved_chunks = results['documents'][0]
    retrieved_urls = [meta['url'] for meta in results['metadatas'][0]]
    
    context = ""
    for i in range(len(retrieved_chunks)):
        context += f"Source ({retrieved_urls[i]}): {retrieved_chunks[i]}\n\n"
        
    # 4. Strict Prompt
    prompt = f"""You are a research assistant. Answer the user's question using ONLY the context provided below. 
    If the answer is not present in the context, explicitly say 'Not found in sources'. Do not hallucinate. 
    Append the source URL to each factual statement you make.
    
    Context:
    {context}
    
    User Question: {user_question}
    """
    
    # 5. Gemini API Call
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents=prompt
    )
    
    return response.text

print("Google Gemini (New SDK) RAG Backend Setup Successfully!")