# Project Structure

## Overview

This document defines the folder structure and organization of the Government Health Data Automation SaaS application.

## Technology Stack Decision: Python + FastAPI

**Rationale**:
- Python ecosystem excels at document processing (python-docx, PyPDF2, Tesseract)
- FastAPI provides async performance with excellent documentation
- Strong data science libraries for future analytics expansion
- Easy integration with PostgreSQL via SQLAlchemy
- Excellent for rule engines and text processing

## Root Directory Structure

```
GHDA-SaaS/
├── README.md
├── ARCHITECTURE.md
├── SCHEMA.md
├── PROJECT_STRUCTURE.md
├── .gitignore
├── .env.example
├── docker-compose.yml
├── docker-compose.dev.yml
├── Dockerfile
├── pyproject.toml              # Poetry dependency management
├── poetry.lock
├── requirements.txt            # Generated from poetry
│
├── alembic/                    # Database migrations
│   ├── alembic.ini
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── app/                        # Main application code
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Configuration management
│   ├── dependencies.py         # FastAPI dependencies
│   │
│   ├── api/                    # API endpoints
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── router.py       # Main router
│   │   │   ├── documents.py    # Document ingestion endpoints
│   │   │   ├── reports.py      # Report retrieval endpoints
│   │   │   ├── analytics.py    # Analytics endpoints
│   │   │   ├── admin.py        # Admin endpoints
│   │   │   └── health.py       # Health check endpoints
│   │   └── deps.py             # API dependencies
│   │
│   ├── core/                   # Core business logic
│   │   ├── __init__.py
│   │   ├── ingestion/          # Document ingestion layer
│   │   │   ├── __init__.py
│   │   │   ├── base.py         # Base ingestion interface
│   │   │   ├── docx_processor.py
│   │   │   ├── pdf_processor.py
│   │   │   ├── image_processor.py
│   │   │   ├── ocr_engine.py   # Tesseract wrapper
│   │   │   └── preprocessor.py # Text preprocessing
│   │   │
│   │   ├── parser/             # Structural parser
│   │   │   ├── __init__.py
│   │   │   ├── base.py         # Base parser interface
│   │   │   ├── ppc_parser.py   # PPC-specific parser
│   │   │   ├── section_detector.py
│   │   │   ├── table_extractor.py
│   │   │   ├── field_extractor.py
│   │   │   └── schema_validator.py
│   │   │
│   │   ├── normalization/      # Phrase normalization engine
│   │   │   ├── __init__.py
│   │   │   ├── normalizer.py   # Main normalization logic
│   │   │   ├── phrase_matcher.py
│   │   │   ├── intent_mapper.py
│   │   │   ├── dictionary_manager.py
│   │   │   └── confidence_scorer.py
│   │   │
│   │   ├── rules/              # Rule engine
│   │   │   ├── __init__.py
│   │   │   ├── engine.py       # Rule engine core
│   │   │   ├── evaluator.py    # Condition evaluator
│   │   │   ├── rule_loader.py  # Load rules from DB/file
│   │   │   └── evidence_collector.py
│   │   │
│   │   ├── intelligence/       # Qualitative intelligence layer
│   │   │   ├── __init__.py
│   │   │   ├── analyzer.py     # Main analysis orchestrator
│   │   │   ├── pattern_detector.py
│   │   │   ├── frequency_analyzer.py
│   │   │   ├── bottleneck_detector.py
│   │   │   └── weak_signal_detector.py
│   │   │
│   │   ├── scoring/            # Scoring & output generation
│   │   │   ├── __init__.py
│   │   │   ├── scorer.py       # Score calculator
│   │   │   ├── compliance_scorer.py
│   │   │   ├── risk_assessor.py
│   │   │   └── summary_generator.py
│   │   │
│   │   └── pipeline/           # Processing pipeline orchestrator
│   │       ├── __init__.py
│   │       ├── document_pipeline.py
│   │       └── pipeline_stages.py
│   │
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py             # Base model
│   │   ├── document.py         # Document metadata
│   │   ├── facility.py         # Facility master data
│   │   ├── report.py           # Parsed report (JSONB)
│   │   ├── rule.py             # Rule definitions
│   │   ├── phrase_dictionary.py
│   │   ├── audit_log.py        # Audit trail
│   │   └── user.py             # User management
│   │
│   ├── schemas/                # Pydantic schemas (API contracts)
│   │   ├── __init__.py
│   │   ├── document.py
│   │   ├── report.py           # Based on SCHEMA.md
│   │   ├── analytics.py
│   │   ├── rule.py
│   │   └── common.py           # Shared schemas
│   │
│   ├── services/               # Business logic services
│   │   ├── __init__.py
│   │   ├── document_service.py
│   │   ├── report_service.py
│   │   ├── analytics_service.py
│   │   ├── rule_service.py
│   │   └── export_service.py   # PDF/Excel export
│   │
│   ├── db/                     # Database utilities
│   │   ├── __init__.py
│   │   ├── session.py          # Database session management
│   │   ├── base.py             # Base classes
│   │   └── init_db.py          # Database initialization
│   │
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── text_utils.py       # Text processing utilities
│   │   ├── date_utils.py
│   │   ├── file_utils.py
│   │   ├── validation.py
│   │   └── logging.py          # Logging configuration
│   │
│   └── workers/                # Celery workers
│       ├── __init__.py
│       ├── celery_app.py       # Celery configuration
│       ├── document_tasks.py   # Document processing tasks
│       └── analytics_tasks.py  # Analytics computation tasks
│
├── data/                       # Data files (gitignored except samples)
│   ├── phrase_dictionaries/
│   │   ├── ppc_attendance_barriers.json
│   │   ├── ppc_infrastructure_gaps.json
│   │   ├── ppc_lab_issues.json
│   │   └── ppc_asha_performance.json
│   ├── rules/
│   │   └── ppc_rules_v1.json
│   ├── samples/                # Sample documents for testing
│   │   ├── sample_ppc_report_1.docx
│   │   ├── sample_ppc_report_2.pdf
│   │   └── sample_ppc_report_3_scanned.jpg
│   └── uploads/                # User uploaded files (gitignored)
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py             # Pytest configuration
│   ├── fixtures/               # Test fixtures
│   │   ├── documents/
│   │   └── expected_outputs/
│   ├── unit/                   # Unit tests
│   │   ├── test_ingestion.py
│   │   ├── test_parser.py
│   │   ├── test_normalizer.py
│   │   ├── test_rules.py
│   │   └── test_scoring.py
│   ├── integration/            # Integration tests
│   │   ├── test_pipeline.py
│   │   └── test_api.py
│   └── e2e/                    # End-to-end tests
│       └── test_full_workflow.py
│
├── scripts/                    # Utility scripts
│   ├── init_db.sh              # Initialize database
│   ├── seed_data.py            # Seed initial data
│   ├── migrate.sh              # Run migrations
│   ├── export_schema.py        # Export JSON schema
│   └── benchmark.py            # Performance benchmarking
│
├── docs/                       # Additional documentation
│   ├── api/
│   │   └── openapi.json
│   ├── deployment/
│   │   ├── production.md
│   │   └── kubernetes/
│   ├── user_guides/
│   │   ├── admin_guide.md
│   │   └── field_worker_guide.md
│   └── development/
│       ├── setup.md
│       ├── contributing.md
│       └── testing.md
│
├── frontend/                   # Frontend (future phase)
│   ├── package.json
│   ├── src/
│   └── public/
│
└── infrastructure/             # Infrastructure as code
    ├── docker/
    │   ├── api.Dockerfile
    │   └── worker.Dockerfile
    ├── kubernetes/
    │   ├── api-deployment.yaml
    │   ├── worker-deployment.yaml
    │   ├── postgres-deployment.yaml
    │   └── redis-deployment.yaml
    └── terraform/              # Cloud infrastructure (if needed)
        └── aws/
```

