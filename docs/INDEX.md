# 📚 GHDA-SaaS Documentation Hub

<div align="center">

**Government Health Data Automation SaaS**  
*Automating analysis, validation, and intelligence extraction from government health field survey reports*

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](../LICENSE)

[Quick Start](#-quick-start) • [Architecture](#-architecture) • [Development](#-development) • [Performance](#-performance)

</div>

---

## 🎯 Table of Contents

### 🚀 Getting Started
- [Quick Start Guide](#-quick-start)
- [Project Overview](#-project-overview)
- [Installation & Setup](#-installation--setup)

### 🏗️ Architecture & Design
- [System Architecture](#-system-architecture)
- [Data Schema](#-data-schema)
- [Project Structure](#-project-structure)
- [API Specification](#-api-specification)

### 💻 Development
- [Development Guide](#-development-guide)
- [Component Architecture](#-component-architecture)
- [MVP Roadmap](#-mvp-roadmap)

### ⚡ Performance & Optimization
- [Performance Optimizations](#-performance-optimizations)
- [Cost Efficiency](#-cost-efficiency)

### 🔧 POC & Testing
- [POC Guide](#-poc-guide)
- [Troubleshooting](#-troubleshooting)

---

## 🚀 Quick Start

### What is GHDA-SaaS?

GHDA-SaaS is a production-grade system that automates analysis, validation, and intelligence extraction from government health field survey reports. It replaces manual coordination by converting messy, multilingual (Hinglish/Roman Hindi) documents into structured data, gap analysis, compliance insights, and decision-ready outputs.

**Key Features:**
- ✅ **Intelligent Document Processing**: Handles DOCX, PDF, and scanned images with OCR
- ✅ **Multilingual Support**: Processes Hinglish, Roman Hindi, and broken English
- ✅ **Schema-First Architecture**: Converts unstructured reports into canonical JSON
- ✅ **Phrase Normalization**: Maps noisy input to canonical intents without full translation
- ✅ **Rule Engine**: Automated validation, gap detection, and compliance checking
- ✅ **Qualitative Intelligence**: Cross-facility pattern detection and trend analysis
- ✅ **Explainability**: Every decision is traceable to source text
- ✅ **Government-Safe**: Audit trails, versioning, deterministic outputs

### Installation & Setup

#### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Poetry (for dependency management)

#### Quick Setup (5 minutes)

```bash
# 1. Clone the repository
git clone <repo-url>
cd GHDA-SaaS

# 2. Copy environment variables
cp .env.example .env

# 3. Start services with Docker Compose
docker-compose up -d

# 4. Run database migrations
docker-compose exec api alembic upgrade head

# 5. Seed initial data
docker-compose exec api python scripts/seed_data.py

# 6. Access the application
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# MinIO Console: http://localhost:9001
# Flower (Celery): http://localhost:5555
```

**📖 Detailed Setup:** See [GETTING_STARTED.md](GETTING_STARTED.md) for comprehensive setup instructions.

---

## 🏗️ Architecture

### System Architecture

```
Document Upload → Ingestion → Parsing → Normalization → Rules → Scoring → Dashboard
```

**Core Components:**
1. **Document Ingestion**: Accept and normalize various document formats (DOCX, PDF, images)
2. **Structural Parser**: Convert unstructured document into canonical JSON structure
3. **Phrase Normalization**: Map noisy multilingual phrases to canonical intents
4. **Rule Engine**: Encode coordinator logic as explicit, versioned, explainable rules
5. **Qualitative Intelligence**: Extract patterns and signals across reports
6. **Scoring & Output**: Generate actionable scores and summaries

**📖 Full Architecture:** 
- [ARCHITECTURE.md](ARCHITECTURE.md) - Complete system architecture (Original)
- [ARCHITECTURE_V2_AI_POWERED.md](ARCHITECTURE_V2_AI_POWERED.md) - AI-powered architecture V2 ⭐ **Recommended**

### Data Schema

The system uses a **canonical JSON schema** that every report must conform to, regardless of input format.

**Key Schema Principles:**
- Explicit nulls with `missing_reason`
- Confidence scores for extracted values
- Source traceability (link back to document positions)
- Extensible structure for future enhancements

**📖 Full Schema:** [SCHEMA.md](SCHEMA.md) - Complete canonical PPC JSON schema with examples

### Project Structure

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

**📖 Full Structure:** [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Detailed project organization

### API Specification

RESTful API built with FastAPI providing:
- Document management endpoints
- Report retrieval and analytics
- Admin interface for rules and dictionaries
- Health checks and monitoring

**📖 Full API Spec:** [development/API_SPECIFICATION.md](development/API_SPECIFICATION.md) - Complete API documentation

---

## 💻 Development

### Development Guide

**Tech Stack:**
- **Backend**: Python 3.11, FastAPI
- **Database**: PostgreSQL 15+ (with JSONB support)
- **Cache & Queue**: Redis, Celery
- **Object Storage**: MinIO (S3-compatible)
- **Document Processing**: python-docx, PyPDF2, pdfplumber, Tesseract OCR
- **Deployment**: Docker, Docker Compose, Kubernetes (production)

**Local Development:**
```bash
# Install dependencies
poetry install

# Start services (PostgreSQL, Redis, MinIO)
docker-compose up -d postgres redis minio

# Run migrations
poetry run alembic upgrade head

# Start API server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start Celery worker (in another terminal)
poetry run celery -A app.workers.celery_app worker --loglevel=info
```

**📖 Development Details:** See [GETTING_STARTED.md](GETTING_STARTED.md) for full development guide

### Component Architecture

#### Phrase Normalization Engine
Maps noisy multilingual phrases to canonical intents without full translation.

**📖 Details:** [development/PHRASE_NORMALIZATION_ENGINE.md](development/PHRASE_NORMALIZATION_ENGINE.md)

#### Rule Engine
Explicit, versioned rules for validation, gap detection, and compliance checking.

**📖 Details:** [development/RULE_ENGINE_ARCHITECTURE.md](development/RULE_ENGINE_ARCHITECTURE.md)

### MVP Roadmap

12-16 week implementation plan for production-ready MVP:

- **Phase 1 (Weeks 1-4)**: Foundation & Infrastructure
- **Phase 2 (Weeks 5-8)**: Core Processing Pipeline
- **Phase 3 (Weeks 9-10)**: API & Administration
- **Phase 4 (Weeks 11-12)**: Testing & Deployment

**📖 Full Roadmap:** [MVP_ROADMAP.md](MVP_ROADMAP.md) - Detailed implementation timeline

---

## ⚡ Performance & Optimization

### Performance Optimizations

The system has been optimized for **lightning-fast response times** and **cost efficiency**:

#### Response Times
- ⚡ **Cached Requests**: <50ms
- ⚡ **Database Queries**: <200ms (was ~500ms)
- ⚡ **API Responses**: <100ms average (was ~300ms)

#### Resource Usage
- 💾 **Memory**: Reduced by 40-60%
- 🖥️ **CPU**: Better utilization with async operations
- 📡 **Bandwidth**: Reduced by 70-90% with compression
- 🗄️ **Database Load**: Reduced by 60-80% with caching

#### Key Optimizations
- **Database**: Connection pooling (20 connections), asyncpg, comprehensive indexes
- **Caching**: Redis with 50 connection pool, optimized TTLs
- **API**: GZip compression, uvloop, httptools, 4 workers
- **Docker**: Multi-stage builds (40% smaller images), resource limits
- **PostgreSQL**: Optimized shared_buffers, work_mem, max_connections

**📖 Full Details:** [PERFORMANCE_OPTIMIZATIONS.md](PERFORMANCE_OPTIMIZATIONS.md) - Complete optimization guide

### Cost Efficiency

- **Container Resources**: Right-sized with limits
- **Database Connections**: Efficient pooling reduces overhead
- **Storage I/O**: Proper indexing reduces I/O operations
- **Network**: Compression reduces data transfer costs by 70-90%

---

## 🔧 POC & Testing

### POC Guide

The project includes standalone POC scripts for testing AI-powered document analysis:

#### Option 1: Cloud Version (Anthropic Claude)
- **File**: `poc_analyzer.py`
- **Setup**: Requires Anthropic API key
- **Pros**: Highest accuracy, fast (15-30s)
- **Cons**: API costs (~$0.10-0.30 per report)

#### Option 2: Local Version (LM Studio)
- **File**: `poc_analyzer_local.py`
- **Setup**: Requires LM Studio with local model
- **Pros**: 100% offline, zero API costs, government-safe
- **Cons**: Slower (30-90s), requires LM Studio setup

#### Option 3: Enhanced Local (Beautiful PDFs) ⭐ **Recommended**
- **File**: `poc_analyzer_local_enhanced.py`
- **Setup**: Same as Option 2 + PDF libraries
- **Pros**: Everything from Option 2 + beautiful PDF reports
- **Best for**: Government presentations, stakeholder reports

**📖 POC Details:** 
- [README_POST_POC.md](README_POST_POC.md) - Complete POC guide
- [ENHANCED_POC_GUIDE.md](ENHANCED_POC_GUIDE.md) - Enhanced PDF guide
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick reference card

### Model Selection

Guide for selecting and configuring AI models for local POC:

**📖 Details:** [README_MODEL_SELECTION.md](README_MODEL_SELECTION.md) - Model selection guide

### Troubleshooting

Common issues and solutions:

**LM Studio Issues:**
- Connection problems
- Model selection
- Performance tuning

**📖 Details:** [TROUBLESHOOTING_LM_STUDIO.md](TROUBLESHOOTING_LM_STUDIO.md) - Troubleshooting guide

---

## 📊 Documentation Map

### Core Documentation
| Document | Description | Status |
|----------|-------------|--------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Original system architecture | 📘 Reference |
| [ARCHITECTURE_V2_AI_POWERED.md](ARCHITECTURE_V2_AI_POWERED.md) | AI-powered architecture V2 | ⭐ **Recommended** |
| [SCHEMA.md](SCHEMA.md) | Canonical JSON schema | 📘 Essential |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Project organization | 📘 Reference |
| [GETTING_STARTED.md](GETTING_STARTED.md) | Setup and development guide | 📘 Essential |

### Development Documentation
| Document | Description | Status |
|----------|-------------|--------|
| [MVP_ROADMAP.md](MVP_ROADMAP.md) | Implementation roadmap | 📘 Planning |
| [development/API_SPECIFICATION.md](development/API_SPECIFICATION.md) | API endpoints | 📘 Reference |
| [development/PHRASE_NORMALIZATION_ENGINE.md](development/PHRASE_NORMALIZATION_ENGINE.md) | Phrase normalization design | 📘 Technical |
| [development/RULE_ENGINE_ARCHITECTURE.md](development/RULE_ENGINE_ARCHITECTURE.md) | Rule engine design | 📘 Technical |

### Performance & Optimization
| Document | Description | Status |
|----------|-------------|--------|
| [PERFORMANCE_OPTIMIZATIONS.md](PERFORMANCE_OPTIMIZATIONS.md) | Performance guide | ⚡ **Essential** |

### POC & Testing
| Document | Description | Status |
|----------|-------------|--------|
| [README_POST_POC.md](README_POST_POC.md) | POC overview | 🔧 Testing |
| [ENHANCED_POC_GUIDE.md](ENHANCED_POC_GUIDE.md) | Enhanced PDF guide | 🔧 Testing |
| [QUICK_REFERENCE.md](QUICK_REFERENCE.md) | Quick reference | 🔧 Testing |
| [README_MODEL_SELECTION.md](README_MODEL_SELECTION.md) | Model selection | 🔧 Testing |
| [TROUBLESHOOTING_LM_STUDIO.md](TROUBLESHOOTING_LM_STUDIO.md) | Troubleshooting | 🔧 Testing |

---

## 🎯 Quick Links by Role

### For Developers
- [Getting Started](GETTING_STARTED.md) - Setup and development
- [Project Structure](PROJECT_STRUCTURE.md) - Code organization
- [API Specification](development/API_SPECIFICATION.md) - API endpoints
- [Performance Optimizations](PERFORMANCE_OPTIMIZATIONS.md) - Performance guide

### For Architects
- [Architecture V2](ARCHITECTURE_V2_AI_POWERED.md) - System architecture
- [Schema](SCHEMA.md) - Data structure
- [Phrase Normalization](development/PHRASE_NORMALIZATION_ENGINE.md) - Component design
- [Rule Engine](development/RULE_ENGINE_ARCHITECTURE.md) - Component design

### For Project Managers
- [MVP Roadmap](MVP_ROADMAP.md) - Implementation timeline
- [Architecture Overview](ARCHITECTURE.md) - High-level overview
- [Performance Metrics](PERFORMANCE_OPTIMIZATIONS.md) - Performance benchmarks

### For Testers
- [POC Guide](README_POST_POC.md) - Testing with POC scripts
- [Quick Reference](QUICK_REFERENCE.md) - Quick commands
- [Troubleshooting](TROUBLESHOOTING_LM_STUDIO.md) - Common issues

---

## 📝 Contributing

1. Read the [Architecture](ARCHITECTURE_V2_AI_POWERED.md) documentation
2. Follow the [Project Structure](PROJECT_STRUCTURE.md) guidelines
3. Review the [MVP Roadmap](MVP_ROADMAP.md) for current priorities
4. Check [Performance Optimizations](PERFORMANCE_OPTIMIZATIONS.md) for best practices

---

## 🔗 External Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Redis**: https://redis.io/docs/
- **Celery**: https://docs.celeryq.dev/
- **Docker**: https://docs.docker.com/

---

<div align="center">

**Built with ❤️ for public health impact**

*Last Updated: February 18, 2026*

</div>
