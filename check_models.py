import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API Key nahi mili! .env check karein.")
else:
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        print("\n✅ Aapki API key par ye exact models available hain:\n")
        models = response.json().get("models", [])
        for m in models:
            # Sirf text generate karne wale models filter kar rahe hain
            if "generateContent" in m.get("supportedGenerationMethods", []):
                clean_name = m.get("name").replace("models/", "")
                print(f"- {clean_name}")
    else:
        print(f"Error fetching models: {response.text}")