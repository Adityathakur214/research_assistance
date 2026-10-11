import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys & Paths
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
CHROMA_DB_PATH = "./chroma_db"
COLLECTION_NAME = "research_assistant"

# Model Config
GEMINI_MODEL_NAME = "gemini-3.8-flash"
CHUNK_RESULTS = 3