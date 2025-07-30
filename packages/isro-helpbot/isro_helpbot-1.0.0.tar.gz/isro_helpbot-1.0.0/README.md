Here's a professional, clean, and complete `README.md` for your **ISRO HelpBot** project, optimized for both GitHub and PyPI packaging:

---

```markdown
# 🚀 ISRO HelpBot

An AI-powered conversational assistant designed for information retrieval from ISRO's knowledge resources using a Knowledge Graph, Natural Language Processing (NLP), and semantic search. Built for the [ISRO Bharatiya Antariksh Hackathon 2025](https://www.isrohack.in/), this project aims to revolutionize access to space-related information.

---

## 📌 Features

- 🔎 **Query Understanding**: Extracts intent and named entities from natural language queries.
- 🧠 **Knowledge Graph Builder**: Builds a semantic knowledge graph from `.txt`, `.pdf`, `.docx`, and `.xlsx` documents.
- 🌐 **Geospatial Awareness**: Recognizes and links locations (e.g., "Bay of Bengal", "17°N") from queries and documents.
- 💬 **Frontend Chat UI**: Built using Streamlit with file upload and interactive conversation.
- ⚙️ **Backend API**: FastAPI-powered backend to serve query results via RESTful endpoints.
- 📈 **Evaluation Metrics**: Real-time performance metrics to assess accuracy and responsiveness.

---

## 🗂️ Project Structure

```



```
ISRO HELPBOT/
├── __pycache__/                       # Compiled Python bytecode
├── .vscode/                           # VS Code settings for development
│   └── settings.json                  # Editor preferences and configurations
│
├── api/                               # FastAPI backend for handling API requests
│   ├── __pycache__/
│   ├── data/                          # API-level data files (temporary or static)
│   ├── static/                        # Static assets for FastAPI (CSS, JS, etc.)
│   ├── __init__.py                    # Marks directory as a Python package
│   ├── main_api.py                    # Uvicorn entrypoint with FastAPI app instance
│   ├── query_handler.py               # Logic to handle and respond to queries via API
│   └── routes.py                      # API endpoint definitions and routing
│
├── app/                               # Supplementary app scripts
│   ├── __pycache__/
│   └── main.py                        # Optional script for centralized app execution
│
├── core/                              # Chat logic and shared application functionality
│   ├── __pycache__/
│   └── chat_engine.py                 # Core engine handling conversations and message flow
│
├── data/                              # Datasets and documents used in KG construction
│   ├── clean_text/                    # Cleaned versions of raw text documents
│   ├── graph/                         # Serialized Knowledge Graphs
│   │   └── knowledge_graph.pkl        # Pickled NetworkX graph
│   ├── html/                          # Raw HTML files from scraped pages
│   ├── mosdac_docs/                   # Original documents (pdf/docx) from MOSDAC
│   ├── mosdac_pages/                  # Full saved MOSDAC HTML pages
│   └── raw_docs/                      # Raw document input before cleaning
│
├── raw_text/                          # Preprocessed plain text documents
│   ├── raw_docs                       # Raw text files for reference
│   └── test.text                      # Sample text used for testing
│
├── evaluation/                        # Evaluation scripts and outputs
│   ├── eval_engine.py                 # Script for evaluating intent/entity/response performance
│   └── results/                       # Output metrics and evaluation results
│       ├── intent_results.json        # JSON containing evaluation result details
│       ├── false_positives.csv        # Queries where intent classification failed
│       └── eval_summary.png           # Bar chart visualization of evaluation metrics
│
├── ingestion/                         # Document parsing and scraping modules
│   ├── docx_extractor.py              # Parse and extract text from .docx
│   ├── dynamic_scraper.py             # Scrape JavaScript-rendered MOSDAC pages
│   ├── html_scraper.py                # Parse static HTML files
│   └── pdf_extractor.py               # Extract content from PDFs
│
├── intent_classifier/                # Intent classification model and routing
│   ├── __pycache__/
│   ├── __init__.py                    # Package initializer
│   ├── intent_predictor.py            # ML model that predicts user intent
│   └── intent_router.py               # Maps intent labels to downstream task handlers
│
├── isro_helpbot/                      # Core pip-installable CLI module
│   ├── __pycache__/
│   ├── __init__.py                    # Package initializer
│   └── cli.py                         # CLI script to launch the bot via terminal
│
├── kg_builder/                        # Knowledge Graph construction modules
│   ├── entity_extractor.py            # Extracts named entities from documents/queries
│   ├── relationship_mapper.py         # Detects relationships among entities
│   ├── response_generator.py          # Forms responses from entities and graph traversal
│   └── text_preprocessor.py           # Cleans, splits and processes raw text
│
├── lib/                               # External shared libraries (if any)
│
├── model/                             # Models and vector storage
│   ├── __pycache__/
│   ├── embedding_generator.py         # Generates embeddings from textual input
│   ├── faiss_store_docs.pkl           # Serialized FAISS-compatible document store
│   ├── faiss_store.index              # FAISS binary index for fast semantic retrieval
│   ├── kg_reasoner.py                 # Reasoning logic using KG + LLM
│   ├── language_model.py              # Wrapper for local or API-based language models
│   ├── qa_pipeline.py                 # Complete pipeline from query to answer
│   └── vector_store.py                # Vector DB abstraction for FAISS, Chroma, etc.
│
├── tests/                             # Unit and integration test scripts
│   ├── test_intent_classifier.py      # Tests for intent classification logic
│   ├── test_kg.py                     # Tests for KG extraction and structure
│   └── test_scrapper.py               # Tests for scraping functions
│
├── ui/                                # Streamlit-based frontend
│   ├── __pycache__/
│   ├── components/                    # Streamlit component scripts (widgets, etc.)
│   ├── static/                        # Static images, graphs, etc.
│   ├── templates/                     # HTML templates (optional for hybrid UI)
│   ├── index.html                     # Frontend base page
│   ├── __init__.py                    # Marks UI as a package
│   └── streamlit_app.py               # Streamlit chatbot UI interface
│
├── venv/                              # Python virtual environment (excluded from Git)
├── .env                               # API keys and environment variables
├── .gitignore                         # Exclude rules for Git
├── build_index.py                     # Builds FAISS index for semantic search
├── config.py                          # Centralized configuration file (e.g., paths, thresholds)
├── entrypoints.py                     # Unified entrypoints for CLI/API/Streamlit
├── LICENSE                            # License file (MIT in this case)
├── main.py                            # Optional main runner script
├── MANIFEST.in                        # Include non-Python files during packaging
├── mosdac_crawler.py                  # Crawler script to fetch data from MOSDAC
├── pyproject.toml                     # Modern Python packaging metadata
├── requirements.txt                   # Required dependencies for pip install
└── setup.py                           # Package installer configuration
```

