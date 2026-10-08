# 🧠 AI Research Assistant with RAG Memory

An advanced Retrieval-Augmented Generation (RAG) system that allows users to chat with multiple web pages simultaneously. It extracts content from provided URLs, embeds the data into a local vector database, and uses Claude AI to answer natural language questions with strict source citations.

## 🌟 Key Features

- **🌐 Multi-Source Ingestion:** Add multiple web URLs to a persistent knowledge base seamlessly.
- **🤖 Grounded AI Responses:** Powered by Anthropic's Claude, it explicitly answers based *only* on the ingested data.
- **📑 Strict Citations:** Every factual statement in the response includes a citation pointing to the exact source URL.
- **🚫 Zero Hallucinations:** Features a strict "Not found in sources" fallback mechanism if the information doesn't exist in the database.
- **💾 Persistent Memory:** Uses ChromaDB for local vector storage, allowing multi-session continuity without losing past URLs.
- **📄 PDF Export:** Download the entire Q&A session as a formatted PDF document.

## 🏗️ Architecture & Tech Stack

This project is divided into two primary phases: Data Ingestion and AI Retrieval.

- **Frontend / UI:** [Streamlit](https://streamlit.io/)
- **LLM Engine:** [Anthropic Claude API](https://www.anthropic.com/api)
- **Embeddings:** [OpenAI API](https://platform.openai.com/docs/guides/embeddings) (`text-embedding-3-small`)
- **Vector Database:** [ChromaDB](https://www.trychroma.com/) (Local persistent storage)
- **Data Pipeline (Ingestion):** [n8n](https://n8n.io/) Webhook for web scraping and chunking.

---

## 🚀 Getting Started

### 1. Prerequisites
Make sure you have the following installed on your local machine:
- Python 3.10 or higher
- Git
- n8n (Node.js or Docker setup)

### 2. Installation
Clone the repository and set up the virtual environment:

```bash
# Clone the repo
git clone [https://github.com/your-username/rag-research-assistant.git](https://github.com/your-username/rag-research-assistant.git)
cd rag-research-assistant

# Create and activate virtual environment
python -m venv venv

# For Windows:
venv\Scripts\activate
# For Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
