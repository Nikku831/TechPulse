# Local AUTOSAR Assistant

This repository contains a local, document-grounded chat assistant for AUTOSAR. It uses retrieval-augmented generation (RAG): PDFs are extracted into text, divided into smaller passages, embedded and stored in a vector database, then retrieved as context for a language model's answer.

The main user interface is a Streamlit app. It can answer general AUTOSAR questions, answer questions about PDFs uploaded in the app, and generate a PlantUML block diagram when a prompt includes `/bd`.

## How the project fits together

```text
PDF uploaded in Streamlit
        |
        v
AutosarLoader (extract PDF text) -> AutosarSplitter (make chunks)
        |
        v
Qdrant vector database <- Ollama embeddings
        |
User question -> retrieve relevant chunks -> Ollama/OpenAI chat model
        |
        v
Streamlit answer (and optionally a PlantUML diagram)

PostgreSQL stores assistant/chat runs and history.
```

### Main application flow

1. `app.py` builds the Streamlit page, model selectors, chat, PDF uploader, and knowledge-base controls.
2. `autosar_rag/autosar_loader.py` extracts PDF text into LangChain documents. The current loader reads at most the first five pages of each uploaded PDF.
3. `autosar_rag/autosar_splitter.py` splits extracted text into overlapping chunks before indexing.
4. `assistant/assistant.py` configures the Phidata assistant, Ollama or OpenAI chat model, Ollama embedder, Qdrant vector store, and PostgreSQL assistant storage.
5. For questions, the assistant retrieves relevant passages from Qdrant and supplies them to the selected language model as context.
6. Include `/bd` in a question to ask for a PlantUML block diagram based on `assets/autosar_basic.puml`. The generated PlantUML is rendered with the bundled PlantUML JAR.

Uploaded documents are added to the Qdrant knowledge base and remain available there until the knowledge base is cleared or its backing storage is removed. Chat/run storage is separate and is kept in PostgreSQL.

## Repository guide

| Path | Purpose |
| --- | --- |
| `app.py` | Main Streamlit interface and application orchestration. |
| `assistant/assistant.py` | Creates the assistant, language model, embedder, vector database, and PostgreSQL storage. |
| `autosar_rag/autosar_loader.py` | Extracts text and page metadata from uploaded PDFs. |
| `autosar_rag/autosar_splitter.py` | Splits PDF text into retrieval chunks. |
| `docparser/docparser.py` | A small alternative PDF parsing helper using Phidata's `PDFReader`. |
| `posthdl/puml2img.py` | Runs PlantUML to render a `.puml` diagram as an image. |
| `prompt/` | Prompt template model and assistant-related prompt code. |
| `assets/` | AUTOSAR reference PDFs, architecture diagrams, PlantUML examples, and the app's robot image. |
| `plantuml-1.2024.7.jar` | PlantUML renderer used for generated diagrams; Java is required to run it. |
| `cookbook/requirements.txt` | Pinned Python dependencies used to run the main app. |
| `cookbook/run_pgvector.sh` | Optional Docker command for starting the PostgreSQL/pgvector service used for assistant storage. |
| `cookbook/run_qdrant.sh` | Optional Docker command for starting Qdrant, which stores document embeddings. |
| `cookbook/langchain_retriever_ollama.py` | Separate LangChain/Ollama retrieval example in the cookbook. |
| `cookbook/data/` | Example AUTOSAR and demo documents for the cookbook. |
| `qa_chain/` | Earlier, separate LangChain QA-chain experiments and a notebook; these are not the entry point used by `app.py`. |
| `set_api_key.sh` | Bash helper to securely prompt for and export an OpenAI API key in the current shell. |

The main app uses the Phidata-based implementation in `assistant/`. The `qa_chain/` files and the cookbook retriever are exploratory examples with their own dependencies and should not be treated as part of the main app's startup path.

## Requirements

- Python 3.9.6 is the version recorded by the original project as its target. Other Python versions may require dependency adjustments.
- Docker, for PostgreSQL/pgvector and Qdrant.
- Ollama for local chat and embedding models.
- Java for PlantUML diagram rendering.
- Linux or macOS is the simplest environment for the provided shell scripts. The Streamlit app can also be run on Windows; use PowerShell equivalents for environment setup and start the Docker containers separately if needed.
- An OpenAI API key is optional and only needed if you select the OpenAI chat model.

