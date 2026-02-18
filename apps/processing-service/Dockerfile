FROM python:3.12-slim AS builder
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    tesseract-ocr \
    tesseract-ocr-eng \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy workspace files (if they exist)
COPY pnpm-lock.yaml pnpm-workspace.yaml ./

# Copy packages
COPY packages/db ./packages/db

# Copy service
COPY apps/processing-service/pyproject.toml apps/processing-service/
COPY apps/processing-service/src ./apps/processing-service/src

# Install Python dependencies
RUN pip install --no-cache-dir -e ./packages/db
RUN pip install --no-cache-dir -e ./apps/processing-service

FROM python:3.12-slim
WORKDIR /app

# Install runtime dependencies for OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source code
COPY apps/processing-service/src ./apps/processing-service/src

EXPOSE 8004
CMD ["uvicorn", "processing_service.main:app", "--host", "0.0.0.0", "--port", "8004"]
