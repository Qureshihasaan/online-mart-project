# 📦 Product Service

> Manages the product catalog for the Online Mart platform — CRUD operations with Kafka event streaming for real-time inter-service communication.

---

## ✨ Features

- **Product CRUD** — Create, read, update, and delete product listings
- **Kafka Events** — Publishes product lifecycle events for other services to consume
- **Kafka Consumer** — Listens for product-related events from other services
- **PostgreSQL Storage** — Persistent product data with SQLModel ORM

---

## 🚀 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/product` | Create a new product |
| `GET` | `/product/` | Retrieve all products |
| `PUT` | `/product/{product_id}` | Update a specific product |
| `DELETE` | `/product/{product_id}` | Delete a specific product |

---

## 📊 Data Model

**Product**

| Field | Type | Description |
|-------|------|-------------|
| `product_id` | `int` | Primary key (auto-generated) |
| `Product_name` | `str` | Name of the product |
| `Product_details` | `str` | Product description |
| `product_quantity` | `int` | Available quantity (default: `0`) |
| `price` | `float` | Price (must be > 0) |

---

## 📂 Project Structure

```
product_services/
├── product_services/
│   ├── __init__.py
│   ├── main.py          # FastAPI app — endpoints
│   ├── database.py      # SQLModel models & engine
│   ├── setting.py       # Environment config
│   ├── consumer.py      # Kafka consumer
│   ├── producer.py      # Kafka producer
│   └── product_event.py # Event definitions
├── tests/
├── Dockerfile
├── pyproject.toml
└── .env
```

---

## ⚙️ Environment Variables

| Variable | Description |
|----------|-------------|
| `PRODUCT_SERVICE_DATABASE_URL` | PostgreSQL connection string |
| `KAFKA_BOOTSTRAP_SERVER` | Kafka broker address |
| `KAFKA_PRODUCT_TOPIC` | Topic for product events |
| `KAFKA_CONSUMER_GROUP_ID_FOR_PRODUCT` | Kafka consumer group ID |
| `GEMINI_API_KEY` | Google Gemini API key (AI features) |
| `PINECONE_API_KEY` | Pinecone API key |
| `PINECONE_INDEX_NAME` | Pinecone index name (default: `online-mart-products`) |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | REST API framework |
| **SQLModel** | Database ORM |
| **AIOKafka** | Kafka producer/consumer |
| **psycopg2** | PostgreSQL adapter |
| **Pinecone** | Vector database (planned) |
| **Google Generative AI** | AI features (planned) |

---

## 🐳 Docker

```bash
docker build -t product-service .
docker run -p 8000:8000 --env-file .env product-service
```

---

## 🏃 Local Development

```bash
uv sync
uvicorn product_services.main:app --reload
```

- **Swagger UI** — http://localhost:8000/docs
- **ReDoc** — http://localhost:8000/redoc

---

## 📡 Kafka Event Flow

| Event | Trigger |
|-------|---------|
| `Product_Created` | New product added |
| `Product_Updated` | Product details modified |
| `Product_Deleted` | Product removed |

Events are consumed by **Inventory Service** to auto-sync stock records.