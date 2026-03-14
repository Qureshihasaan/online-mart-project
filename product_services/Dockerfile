FROM python:3.12-slim

LABEL maintainer="hasaanqureshi"

WORKDIR /code

RUN  apt-get update && apt-get install -y\
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install uv

COPY pyproject.toml /code/pyproject.toml

COPY . .

# RUN uv sync --frozen --no-install-project

EXPOSE 8000

# Production-ready command without --reload
CMD [ "uv", "run", "uvicorn", "product_services.main:app", "--host", "0.0.0.0", "--port", "8000" ]