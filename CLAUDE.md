# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project is a microservices-based online mart application. It implements a modern microservices architecture with separate services for products, inventory, users, orders, notifications, and payments. The services communicate via Apache Kafka and are orchestrated using Docker Compose.

## Technology Stack

* **Programming Language**: Python 3.12+
* **Web Framework**: FastAPI
* **Database**: PostgreSQL with SQLModel (SQLAlchemy + Pydantic)
* **Message Broker**: Apache Kafka
* **Containerization**: Docker, Docker Compose
* **Dependency Management**: uv (with pyproject.toml and uv.lock)
* **AI/Vector Database**: Pinecone for vector embeddings and RAG (Retrieval Augmented Generation)
* **AI Integration**: Google Gemini with OpenRouter API
* **Frontend UI**: Chainlit for AI chatbot interface

## Architecture Overview

### Core Services:
1. **Product Services** - Manages product catalog, integrates with Pinecone for AI-powered search
2. **Inventory Services** - Tracks stock levels and inventory management
3. **User Services** - Handles user authentication and profiles
4. **Order Services** - Manages order processing and lifecycle
5. **Payment Services** - Processes payments and transactions
6. **Notification Services** - Sends notifications via email and other channels
7. **AI Services** - Provides AI chatbot functionality with RAG capabilities

### Communication Pattern:
- Services communicate asynchronously via Apache Kafka topics
- Each service maintains its own database (microservices principle)
- Event-driven architecture with producers and consumers

### AI Integration:
- Vector embeddings stored in Pinecone for semantic search
- RAG (Retrieval Augmented Generation) system for AI responses
- Chainlit UI for chatbot interface
- Google Gemini model via OpenRouter API

## Directory Structure

```
D:\online-mart-project/
├── .env
├── compose.yaml
├── pyproject.toml
├── uv.lock
├── ai_services/                 # AI chatbot and RAG services
│   ├── ai_chatbot/            # Main chatbot implementation
│   │   ├── app.py             # Chainlit UI
│   │   ├── chatbot.py         # Core chatbot logic
│   │   └── dynamic_instruction.md # AI instructions
│   └── ai_design_generation_visualization/ # Design agents
├── product_services/           # Product catalog management
├── inventory_services/         # Inventory tracking
├── user_services/              # User authentication/profiles
├── order_services/             # Order processing
├── payment_services/           # Payment processing
├── notification_services/      # Notifications
└── ...
```

## Key Commands

* **Start all services**:
  ```bash
  docker compose up -d
  ```

* **Stop all services**:
  ```bash
  docker compose down
  ```

* **View logs**:
  ```bash
  docker compose logs -f <service_name>
  ```

* **Install dependencies** (for individual services):
  ```bash
  uv sync
  ```
  or
  ```bash
  pip install -e .
  ```

* **Run AI chatbot locally**:
  ```bash
  cd ai_services/ai_chatbot
  chainlit run app.py
  ```

* **Run tests for a specific service**:
  ```bash
  cd <service_directory>
  python -m pytest
  ```

## Important Notes

* **Environment Variables**: The `.env` file contains sensitive information and API keys (GEMINI_API_KEY, PINECONE_API_KEY). These are loaded in each service via starlette.config.
* **Kafka Configuration**: All services depend on the Kafka broker for inter-service communication.
* **Database Configuration**: Each service has its own PostgreSQL database with health checks configured.
* **AI Integration**: Product services integrate with Pinecone for vector embeddings, enabling AI-powered search capabilities.
* **API Endpoints**: Each service exposes REST APIs on different ports (product: 8000, inventory: 8001, user: 8002, order: 8003, notification: 8004, payment: 8005, ai: 8006).
* **Development Volumes**: Docker Compose mounts local directories to containers for live development.

## Development Workflow

1. **Setup**: Copy `.env.example` to `.env` and add required API keys
2. **Build**: Run `docker compose build` to build all services
3. **Run**: Execute `docker compose up -d` to start the system
4. **Develop**: Code changes are reflected in containers due to volume mounting
5. **Test**: Access services individually via their exposed ports

## AI Services Specifics

The AI services provide:
- **AI Chatbot Service**: RAG (Retrieval Augmented Generation) system for knowledge base queries
  - Vector embeddings using Pinecone for semantic search
  - Chainlit-based chatbot UI accessible at port 8006
  - Integration with Google Gemini model via OpenRouter API
  - Session persistence using SQLite
  - Dynamic instruction system for AI behavior control

- **AI Design Generation & Visualization Service**: Product design and visualization capabilities
  - Professional product design architecture for physical product printing
  - Image generation with Base64 conversion for processing
  - Technical specifications for print optimization (aspect ratios, resolution)
  - Visual DNA extraction from reference images
  - Zero-hallucination policy for precise design execution

## Environment Configuration

Key environment variables required in `.env` file:
- `GEMINI_API_KEY`: Google Gemini API key for AI models
- `PINECONE_API_KEY`: Pinecone API key for vector database
- `PINECONE_INDEX_NAME`: Name of the Pinecone index
- `PRODUCT_SERVICE_DATABASE_URL`: PostgreSQL connection string for product service
- `BOOTSTRAP_SERVER`: Kafka broker address (typically localhost:9092)
- `KAFKA_PRODUCT_TOPIC`: Kafka topic name for product events

## Development Considerations

- The project uses uv for dependency management (similar to Poetry but faster)
- Pinecone integration is implemented in product services for AI-powered search
- Each microservice follows the same pattern: FastAPI + SQLModel + Kafka producer/consumer
- The system supports both synchronous REST APIs and asynchronous event-driven communication
- AI services can run independently or integrated with the main microservices