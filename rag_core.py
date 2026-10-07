import os
from dotenv import load_dotenv
import chromadb
from openai import OpenAI
from anthropic import Anthropic

# .env file se saari API keys load karein
load_dotenv()

# API Clients Initialize karein
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
claude_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ChromaDB Initialize karein (Local storage ke liye)
db_client = chromadb.PersistentClient(path="./chroma_db")
collection = db_client.get_or_create_collection(name="research_assistant")

print("Backend setup successful! ChromaDB aur APIs initialize ho gaye hain.")