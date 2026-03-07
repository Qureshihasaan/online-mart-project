# AI Chatbot Service

AI-powered chatbot for the Online Mart platform (Takhleeq). Uses Retrieval Augmented Generation (RAG) with Pinecone vector search and the OpenAI Agents SDK to answer user queries about products and platform features.

## Features

- **AI-Powered Conversations**: Intelligent responses using Google Gemini model via OpenRouter
- **RAG (Retrieval Augmented Generation)**: Searches a Pinecone knowledge base for accurate, grounded answers
- **Session Persistence**: Conversation history stored in SQLite via the OpenAI Agents SDK
- **Streaming Responses**: Real-time token streaming for responsive chat
- **Dynamic Instructions**: Configurable AI behavior through `dynamic_instruction.md`
- **FastAPI REST API**: HTTP endpoint for integration with frontends and other services

## Architecture

| Component | File | Description |
|-----------|------|-------------|
| **REST API** | `app.py` | FastAPI app with `/chat` and `/health` endpoints |
| **Core Logic** | `chatbot.py` | Agent definition, RAG tool, streaming, session management |
| **Vector Embedding** | `vector_embedding.py` | Pinecone integration for knowledge base ingestion |
| **Instructions** | `dynamic_instruction.md` | System prompt loaded at runtime |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/chat` | Send a message and get an AI response |

### `POST /chat`

**Request:**

```json
{
  "message": "What is Takhleeq?",
  "session_id": "optional-session-id"
}
```

**Response:**

```json
{
  "reply": "Takhleeq is ...",
  "session_id": "uuid-for-continuing-conversation"
}
```

## Dependencies

- **FastAPI** — REST API framework
- **Uvicorn** — ASGI server
- **OpenAI Agents SDK** — Agent orchestration with function tools
- **Pinecone** — Vector database for knowledge base search
- **python-dotenv** — Environment variable management

## Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | OpenRouter API key for LLM access |
| `PINECONE_API_KEY` | Pinecone API key for vector search |

## Usage

```bash
uvicorn app:app --host 0.0.0.0 --port 8006 --reload
```

The service will be available at `http://localhost:8006` — API docs at `/docs`.

### CLI Mode

You can also run the chatbot interactively from the terminal:

```bash
python chatbot.py
```

## Configuration

The chatbot's behavior is configured via `dynamic_instruction.md`, which defines:

- System persona and role
- Response formatting guidelines
- Safety and moderation rules
- Knowledge base search behavior