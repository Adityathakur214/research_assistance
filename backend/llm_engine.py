from google import genai
from backend.config import GEMINI_API_KEY, GEMINI_MODEL_NAME
from backend.prompts import RAG_PROMPT_TEMPLATE
from backend.retriever import get_relevant_context

# Initialize Gemini Client for Text Generation ONLY
client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None

def query_assistant(user_question):
    """Retriever se context lakar Gemini Flash se answer generate karta hai."""
    context = get_relevant_context(user_question)
    
    if not context:
        return "Not found in sources."
        
    # Prompt ko context aur question ke sath format karna
    prompt = RAG_PROMPT_TEMPLATE.format(
        context=context, 
        user_question=user_question
    )
    
    # Gemini API for final answer generation
    response = client.models.generate_content(
        model=GEMINI_MODEL_NAME,
        contents=prompt
    )
    return response.text