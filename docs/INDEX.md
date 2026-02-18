# 📚 GHDA-SaaS Documentation Index

<div align="center">

**Government Health Data Automation SaaS**  
*Production-Grade Microservices Architecture*

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Node.js](https://img.shields.io/badge/node-20+-green.svg)](https://nodejs.org/)

[Quick Start](QUICKSTART.md) • [Architecture](#architecture) • [API](#api) • [Development](#development)

</div>

---

## 🎯 Table of Contents

- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Services](#services)
- [API Reference](#api-reference)
- [Development](#development)
- [Performance](#performance)
- [Deployment](#deployment)

---

## 🚀 Quick Start

Get started in 5 minutes. See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

```bash
# Install dependencies
pnpm install

# Start infrastructure
docker-compose -f infra/docker/docker-compose.yml up -d

# Start services
pnpm dev
```

**Access Points:**
- API Gateway: http://localhost:3000
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (admin/admin)

---

## 🏗️ Architecture

### Microservices Architecture

```
API Gateway (Fastify) → Microservices → Infrastructure
├── Document Service (8001)
├── Report Service (8002)
├── Analytics Service (8003)
└── Processing Service (8004)
```

### Technology Stack

- **API Gateway**: Fastify/TypeScript
- **Microservices**: FastAPI/Python 3.11+
- **Database**: PostgreSQL 15+ (JSONB support)
- **Cache**: Redis
- **Storage**: MinIO (S3-compatible)
- **Observability**: Prometheus + Grafana
- **Build**: Turborepo + pnpm

### Project Structure

```
GHDA-SaaS/
├── apps/                  # Microservices
│   ├── api-gateway/       # Fastify API Gateway
│   ├── document-service/  # Document upload & storage
│   ├── report-service/    # Report retrieval
│   ├── analytics-service/ # Analytics & insights
│   └── processing-service/# Document processing
├── packages/              # Shared packages
│   ├── db/               # Database models & connection
│   ├── logging/          # Logging utilities
│   ├── config/           # Configuration management
│   └── auth/             # Authentication utilities
├── frontend/             # Frontend applications
├── infra/                # Infrastructure
│   ├── docker/           # Docker Compose
│   └── k8s/              # Kubernetes manifests
└── docs/                 # Documentation
```

---

## 🔧 Services

### API Gateway
- **Port**: 3000
- **Technology**: Fastify/TypeScript
- **Responsibilities**: Request routing, authentication, rate limiting
- **Health**: http://localhost:3000/health

### Document Service
- **Port**: 8001
- **Technology**: FastAPI/Python
- **Responsibilities**: Document upload, storage, metadata
- **Health**: http://localhost:8001/health

### Report Service
- **Port**: 8002
- **Technology**: FastAPI/Python
- **Responsibilities**: Report retrieval, management, export
- **Status**: To be implemented

### Analytics Service
- **Port**: 8003
- **Technology**: FastAPI/Python
- **Responsibilities**: Analytics, trends, insights
- **Status**: To be implemented

### Processing Service
- **Port**: 8004
- **Technology**: FastAPI/Python
- **Responsibilities**: Document processing, parsing, normalization
- **Status**: To be implemented

---

## 📡 API Reference

### API Gateway Endpoints

**Base URL**: http://localhost:3000

#### Health Check
```http
GET /health
```

#### Service Health
```http
GET /health/services
```

#### Document Upload
```http
POST /api/v1/document-service/documents/upload
Content-Type: multipart/form-data

file: <file>
tenant_id: <number>
```

#### Get Document
```http
GET /api/v1/document-service/documents/{document_id}
```

#### Get Document Status
```http
GET /api/v1/document-service/documents/{document_id}/status
```

### Service Endpoints

All services expose:
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

---

## 💻 Development

### Local Development

```bash
# Install dependencies
pnpm install

# Start infrastructure
docker-compose -f infra/docker/docker-compose.yml up -d

# Start all services (development)
pnpm dev

# Build all services
pnpm build

# Run tests
pnpm test
```

### Service Development

**API Gateway:**
```bash
cd apps/api-gateway
pnpm dev
```

**Document Service:**
```bash
cd apps/document-service
python3 -m uvicorn document_service.main:app --reload --host 0.0.0.0 --port 8001
```

### Environment Variables

Key environment variables (see `.env.example`):
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string
- `API_GATEWAY_PORT` - API Gateway port (default: 3000)
- `JWT_SECRET` - JWT secret key
- `STORAGE_ENDPOINT` - MinIO/S3 endpoint

---

## ⚡ Performance

### Optimizations

- **Database**: Connection pooling (20 connections), asyncpg, comprehensive indexes
- **Caching**: Redis with 50 connection pool, optimized TTLs
- **API**: GZip compression, uvloop, httptools, 4 workers
- **Docker**: Multi-stage builds (40% smaller images), resource limits

### Performance Targets

- **Cached Requests**: <50ms
- **Database Queries**: <200ms
- **API Responses**: <100ms average
- **Throughput**: 1000+ requests/second

### Monitoring

- **Prometheus**: Metrics collection at http://localhost:9090
- **Grafana**: Visualization at http://localhost:3001
- **Health Checks**: All services expose `/health` endpoint

---

## 🚢 Deployment

### Docker Compose

```bash
# Start all services
docker-compose -f infra/docker/docker-compose.yml up -d

# Stop services
docker-compose -f infra/docker/docker-compose.yml down

# View logs
docker-compose -f infra/docker/docker-compose.yml logs -f
```

### Production

1. **Build Services**
   ```bash
   pnpm build
   ```

2. **Deploy Infrastructure**
   - Use Kubernetes manifests in `infra/k8s/`
   - Or use managed services (RDS, ElastiCache, S3)

3. **Configure Environment**
   - Set production environment variables
   - Configure secrets management
   - Set up monitoring and alerting

---

## 📖 Additional Resources

### Data Schema
- **Canonical JSON Schema**: See `data/rules/` and `data/phrase_dictionaries/`
- **Database Models**: See `packages/db/src/ghda_db/models.py`

### Component Architecture
- **Phrase Normalization**: See `docs/development/PHRASE_NORMALIZATION_ENGINE.md`
- **Rule Engine**: See `docs/development/RULE_ENGINE_ARCHITECTURE.md`
- **API Specification**: See `docs/development/API_SPECIFICATION.md`

### Shared Packages
- **Database**: `packages/db/` - Models, connection pooling
- **Logging**: `packages/logging/` - Structured logging
- **Config**: `packages/config/` - Service registry
- **Auth**: `packages/auth/` - JWT utilities

---

## 🆘 Support

### Troubleshooting

**Services not starting:**
- Check Docker containers: `docker-compose ps`
- Verify environment variables
- Check service logs

**Database connection issues:**
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Ensure database exists

**Port conflicts:**
- Check if ports are in use
- Change ports in .env if needed

### Getting Help

- **Documentation**: This index
- **Quick Start**: [QUICKSTART.md](QUICKSTART.md)
- **Project README**: [../README.md](../README.md)

---

<div align="center">

**Built with ❤️ for public health impact**

*Last Updated: February 18, 2026*

</div>
