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
COPY apps/report-service/pyproject.toml apps/report-service/
COPY apps/report-service/src ./apps/report-service/src

# Install Python dependencies
RUN pip install --no-cache-dir -e ./packages/db
RUN pip install --no-cache-dir -e ./apps/report-service

FROM python:3.12-slim
WORKDIR /app

# Copy installed packages
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy source code
COPY apps/report-service/src ./apps/report-service/src

EXPOSE 8002
CMD ["uvicorn", "report_service.main:app", "--host", "0.0.0.0", "--port", "8002"]
