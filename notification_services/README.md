# 🔔 Notification Service

> Event-driven notification service for the Online Mart platform — consumes Kafka events from User, Order, and Payment services to send email notifications automatically.

---

## ✨ Features

- **Event-Driven Architecture** — No manual API calls needed; reacts to Kafka events
- **Multi-Consumer** — Runs three Kafka consumers in parallel (user, order, payment)
- **Email Notifications** — Sends emails for signups, order confirmations, and payment receipts
- **Graceful Shutdown** — Properly cancels consumer tasks on application shutdown

---

## 🚀 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Welcome message / health check |

> **Note**: This service is primarily event-driven. It listens to Kafka topics and sends notifications automatically — the main functionality is **not** exposed via REST endpoints.

---

## 🏗️ Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│ User Service │     │ Order Service│     │Payment Service│
└──────┬───────┘     └──────┬───────┘     └──────┬───────┘
       │                    │                    │
       ▼                    ▼                    ▼
┌──────────────────────────────────────────────────────┐
│                    Apache Kafka                       │
│  user_topic    │   order_topic   │  payment_topic    │
└──────┬─────────┴────────┬────────┴──────────┬────────┘
       │                  │                   │
       ▼                  ▼                   ▼
┌──────────────────────────────────────────────────────┐
│              Notification Service                     │
│                                                      │
│  ┌─────────────┐ ┌─────────────┐ ┌────────────────┐ │
│  │ User Consumer│ │Order Consumer│ │Payment Consumer│ │
│  └──────┬──────┘ └──────┬──────┘ └───────┬────────┘ │
│         │               │                │           │
│         └───────────────┼────────────────┘           │
│                         ▼                            │
│                  📧 Send Email                       │
└──────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
notification_services/
├── notification_services/
│   ├── __init__.py
│   ├── main.py              # FastAPI app & lifespan (starts consumers)
│   ├── email_services.py    # Email sending logic
│   ├── database.py          # Database models
│   ├── setting.py           # Environment config
│   └── Consumer/
│       ├── kafka_user_consumer.py     # Handles user events
│       ├── kafka_order_consumer.py    # Handles order events
│       └── kafka_payment_consumer.py  # Handles payment events
├── tests/
├── Dockerfile
├── pyproject.toml
└── .env
```

---

## ⚙️ Environment Variables

| Variable | Description |
|----------|-------------|
| `KAFKA_BOOTSTRAP_SERVER` | Kafka broker address |
| `KAFKA_USER_TOPIC` | Topic for user events |
| `KAFKA_ORDER_TOPIC` | Topic for order events |
| `KAFKA_PAYMENT_TOPIC` | Topic for payment events |
| `KAFKA_TOPIC_FOR_ORDER_CANCELLED` | Topic for order cancellation events |
| `KAFKA_CONSUMER_GROUP_ID_FOR_NOTIFICATION_SERVICE` | Kafka consumer group ID |
| `SENDER_EMAIL` | Sender email address |
| `SENDER_EMAIL_PASSWORD` | Sender email password / app password |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | App framework & lifespan management |
| **AIOKafka** | Kafka consumers |
| **smtplib** | Email delivery (Python built-in) |

---

## 🐳 Docker

```bash
docker build -t notification-service .
docker run -p 8004:8000 --env-file .env notification-service
```

---

## 🏃 Local Development

```bash
uv sync
uvicorn notification_services.main:app --reload
```

- **Swagger UI** — http://localhost:8004/docs

---

## 📡 Kafka Event Flow

| Consumer | Event | Action |
|----------|-------|--------|
| User Consumer | `User_Created` | Sends welcome email |
| Order Consumer | `Order_Created` | Sends order confirmation email |
| Payment Consumer | `Payment_Created` | Sends payment receipt email |