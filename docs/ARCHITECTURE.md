# Government Health Data Automation SaaS - System Architecture

## Executive Summary

This system automates the analysis, validation, and intelligence extraction from government health field survey reports, specifically targeting Preconception/Maternal Health Clinics (PPC) in Indian government health programs. It replaces manual coordination by converting messy, multilingual (Hinglish/Roman Hindi) documents into structured data, gap analysis, and decision-ready outputs.

## Core Design Philosophy

### 1. Schema-First, Language-Second
- **Principle**: Force all inputs into a strict data model
- **Rationale**: Cannot rely on perfect NLP with noisy, multilingual input
- **Implementation**: Canonical JSON schema with explicit null handling and missing_reason fields

### 2. Assume Data is Sloppy
- Broken sentences and mixed languages (Hinglish, Roman Hindi, broken English)
- Inconsistent grammar, spelling, and phrasing
- Partial answers and repeated phrases
- Design for chaos, not ideal conditions

### 3. Explainability > Fancy ML
- Every flag, gap, or insight must be traceable to source text
- Deterministic rules alongside AI inference
- Audit-safe for government use
- No black-box outputs

### 4. Government-Safe Architecture
- Transparent decision-making processes
- Complete audit trails
- Versioned rule engines
- Reproducible results

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         API Gateway Layer                        │
│                    (Authentication, Rate Limiting)               │
└─────────────────────────────────────────────────────────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│   Document      │   │   Analytics     │   │   Admin         │
│   Ingestion     │   │   Engine        │   │   Interface     │
│   Service       │   │                 │   │                 │
└─────────────────┘   └─────────────────┘   └─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Document Processing Pipeline                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Text    │→ │Structural│→ │  Phrase  │→ │   Rule   │       │
│  │Extraction│  │  Parser  │  │Normalize │  │  Engine  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
         │                                              │
         ▼                                              ▼
┌─────────────────┐                          ┌─────────────────┐
│   PostgreSQL    │                          │  Qualitative    │
│   (Structured)  │                          │  Intelligence   │
│                 │                          │     Layer       │
└─────────────────┘                          └─────────────────┘
         │                                              │
         └──────────────────┬───────────────────────────┘
                            ▼
                ┌─────────────────────────┐
                │   Scoring & Output      │
                │   Generation Engine     │
                └─────────────────────────┘
                            │
                            ▼
                ┌─────────────────────────┐
                │   Dashboard & Reports   │
                └─────────────────────────┘
```

## Component Architecture

### 1. Document Ingestion Layer

**Purpose**: Accept and normalize various document formats

**Supported Formats**:
- DOCX (Microsoft Word)
- PDF (text-based and scanned)
- Images (PNG, JPG) with OCR fallback

**Responsibilities**:
- Extract raw text with layout preservation
- Preserve section boundaries and hierarchies
- Extract tables and maintain structure
- Preserve checkbox semantics (Yes/No/NA)
- Timestamp and track ingestion metadata
- Store original documents for audit trail

**Technology Stack**:
- **DOCX**: python-docx
- **PDF**: PyPDF2 (text), pdfplumber (tables)
- **OCR**: Tesseract with Hindi language pack
- **Storage**: S3-compatible object storage + PostgreSQL metadata

**Output**: Raw document object with structured text blocks

```json
{
  "document_id": "doc_2025_001",
  "ingestion_timestamp": "2025-01-07T10:00:00Z",
  "source_type": "DOCX",
  "raw_text": "...",
  "sections": [
    {
      "heading": "Facility Information",
      "content": "...",
      "tables": [],
      "position": 1
    }
  ],
  "metadata": {
    "file_size": 123456,
    "page_count": 5
  }
}
```

### 2. Structural Parser (CRITICAL COMPONENT)

**Purpose**: Convert unstructured document into canonical JSON structure

**Detection Capabilities**:
- Section headings (multiple levels)
- Sub-sections and nested structures
- Tables with header detection
- Checkbox fields (Yes/No/NA/Blank)
- Numeric fields with units
- Free-text observation blocks
- Date fields

**Parsing Strategy**:
1. **Template Matching**: Identify document type using known patterns
2. **Section Extraction**: Map headings to schema sections
3. **Field Extraction**: Extract values using regex + position heuristics
4. **Table Parsing**: Convert tabular data to structured arrays
5. **Completeness Check**: Mark missing fields explicitly

**Handling Incompleteness**:
- Every field has three states: `present`, `missing`, `invalid`
- Track `missing_reason`: "not_found", "unreadable", "ambiguous"
- Store extraction confidence scores
- Link extracted data back to source text positions

**Output**: Canonical JSON (see Schema section)

### 3. Phrase Normalization Engine

**Purpose**: Map noisy multilingual phrases to canonical intents WITHOUT full translation

**Why Not Translation**:
- Roman Hindi/Hinglish doesn't translate cleanly
- Domain-specific terminology
- Faster and more deterministic
- Preserves original phrasing for audit

**Architecture**:

```
Input Phrase
    │
    ▼
