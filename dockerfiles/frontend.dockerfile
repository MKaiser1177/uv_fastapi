FROM python:3.13-slim

COPY frontend/ /app/

RUN pip install --no-cache-dir uv

WORKDIR /app

RUN uv sync --no-dev

CMD ["uv", "run", "streamlit", "run", "src/frontend/dashboard.py", "--server.address=0.0.0.0"]