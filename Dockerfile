FROM python:3.10-slim

WORKDIR /app

COPY . /app

RUN apt-get update && apt-get install -y poppler-utils curl

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:${PATH}"

RUN uv sync

ENV PATH="/usr/local/bin:/root/.local/bin:${PATH}"

ENV UV_CACHE_DIR="/app/.cache/uv"

RUN mkdir -p "$UV_CACHE_DIR"

RUN chmod 777 -R "/app"

EXPOSE 7860

CMD ["uv", "run", "-m", "streamlit", "run", "main.py", "--server.address", "0.0.0.0", "--server.port", "7860"]