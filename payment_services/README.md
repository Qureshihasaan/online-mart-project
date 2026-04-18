# 💳 Payment Service

> Manages payment records and transaction processing for the Online Mart platform — with Kafka event streaming for notifications and order coordination.

---

## ✨ Features

- **Payment CRUD** — Create, read, update, and delete payment records
- **Status Tracking** — Track payment status (`Pending`, `Completed`, `Failed`)
- **Kafka Events** — Publishes payment events for Notification Service
- **Kafka Consumer** — Listens for payment-related events

---

## 🚀 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/create_payment/` | Create a new payment record |
| `GET` | `/get_all_payment` | Retrieve all payments |
| `GET` | `/get_single_payment` | Get a payment by `payment_id` query param |
| `PUT` | `/update_payment` | Update a payment by `payment_id` query param |
| `DELETE` | `/delete_payment` | Delete a payment by `payment_id` query param |

---

## 📊 Data Models

**Payment** (database table)

| Field | Type | Description |
|-------|------|-------------|
| `payment_id` | `int` | Primary key (auto-generated) |
| `order_id` | `int` | Reference to the associated order |
| `amount` | `float` | Payment amount |
| `status` | `str` | `"Pending"` / `"Completed"` / `"Failed"` |

**payment_response**

| Field | Type |
|-------|------|
| `payment_id` | `int` |
| `order_id` | `int` |
| `amount` | `float` |
| `status` | `str` |

---

## 📂 Project Structure

```
payment_services/
├── payment_services/
│   ├── __init__.py
│   ├── main.py             # FastAPI app — endpoints
│   ├── model.py            # SQLModel models
│   ├── database.py         # Engine & session
│   ├── setting.py          # Environment config
│   ├── consumer.py         # Kafka consumer
│   ├── producer.py         # Kafka producer
│   └── authentication.py   # Auth utilities
├── tests/
├── Dockerfile
├── pyproject.toml
└── .env
```

---

## ⚙️ Environment Variables

| Variable | Description |
|----------|-------------|
| `PAYMENT_DATABASE_URL` | PostgreSQL connection string |
| `KAFKA_BOOTSTRAP_SERVER` | Kafka broker address |
| `KAFKA_PAYMENT_TOPIC` | Topic for payment events |
| `KAFKA_CONSUMER_GROUP_ID_FOR_PAYMENT` | Kafka consumer group ID |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | REST API framework |
| **SQLModel** | Database ORM |
| **AIOKafka** | Kafka producer/consumer |
| **psycopg2** | PostgreSQL adapter |

---

## 🐳 Docker

```bash
docker build -t payment-service .
docker run -p 8005:8000 --env-file .env payment-service
```

---

## 🏃 Local Development

```bash
uv sync
uvicorn payment_services.main:app --reload
```

- **Swagger UI** — http://localhost:8005/docs
- **ReDoc** — http://localhost:8005/redoc

---

## 📡 Kafka Event Flow

| Event | Trigger |
|-------|---------|
| `Payment_Created` | New payment record created |

Events are consumed by **Notification Service** to send payment confirmation emails.