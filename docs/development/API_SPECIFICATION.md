# API Specification - Government Health Data Automation SaaS

## Base URL

```
Production: https://api.ghda-saas.gov.in/api/v1
Staging: https://staging-api.ghda-saas.gov.in/api/v1
Development: http://localhost:8000/api/v1
```

## Authentication

All API endpoints (except public health checks) require JWT authentication.

### Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response 200:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Authenticated Requests

Include JWT token in Authorization header:

```http
GET /reports
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## Document Management

### Upload Document

```http
POST /documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

Form Data:
- file: <file> (required) - DOCX, PDF, or image file
- program: string (optional, default: "PPC") - Program type
- facility_id: uuid (optional) - Facility UUID

Response 201:
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "ppc_report_jan_2025.docx",
  "file_type": "DOCX",
  "file_size": 45632,
  "status": "pending",
  "uploaded_at": "2025-01-07T10:30:00Z",
  "processing_url": "/api/v1/documents/550e8400-e29b-41d4-a716-446655440000/status"
}
```

### Get Document Status

```http
GET /documents/{document_id}/status
Authorization: Bearer <token>

Response 200:
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing" | "completed" | "failed",
  "progress": 75,
  "current_stage": "normalization",
  "stages": {
    "ingestion": {"status": "completed", "duration_ms": 1234},
    "parsing": {"status": "completed", "duration_ms": 2345},
    "normalization": {"status": "in_progress", "duration_ms": null},
    "rules": {"status": "pending", "duration_ms": null},
    "scoring": {"status": "pending", "duration_ms": null}
  },
  "report_id": "660e8400-e29b-41d4-a716-446655440001",
  "errors": []
}
```

### Get Document Metadata

```http
GET /documents/{document_id}
Authorization: Bearer <token>

Response 200:
{
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "ppc_report_jan_2025.docx",
  "file_type": "DOCX",
  "file_size": 45632,
  "status": "completed",
  "uploaded_at": "2025-01-07T10:30:00Z",
  "uploaded_by": {
    "user_id": "770e8400-e29b-41d4-a716-446655440002",
    "name": "Dr. Sharma",
    "email": "sharma@example.com"
  },
  "processing_completed_at": "2025-01-07T10:35:42Z",
  "processing_duration_ms": 28563,
  "report_id": "660e8400-e29b-41d4-a716-446655440001"
}
```

### List Documents

```http
GET /documents?status=completed&program=PPC&limit=20&offset=0
Authorization: Bearer <token>

Query Parameters:
- status: string (optional) - Filter by status
- program: string (optional) - Filter by program
- facility_id: uuid (optional) - Filter by facility
- date_from: date (optional) - Filter from date
- date_to: date (optional) - Filter to date
- limit: int (default: 20, max: 100)
- offset: int (default: 0)

Response 200:
{
  "total": 156,
  "limit": 20,
  "offset": 0,
  "documents": [
    {
      "document_id": "...",
      "filename": "...",
      "status": "completed",
      "uploaded_at": "...",
      "report_id": "..."
    }
  ]
}
```

### Delete Document

```http
DELETE /documents/{document_id}
Authorization: Bearer <token>

Response 204: No Content
```

## Reports

### Get Report

```http
GET /reports/{report_id}
Authorization: Bearer <token>

Response 200:
{
  "report_id": "660e8400-e29b-41d4-a716-446655440001",
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "schema_version": "1.0.0",
  "data": {
    // Full canonical JSON (see SCHEMA.md)
    "document_metadata": { ... },
    "facility": { ... },
    "clinic_details": { ... },
    "beneficiaries": { ... },
    ...
  },
  "quality_indicators": {
    "data_completeness_score": 0.93,
    "compliance_score": 72,
    "process_adherence_score": 68,
    "risk_level": "medium"
  },
  "created_at": "2025-01-07T10:35:42Z"
}
```

### List Reports

```http
GET /reports?facility_id=...&date_from=2025-01-01&limit=20
Authorization: Bearer <token>