## Key Design Decisions

### 1. Modular Core Architecture

The `app/core/` directory is organized by processing stage:
- **ingestion**: Convert documents to raw text
- **parser**: Convert text to structured JSON
- **normalization**: Normalize multilingual phrases
- **rules**: Apply validation and compliance rules
- **intelligence**: Extract cross-document insights
- **scoring**: Generate scores and summaries

Each module is independent and testable.

### 2. API Versioning

APIs are versioned (`api/v1/`) to support future breaking changes without disrupting existing integrations.

### 3. Service Layer Pattern

Business logic is in `services/`, separating it from:
- **API layer** (`api/`): HTTP concerns
- **Core layer** (`core/`): Pure processing logic
- **Models layer** (`models/`): Database entities

### 4. Schema-First Development

Pydantic schemas (`schemas/`) define API contracts and match the canonical JSON schema from SCHEMA.md.

### 5. Async Task Processing

Celery workers (`workers/`) handle long-running document processing asynchronously.

### 6. Configuration Management

- `config.py`: Centralized configuration
- `.env` files: Environment-specific settings
- Pydantic Settings for validation

### 7. Data Isolation

- `data/phrase_dictionaries/`: Version-controlled domain knowledge
- `data/rules/`: Version-controlled business rules
- `data/uploads/`: Runtime data (gitignored)

