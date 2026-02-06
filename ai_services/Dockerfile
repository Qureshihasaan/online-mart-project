FROM python:3.12-slim

WORKDIR /code

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /code

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn openai pinecone-client

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]