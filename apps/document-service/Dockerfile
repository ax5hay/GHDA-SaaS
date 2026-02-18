FROM python:3.12-slim AS builder
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy workspace files (if they exist)
COPY pnpm-lock.yaml pnpm-workspace.yaml ./

# Copy packages
COPY packages/db ./packages/db

# Copy service
COPY apps/document-service/pyproject.toml apps/document-service/
COPY apps/document-service/src ./apps/document-service/src

# Install Python dependencies
RUN pip install --no-cache-dir -e ./packages/db
RUN pip install --no-cache-dir -e ./apps/document-service

FROM python:3.12-slim
WORKDIR /app

# Copy installed packages
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source code
COPY apps/document-service/src ./apps/document-service/src

EXPOSE 8001
CMD ["uvicorn", "document_service.main:app", "--host", "0.0.0.0", "--port", "8001"]