Query Parameters:
- facility_id: uuid (optional)
- program: string (optional)
- date_from: date (optional)
- date_to: date (optional)
- risk_level: string (optional) - low, medium, high, critical
- min_compliance_score: int (optional)
- limit: int (default: 20, max: 100)
- offset: int (default: 0)
- sort_by: string (default: "created_at")
- sort_order: string (default: "desc")

Response 200:
{
  "total": 89,
  "limit": 20,
  "offset": 0,
  "reports": [
    {
      "report_id": "...",
      "facility": {
        "name": "CHC Badsali",
        "district": "Una"
      },
      "clinic_date": "2025-12-04",
      "compliance_score": 72,
      "risk_level": "medium",
      "flags_count": 3,
      "created_at": "2025-01-07T10:35:42Z"
    }
  ]
}
```

### Get Report Findings

```http
GET /reports/{report_id}/findings
Authorization: Bearer <token>

Query Parameters:
- severity: string (optional) - Filter by severity
- category: string (optional) - Filter by category

Response 200:
{
  "report_id": "660e8400-e29b-41d4-a716-446655440001",
  "total_findings": 3,
  "findings": [
    {
      "finding_id": "880e8400-e29b-41d4-a716-446655440003",
      "rule_id": "R_PPC_003",
      "rule_version": "1.0",
      "rule_name": "Low beneficiary attendance",
      "category": "MOBILIZATION",
      "severity": "high",
      "flag": "MOBILIZATION_FAILURE",
      "message": "Beneficiary attendance rate below 50% - mobilization failure",
      "remediation": "Review ASHA mobilization activities; improve advance notification",
      "evidence": {
        "beneficiaries.expected_count": 8,
        "beneficiaries.actual_count": 1,
        "beneficiaries.attendance_rate": 0.125
      },
      "evaluated_at": "2025-01-07T10:35:40Z"
    }
  ]
}
```

### Export Report

```http
GET /reports/{report_id}/export?format=pdf
Authorization: Bearer <token>

Query Parameters:
- format: string (required) - pdf, excel, json

Response 200:
Content-Type: application/pdf (or appropriate type)
Content-Disposition: attachment; filename="report_660e8400.pdf"

<binary file content>
```

## Analytics

### Facility Trends

```http
GET /analytics/facilities/{facility_id}/trends
Authorization: Bearer <token>

Query Parameters:
- date_from: date (required)
- date_to: date (required)
- metrics: string[] (optional) - List of metrics to include

Response 200:
{
  "facility": {
    "facility_id": "...",
    "name": "CHC Badsali",
    "district": "Una"
  },
  "period": {
    "from": "2024-10-01",
    "to": "2025-01-07"
  },
  "trends": {
    "compliance_score": [
      {"date": "2024-10-01", "value": 68},
      {"date": "2024-11-01", "value": 72},
      {"date": "2024-12-01", "value": 75}
    ],
    "attendance_rate": [
      {"date": "2024-10-01", "value": 0.45},
      {"date": "2024-11-01", "value": 0.52},
      {"date": "2024-12-01", "value": 0.48}
    ],
    "beneficiaries_served": [
      {"date": "2024-10-01", "value": 12},
      {"date": "2024-11-01", "value": 15},
      {"date": "2024-12-01", "value": 11}
    ]
  }
}
```

### Attendance Barriers Analysis

```http
GET /analytics/attendance-barriers
Authorization: Bearer <token>

Query Parameters:
- date_from: date (optional)
- date_to: date (optional)
- facility_id: uuid (optional)
- district: string (optional)
- limit: int (default: 20)

Response 200:
{
  "period": {
    "from": "2024-10-01",
    "to": "2025-01-07"
  },
  "facilities_analyzed": 45,
  "reports_analyzed": 234,
  "top_barriers": [
    {
      "canonical_intent": "REASON_BENEFICIARY_AT_MATERNAL_HOME",
      "frequency": 87,
      "percentage": 34.2,
      "category": "CULTURAL_SOCIAL",
      "severity": "medium",
      "trend": "stable",
      "affected_facilities": 32
    },
    {
      "canonical_intent": "ASHA_COMMUNICATION_FAILURE",
      "frequency": 56,
      "percentage": 22.0,
      "category": "COMMUNICATION_FAILURE",
      "severity": "high",
      "trend": "increasing",
      "affected_facilities": 18
    }
  ],
  "recommendations": [
    {
      "priority": "high",
      "action": "ASHA training intervention required",
      "rationale": "Communication failure detected in 18 facilities"
    }
  ]
}
```

### ASHA Performance Analysis

```http
GET /analytics/asha-performance
Authorization: Bearer <token>