## Module Responsibilities

### app/core/ingestion/
**Purpose**: Accept documents and extract raw text

**Key Files**:
- `docx_processor.py`: Handle .docx files
- `pdf_processor.py`: Handle PDFs (text and tables)
- `image_processor.py`: Handle images with OCR
- `ocr_engine.py`: Tesseract wrapper with Hindi support

**Input**: File upload (DOCX/PDF/image)
**Output**: Raw document object with sections

### app/core/parser/
**Purpose**: Convert raw text to canonical JSON structure

**Key Files**:
- `ppc_parser.py`: PPC-specific parsing logic
- `section_detector.py`: Identify document sections
- `table_extractor.py`: Extract and normalize tables
- `field_extractor.py`: Extract specific field values
- `schema_validator.py`: Validate against JSON schema

**Input**: Raw document object
**Output**: Canonical PPC JSON (per SCHEMA.md)

### app/core/normalization/
**Purpose**: Map noisy phrases to canonical intents

**Key Files**:
- `normalizer.py`: Main normalization orchestrator
- `phrase_matcher.py`: Fuzzy matching algorithms
- `intent_mapper.py`: Map matches to canonical intents
- `dictionary_manager.py`: Load and manage phrase dictionaries
- `confidence_scorer.py`: Calculate confidence scores

**Input**: Free-text phrase (Hinglish/broken Hindi)
**Output**: Canonical intent + confidence + category

### app/core/rules/
**Purpose**: Evaluate validation and compliance rules

**Key Files**:
- `engine.py`: Rule engine orchestrator
- `evaluator.py`: Evaluate rule conditions against data
- `rule_loader.py`: Load rules from database or files
- `evidence_collector.py`: Collect evidence for rule violations

**Input**: Parsed report JSON + rule definitions
**Output**: List of findings (flags, violations, gaps)

### app/core/intelligence/
**Purpose**: Extract patterns and insights across reports

**Key Files**:
- `analyzer.py`: Main analysis orchestrator
- `pattern_detector.py`: Detect recurring patterns
- `frequency_analyzer.py`: Frequency analysis
- `bottleneck_detector.py`: Identify systemic bottlenecks
- `weak_signal_detector.py`: Early warning detection

**Input**: Collection of parsed reports
**Output**: Insights, trends, patterns

### app/core/scoring/
**Purpose**: Calculate scores and generate summaries

**Key Files**:
- `scorer.py`: Overall score calculator
- `compliance_scorer.py`: Compliance-specific scoring
- `risk_assessor.py`: Risk level assessment
- `summary_generator.py`: Plain English summaries

**Input**: Parsed report + findings
**Output**: Scores, risk levels, summaries

### app/core/pipeline/
**Purpose**: Orchestrate the entire processing pipeline

**Key Files**:
- `document_pipeline.py`: Main pipeline orchestrator
- `pipeline_stages.py`: Individual pipeline stages

**Flow**:
```
Upload → Ingestion → Parsing → Normalization → Rules → Scoring → Storage
```

## Database Schema (PostgreSQL)

### Key Tables