The diagram-rendering helper currently calls the Unix `mv` command after running Java. Native Windows users may need a Unix-like `mv` available on `PATH` to use `/bd` diagram rendering.

## Setup

### 1. Install Ollama and download models

Install [Ollama](https://ollama.com/) and fetch the default chat and embedding models:

```shell
ollama pull llama3
ollama pull nomic-embed-text
```

Ollama must be running while using local models. The app also offers other model names in its selectors; download the selected model with `ollama pull <model>` before choosing it.

### 2. Create and activate a Python virtual environment

Linux/macOS:

```shell
python3 -m venv ~/.venvs/aienv
source ~/.venvs/aienv/bin/activate
```

Windows PowerShell:

```powershell
py -3.9 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use the Python executable directly from `.venv\Scripts\python.exe` and `.venv\Scripts\streamlit.exe`, or follow your organization's PowerShell execution-policy guidance.

### 3. Install Python dependencies

From the repository root, install the pinned dependency list:

```shell
pip install -r cookbook/requirements.txt
```

### 4. Install and start Docker

Install [Docker Desktop](https://docs.docker.com/get-started/get-docker/) or Docker Engine and ensure the Docker daemon is running.

### 5. Start PostgreSQL with pgvector

The provided helper script is intended for Bash:

```shell
./cookbook/run_pgvector.sh
```

Alternatively, run the Docker command directly:

```shell
docker run -d \
  -e POSTGRES_DB=ai \
  -e POSTGRES_USER=ai \
  -e POSTGRES_PASSWORD=ai \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v pgvolume:/var/lib/postgresql/data \
  -p 5532:5432 \
  --name pgvector \
  phidata/pgvector:16
```

The app connects to PostgreSQL on `localhost:5532` with the development database settings configured in `assistant/assistant.py`. Do not reuse these demo settings for a publicly exposed or production database.

### 6. Start Qdrant

The provided helper script is intended for Bash:

```shell
./cookbook/run_qdrant.sh
```

Alternatively, run Qdrant directly:

```shell
docker run -itd --name=qdrant \
  -p 6333:6333 \
  -p 6334:6334 \
  -e "QDRANT__SERVICE__API_KEY=123456" \
  -e "QDRANT__SERVICE__JWT_RBAC=true" \
  -v qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

The application is configured to connect to Qdrant at `http://localhost:6333` with the development API key shown above. Keep this service local; replace the demo credentials and configure appropriate access controls before exposing it to a network.

If Docker cannot pull the images, check network/proxy access or configure an accessible Docker image mirror.

### 7. (Optional) Configure OpenAI access

The default local Ollama model does not need an API key. To use the optional OpenAI model, set `OPENAI_API_KEY` in the environment where Streamlit will run.

Set it explicitly in the current shell:

```shell
export OPENAI_API_KEY="your-key"
```

PowerShell:

```powershell
$env:OPENAI_API_KEY = "your-key"
```

Do not commit API keys or put them in source files. If a real key was previously committed or shared, revoke it with its provider and create a replacement.

### 8. Run the app

From the repository root, with the virtual environment active and the database services and Ollama running:

```shell
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in a browser. Choose a model in the sidebar, ask an AUTOSAR question, or upload a PDF. To generate a block diagram, include `/bd` in the prompt. Use **Clear Knowledge Base** to remove indexed documents from Qdrant.

An example AUTOSAR PDF is available at `cookbook/data/AUTOSAR/AUTOSAR_CP_SWS_DiagnosticCommunicationManager-54-78.pdf`.

## Notes and limitations

- Switching embedding models requires documents to be indexed again with the selected embedder.
- The bundled PDFs and diagrams are reference materials; they are not all automatically loaded into the running app. Add a PDF through the UI to index it.
- The sample Docker ports, database credentials, and Qdrant API key are development defaults and are not suitable for deployment on an untrusted network.
- The legacy QA-chain code in `qa_chain/` is not wired into the Streamlit app and has different assumptions from the main application's Phidata setup.