Query Parameters:
- date_from: date (optional)
- date_to: date (optional)
- district: string (optional)
- min_reports: int (default: 3) - Minimum reports for analysis

Response 200:
{
  "period": {
    "from": "2024-10-01",
    "to": "2025-01-07"
  },
  "asha_workers_analyzed": 45,
  "performance_metrics": {
    "avg_mobilization_rate": 0.68,
    "communication_failure_rate": 0.22,
    "top_performers": [
      {
        "asha_name": "Sunita Devi",
        "facility": "CHC Badsali",
        "mobilization_rate": 0.89,
        "reports_analyzed": 12
      }
    ],
    "underperformers": [
      {
        "asha_name": "Rita Sharma",
        "facility": "PHC Amb",
        "mobilization_rate": 0.34,
        "communication_failures": 8,
        "reports_analyzed": 10
      }
    ]
  },
  "systemic_issues": [
    {
      "issue": "Late notification",
      "frequency": 23,
      "affected_workers": 12
    }
  ]
}
```

### Lab Bottlenecks Analysis

```http
GET /analytics/lab-bottlenecks
Authorization: Bearer <token>

Query Parameters:
- date_from: date (optional)
- date_to: date (optional)
- district: string (optional)

Response 200:
{
  "period": {
    "from": "2024-10-01",
    "to": "2025-01-07"
  },
  "labs_analyzed": 12,
  "bottlenecks": [
    {
      "issue": "LAB_CAPACITY_OVERLOAD",
      "frequency": 34,
      "affected_facilities": ["CHC Badsali", "PHC Haroli"],
      "avg_delay_days": 5.2,
      "impact": "high"
    },
    {
      "issue": "LAB_SAMPLE_STORAGE_VIOLATION",
      "frequency": 12,
      "severity": "critical",
      "affected_facilities": ["PHC Amb"]
    }
  ],
  "recommendations": [
    {
      "priority": "critical",
      "action": "Consider mobile lab unit for Una district",
      "rationale": "Consistent delays >5 days in 2 facilities"
    }
  ]
}
```

### Compliance Summary

```http
GET /analytics/compliance-summary
Authorization: Bearer <token>

Query Parameters:
- date_from: date (optional)
- date_to: date (optional)
- district: string (optional)
- program: string (optional)

Response 200:
{
  "period": {
    "from": "2024-10-01",
    "to": "2025-01-07"
  },
  "reports_analyzed": 234,
  "facilities_analyzed": 45,
  "overall_compliance": {
    "avg_compliance_score": 74.3,
    "avg_process_adherence": 71.2,
    "risk_distribution": {
      "low": 89,
      "medium": 112,
      "high": 28,
      "critical": 5
    }
  },
  "top_violations": [
    {
      "rule_id": "R_PPC_003",
      "rule_name": "Low beneficiary attendance",
      "frequency": 78,
      "severity": "high"
    }
  ],
  "improvement_areas": [
    {
      "area": "Beneficiary mobilization",
      "current_score": 65,
      "target_score": 80,
      "gap": 15
    }
  ]
}
```

## Admin

### List Rules

```http
GET /admin/rules
Authorization: Bearer <token>

Query Parameters:
- program: string (optional)
- category: string (optional)
- active: boolean (optional)
- limit: int (default: 50)
- offset: int (default: 0)