┌─────────────────┐
│ Preprocessing   │ (lowercase, trim, remove special chars)
│                 │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Token Matching  │ (fuzzy match against phrase dictionary)
│                 │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│ Intent Mapping  │ (map to canonical intent codes)
│                 │
└─────────────────┘
    │
    ▼
Normalized Intent + Confidence
```

**Phrase Dictionary Structure**:

```json
{
  "phrases": [
    {
      "raw_patterns": [
        "pti ka exident",
        "pati ka accident",
        "husband accident",
        "pti ka accident ho gya"
      ],
      "canonical_intent": "REASON_HUSBAND_ACCIDENT",
      "category": "ATTENDANCE_BARRIER",
      "severity": "high",
      "match_type": "fuzzy",
      "min_confidence": 0.7
    },
    {
      "raw_patterns": [
        "mayke gyi",
        "mayke me hai",
        "maternal home",
        "sasural se mayke"
      ],
      "canonical_intent": "REASON_BENEFICIARY_AT_MATERNAL_HOME",
      "category": "ATTENDANCE_BARRIER",
      "severity": "medium",
      "match_type": "fuzzy",
      "min_confidence": 0.75
    },
    {
      "raw_patterns": [
        "asha nai btaya",
        "asha ne nahi bataya",
        "asha did not inform",
        "asha se inform nahi"
      ],
      "canonical_intent": "ASHA_COMMUNICATION_FAILURE",
      "category": "SYSTEM_FAILURE",
      "severity": "high",
      "match_type": "fuzzy",
      "min_confidence": 0.8
    },
    {
      "raw_patterns": [
        "sample room temp",
        "sample room temperature me",
        "cold chain nahi",
        "fridge me nahi rakha"
      ],
      "canonical_intent": "LAB_SAMPLE_STORAGE_VIOLATION",
      "category": "PROTOCOL_VIOLATION",
      "severity": "critical",
      "match_type": "fuzzy",
      "min_confidence": 0.85
    }
  ]
}
```

**Matching Algorithm**:
1. Preprocess input phrase
2. Compute similarity scores against all patterns (Levenshtein distance, token overlap)
3. Select best match above confidence threshold
4. Return canonical intent + confidence + original phrase
5. Log unmatched phrases for dictionary expansion

**Storage**:
```json
{
  "raw_phrase": "pti ka exident ho gya",
  "normalized_intent": "REASON_HUSBAND_ACCIDENT",
  "confidence": 0.87,
  "match_pattern": "pti ka accident ho gya",
  "category": "ATTENDANCE_BARRIER",
  "severity": "high"
}
```

### 4. Rule Engine (COORDINATOR REPLACEMENT)

**Purpose**: Encode coordinator logic as explicit, versioned, explainable rules

**Rule Categories**:

1. **Completeness Rules**: Detect missing data
2. **Consistency Rules**: Detect logical contradictions
3. **Protocol Rules**: Detect protocol violations
4. **Compliance Rules**: Check against government guidelines

**Rule Structure**:

```json
{
  "rule_id": "R_PPC_001",
  "version": "1.0",
  "name": "High BMI without exercise counselling",
  "category": "PROTOCOL_VIOLATION",
  "severity": "medium",
  "condition": {
    "and": [
      {"field": "beneficiary.bmi", "operator": ">=", "value": 25},
      {"field": "counselling.exercise_provided", "operator": "!=", "value": true}
    ]
  },
  "action": {
    "flag": "MISSING_EXERCISE_COUNSELLING_HIGH_BMI",
    "message": "Beneficiary has BMI >= 25 but no exercise counselling recorded",
    "remediation": "Ensure exercise counselling is provided and documented for overweight beneficiaries"
  },
  "evidence_fields": ["beneficiary.bmi", "counselling.exercise_provided"]
}
```

**Example Rules**:

```json
{
  "rules": [
    {
      "rule_id": "R_PPC_002",
      "name": "Lab sample storage violation",
      "condition": {
        "and": [
          {"field": "lab.sample_storage", "operator": "==", "value": "room_temperature"},
          {"field": "lab.storage_duration_hours", "operator": ">", "value": 2}
        ]
      },
      "action": {
        "flag": "CRITICAL_LAB_SAMPLE_STORAGE_VIOLATION",
        "severity": "critical"
      }
    },
    {
      "rule_id": "R_PPC_003",
      "name": "Low beneficiary turnout",
      "condition": {
        "field": "clinic.beneficiary_count",
        "operator": "<",
        "value_from": "clinic.expected_count",
        "threshold_percent": 50
      },
      "action": {
        "flag": "MOBILIZATION_FAILURE",
        "severity": "high"
      }
    },
    {
      "rule_id": "R_PPC_004",
      "name": "Lab tests done but no report sharing",
      "condition": {
        "and": [
          {"field": "lab.tests_completed", "operator": "==", "value": true},
          {"field": "lab.reports_shared_with_beneficiary", "operator": "==", "value": false}
        ]
      },
      "action": {
        "flag": "LAB_FOLLOW_UP_FAILURE",
        "severity": "medium"
      }
    }
  ]
}
```

**Rule Engine Implementation**:

```python
class RuleEngine:
    def __init__(self, rule_definitions):
        self.rules = self._load_rules(rule_definitions)

    def evaluate(self, document_data):
        """Evaluate all rules against document data"""
        findings = []

        for rule in self.rules:
            if self._evaluate_condition(rule['condition'], document_data):
                finding = {
                    'rule_id': rule['rule_id'],
                    'rule_name': rule['name'],
                    'severity': rule['action']['severity'],
                    'flag': rule['action']['flag'],
                    'message': rule['action']['message'],
                    'evidence': self._extract_evidence(
                        rule['evidence_fields'],
                        document_data
                    ),
                    'timestamp': datetime.utcnow()
                }
                findings.append(finding)

        return findings

    def _evaluate_condition(self, condition, data):
        """Recursively evaluate condition tree"""
        if 'and' in condition:
            return all(self._evaluate_condition(c, data) for c in condition['and'])
        elif 'or' in condition:
            return any(self._evaluate_condition(c, data) for c in condition['or'])
        else:
            return self._evaluate_simple_condition(condition, data)
