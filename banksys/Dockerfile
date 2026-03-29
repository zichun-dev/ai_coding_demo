FROM python:3.11-slim

WORKDIR /app

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir uv

COPY pyproject.toml ./

COPY src/ ./src/

COPY data/ ./data/

RUN uv sync

EXPOSE 6100

CMD ["uv", "run", "python", "-m", "uvicorn", "src.backend.app:app", "--host", "0.0.0.0", "--port", "6100"]