Response 200:
{
  "total": 12,
  "rules": [
    {
      "rule_id": "R_PPC_001",
      "version": "1.0",
      "name": "High BMI without exercise counselling",
      "category": "PROTOCOL_VIOLATION",
      "severity": "medium",
      "active": true,
      "created_at": "2025-01-01T00:00:00Z",
      "updated_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### Get Rule Details

```http
GET /admin/rules/{rule_id}
Authorization: Bearer <token>

Response 200:
{
  "rule_id": "R_PPC_001",
  "version": "1.0",
  "name": "High BMI without exercise counselling",
  "category": "PROTOCOL_VIOLATION",
  "severity": "medium",
  "condition": { ... },
  "action": { ... },
  "evidence_fields": [ ... ],
  "active": true,
  "evaluation_count": 1234,
  "triggered_count": 234,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

### Create Rule

```http
POST /admin/rules
Authorization: Bearer <token>
Content-Type: application/json

{
  "rule_id": "R_PPC_NEW_001",
  "version": "1.0",
  "name": "New validation rule",
  "category": "PROTOCOL_VIOLATION",
  "severity": "medium",
  "condition": { ... },
  "action": { ... },
  "evidence_fields": [ ... ]
}

Response 201:
{
  "rule_id": "R_PPC_NEW_001",
  "version": "1.0",
  ...
}
```

### Update Rule

```http
PUT /admin/rules/{rule_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated rule name",
  "severity": "high",
  ...
}

Response 200:
{
  "rule_id": "R_PPC_001",
  "version": "1.1",
  ...
}
```

### Deactivate Rule

```http
DELETE /admin/rules/{rule_id}
Authorization: Bearer <token>

Response 204: No Content
```

### Phrase Dictionary Management

```http
GET /admin/phrase-dictionary?category=attendance_barriers
POST /admin/phrase-dictionary
PUT /admin/phrase-dictionary/{phrase_id}
DELETE /admin/phrase-dictionary/{phrase_id}
```

### Audit Logs

```http
GET /admin/audit-logs
Authorization: Bearer <token>

Query Parameters:
- user_id: uuid (optional)
- action: string (optional)
- resource_type: string (optional)
- date_from: date (optional)
- date_to: date (optional)
- limit: int (default: 50)
- offset: int (default: 0)

Response 200:
{
  "total": 567,
  "logs": [
    {
      "log_id": "...",
      "user": {
        "user_id": "...",
        "name": "Admin User",
        "email": "admin@example.com"
      },
      "action": "rule_updated",
      "resource_type": "rule",
      "resource_id": "R_PPC_001",
      "changes": { ... },
      "ip_address": "192.168.1.1",
      "timestamp": "2025-01-07T10:30:00Z"
    }
  ]
}
```

## Health Checks

### Basic Health

```http
GET /health

Response 200:
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "production",
  "timestamp": "2025-01-07T10:30:00Z"
}
```

### Database Health

```http
GET /health/db
Authorization: Bearer <token>

Response 200:
{
  "status": "healthy",
  "database": "connected",
  "response_time_ms": 12,
  "pool_size": 10,
  "active_connections": 3
}
```

### Worker Health

```http
GET /health/workers
Authorization: Bearer <token>

Response 200:
{
  "status": "healthy",
  "workers": [
    {
      "worker_id": "worker-1",
      "status": "online",
      "queued_tasks": 5,
      "active_tasks": 2
    }
  ]
}
```

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { ... },
    "timestamp": "2025-01-07T10:30:00Z",
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### Common Error Codes

- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Missing or invalid authentication
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `409 Conflict`: Resource conflict
- `413 Payload Too Large`: File too large
- `415 Unsupported Media Type`: Invalid file type
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

## Rate Limiting

- **Authenticated Users**: 1000 requests/hour
- **Document Upload**: 50 uploads/hour
- **Analytics**: 100 requests/hour

Rate limit headers included in all responses:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1704628800
```

## Pagination

All list endpoints support pagination:

- `limit`: Number of items (max 100)
- `offset`: Starting position
- Response includes `total`, `limit`, `offset`

## Sorting

List endpoints support sorting:

- `sort_by`: Field name
- `sort_order`: `asc` or `desc`

## Filtering

Most list endpoints support filtering via query parameters. See individual endpoint documentation.

## Webhooks (Future)

Webhook support planned for Phase 2:

- Document processing completed
- Critical findings detected
- Report thresholds breached
