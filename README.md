# 🧠 Research Assistant With Memory
**A Persistent, Multi-Source AI Knowledge Assistant**

Drop URLs. Ask questions across all of them as if they were one document.

Research Assistant With Memory is an AI-powered knowledge retrieval system designed to transform web pages into a persistent, searchable knowledge base. Users can submit URLs, ingest their content, and ask natural-language questions across multiple sources through a Streamlit interface.

The system combines workflow automation with semantic search and large language models (Google Gemini) to generate context-aware answers grounded in retrieved source content. Each answer is designed to include source URL citations, with an explicit fallback when the available sources do not contain sufficient information.

Unlike a single-session chatbot, the system retains previously ingested knowledge so users can add new sources over time without losing their existing collection.

**Core technologies:** n8n · Gemini API (gemini-1.5-flash) · ChromaDB · Streamlit · Python · python-dotenv

---

## 📌 1. Original Problem Statement
**“Drop URLs, ask questions across all of them like they are one document.”**

Build a system where an n8n webhook receives URLs, scrapes the HTML content, and chunks and embeds it into ChromaDB. A Streamlit app lets the user ask natural-language questions across all ingested sources. Gemini retrieves relevant chunks and answers with citations showing which URL each fact came from. New URLs can be added at any time without losing prior ones.

**Required capabilities:**
*   **Automated ingestion:** Accept URLs through an n8n webhook and extract their raw HTML text.
*   **Semantic indexing:** Split extracted text into manageable chunks, generate embeddings, and store them in ChromaDB.
*   **Multi-source question answering:** Answer questions using relevant information retrieved from all previously ingested sources.
*   **Source-grounded responses:** Generate answers using Gemini and include citations that identify the originating URLs.
*   **Explicit fallback:** Return a clear “Not found in sources” response when the indexed knowledge does not support an answer.
*   **Persistent memory:** Retain previously indexed content across application sessions and support incremental ingestion.

## 🎯 2. Project Overview
Traditional research often involves opening multiple articles, switching between browser tabs, manually comparing information, and repeatedly searching for the same facts. This project introduces a unified research workflow in which users can build a personal knowledge base from web sources and query it through a conversational interface.

The application follows a **Retrieval-Augmented Generation (RAG)** approach. Instead of relying solely on a language model's pretrained knowledge, it retrieves relevant passages from the indexed documents and uses those passages as the evidence for answering questions.

| Challenge | Proposed Solution |
| :--- | :--- |
| Information scattered across multiple URLs | Unified persistent knowledge base |
| Manual content collection | n8n-based ingestion workflow (Webhook -> HTTP -> HTML Extract) |
| Difficulty locating relevant passages | Embedding-based semantic retrieval via ChromaDB |
| Unsupported AI-generated answers | Source-grounded generation and explicit fallback |
| Repeated ingestion of existing material | Persistent vector storage and incremental indexing |

## ✨ 3. Core Features

### 3.1 Automated URL ingestion
The ingestion workflow begins when a user submits one or more URLs to an n8n webhook. The workflow is responsible for receiving the URLs, retrieving accessible web content, extracting meaningful text using HTML extraction nodes, and preparing it for indexing. 

### 3.2 Text chunking and embedding generation
Long web pages are divided into smaller text chunks. Each chunk can be retrieved independently, allowing the system to identify specific passages rather than supplying an entire article to the language model. Embeddings convert these chunks into numerical vector representations that capture semantic relationships.

### 3.3 Persistent vector database
ChromaDB stores the document embeddings together with the associated text and source metadata. The metadata preserves the originating URL for every chunk so that retrieved evidence can be traced back to its source. 

### 3.4 Natural-language question answering
A Streamlit interface provides the user-facing research experience. Users can ask questions in ordinary language. The retrieval layer identifies relevant chunks from ChromaDB, and Google Gemini uses the retrieved evidence to formulate a readable response.

