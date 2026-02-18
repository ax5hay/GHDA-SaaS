# Getting Started - Government Health Data Automation SaaS

Welcome! This guide will help you understand and start working with the GHDA-SaaS project.

## 🎯 What Is This Project?

GHDA-SaaS automates the analysis, validation, and intelligence extraction from government health field survey reports. It replaces manual coordinators by converting messy, multilingual (Hinglish/Roman Hindi) documents into structured data, gap analysis, and decision-ready outputs.

**Current Focus**: Preconception/Maternal Health Clinics (PPC) reports from Indian government health programs.

## 📚 Essential Reading

Start here to understand the project:

1. **[README.md](README.md)** - Project overview and quick start
2. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Complete system architecture
3. **[SCHEMA.md](SCHEMA.md)** - Canonical PPC JSON schema
4. **[MVP_ROADMAP.md](MVP_ROADMAP.md)** - Implementation roadmap

## 🏗️ Architecture Overview

```
Document Upload → Ingestion → Parsing → Normalization → Rules → Scoring → Dashboard
```

### Key Components

1. **Document Ingestion**: Accept DOCX/PDF/images with OCR
2. **Structural Parser**: Convert to canonical JSON schema
3. **Phrase Normalization**: Map Hinglish phrases to canonical intents
4. **Rule Engine**: Automated validation and compliance checking
5. **Qualitative Intelligence**: Cross-facility pattern detection
6. **Scoring & Output**: Compliance scores and summaries

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- Poetry (optional, for local development)

### Setup in 5 Minutes

```bash
# 1. Clone repository
git clone <repo-url>
cd GHDA-SaaS

# 2. Copy environment file
cp .env.example .env

# 3. Start all services
docker-compose up -d

# 4. Wait for services to start (30-60 seconds)
docker-compose ps

# 5. Access the application
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# MinIO Console: http://localhost:9001
```

That's it! The system is now running.

## 📁 Project Structure

```
GHDA-SaaS/
├── app/                    # Main application code
│   ├── api/               # API endpoints (FastAPI)
│   ├── core/              # Core processing logic
│   │   ├── ingestion/     # Document processing
│   │   ├── parser/        # Text → JSON conversion
│   │   ├── normalization/ # Phrase normalization
│   │   ├── rules/         # Rule engine
│   │   ├── intelligence/  # Analytics
│   │   └── scoring/       # Scoring system
│   ├── models/            # Database models
│   ├── schemas/           # API schemas (Pydantic)
│   ├── services/          # Business logic
│   └── workers/           # Async tasks (Celery)
│
├── data/                  # Data files
│   ├── phrase_dictionaries/ # Phrase → intent mappings
│   ├── rules/             # Validation rules
│   └── samples/           # Sample documents
│
├── tests/                 # Test suite
└── docs/                  # Documentation
```

See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) for complete details.

## 🔑 Core Concepts

### 1. Schema-First Design

Every report is forced into a strict JSON schema, even if incomplete:

```json
{
  "facility": {
    "name": "CHC Badsali",
    "district": "Una"
  },
  "beneficiaries": {
    "expected_count": 8,
    "actual_count": 1,
    "attendance_rate": 0.125
  }
}
```

Missing data is explicit: `null` with `missing_reason`.

### 2. Phrase Normalization (NOT Translation)

Maps noisy input to canonical intents:

| Input (Hinglish) | Canonical Intent |
|-----------------|------------------|
| "pti ka exident ho gya" | `REASON_HUSBAND_ACCIDENT` |
| "asha nai btaya" | `ASHA_COMMUNICATION_FAILURE` |
| "mayke gyi thi" | `REASON_BENEFICIARY_AT_MATERNAL_HOME` |

See [docs/development/PHRASE_NORMALIZATION_ENGINE.md](docs/development/PHRASE_NORMALIZATION_ENGINE.md).

### 3. Rule Engine

Explicit, versioned rules replace human coordinators:

