# Online Mart - Microservices Architecture

A modern e-commerce platform built with a microservices architecture using Python, FastAPI, PostgreSQL, and Apache Kafka for inter-service communication. The platform includes AI-powered features for enhanced user experience.

## 🏗️ Architecture Overview

This application follows a microservices architecture with the following core services:

- **Product Services**: Manages product catalog with AI-powered search capabilities using Pinecone vector database
- **User Services**: Handles user authentication, profiles, and account management
- **Order Services**: Manages order processing and lifecycle
- **Inventory Services**: Tracks stock levels and inventory management
- **Payment Services**: Processes payments and transactions
- **Notification Services**: Sends notifications via email and other channels
- **AI Services**: AI chatbot with RAG (Retrieval Augmented Generation) and AI-powered design generation & product visualization

## 🛠️ Tech Stack

- **Backend**: Python 3.12+, FastAPI
- **Database**: PostgreSQL with SQLModel (SQLAlchemy + Pydantic)
- **Message Broker**: Apache Kafka
- **Containerization**: Docker, Docker Compose
- **Dependency Management**: uv
- **AI/Vector Database**: Pinecone for vector embeddings and RAG
- **AI Integration**: Google Gemini with OpenRouter API
- **AI Agents**: OpenAI Agents SDK for agent orchestration
- **Image Generation**: Flux & Gemini models via OpenRouter

## 📁 Directory Structure

```
online-mart-project/
├── .env                      # Environment variables
├── compose.yaml             # Docker Compose configuration
├── pyproject.toml           # Project dependencies
├── ai_services/             # AI chatbot and design generation services
│   ├── ai_chatbot/          # Main chatbot implementation
│   └── ai_design_generation_visualization/ # Design agents
├── product_services/        # Product catalog management
├── user_services/           # User authentication and profiles
├── order_services/          # Order processing
├── inventory_services/      # Inventory tracking
├── payment_services/        # Payment processing
├── notification_services/   # Notifications
└── ...
```

## 🚀 Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd online-mart-project
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

   Add your API keys to the `.env` file:
   - `GEMINI_API_KEY`: Google Gemini API key
   - `PINECONE_API_KEY`: Pinecone API key
   - `PINECONE_INDEX_NAME`: Name of the Pinecone index
   - Other database and Kafka configurations

3. **Install dependencies**
   ```bash
   uv sync
   ```

4. **Start all services with Docker Compose**
   ```bash
   docker compose up -d
   ```

5. **Access the services**
   - Product Service: http://localhost:8000
   - Inventory Service: http://localhost:8001
   - User Service: http://localhost:8002
   - Order Service: http://localhost:8003
   - Notification Service: http://localhost:8004
   - Payment Service: http://localhost:8005
   - AI Chatbot: http://localhost:8006
   - AI Design Visualization: http://localhost:8007

## 🔧 Running Individual Services

To run a specific service locally for development:

```bash
cd product_services
uv sync
python -m product_services.main
```

For the AI chatbot service:
```bash
cd ai_services/ai_chatbot
uvicorn app:app --host 0.0.0.0 --port 8006 --reload
```

## 🧪 Testing

To run tests for a specific service:
```bash
cd <service_directory>
python -m pytest
```

## 🌐 API Documentation

Each service provides automatic API documentation:
- Product Service: http://localhost:8000/docs
- Inventory Service: http://localhost:8001/docs
- User Service: http://localhost:8002/docs
- Order Service: http://localhost:8003/docs
- Notification Service: http://localhost:8004/docs
- Payment Service: http://localhost:8005/docs
- AI Chatbot: http://localhost:8006/docs
- AI Design Visualization: http://localhost:8007/docs

## 🤖 AI Features

The platform includes advanced AI capabilities:

- **AI Chatbot**: RAG (Retrieval Augmented Generation) system for knowledge base queries with vector embeddings in Pinecone
- **AI Design Generation**: Product design and visualization capabilities with technical specifications for print optimization
- **AI-Powered Search**: Semantic search using vector embeddings for better product discovery

## 🚢 Deployment

The application is designed for containerized deployment using Docker Compose. Production deployment can be achieved by:

1. Configuring environment variables for production
2. Setting up production-grade databases
3. Configuring load balancers and monitoring
4. Using orchestration platforms like Kubernetes

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.