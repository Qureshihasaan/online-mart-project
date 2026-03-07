# 🛒 Online Mart — Microservices E-Commerce Platform

> A modern e-commerce platform built with **Python**, **FastAPI**, **Apache Kafka**, and **AI-powered services** — following a microservices architecture for scalability and modularity.

---

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────┐
│                          API Gateway (Kong)                              │
│                         ports: 8008 / 8009                               │
└────────────────────────────────┬─────────────────────────────────────────┘
                                 │
     ┌───────────┬───────────┬───┴────┬────────────┬────────────┬─────────┐
     ▼           ▼           ▼        ▼            ▼            ▼         ▼
┌─────────┐┌─────────┐┌─────────┐┌─────────┐┌──────────┐┌─────────┐┌─────────┐
│ Product ││  User   ││  Order  ││Inventory││Notifica- ││ Payment ││   AI    │
│ Service ││ Service ││ Service ││ Service ││  tion    ││ Service ││Services │
│  :8000  ││  :8002  ││  :8003  ││  :8001  ││  :8004   ││  :8005  ││:8006-07 │
└────┬────┘└────┬────┘└────┬────┘└────┬────┘└────┬─────┘└────┬────┘└─────────┘
     │          │          │          │          │           │
     └──────────┴──────────┴──────┬───┴──────────┴───────────┘
                                  ▼
                        ┌──────────────────┐
                        │   Apache Kafka   │
                        │    (broker)      │
                        └──────────────────┘
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| **Product Service** | `8000` | Product catalog CRUD with Kafka event streaming |
| **Inventory Service** | `8001` | Stock tracking, synced via Kafka product/order events |
| **User Service** | `8002` | User registration, JWT authentication, profiles |
| **Order Service** | `8003` | Order processing with inventory checks and auth |
| **Notification Service** | `8004` | Event-driven email notifications via Kafka consumers |
| **Payment Service** | `8005` | Payment records and transaction management |
| **AI Chatbot** | `8006` | RAG-powered chatbot with Pinecone vector search |
| **AI Design Visualization** | `8007` | AI design generation & product visualization pipeline |
| **Kafka UI** | `8081` | Web UI for monitoring Kafka topics and messages |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.12+** | Core language |
| **FastAPI** | REST API framework for all services |
| **SQLModel** | Database ORM (SQLAlchemy + Pydantic) |
| **PostgreSQL** | Persistent storage (per-service databases) |
| **Apache Kafka** | Event streaming & inter-service communication |
| **Docker & Compose** | Containerization and orchestration |
| **uv** | Fast Python dependency management |
| **Pinecone** | Vector database for AI search & RAG |
| **OpenAI Agents SDK** | Agent orchestration with function tools |
| **OpenRouter** | LLM/image model gateway (Gemini, Qwen, Flux) |

---

## 📁 Project Structure

```
online-mart-project/
├── compose.yaml                 # Docker Compose — all services
├── .env                         # Root environment variables
├── pyproject.toml               # Root dependencies
│
├── product_services/            # Product catalog management
├── user_services/               # Authentication & user profiles
├── order_services/              # Order processing
├── inventory_services/          # Stock tracking
├── notification_services/       # Event-driven email notifications
├── payment_services/            # Payment processing
│
└── ai_services/
    ├── ai_chatbot/              # RAG chatbot with Pinecone
    └── ai_design_generation_visualization/  # Design generation & product mockups
```

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd online-mart-project
```

### 2. Set up environment variables

```bash
cp .env.example .env
```

Add your API keys to `.env`:

```env
GEMINI_API_KEY=your-gemini-key
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=online-mart-products
OPENROUTER_API_KEY=your-openrouter-key
```

### 3. Start all services

```bash
docker compose up -d
```

### 4. Access the services

| Service | URL |
|---------|-----|
| Product Service | http://localhost:8000/docs |
| Inventory Service | http://localhost:8001/docs |
| User Service | http://localhost:8002/docs |
| Order Service | http://localhost:8003/docs |
| Notification Service | http://localhost:8004/docs |
| Payment Service | http://localhost:8005/docs |
| AI Chatbot | http://localhost:8006/docs |
| AI Design Visualization | http://localhost:8007/docs |
| Kafka UI | http://localhost:8081 |

---

## 🔧 Running Individual Services

```bash
cd product_services
uv sync
uvicorn product_services.main:app --reload
```

For AI services:

```bash
cd ai_services/ai_chatbot
uv sync
uvicorn app:app --host 0.0.0.0 --port 8006 --reload
```

---

## 🧪 Testing

```bash
cd <service_directory>
python -m pytest
```

---

## 🤖 AI Features

- **AI Chatbot** — RAG system with Pinecone vector search for intelligent product Q&A
- **AI Design Generation** — Text-to-design generation using Flux models via OpenRouter
- **Product Visualization** — AI-powered design application onto product mockups with color enhancement
- **Semantic Search** — Vector embeddings for natural language product discovery (planned)

---

## 📜 License

This project is licensed under the MIT License.
