# 🛍️ Order Service

> Manages order processing for the Online Mart platform — with inventory validation, JWT authentication, and Kafka event streaming.

---

## ✨ Features

- **Order Management** — Create, read, update, and delete orders
- **Inventory Validation** — Checks stock availability via the Inventory Service before order creation
- **JWT Authentication** — Orders are tied to authenticated users via token verification
- **Kafka Events** — Publishes order lifecycle events
- **CORS Support** — Cross-origin resource sharing enabled

---

## 🚀 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/create_order` | Create a new order (requires JWT) |
| `PUT` | `/update_order{order_id}` | Update an existing order |
| `GET` | `/get_order` | Retrieve all orders |
| `GET` | `/get_single_order` | Get a single order by `order_id` query param |
| `DELETE` | `/delete_order` | Delete an order by `order_id` query param |

---

## 📊 Data Models

**Order** (database table)

| Field | Type | Description |
|-------|------|-------------|
| `order_id` | `int` | Primary key (auto-generated) |
| `user_id` | `int` | ID of the ordering user (set from JWT) |
| `user_email` | `EmailStr` | User's email address |
| `product_id` | `int` | ID of the ordered product |
| `total_amount` | `int` | Total order amount |
| `product_quantity` | `int` | Quantity ordered |
| `payment_status` | `str` | Status (default: `"Pending"`) |

**OrderResponse**

| Field | Type |
|-------|------|
| `order_id` | `int` |
| `user_id` | `int` |
| `product_id` | `int` |
| `total_amount` | `int` |
| `product_quantity` | `int` |
| `payment_status` | `str` |

---

## 📂 Project Structure

```
order_services/
├── order_services/
│   ├── __init__.py
│   ├── main.py           # FastAPI app — endpoints
│   ├── database.py       # SQLModel models & engine
│   ├── authenticate.py   # JWT token verification
│   ├── setting.py        # Environment config
│   ├── consumer.py       # Kafka consumer
│   ├── producer.py       # Kafka producer
│   └── utils.py          # Utility functions
├── tests/
├── Dockerfile
├── pyproject.toml
└── .env
```

---

## ⚙️ Environment Variables

| Variable | Description |
|----------|-------------|
| `ORDER_DATABASE_URL` | PostgreSQL connection string |
| `KAFKA_BOOTSTRAP_SERVER` | Kafka broker address |
| `KAFKA_ORDER_TOPIC` | Topic for order events |
| `KAFKA_CONSUMER_GROUP_ID_FOR_ORDER` | Kafka consumer group ID |
| `KAFKA_TOPIC_FROM_USER_TO_ORDER` | Topic for user→order communication |
| `SECRET_KEY` | JWT signing secret key |
| `ALGORITHM` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration in minutes |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | REST API framework |
| **SQLModel** | Database ORM |
| **AIOKafka** | Kafka producer/consumer |
| **python-jose** | JWT token verification |
| **httpx** | HTTP client for inventory checks |
| **psycopg2** | PostgreSQL adapter |

---

## 🐳 Docker

```bash
docker build -t order-service .
docker run -p 8003:8000 --env-file .env order-service
```

---

## 🏃 Local Development

```bash
uv sync
uvicorn order_services.main:app --reload
```

- **Swagger UI** — http://localhost:8003/docs
- **ReDoc** — http://localhost:8003/redoc

---

## 📡 Kafka Event Flow

| Event | Trigger |
|-------|---------|
| `Order_Created` | New order placed |
| `Order_Updated` | Order details modified |
| `Order_Deleted` | Order removed |

Events are consumed by **Inventory Service** (stock adjustment) and **Notification Service** (email alerts).

---

## 🔗 Inter-Service Communication

- **Inventory Service** — `GET /check_inventory/{product_id}/{quantity}` is called before order creation to verify stock availability
- **User Service** — JWT tokens issued by User Service are verified via `authenticate.py`