# Government Health Data Automation SaaS (GHDA-SaaS)

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Overview

GHDA-SaaS is a production-grade system that automates analysis, validation, and intelligence extraction from government health field survey reports. It replaces manual coordination by converting messy, multilingual (Hinglish/Roman Hindi) documents into structured data, gap analysis, compliance insights, and decision-ready outputs.

### Initial Domain: Preconception/Maternal Health Clinics (PPC)

The system currently focuses on PPC reports from Indian government health programs, but is designed to be extensible to other health programs.

## Key Features

- **Intelligent Document Processing**: Handles DOCX, PDF, and scanned images with OCR
- **Multilingual Support**: Processes Hinglish, Roman Hindi, and broken English
- **Schema-First Architecture**: Converts unstructured reports into canonical JSON
- **Phrase Normalization**: Maps noisy input to canonical intents without full translation
- **Rule Engine**: Automated validation, gap detection, and compliance checking
- **Qualitative Intelligence**: Cross-facility pattern detection and trend analysis
- **Explainability**: Every decision is traceable to source text
- **Government-Safe**: Audit trails, versioning, deterministic outputs

## Architecture

```
Document Upload → Ingestion → Parsing → Normalization → Rules → Scoring → Dashboard
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for complete system architecture.

## Tech Stack

- **Backend**: Python 3.11, FastAPI
- **Database**: PostgreSQL 15+ (with JSONB support)
- **Cache & Queue**: Redis, Celery
- **Object Storage**: MinIO (S3-compatible)
- **Document Processing**: python-docx, PyPDF2, pdfplumber, Tesseract OCR
- **Deployment**: Docker, Docker Compose, Kubernetes (production)

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Poetry (for dependency management)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd GHDA-SaaS
   ```

2. **Copy environment variables**
   ```bash
   cp .env.example .env
   ```

3. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

   This will start:
   - PostgreSQL (port 5432)
   - Redis (port 6379)
   - MinIO (port 9000, console 9001)
   - API Server (port 8000)
   - Celery Worker
   - Flower (Celery monitoring, port 5555)

4. **Run database migrations**
   ```bash
   docker-compose exec api alembic upgrade head
   ```

5. **Seed initial data**
   ```bash
   docker-compose exec api python scripts/seed_data.py
   ```

6. **Access the application**
   - API: http://localhost:8000
   - API Docs (Swagger): http://localhost:8000/docs
   - MinIO Console: http://localhost:9001 (minioadmin / minioadmin)
   - Flower (Celery monitoring): http://localhost:5555

### Local Development (without Docker)

1. **Install dependencies**
   ```bash
   poetry install
   ```

2. **Start PostgreSQL and Redis**
   ```bash
   docker-compose up -d postgres redis minio
   ```

3. **Run migrations**
   ```bash
   poetry run alembic upgrade head
   ```

4. **Start API server**
   ```bash
   poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Start Celery worker (in another terminal)**
   ```bash
   poetry run celery -A app.workers.celery_app worker --loglevel=info
   ```

## Usage

### Upload a Document

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@path/to/ppc_report.docx"
```

### Check Processing Status

```bash
curl "http://localhost:8000/api/v1/documents/{document_id}/status"
```

### Get Parsed Report

```bash
curl "http://localhost:8000/api/v1/reports/{report_id}"
```

### Get Analytics

```bash
# Facility trends
curl "http://localhost:8000/api/v1/analytics/facilities/{facility_id}/trends"

# Attendance barriers analysis
curl "http://localhost:8000/api/v1/analytics/attendance-barriers"

# ASHA performance
curl "http://localhost:8000/api/v1/analytics/asha-performance"
```

## Project Structure

```
GHDA-SaaS/
├── app/                    # Main application code
│   ├── api/               # API endpoints
│   ├── core/              # Core processing logic
│   │   ├── ingestion/     # Document ingestion
│   │   ├── parser/        # Structural parsing
│   │   ├── normalization/ # Phrase normalization
│   │   ├── rules/         # Rule engine
│   │   ├── intelligence/  # Pattern analysis
│   │   └── scoring/       # Scoring & summaries
│   ├── models/            # Database models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic
│   └── workers/           # Celery tasks
├── data/                  # Data files
│   ├── phrase_dictionaries/
│   ├── rules/
│   └── samples/
├── tests/                 # Test suite
└── docs/                  # Documentation
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for detailed structure.

## Core Concepts

### 1. Canonical JSON Schema

Every report is converted to a strict JSON schema. See [SCHEMA.md](SCHEMA.md).

### 2. Phrase Normalization

Maps noisy multilingual phrases to canonical intents:
- "pti ka exident ho gya" → `REASON_HUSBAND_ACCIDENT`
- "asha nai btaya" → `ASHA_COMMUNICATION_FAILURE`
- "mayke gyi thi" → `REASON_BENEFICIARY_AT_MATERNAL_HOME`

### 3. Rule Engine

Explicit, versioned rules for validation:
```json
{
  "rule_id": "R_PPC_001",
  "condition": {
    "and": [
      {"field": "beneficiary.bmi", "operator": ">=", "value": 25},
      {"field": "counselling.exercise_provided", "operator": "!=", "value": true}
    ]
  },
  "action": {
    "flag": "MISSING_EXERCISE_COUNSELLING_HIGH_BMI",
    "severity": "medium"
  }
}
```

### 4. Scoring System

- **Compliance Score** (0-100): Protocol adherence
- **Process Adherence Score** (0-100): Workflow completion
- **Risk Level**: Low / Medium / High / Critical

## Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test types
poetry run pytest tests/unit/
poetry run pytest tests/integration/
poetry run pytest tests/e2e/

# Run specific test file
poetry run pytest tests/unit/test_parser.py -v
```

## API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Design Principles

1. **Schema-First, Language-Second**: Force all inputs into strict data model
2. **Assume Data is Sloppy**: Design for chaos, not ideal conditions
3. **Explainability > Fancy ML**: Every decision traceable to source
4. **Government-Safe**: Transparent, auditable, reproducible

## MVP Scope

### Phase 1 (Current)
- ✅ PPC report ingestion
- ✅ Schema enforcement
- ✅ Gap detection
- ✅ Rule-based compliance
- ⏳ Simple dashboard

### Phase 2 (Planned)
- Cross-report analytics
- Trend detection
- Performance heatmaps
- Predictive insights

## Performance Targets

- Document processing: < 30 seconds per document (p95)
- API response time: < 2 seconds (p95)
- Concurrent users: 50+
- System uptime: 99.5%

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [docs/development/contributing.md](docs/development/contributing.md) for details.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- **Issues**: GitHub Issues
- **Documentation**: [docs/](docs/)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Schema**: [SCHEMA.md](SCHEMA.md)

## Roadmap

- [ ] Phase 1 MVP completion
- [ ] Frontend dashboard (React)
- [ ] Multi-program support (ANC, immunization)
- [ ] Mobile app for field workers
- [ ] Integration with government HMIS
- [ ] Machine learning for anomaly detection
- [ ] Predictive analytics
- [ ] State-level aggregation

## Acknowledgments

Built for real-world government health programs with the goal of improving health outcomes through better data quality and faster insights.

---

**Built with ❤️ for public health impact**
