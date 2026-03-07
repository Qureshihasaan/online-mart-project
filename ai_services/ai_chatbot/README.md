# 🤖 AI Chatbot Service

> RAG-powered AI chatbot for the Online Mart platform (Takhleeq) — built with OpenAI Agents SDK, Pinecone vector search, and FastAPI.

---

## ✨ Features

- **AI-Powered Conversations** — Intelligent responses using Google Gemini via OpenRouter
- **RAG (Retrieval Augmented Generation)** — Searches Pinecone knowledge base for grounded, accurate answers
- **Session Persistence** — Conversation history stored in SQLite via the OpenAI Agents SDK
- **Streaming Responses** — Real-time token streaming for responsive chat
- **Dynamic Instructions** — Configurable AI behavior via `dynamic_instruction.md`
- **REST API** — Simple `/chat` endpoint for frontend integration

---

## 🚀 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/chat` | Send a message and get an AI response |

### `POST /chat`

**Request:**

```json
{
  "message": "What is Takhleeq?",
  "session_id": "optional-uuid-to-continue-conversation"
}
```

**Response:**

```json
{
  "reply": "Takhleeq is a creative design platform that...",
  "session_id": "abc12345-..."
}
```

Omit `session_id` to start a new conversation. Include it to continue a previous one.

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────┐
│                    FastAPI (app.py)                    │
│                   POST /chat                          │
└──────────────────────┬───────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│              OpenAI Agents SDK (chatbot.py)           │
│                                                      │
│   ┌─────────────────┐    ┌───────────────────────┐   │
│   │ Takhleeq Agent  │───▶│ search_knowledge_base │   │
│   │ (Gemini model)  │    │    (function tool)     │   │
│   └─────────────────┘    └───────────┬───────────┘   │
│                                      │               │
└──────────────────────────────────────┼───────────────┘
                                       │
                                       ▼
                              ┌─────────────────┐
                              │    Pinecone      │
                              │  Vector Search   │
                              │  + BGE Reranker  │
                              └─────────────────┘
```

---

## 📂 Project Structure

```
ai_chatbot/
├── app.py                   # FastAPI app — /chat and /health endpoints
├── chatbot.py               # Agent definition, RAG tool, streaming & sessions
├── vector_embedding.py      # Pinecone knowledge base ingestion
├── dynamic_instruction.md   # System prompt (loaded at runtime)
├── sessions/                # SQLite session storage directory
├── docs/                    # Documentation files
├── Dockerfile
├── pyproject.toml
└── .env
```

---

## ⚙️ Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENROUTER_API_KEY` | OpenRouter API key for LLM access (Gemini) |
| `PINECONE_API_KEY` | Pinecone API key for vector search |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | REST API framework |
| **Uvicorn** | ASGI server |
| **OpenAI Agents SDK** | Agent orchestration with function tools |
| **Pinecone** | Vector database for RAG knowledge base |
| **python-dotenv** | Environment variable management |

---

## 🐳 Docker

```bash
docker build -t ai-chatbot .
docker run -p 8006:8000 --env-file .env ai-chatbot
```

---

## 🏃 Local Development

```bash
uv sync
uvicorn app:app --host 0.0.0.0 --port 8006 --reload
```

- **Swagger UI** — http://localhost:8006/docs
- **ReDoc** — http://localhost:8006/redoc

### CLI Mode

Run an interactive terminal chat:

```bash
python chatbot.py
```

---

## 🧠 RAG Pipeline

1. User sends a message via `/chat`
2. Agent decides whether to call `search_knowledge_base` tool
3. Tool queries Pinecone with the user's question
4. Top results are re-ranked using BGE Reranker
5. Retrieved context is passed to the Gemini model
6. Model generates a grounded response