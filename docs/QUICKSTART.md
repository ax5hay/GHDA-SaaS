# 🚀 Quick Start Guide - GHDA-SaaS

Get GHDA-SaaS up and running in minutes.

## Prerequisites

- **Node.js** 20+ and **pnpm** 10+
- **Python** 3.11+
- **Docker** & Docker Compose

## Installation

### 1. Install pnpm (if not installed)
```bash
npm install -g pnpm@10.28.1
```

### 2. Install Dependencies
```bash
pnpm install
```

### 3. Set Up Environment
```bash
cp .env.example .env
# Edit .env if needed
```

### 4. Start Infrastructure
```bash
docker-compose -f infra/docker/docker-compose.yml up -d
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- MinIO (ports 9000/9001)
- Prometheus (port 9090)
- Grafana (port 3001)

### 5. Start Services

**Option A: Start all services**
```bash
pnpm dev
```

**Option B: Start individually**
```bash
# Terminal 1: API Gateway
cd apps/api-gateway && pnpm dev

# Terminal 2: Document Service
cd apps/document-service && python3 -m uvicorn document_service.main:app --host 0.0.0.0 --port 8001
```

## Verify Installation

```bash
# Check infrastructure
docker-compose -f infra/docker/docker-compose.yml ps

# Test API Gateway
curl http://localhost:3000/health

# Test Document Service
curl http://localhost:8001/health

# Test Prometheus
curl http://localhost:9090/-/healthy

# Test Grafana
curl http://localhost:3001/api/health
```

## Access Points

- **API Gateway**: http://localhost:3000
- **API Gateway Health**: http://localhost:3000/health
- **Document Service**: http://localhost:8001
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)
- **MinIO Console**: http://localhost:9001 (minioadmin/minioadmin)

## Project Structure

```
GHDA-SaaS/
├── apps/                  # Microservices
│   ├── api-gateway/       # API Gateway (Fastify/TypeScript)
│   └── document-service/  # Document Service (FastAPI/Python)
├── packages/              # Shared packages
│   ├── db/               # Database models
│   ├── logging/          # Logging utilities
│   ├── config/           # Configuration
│   └── auth/             # Authentication
├── infra/                # Infrastructure
│   └── docker/           # Docker Compose
└── docs/                 # Documentation
```

## Common Commands

```bash
# Start infrastructure
docker-compose -f infra/docker/docker-compose.yml up -d

# Stop infrastructure
docker-compose -f infra/docker/docker-compose.yml down

# View logs
docker-compose -f infra/docker/docker-compose.yml logs -f

# Build packages
pnpm run build

# Run tests
pnpm test
```

## Troubleshooting

### Services not starting
- Check Docker is running: `docker ps`
- Verify ports are not in use
- Check logs: `docker-compose -f infra/docker/docker-compose.yml logs`

### Database connection issues
- Verify PostgreSQL is running: `docker-compose ps`
- Check DATABASE_URL in .env
- Wait for database to be ready (10-15 seconds after start)

### Port conflicts
- Check if ports 3000, 8001, 5432, 6379, 9000, 9090, 3001 are available
- Stop conflicting services or change ports in .env

## Next Steps

1. **Explore Services**
   - Check API Gateway: http://localhost:3000/health
   - Check Document Service: http://localhost:8001/health

2. **View Metrics**
   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3001

3. **Read Documentation**
   - See [INDEX.md](INDEX.md) for complete documentation
   - See [README.md](../README.md) for project overview

---

**Need Help?** See [INDEX.md](INDEX.md) for complete documentation.