```

**Rule Versioning**:
- Rules stored in database with version history
- Each evaluation records rule version used
- Allows historical re-evaluation with updated rules
- Rule changes trigger impact analysis

### 5. Qualitative Intelligence Layer

**Purpose**: Extract patterns and signals that humans miss

**Analysis Types**:

1. **Frequency Analysis**
   - Most common attendance barriers
   - Recurring facility issues
   - Frequent protocol violations

2. **Pattern Detection**
   - ASHA performance patterns across facilities
   - Time-based trends (seasonal, day-of-week)
   - Geographic patterns

3. **Systemic Bottleneck Identification**
   - Infrastructure gaps (space, equipment)
   - Staffing patterns
   - Lab capacity issues
   - Supply chain problems

4. **Weak Signal Detection**
   - Early warning indicators
   - Emerging issues before they become critical
   - Correlation between seemingly unrelated factors

**Implementation Strategy**:

```python
class QualitativeIntelligence:
    def analyze_cross_facility(self, documents, time_range):
        """Analyze patterns across multiple facilities"""

        insights = {
            'attendance_barriers': self._analyze_attendance_patterns(documents),
            'asha_performance': self._analyze_asha_performance(documents),
            'lab_bottlenecks': self._detect_lab_issues(documents),
            'systemic_gaps': self._identify_systemic_gaps(documents),
            'weak_signals': self._detect_weak_signals(documents)
        }

        return insights

    def _analyze_attendance_patterns(self, documents):
        """Group and rank attendance barriers"""
        barriers = defaultdict(int)

        for doc in documents:
            for reason in doc.get('beneficiary', {}).get('attendance_issues', []):
                intent = self.phrase_normalizer.normalize(reason)
                barriers[intent['canonical_intent']] += 1

        return sorted(barriers.items(), key=lambda x: x[1], reverse=True)