### 3.5 Source citations and grounded answers
Responses identify the URL associated with each relevant piece of evidence. Citations are derived from retrieved source metadata rather than generated as unsupported links. When the retrieved context is insufficient, the system explicitly responds: *"Not found in sources."*

## 🏗️ 4. System Architecture
The architecture consists of two connected workflows: document ingestion and question answering.

flowchart TD
    A[User submits URLs] --> B[n8n Webhook]
    B --> C[HTTP Request: Fetch web pages]
    C --> D[HTML Node: Extract text]
    D --> E[Python Backend: Split into chunks]
    E --> F[Generate Embeddings]
    F --> G[ChromaDB]
    G --> H[Persistent Knowledge Base]

    I[User asks a question] --> J[Streamlit Interface]
    J --> K[Generate query embedding]
    K --> L[Semantic retrieval from ChromaDB]
    H --> L
    L --> M{Relevant evidence found?}
    M -->|Yes| N[Gemini API - 1.5 Flash]
    M -->|No| O[Not found in sources]
    N --> P[Answer with source citations]
    O --> Q[Display fallback]

 
 🧰 5. Technology Stack
Python: Application logic, backend processing, and RAG pipeline.

n8n: Visual workflow automation, webhook orchestration, and HTML scraping.

Gemini API (gemini-1.5-flash): Context-aware answer generation and fast inference.

ChromaDB: Local vector storage and similarity search.

Streamlit: Interactive user interface (app.py).

python-dotenv: Environment-based configuration management.

📂 6. Project Structure
Based on the implemented architecture, the repository is structured as follows:

Plaintext
research-assistant/
│
├── backend/
│   ├── config.py             # Environment & model configuration
│   ├── database.py           # Database connection logic
│   ├── llm_engine.py         # Gemini API integration
│   ├── prompts.py            # System prompts & citation formatting
│   └── retriever.py          # ChromaDB semantic search logic
│
├── frontend/
│   └── app.py                # Streamlit user interface
│
├── chroma_db/                # Persistent local vector database directory
├── n8n/
│   └── workflow.json         # Exported n8n ingestion workflow
│
├── .env                      # API keys (Git ignored)
├── .env.example              # Environment variables template
├── .gitignore                # Security exclusions
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation

⚙️ 7. Prerequisites & Environment Configuration
Python 3.10+ installed locally.

An active n8n instance (Cloud or Local).

A Google Gemini API Key.

Create a .env file in the root directory based on your config.py setup:

Code snippet
# Gemini AI Configuration
GEMINI_API_KEY=your_gemini_api_key_here

# Database Configuration
CHROMA_DB_PATH=./chroma_db
COLLECTION_NAME=research_assistant
Security Note: Never commit your .env file. It is explicitly ignored in the .gitignore.

🚀 8. Installation and Setup
Clone the repository:

Bash
git clone <your-repository-url>
cd research-assistant
Set up the virtual environment:

Bash
python -m venv venv
.\venv\Scripts\activate  # Windows
Install dependencies:

Bash
pip install -r requirements.txt
Configure n8n: Import the workflow.json into n8n. Ensure the Webhook URL is active and the HTML extraction node is properly linked to your backend ingestion endpoint.

Launch the Application:

Bash
streamlit run frontend/app.py
🛡️ 9. Reliability, Grounding, and Error Handling
Retrieval-grounded generation: The prompts.py file strictly instructs Gemini to use only supplied passages as evidence and explicitly acknowledge missing information.

Source metadata integrity: Every indexed chunk in ChromaDB retains its original URL as metadata, ensuring accurate tracing back to the source.

Persistent storage: chroma_db is stored locally within the project directory, ensuring that data persists across application and server restarts.

🎓 10. Conclusion
The Research Assistant With Memory creates a robust workflow where users can continuously expand their knowledge base and ask questions across previously indexed sources. By utilizing Gemini's rapid inference, n8n's seamless webhooks, and ChromaDB's persistent semantic retrieval, the system prioritizes grounded, verifiable answers over AI hallucinations.
