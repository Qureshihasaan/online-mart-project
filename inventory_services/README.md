# 📦 Inventory Service

> Tracks stock levels for the Online Mart platform — automatically synced via Kafka events from Product and Order services.

---

## ✨ Features

- **Stock Tracking** — Real-time product quantity and status tracking
- **Inventory Checks** — API endpoint for other services to verify stock availability
- **Event-Driven Sync** — Kafka consumers auto-update stock from product and order events
- **RESTful API** — FastAPI-based endpoints for inventory queries

---

## 🚀 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/get_stock_update` | Retrieve all stock records |
| `GET` | `/get_single_stock_update` | Get a stock record by `stock_id` query param |
| `GET` | `/check_inventory/{product_id}/{quantity}` | Check if product has sufficient stock |
| `DELETE` | `/delete_stock{stock_id}` | Delete a stock record |

### Check Inventory Response

```json
{ "available": true }
```

Returns `true` if the product has `>= quantity` in stock, `false` otherwise.

---

## 📊 Data Models

**Stock_update** (database table)

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Primary key (auto-generated) |
| `product_id` | `int` | Reference to the product |
| `product_name` | `str` | Product name |
| `product_quantity` | `int` | Current stock quantity |
| `status` | `str` | Stock status (default: `"In Stock"`) |

**Inventory_update** (update schema)

| Field | Type |
|-------|------|
| `product_id` | `int` |
| `product_quantity` | `int` |
| `status` | `str` |

---

## 📂 Project Structure

```
inventory_services/
├── inventory_services/
│   ├── __init__.py
│   ├── main.py                # FastAPI app — endpoints
│   ├── model.py               # SQLModel models
│   ├── database.py            # Engine & table creation
│   ├── setting.py             # Environment config
│   ├── conusmer.py            # Kafka consumers (product + order events)
│   ├── producer.py            # Kafka producer
│   └── Producer_for_order.py  # Order-specific producer
├── tests/
├── Dockerfile
├── pyproject.toml
└── .env
```

---

## ⚙️ Environment Variables

| Variable | Description |
|----------|-------------|
| `INVENTORY_DATABASE_URL` | PostgreSQL connection string |
| `KAFKA_BOOTSTRAP_SERVER` | Kafka broker address |
| `KAFKA_PRODUCT_TOPIC` | Topic for consuming product events |
| `KAFKA_ORDER_TOPIC` | Topic for consuming order events |
| `KAFKA_CONSUMER_GROUP_ID_FOR_INVENTORY` | Kafka consumer group ID |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **FastAPI** | REST API framework |
| **SQLModel** | Database ORM |
| **AIOKafka** | Kafka consumers for event-driven sync |
| **psycopg2** | PostgreSQL adapter |

---

## 🐳 Docker

```bash
docker build -t inventory-service .
docker run -p 8001:8000 --env-file .env inventory-service
```

---

## 🏃 Local Development

```bash
uv sync
uvicorn inventory_services.main:app --reload
```

- **Swagger UI** — http://localhost:8001/docs
- **ReDoc** — http://localhost:8001/redoc

---

## 📡 Kafka Event Flow

**Consumes:**

| Source | Events |
|--------|--------|
| Product Service | `Product_Created`, `Product_Updated`, `Product_Deleted` |
| Order Service | `Order_Created` (adjusts stock levels) |

**Provides:**

- `/check_inventory/{product_id}/{quantity}` — Called by Order Service before creating an order