```json
{
  "rule_id": "R_PPC_003",
  "name": "Low beneficiary attendance",
  "condition": {
    "field": "beneficiaries.attendance_rate",
    "operator": "<",
    "value": 0.5
  },
  "action": {
    "flag": "MOBILIZATION_FAILURE",
    "severity": "high"
  }
}
```

See [docs/development/RULE_ENGINE_ARCHITECTURE.md](docs/development/RULE_ENGINE_ARCHITECTURE.md).

## 🛠️ Development Workflow

### Local Development (Without Docker)

```bash
# 1. Install dependencies
poetry install

# 2. Start PostgreSQL, Redis, MinIO
docker-compose up -d postgres redis minio

# 3. Run migrations
poetry run alembic upgrade head

# 4. Start API server
poetry run uvicorn app.main:app --reload

# 5. Start Celery worker (in another terminal)
poetry run celery -A app.workers.celery_app worker --loglevel=info
```

### Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app --cov-report=html

# Run specific test types
poetry run pytest tests/unit/
poetry run pytest tests/integration/
```

### Code Quality

```bash
# Format code
poetry run black app tests

# Lint
poetry run ruff check app tests

# Type checking
poetry run mypy app
```

## 📊 Example Workflow

### 1. Upload a Document

```bash
curl -X POST "http://localhost:8000/api/v1/documents/upload" \
  -H "Authorization: Bearer <token>" \
  -F "file=@ppc_report.docx"
```

### 2. Check Processing Status

```bash
curl "http://localhost:8000/api/v1/documents/{document_id}/status"
```

### 3. Get Parsed Report

```bash
curl "http://localhost:8000/api/v1/reports/{report_id}"
```

### 4. View Findings

```bash
curl "http://localhost:8000/api/v1/reports/{report_id}/findings"
```

### 5. Get Analytics

```bash
curl "http://localhost:8000/api/v1/analytics/attendance-barriers"
```

See [docs/development/API_SPECIFICATION.md](docs/development/API_SPECIFICATION.md) for complete API documentation.

## 🎓 Learning Path

### For Backend Developers

1. Read [ARCHITECTURE.md](ARCHITECTURE.md)
2. Explore `app/core/` components
3. Review [SCHEMA.md](SCHEMA.md)
4. Study phrase normalization and rule engine docs
5. Write unit tests for core components

**First Task**: Implement a simple document processor for DOCX files.

### For Data Engineers

1. Read [SCHEMA.md](SCHEMA.md)
2. Study [docs/development/PHRASE_NORMALIZATION_ENGINE.md](docs/development/PHRASE_NORMALIZATION_ENGINE.md)
3. Review phrase dictionaries in `data/phrase_dictionaries/`
4. Understand OCR pipeline
5. Analyze sample documents

**First Task**: Expand phrase dictionary with 10 new patterns.

### For DevOps Engineers

1. Review [docker-compose.yml](docker-compose.yml) and [Dockerfile](Dockerfile)
2. Study infrastructure requirements in [ARCHITECTURE.md](ARCHITECTURE.md)
3. Review CI/CD in `.github/workflows/`
4. Plan deployment strategy
5. Set up monitoring (Prometheus + Grafana)

**First Task**: Set up staging environment.

### For Product Managers

1. Read [README.md](README.md) and [ARCHITECTURE.md](ARCHITECTURE.md)
2. Review [MVP_ROADMAP.md](MVP_ROADMAP.md)
3. Understand core concepts (schema-first, phrase normalization, rules)
4. Review success metrics
5. Study user workflows

**First Task**: Define pilot facility selection criteria.

## 🧪 Testing Strategy

### Unit Tests

Test individual components in isolation:

```python
def test_phrase_normalization():
    normalizer = PhraseNormalizer('test_dictionary.json')
    result = normalizer.normalize("asha nai btaya")

    assert result['canonical_intent'] == 'ASHA_COMMUNICATION_FAILURE'
    assert result['confidence'] > 0.8
```

### Integration Tests

Test component interactions:

```python
def test_document_processing_pipeline():
    # Upload document
    doc_id = upload_document('test.docx')

    # Wait for processing
    wait_for_completion(doc_id)

    # Verify report created
    report = get_report(doc_id)
    assert report['data']['facility']['name'] == 'CHC Badsali'
