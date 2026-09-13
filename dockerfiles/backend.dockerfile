FROM python:3.13-slim

COPY backend/ /app/

RUN pip install --no-cache-dir uv

WORKDIR /app

RUN uv sync --no-dev

CMD ["uv", "run", "uvicorn", "backend.api:app", "--host", "0.0.0.0"]