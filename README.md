# Online Mart - Microservices E-commerce Platform

An advanced microservices-based e-commerce platform featuring AI-powered search, chatbot assistance, and event-driven architecture.

## 🚀 Features

- **Microservices Architecture**: Scalable services for products, inventory, users, orders, payments, and notifications
- **AI Integration**: Gemini-powered chatbot with RAG capabilities for intelligent customer support
- **Event-Driven Communication**: Apache Kafka for asynchronous service communication
- **Modern Tech Stack**: Python, FastAPI, SQLModel, Docker, PostgreSQL
- **AI-Powered Search**: Pinecone vector database for semantic product search
- **Design Generation**: AI-powered product design and visualization capabilities
- **Cloud-Native**: Containerized with Docker for easy deployment anywhere

## 🏗️ Architecture Overview

The system consists of multiple interconnected microservices:

- **Product Services**: Product catalog management with AI-powered search via Pinecone
- **Inventory Services**: Real-time stock tracking and management
- **User Services**: Authentication, user profiles, and account management
- **Order Services**: Order processing and lifecycle management
- **Payment Services**: Secure payment processing
- **Notification Services**: Email and push notifications
- **AI Chatbot Services**: RAG-powered customer support chatbot
- **AI Design Generation**: Product design and visualization capabilities

## 🛠️ Technology Stack

- **Backend**: Python 3.12+, FastAPI
- **Database**: PostgreSQL with SQLModel (SQLAlchemy + Pydantic)
- **Message Broker**: Apache Kafka (Azure Event Hubs compatible)
- **AI/ML**: Google Gemini, Pinecone vector database, OpenRouter API
- **Frontend UI**: Chainlit for AI chatbot interface
- **Containerization**: Docker, Docker Compose
- **Dependency Management**: uv (Python package manager)
- **Messaging**: Apache Kafka for event-driven architecture

## 📁 Directory Structure

```
D:\online-mart-project/
├── .env
├── compose.yaml
├── pyproject.toml
├── uv.lock
├── ai_services/                 # AI chatbot and RAG services
│   ├── ai_chatbot/            # Main chatbot implementation
│   └── ai_design_generation_visualization/ # Design agents
├── product_services/           # Product catalog management
├── inventory_services/         # Inventory tracking
├── user_services/              # User authentication/profiles
├── order_services/             # Order processing
├── payment_services/           # Payment processing
├── notification_services/      # Notifications
└── ...
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.12+
- uv package manager
- API keys for Gemini and Pinecone

### Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd online-mart-project
   ```

2. Copy the environment file and add your API keys:
   ```bash
   cp .env.example .env
   ```
   Add your API keys to the `.env` file:
   - `GEMINI_API_KEY`: Google Gemini API key
   - `PINECONE_API_KEY`: Pinecone API key
   - `PINECONE_INDEX_NAME`: Name of your Pinecone index

3. Install dependencies:
   ```bash
   uv sync
   ```

4. Start all services:
   ```bash
   docker compose up -d
   ```

5. Access the services:
   - Product Service: http://localhost:8000
   - Inventory Service: http://localhost:8001
   - User Service: http://localhost:8002
   - Order Service: http://localhost:8003
   - Notification Service: http://localhost:8004
   - Payment Service: http://localhost:8005
   - AI Chatbot: http://localhost:8006
   - AI Design Service: http://localhost:8007
   - Kafka UI: http://localhost:8081

### Stopping Services

```bash
docker compose down
```

## 🚢 Deployment

The application is containerized with Docker Compose for easy deployment anywhere. You can run it locally or deploy it to any container orchestration platform.

### Local Deployment

For local development and testing, simply use Docker Compose:

1. Make sure you have Docker and Docker Compose installed
2. Set up your environment variables in a `.env` file
3. Run the services with Docker Compose:

```bash
docker compose up -d
```

### Custom Deployment

For custom deployments to cloud platforms or your own infrastructure:
1. Build the Docker images using the provided Dockerfiles
2. Push images to your preferred container registry
3. Configure your environment with the necessary environment variables
4. Deploy the services using your preferred container orchestration platform

## 🔐 Environment Variables

The application uses several environment variables for configuration:

- `GEMINI_API_KEY`: Google Gemini API key for AI services
- `PINECONE_API_KEY`: Pinecone API key for vector database
- `PINECONE_INDEX_NAME`: Name of the Pinecone index
- `DATABASE_URL`: PostgreSQL connection string
- `BOOTSTRAP_SERVER`: Kafka broker address
- `KAFKA_*_TOPIC`: Various Kafka topic names
- `OPENROUTER_API_KEY`: OpenRouter API key for AI models

## 🧪 Testing

To run tests for a specific service:
```bash
cd <service_directory>
python -m pytest
```

## 🤖 AI Services

### AI Chatbot
- RAG (Retrieval Augmented Generation) system for knowledge base queries
- Vector embeddings using Pinecone for semantic search
- Chainlit-based chatbot UI
- Integration with Google Gemini model via OpenRouter API
- Session persistence using SQLite

### AI Design Generation & Visualization
- Professional product design and visualization capabilities
- Image generation with Base64 conversion
- Technical specifications for print optimization
- Visual DNA extraction from reference images

## 📊 Kafka Topics

The system uses the following Kafka topics for inter-service communication:
- `product-topic`: Product-related events
- `inventory-topic`: Inventory updates
- `user-topic`: User-related events
- `order-topic`: Order processing events
- `notification-topic`: Notification triggers
- `payment-topic`: Payment events
- `design-topic`: Design generation requests

## 🚨 Troubleshooting

### Common Issues

1. **Service startup failures**: Check that all required environment variables are set
2. **Database connection issues**: Verify PostgreSQL connection strings and credentials
3. **Kafka connectivity**: Ensure the Kafka broker is running and accessible
4. **AI service errors**: Confirm API keys are valid and have sufficient quota

### Logs

View service logs:
```bash
docker compose logs -f <service_name>
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support, please open an issue in the GitHub repository.