```sql
-- Documents (metadata)
documents (
    id UUID PRIMARY KEY,
    filename VARCHAR,
    file_type VARCHAR,
    file_size INTEGER,
    checksum VARCHAR,
    uploaded_at TIMESTAMP,
    uploaded_by UUID REFERENCES users(id),
    status VARCHAR,  -- 'pending', 'processing', 'completed', 'failed'
    storage_path VARCHAR
)

-- Facilities (master data)
facilities (
    id UUID PRIMARY KEY,
    name VARCHAR,
    type VARCHAR,
    block VARCHAR,
    district VARCHAR,
    state VARCHAR,
    facility_code VARCHAR UNIQUE,
    created_at TIMESTAMP
)

-- Reports (parsed data stored as JSONB)
reports (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(id),
    facility_id UUID REFERENCES facilities(id),
    clinic_date DATE,
    schema_version VARCHAR,
    data JSONB,  -- Full canonical JSON
    quality_indicators JSONB,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

-- Rules (versioned)
rules (
    id UUID PRIMARY KEY,
    rule_id VARCHAR UNIQUE,
    version VARCHAR,
    name VARCHAR,
    category VARCHAR,
    severity VARCHAR,
    condition JSONB,
    action JSONB,
    evidence_fields JSONB,
    active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
)

-- Phrase Dictionary
phrase_dictionary (
    id UUID PRIMARY KEY,
    raw_pattern VARCHAR,
    canonical_intent VARCHAR,
    category VARCHAR,
    severity VARCHAR,
    match_type VARCHAR,
    min_confidence FLOAT,
    active BOOLEAN,
    created_at TIMESTAMP
)

-- Findings (rule evaluation results)
findings (
    id UUID PRIMARY KEY,
    report_id UUID REFERENCES reports(id),
    rule_id UUID REFERENCES rules(id),
    severity VARCHAR,
    flag VARCHAR,
    message TEXT,
    evidence JSONB,
    created_at TIMESTAMP
)

-- Audit Log
audit_logs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action VARCHAR,
    resource_type VARCHAR,
    resource_id UUID,
    changes JSONB,
    ip_address VARCHAR,
    created_at TIMESTAMP
)

-- Users
users (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE,
    hashed_password VARCHAR,
    full_name VARCHAR,
    role VARCHAR,  -- 'admin', 'analyst', 'viewer'
    active BOOLEAN,
    created_at TIMESTAMP
)
```

### Indexes

```sql
CREATE INDEX idx_reports_facility_date ON reports(facility_id, clinic_date);
CREATE INDEX idx_reports_data_gin ON reports USING gin(data);
CREATE INDEX idx_findings_report_severity ON findings(report_id, severity);
CREATE INDEX idx_documents_status ON documents(status);
```

## API Endpoints Structure

### Document Management
- `POST /api/v1/documents/upload` - Upload document
- `GET /api/v1/documents/{id}` - Get document metadata
- `GET /api/v1/documents/{id}/status` - Check processing status
- `DELETE /api/v1/documents/{id}` - Delete document

### Reports
- `GET /api/v1/reports` - List reports (with filters)
- `GET /api/v1/reports/{id}` - Get single report
- `GET /api/v1/reports/{id}/export` - Export report (PDF/Excel)
- `GET /api/v1/reports/{id}/findings` - Get findings for report

### Analytics
- `GET /api/v1/analytics/facilities/{id}/trends` - Facility trends
- `GET /api/v1/analytics/attendance-barriers` - Cross-facility barriers
- `GET /api/v1/analytics/asha-performance` - ASHA performance analysis
- `GET /api/v1/analytics/lab-bottlenecks` - Lab capacity analysis
- `GET /api/v1/analytics/compliance-summary` - Overall compliance

### Admin
- `GET /api/v1/admin/rules` - List rules
- `POST /api/v1/admin/rules` - Create rule
- `PUT /api/v1/admin/rules/{id}` - Update rule
- `GET /api/v1/admin/phrase-dictionary` - Manage phrases
- `POST /api/v1/admin/phrase-dictionary` - Add phrases
- `GET /api/v1/admin/audit-logs` - View audit logs

