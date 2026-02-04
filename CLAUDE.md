
## CLAUDE.md

### Project Overview

This project is a microservices-based online mart application. It is designed with separate services for products, inventory, users, orders, notifications, and payments, orchestrated using Docker Compose and communicating via Kafka.

### Technology Stack

*   **Programming Language**: Python
*   **Containerization**: Docker, Docker Compose
*   **Message Broker**: Apache Kafka
*   **Database**: PostgreSQL
*   **API Gateway**: Kong (commented out in `compose.yaml`)
*   **Dependency Management**: Poetry

### Directory Structure

```
D:\\Hasaan's_Work\\Projects\\Online_Mart_Project\\Online_mart_Project/\
├── .env
├── .gitignore
├── compose.yaml
├── inventory_services
│   ├── Dockerfile
│   ├── inventory_services
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   ├── conusmer.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── model.py
│   │   ├── producer.py
│   │   ├── Producer_for_order.py
│   │   ├── setting.py
│   │   └── tests
│   │       └── __init__.py
│   ├── poetry.lock
│   ├── pyproject.toml
│   └── README.md
├── notification_services
│   ├── Dockerfile
│   ├── env_config.txt
│   ├── notification_services
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   ├── Consumer
│   │   │   ├── __pycache__
│   │   │   ├── kafka_order_consumer.py
│   │   │   ├── kafka_payment_consumer.py
│   │   │   └── kafka_user_consumer.py
│   │   ├── database.py
│   │   ├── email_services.py
│   │   ├── main.py
│   │   └── setting.py
│   ├── poetry.lock
│   ├── pyproject.toml
│   └── README.md
├── order_services
│   ├── Dockerfile
│   ├── order_services
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   ├── authenticate.py
│   │   ├── consumer.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── producer.py
│   │   ├── setting.py
│   │   └── utils.py
│   ├── poetry.lock
│   ├── pyproject.toml
│   └── README.md
├── payment_services
│   ├── Dockerfile
│   ├── payment_services
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   ├── authentication.py
│   │   ├── consumer.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── model.py
│   │   ├── producer.py
│   │   ├── schema.py
│   │   └── setting.py
│   ├── poetry.lock
│   ├── pyproject.toml
│   └── README.md
├── product_services
│   ├── Dockerfile
│   ├── poetry.lock
│   ├── product_services
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   ├── consumer.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── producer.py
│   │   ├── product_event.py
│   │   └── setting.py
│   ├── pyproject.toml
│   └── README.md
├── user_services
│   ├── Dockerfile
│   ├── poetry.lock
│   ├── pyproject.toml
│   ├── README.md
│   ├── tests
│   │   └── __init__.py
│   └── user_services
│       ├── __init__.py
│       ├── __pycache__
│       ├── consumer.py
│       ├── database.py
│       ├── main.py
│       ├── model.py
│       ├── producer.py
│       ├── schema.py
│       ├── setting.py
│       └── utils.py
└── Readme.md
```

### Coding Conventions

*   **Python**: Based on the presence of `pyproject.toml` and `poetry.lock` files in each service, it's assumed Poetry is used for dependency management and linting/formatting might be configured within `pyproject.toml`.
*   **Dockerfiles**: Each service has a `Dockerfile` indicating a containerized build process.
*   **Environment Variables**: Usage of `.env` file and environment variables (e.g., `${POSTGRES_USER_PRODUCT}`) suggests configuration is managed via environment variables, likely loaded from `.env` by Docker Compose.
*   **File Naming**: Consistent use of `snake_case` for Python files and directories.
*   **Comments**: Comments in `compose.yaml` provide explanations for configurations.

### Key Commands

*   **Start all services**:
    ```bash
    docker compose up -d
    ```
*   **Stop all services**:
    ```bash
    docker compose down
    ```
*   **View logs**:
    ```bash
    docker compose logs -f <service_name>
    ```
    (e.g., `docker compose logs -f product_services`)
*   **Install dependencies for a specific service**:
    ```bash
    cd <service_directory>
    poetry install
    ```
    (e.g., `cd product_services && poetry install`)
*   **Run tests for a specific service**:
    ```bash
    cd <service_directory>
    poetry run pytest
    ```
    (e.g., `cd user_services && poetry run pytest`)

### Important Notes

*   **Database Credentials**: The `compose.yaml` file uses environment variables for PostgreSQL credentials (e.g., `${POSTGRES_USER_PRODUCT}`). Ensure these variables are properly set in a `.env` file in the root directory.
*   **Kafka Configuration**: The Kafka setup in `compose.yaml` uses specific listener configurations. The `kafka-ui` service depends on `broker:19092` for connection.
*   **Commented-out Services**: Several services and configurations (e.g., Kong, notification DB) are commented out in `compose.yaml`. They can be uncommented and configured if needed.
*   **`.env` File**: The presence of `.env` in `.gitignore` suggests it contains sensitive information and should not be committed to version control.
*   **Database Health Checks**: PostgreSQL services have health checks configured to ensure services depending on them start only after the database is ready.
