FROM python:3.11-slim

WORKDIR /app

# install uv (build-time tool only)
RUN pip install --no-cache-dir uv

# copy dependency metadata
COPY pyproject.toml uv.lock ./

# install deps into system python
RUN uv pip install --system .

# copy application code
COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