### Health
- `GET /api/v1/health` - Health check
- `GET /api/v1/health/db` - Database connectivity
- `GET /api/v1/health/workers` - Worker status

## Environment Variables

```bash
# Application
APP_NAME=GHDA-SaaS
APP_VERSION=1.0.0
ENVIRONMENT=development  # development, staging, production
DEBUG=true

# API
API_HOST=0.0.0.0
API_PORT=8000
API_PREFIX=/api/v1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ghda_saas
DATABASE_POOL_SIZE=10

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Object Storage (MinIO/S3)
STORAGE_TYPE=minio  # minio, s3
STORAGE_ENDPOINT=localhost:9000
STORAGE_ACCESS_KEY=minioadmin
STORAGE_SECRET_KEY=minioadmin
STORAGE_BUCKET=ghda-documents
STORAGE_REGION=us-east-1

# OCR
TESSERACT_PATH=/usr/bin/tesseract
TESSERACT_LANG=eng+hin

# Security
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# Processing
MAX_UPLOAD_SIZE_MB=50
DOCUMENT_PROCESSING_TIMEOUT_SECONDS=300
```

## Development Workflow

### 1. Setup
```bash
# Clone repo
git clone <repo-url>
cd GHDA-SaaS

# Install dependencies
poetry install

# Copy environment file
cp .env.example .env

# Start services
docker-compose -f docker-compose.dev.yml up -d

# Run migrations
poetry run alembic upgrade head

# Seed initial data
poetry run python scripts/seed_data.py
```

### 2. Development
```bash
# Run API server (with auto-reload)
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run Celery worker
poetry run celery -A app.workers.celery_app worker --loglevel=info

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=app --cov-report=html
```

### 3. Testing
```bash
# Unit tests
poetry run pytest tests/unit/

# Integration tests
poetry run pytest tests/integration/

# E2E tests
poetry run pytest tests/e2e/

# Specific test file
poetry run pytest tests/unit/test_parser.py -v
```

## Deployment

### Docker Compose (Development/Staging)
```bash
docker-compose up -d
```

### Kubernetes (Production)
```bash
kubectl apply -f infrastructure/kubernetes/
```

## CI/CD Pipeline

```yaml
# .github/workflows/main.yml
- Lint (ruff, black)
- Type check (mypy)
- Unit tests
- Integration tests
- Build Docker images
- Deploy to staging
- Automated smoke tests
- Deploy to production (on tag)
```

## Monitoring & Observability

- **Logs**: Structured JSON logging to stdout
- **Metrics**: Prometheus metrics exposed at `/metrics`
- **Tracing**: OpenTelemetry (future)
- **Health Checks**: `/api/v1/health` endpoints

## Security Considerations

- **Authentication**: JWT-based authentication
- **Authorization**: Role-based access control (RBAC)
- **Data Encryption**: At rest (database encryption) and in transit (HTTPS)
- **Input Validation**: Pydantic schemas for all inputs
- **SQL Injection**: Prevented by SQLAlchemy ORM
- **File Upload**: Virus scanning, file type validation, size limits
- **Audit Logging**: All data access and modifications logged

## Performance Targets

- **Document Processing**: < 30 seconds per document (p95)
- **API Response Time**: < 2 seconds (p95)
- **Concurrent Users**: Support 50 concurrent users
- **Database Queries**: < 500ms (p95)
- **System Uptime**: 99.5%

## Future Enhancements

### Phase 2
- Frontend dashboard (React/Vue)
- Real-time processing status updates (WebSockets)
- Batch upload and processing
- Advanced analytics visualizations

### Phase 3
- Mobile app for field workers
- SMS notifications
- Integration with government HMIS systems
- Multi-program support (ANC, immunization)

### Phase 4
- Machine learning for anomaly detection
- Predictive analytics
- Automated report generation
- State-level aggregation

## Conclusion

This structure prioritizes:
1. **Modularity**: Each component is independent
2. **Testability**: Clear separation of concerns
3. **Scalability**: Async processing, horizontal scaling
4. **Maintainability**: Clear organization, documentation
5. **Government-readiness**: Audit trails, versioning, explainability

The architecture supports the MVP while providing a foundation for future growth.