Let me know if you want this as a downloadable `.md` or `.txt` file or integrated into your `README.md`.

````

---

## ⚙️ Installation

```bash
pip install isro-helpbot
````

Or clone and run locally:

```bash
git clone https://github.com/Gaurav9693089415/ISRO-HelpBot.git
cd ISRO-HelpBot
pip install -e .
```

---

## 🚀 Usage

### 📍 Launch Chatbot UI

```bash
isro-helpbot
```

This opens the Streamlit interface at `http://localhost:8501/`.

### 📍 Run Backend API

```bash
uvicorn backend.main:app --reload --port 8080
```

---

## 📊 Evaluation Metrics

Evaluation metrics like accuracy, precision, recall, and response latency are automatically logged and can be viewed in the Streamlit sidebar.

---

## 📂 Supported Document Types

* `.txt` – Plain text files
* `.pdf` – Scanned and digital PDFs
* `.docx` – Microsoft Word
* `.xlsx` – Excel Sheets

Uploaded files auto-update the Knowledge Graph.

---

## 💻 Technologies Used

| Category    | Tools/Tech Stack                  |
| ----------- | --------------------------------- |
| NLP         | spaCy, NLTK, SentenceTransformers |
| KG + Search | NetworkX, FAISS, PyVis            |
| UI          | Streamlit                         |
| Backend     | FastAPI, Uvicorn                  |
| Others      | LangChain, OpenAI API, Selenium   |

---

## 🎯 Objectives (As per ISRO Hackathon)

* Convert web portal content into machine-readable knowledge.
* Enable geospatial semantic search.
* Build a dynamic, AI-based helpbot interface.
* Provide API for external access to the system.

---

## 🏁 Final Outcome

An end-to-end, modular AI HelpBot that:

* Parses ISRO content into a Knowledge Graph.
* Understands user questions contextually.
* Answers using accurate and semantically relevant data.
* Offers CLI + UI + REST API + pip packaging.

---

## 🛡️ License

MIT License. See `LICENSE` file.

---

## 🙌 Acknowledgement

Special thanks to **ISRO**, **IN-SPACe**, and **AICTE** for organizing the [Bharatiya Antariksh Hackathon 2025](https://www.isrohack.in/).

---

## ✨ Future Enhancements

* Voice interaction
* Image-based QnA using satellite maps
* Integration with live ISRO data streams

```

---

Let me know if you'd like me to:
- Add badges (PyPI, License, Build)
- Generate this as a downloadable file
- Translate it into Hindi (for local repo presentation)

Ready to proceed with packaging now?
```