```

**Output Examples**:

```json
{
  "time_period": "2025-Q4",
  "facilities_analyzed": 45,
  "insights": {
    "top_attendance_barriers": [
      {
        "barrier": "REASON_BENEFICIARY_AT_MATERNAL_HOME",
        "frequency": 87,
        "percentage": 34.2,
        "severity": "medium",
        "recommendation": "Schedule clinics around local festivals; improve advance notification"
      },
      {
        "barrier": "ASHA_COMMUNICATION_FAILURE",
        "frequency": 56,
        "percentage": 22.0,
        "severity": "high",
        "recommendation": "ASHA training intervention required; implement SMS backup system"
      }
    ],
    "systemic_bottlenecks": [
      {
        "issue": "LAB_CAPACITY_OVERLOAD",
        "affected_facilities": ["CHC Badsali", "PHC Haroli"],
        "evidence": "Sample processing delays > 48hrs in 78% of cases",
        "recommendation": "Consider mobile lab unit or increase lab staffing"
      }
    ],
    "weak_signals": [
      {
        "signal": "Increasing 'family emergency' mentions",
        "trend": "up 23% month-over-month",
        "hypothesis": "Economic stress leading to migration/work conflicts",
        "action": "Monitor; consider evening clinic pilot"
      }
    ]
  }
}
```

### 6. Scoring & Output Generation

**Purpose**: Generate actionable scores and summaries

**Scoring Components**:

1. **Facility Compliance Score** (0-100)
   - Data completeness: 30%
   - Protocol adherence: 40%
   - Outcome quality: 30%

2. **Process Adherence Score** (0-100)
   - Pre-clinic preparation: 25%
   - Clinic execution: 50%
   - Post-clinic follow-up: 25%

3. **Risk Flags**
   - **Low**: Minor documentation gaps
   - **Medium**: Protocol deviations
   - **High**: Critical violations or systemic failures

**Output Formats**:

1. **Executive Summary** (Plain English)
2. **Detailed Report** (PDF with drill-down)
3. **Dashboard Data** (JSON API)
4. **Excel Export** (For government stakeholders)

**Example Output**:

```json
{
  "facility": "CHC Badsali",
  "report_date": "2025-12-04",
  "scores": {
    "compliance": 72,
    "process_adherence": 68,
    "data_quality": 85
  },
  "risk_level": "medium",
  "flags": [
    {
      "severity": "high",
      "category": "MOBILIZATION",
      "message": "Only 1 beneficiary attended vs. 8 expected"
    },
    {
      "severity": "medium",
      "category": "PROTOCOL",
      "message": "High BMI case without exercise counselling"
    }
  ],
  "executive_summary": "CHC Badsali conducted PPC clinic on 04-Dec-2025 with significantly low turnout (1/8 beneficiaries). Primary barriers: ASHA communication failure and beneficiaries at maternal homes. Protocol adherence was generally good except for missing exercise counselling for overweight beneficiary. Recommend ASHA training and improved advance notification system.",
  "recommendations": [
    {
      "priority": "high",
      "action": "Conduct ASHA training on beneficiary mobilization",
      "owner": "Block Coordinator"
    },
    {
      "priority": "medium",
      "action": "Implement SMS backup notification system",
      "owner": "IT Team"
    }
  ]
}
```

## Data Models

See [SCHEMA.md](SCHEMA.md) for complete canonical JSON schema.

## Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI (async, high performance)
- **Task Queue**: Celery + Redis
- **Document Processing**: python-docx, PyPDF2, pdfplumber, Tesseract OCR

### Database
- **Primary**: PostgreSQL 15+ (structured data, JSONB support)
- **Cache**: Redis
- **Object Storage**: MinIO (S3-compatible) or AWS S3
- **Optional**: PostgreSQL pgvector for future semantic search

### API & Integration
- **API**: RESTful with FastAPI
- **Authentication**: JWT-based
- **Rate Limiting**: Redis-based
- **Documentation**: OpenAPI/Swagger

### Frontend (Future)
- **Framework**: React or Vue.js
- **Visualization**: Chart.js, D3.js
- **Export**: jsPDF, xlsx

### DevOps
- **Containerization**: Docker
- **Orchestration**: Docker Compose (dev), Kubernetes (production)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana

## Security & Compliance

### Data Privacy
- All PII encrypted at rest
- Role-based access control (RBAC)
- Audit logging for all data access

### Government Compliance
- Complete audit trails
- Deterministic rule evaluation
- Version control for all rules and schemas
- Data retention policies

### Backup & Recovery
- Daily automated backups
- Point-in-time recovery capability
- Disaster recovery plan

## Scalability Considerations

### Current MVP Target
- 100 facilities
- ~500 reports/month
- 5-10 concurrent users

### Future Scale (Year 2)
- 1000+ facilities
- ~5000 reports/month
- 50+ concurrent users
- Multi-state deployment

### Architecture Decisions for Scale
- Async processing for document ingestion
- Horizontal scaling of API servers
- Read replicas for analytics queries
- CDN for static assets and reports

## Deployment Architecture

### Development Environment
```
Docker Compose:
- API Server (FastAPI)
- PostgreSQL
- Redis
- MinIO (object storage)
- Celery Worker
```

### Production Environment
```
Kubernetes:
- API Server (3 replicas, auto-scaling)
- PostgreSQL (managed service)
- Redis (managed service)
- S3 (managed service)
- Celery Workers (auto-scaling based on queue depth)
- Load Balancer
```

## Assumptions & Limitations

### Assumptions
1. Reports follow generally consistent structure (even if content is messy)
2. Ground workers will continue using similar language patterns
3. Basic internet connectivity available for API access
4. Reports are submitted within reasonable time after clinic (< 1 week)

### Current Limitations
1. **Languages**: Optimized for Hinglish/Roman Hindi; may need tuning for other Indian languages
2. **Document Types**: Initial support for DOCX, PDF, images only
3. **OCR Quality**: Depends on scan quality; may require manual review for very poor scans
4. **Real-time Processing**: Currently batch-oriented; near-real-time possible but not in MVP
5. **Mobile App**: Not in MVP; web-based upload only

### Known Challenges
1. **Phrase Dictionary Maintenance**: Requires ongoing curation as language evolves
2. **Rule Evolution**: Government guidelines change; rules need regular updates
3. **Data Quality Variance**: Some facilities may produce consistently poor data
4. **Adoption Curve**: Change management needed for field teams and coordinators

## Success Metrics

### Technical Metrics
- Document processing accuracy: >95%
- API response time: <2s (p95)
- System uptime: >99.5%
- Data extraction completeness: >90%

### Business Metrics
- Manual coordination effort reduction: >60%
- Time to insights: <24hrs (from submission to analyzed report)
- User satisfaction: >4/5
- Cost per report processed: <$0.50

### Quality Metrics
- False positive rate (incorrect flags): <5%
- False negative rate (missed issues): <2%
- Audit success rate: 100%

## Future Enhancements (Post-MVP)

### Phase 2
- Multi-program support (ANC, immunization, etc.)
- Trend detection and predictive analytics
- Mobile app for field workers
- SMS integration for notifications

### Phase 3
- ML-based anomaly detection
- Automated report generation for government
- Integration with existing government systems (HMIS, etc.)
- Multi-language support expansion

### Phase 4
- Prescription generation assistance
- Resource allocation optimization
- Beneficiary tracking across visits
- State-level aggregation and comparison

## Conclusion

This architecture prioritizes:
1. **Reliability**: Works with messy, real-world data
2. **Explainability**: Every decision is traceable
3. **Scalability**: Can grow from pilot to state-wide
4. **Government-readiness**: Audit-safe and compliant
5. **Maintainability**: Modular, well-documented, version-controlled

The system is designed to handle chaos while producing order—exactly what's needed for government health data automation.
