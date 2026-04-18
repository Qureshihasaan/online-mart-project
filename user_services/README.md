# 👤 User Service

> Handles user registration, JWT-based authentication, and account management for the Online Mart platform.

---

## ✨ Features

- **User Registration** — Secure signup with bcrypt password hashing
- **JWT Authentication** — Token-based login with configurable expiration
- **Token Utilities** — Generate, decode, and verify access tokens
- **User Management** — List, view, and delete user accounts
- **Kafka Events** — Publishes user lifecycle events
- **CORS Support** — Cross-origin resource sharing enabled

---

## 🚀 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/Signup` | Register a new user |
| `POST` | `/login` | Login and receive a JWT access token |
| `GET` | `/get_access_token` | Generate an access token by username |
| `GET` | `/decode_token` | Decode and inspect a JWT token |
| `GET` | `/user/all` | Retrieve all users |
| `GET` | `/user/me` | Get the current authenticated user |
| `GET` | `/user/{user_id}` | Get a specific user (requires token) |
| `DELETE` | `/user/delete/{user_id}` | Delete a user |

---

## 📊 Data Models

**User** (database table)

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Primary key (auto-generated) |
| `username` | `str` | Unique username |
| `email` | `EmailStr` | Unique email address |
| `hashed_password` | `str` | Bcrypt-hashed password |

**CreateUser** (signup request body)

| Field | Type | Description |
|-------|------|-------------|
| `username` | `str` | Desired username |
| `email` | `EmailStr` | Email address |
| `plain_password` | `str` | Plain-text password (hashed before storage) |

**Token** (login response)

| Field | Type | Description |
|-------|------|-------------|
| `access_token` | `str` | JWT access token |
| `token_type` | `str` | Always `"bearer"` |

---

## 📂 Project Structure

```
user_services/
├── user_services/
│   ├── __init__.py
│   ├── main.py        # FastAPI app — endpoints
│   ├── model.py       # SQLModel models (User, CreateUser, Token)
│   ├── schema.py      # bcrypt context & authenticate_user
│   ├── utils.py       # JWT create/decode/verify functions
│   ├── database.py    # Engine & session setup
│   ├── setting.py     # Environment config
│   ├── consumer.py    # Kafka consumer
│   └── producer.py    # Kafka producer
├── tests/
├── Dockerfile
├── pyproject.toml
└── .env
```

---

## ⚙️ Environment Variables

| Variable | Description |
|----------|-------------|
| `USER_SERVICE_DATABASE_URL` | PostgreSQL connection string |
| `KAFKA_BOOTSTRAP_SERVER` | Kafka broker address |
| `KAFKA_USER_TOPIC` | Topic for user events |
| `KAFKA_CONSUMER_GROUP_ID_FOR_USER` | Kafka consumer group ID |
| `KAFKA_TOPIC_FROM_USER_TO_ORDER` | Topic for user→order communication |
| `SECRET_KEY` | JWT signing secret key |
| `ALGORITHMS` | JWT algorithm (e.g. `HS256`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration in minutes |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | REST API framework |
| **SQLModel** | Database ORM |
| **AIOKafka** | Kafka producer/consumer |
| **Passlib** | Password hashing (bcrypt) |
| **python-jose** | JWT encoding/decoding |
| **psycopg2** | PostgreSQL adapter |

---

## 🐳 Docker

```bash
docker build -t user-service .
docker run -p 8002:8000 --env-file .env user-service
```

---

## 🏃 Local Development

```bash
uv sync
uvicorn user_services.main:app --reload
```

- **Swagger UI** — http://localhost:8002/docs
- **ReDoc** — http://localhost:8002/redoc

---

## 📡 Kafka Event Flow

| Event | Trigger |
|-------|---------|
| `User_Created` | New user registered via `/Signup` |

Events are consumed by **Notification Service** to send welcome emails.