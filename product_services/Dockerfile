FROM python:3.12-slim

LABEL maintainer="hasaanqureshi"

WORKDIR /code

# Install system dependencies required for psycopg2 and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install uv and uvicorn
RUN pip install --upgrade pip
RUN pip install uv uvicorn

# Copy project files
COPY pyproject.toml /code/pyproject.toml
# COPY uv.lock /code/uv.lock  

COPY . .

# Install dependencies using uv
# RUN uv sync --frozen

EXPOSE 8000

# Production-ready command without --reload
CMD ["uv", "run", "uvicorn", "product_services.main:app", "--host", "0.0.0.0", "--port", "8000"]