```

### End-to-End Tests

Test complete workflows:

```python
def test_full_workflow():
    # Upload → Process → Analyze → Export
    pass
```

## 📈 Performance Targets

- **Document Processing**: <30 seconds (p95)
- **API Response Time**: <2 seconds (p95)
- **System Uptime**: >99.5%
- **Data Extraction Accuracy**: >90%

## 🔒 Security Considerations

- **Authentication**: JWT-based
- **Authorization**: Role-based access control (admin, analyst, viewer)
- **Data Encryption**: At rest and in transit
- **Input Validation**: Strict validation on all inputs
- **Audit Logging**: Complete audit trail

## 🐛 Troubleshooting

### Docker Issues

```bash
# Clean restart
docker-compose down -v
docker-compose up -d

# View logs
docker-compose logs -f api
docker-compose logs -f worker
```

### Database Issues

```bash
# Reset database
docker-compose exec postgres psql -U ghda_user -d ghda_saas -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Run migrations
docker-compose exec api alembic upgrade head
```

### OCR Issues

```bash
# Check Tesseract installation
docker-compose exec api tesseract --version

# Test OCR
docker-compose exec api tesseract test_image.png stdout -l eng+hin
```

## 📞 Getting Help

- **Issues**: GitHub Issues
- **Documentation**: [docs/](docs/) directory
- **Architecture Questions**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **API Questions**: See [docs/development/API_SPECIFICATION.md](docs/development/API_SPECIFICATION.md)

## 🎯 Next Steps

### If You're Starting Development

1. ✅ Set up local environment
2. ✅ Read architecture docs
3. 📝 Choose a component to implement (see [MVP_ROADMAP.md](MVP_ROADMAP.md))
4. 📝 Write tests first (TDD approach)
5. 📝 Implement feature
6. 📝 Submit PR with tests

### If You're Planning Deployment

1. ✅ Review infrastructure requirements
2. 📝 Set up staging environment
3. 📝 Configure monitoring
4. 📝 Prepare training materials
5. 📝 Define pilot facility criteria

### If You're Managing the Project

1. ✅ Review [MVP_ROADMAP.md](MVP_ROADMAP.md)
2. 📝 Assemble team
3. 📝 Set up project management (Jira/GitHub Projects)
4. 📝 Define sprint goals
5. 📝 Schedule stakeholder demos

## 📋 Checklist for First Week

- [ ] Clone repository
- [ ] Run `docker-compose up` successfully
- [ ] Upload a test document
- [ ] View API documentation at `/docs`
- [ ] Read ARCHITECTURE.md
- [ ] Read SCHEMA.md
- [ ] Review one core component in `app/core/`
- [ ] Run tests successfully
- [ ] Make a small code change and test it
- [ ] Understand the MVP roadmap

## 🌟 Design Philosophy

Remember these principles as you work on the project:

1. **Schema-First, Language-Second**: Force chaos into structure
2. **Assume Data is Sloppy**: Design for worst-case input
3. **Explainability > Fancy ML**: Every decision must be traceable
4. **Government-Safe**: Audit trails, versioning, transparency

## 📚 Additional Resources

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Pydantic Documentation**: https://docs.pydantic.dev/
- **PostgreSQL JSONB**: https://www.postgresql.org/docs/current/datatype-json.html
- **Celery Documentation**: https://docs.celeryq.dev/

## 🚢 Deployment Checklist

Before deploying to production:

- [ ] All tests passing
- [ ] Security audit completed
- [ ] Performance benchmarks met
- [ ] Documentation complete
- [ ] Training materials prepared
- [ ] Monitoring configured
- [ ] Backup procedures tested
- [ ] Rollback plan documented

---

**Welcome to the GHDA-SaaS project!** Let's build something that makes a real difference in public health.

Questions? Start with the [ARCHITECTURE.md](ARCHITECTURE.md) or open a GitHub issue.
