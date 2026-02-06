FROM python:3.12

LABEL maintainer="Hasaan Qureshi"

WORKDIR /code

RUN apt-get update && apt-get install -y\
    build-essential\
    libpq-dev\
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
RUN pip install uv

COPY pyproject.toml ./
COPY . .

RUN --mount=type=cache,target=/root/.cache/uv uv pip install --system -e .

EXPOSE 8000

CMD [ "uvicorn" , "user_services.main:app" , "--host" , "0.0.0.0" , "--reload" ]