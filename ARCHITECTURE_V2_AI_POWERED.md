# Government Health Data Automation SaaS - AI-Powered Architecture V2

## Critical Insight: Why Pattern Matching Fails

**REALITY CHECK**: Ground health workers write in completely unpredictable ways:
- Mixed languages (Hinglish, Roman Hindi, broken English)
- Inconsistent spelling, grammar, abbreviations
- Local slang, colloquialisms, shortcuts
- Varying report structures
- Incomplete information

**CONCLUSION**: Rigid phrase dictionaries and pattern matching **will fail** in real-world conditions.

**SOLUTION**: AI-powered extraction and analysis using Large Language Models.

---

## Architecture Evolution

### ❌ Original Approach (Pattern Matching)

```
Document → Extract Text → Match Phrases → Apply Rules → Output
                            ↑ FAILS HERE
              (Can't handle unexpected input)
```

**Problems**:
- Phrase dictionary requires maintaining 1000s of patterns
- New expressions constantly appear
- Typos break pattern matching
- Context-dependent meanings missed
- Breaks on code-switching (Hinglish)

### ✅ New Approach (AI-Powered)

```
Document → Extract Text → AI Analysis → Structured Output → Validation → Storage
                            ↑ WORKS
              (Understands context, handles chaos)
```

**Advantages**:
- Handles ANY input variation
- Understands context and semantics
- No pattern maintenance
- Works with typos, abbreviations, slang
- Scales to new programs without retraining

---

## Revised System Architecture

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
│   Upload        │   │   Dashboard     │   │   Interface     │
└─────────────────┘   └─────────────────┘   └─────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AI-Powered Processing Pipeline                │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │  Text    │→ │    AI    │→ │  Schema  │→ │   Rule   │       │
│  │Extraction│  │ Analysis │  │Validation│  │  Engine  │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
│                      ↑                                          │
│              (Claude, GPT, or                                   │
│               Local LM Studio)                                  │
└─────────────────────────────────────────────────────────────────┘
         │                                              │
         ▼                                              ▼
┌─────────────────┐                          ┌─────────────────┐
│   PostgreSQL    │                          │  Historical     │
│   (Structured)  │                          │  Trend Analysis │
└─────────────────┘                          └─────────────────┘
```

---

## Core Components Redesign

### 1. Document Ingestion (UNCHANGED)

Still extracts raw text from DOCX/PDF/images with OCR.

**No changes needed** - this component just extracts text.

### 2. AI Analysis Engine (NEW - REPLACES Parser + Normalizer)

**Purpose**: Use LLM to convert raw text → structured JSON

**Input**: Raw, messy text in any language/format
**Output**: Canonical JSON conforming to schema

**Implementation Options**:

#### Option A: Cloud API (Anthropic Claude)
```python
import anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

def analyze_document(raw_text: str) -> dict:
    prompt = f"""Extract structured data from this health report.
    Return JSON matching this schema: {{...}}

    Report: {raw_text}
    """

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response.content[0].text)
```

**Pros**:
- Highest accuracy
- Latest AI capabilities
- No infrastructure needed

**Cons**:
- Requires internet
- API costs (~$0.10-0.30/report)
- Data privacy concerns

**Cost**: ~$100-300 for 1000 reports (negligible for government contracts)

#### Option B: Local LM Studio (RECOMMENDED FOR GOVERNMENT)
```python
from openai import OpenAI

# Connect to local LM Studio
client = OpenAI(
    base_url="http://192.168.56.1:1234/v1",
    api_key="lm-studio"
)

def analyze_document(raw_text: str) -> dict:
    response = client.chat.completions.create(
        model="local-model",
        messages=[
            {"role": "system", "content": "You are a health data analyst..."},
            {"role": "user", "content": f"Analyze: {raw_text}"}
        ],
        temperature=0.3
    )

    return json.loads(response.choices[0].message.content)
```

**Pros**:
- ✅ **100% offline** - no data leaves facility
- ✅ **Zero API costs** - unlimited processing
- ✅ **Government-safe** - data privacy guaranteed
- ✅ **No internet dependency**

**Cons**:
- Requires GPU server (or fast CPU)
- Initial setup needed
- Model quality varies

**Recommended Models** (for LM Studio):
- **Qwen 2.5** (14B/32B) - Excellent for analysis
- **Llama 3.1** (8B/70B) - Good general purpose
- **Mistral** (7B+) - Fast, decent quality

**Infrastructure**:
- GPU: RTX 4090 or better (or A100 for production)
- CPU: 64GB RAM minimum for 14B models
- Or cloud GPU: RunPod, Vast.ai (~$0.50/hour)

#### Option C: Hybrid (BEST OF BOTH WORLDS)
- **Production**: Local LM Studio for privacy
- **Fallback**: Cloud API if local fails
- **Development**: Cloud API for speed

### 3. Schema Validation (NEW)

**Purpose**: Ensure AI output matches canonical schema

**Why Needed**: AI sometimes hallucinates or omits fields

```python
from jsonschema import validate, ValidationError

def validate_and_fix(ai_output: dict) -> dict:
    """Validate AI output and fill missing required fields."""
    try:
        validate(ai_output, PPC_SCHEMA)
        return ai_output
    except ValidationError as e:
        # Fix common issues
        fixed = auto_fix_schema(ai_output, e)
        return fixed

def auto_fix_schema(data: dict, error: ValidationError) -> dict:
    """Automatically fix common schema violations."""
    # Add missing required fields with nulls
    # Fix type mismatches
    # Ensure array fields are arrays
    # etc.
    return fixed_data
```

### 4. Rule Engine (MOSTLY UNCHANGED)

Rules still apply to validated JSON, but now more reliable because:
- Data is already structured by AI
- Fields are consistent
- Better data quality

**Minor enhancement**: Add confidence thresholds

```python
class RuleEngine:
    def evaluate_with_confidence(self, data: dict, min_confidence: float = 0.7):
        """Only apply rules to high-confidence data."""

        findings = []
        for rule in self.rules:
            # Check if relevant fields have sufficient confidence
            if self._has_sufficient_confidence(rule, data, min_confidence):
                if self.evaluate_condition(rule['condition'], data):
                    findings.append(self._create_finding(rule, data))

        return findings
```

### 5. Historical Trend Analysis (NEW)

**Purpose**: Analyze patterns across facilities and time

**Implementation**: Use AI to identify trends

```python
def analyze_trends(reports: List[dict]) -> dict:
    """AI-powered trend analysis across multiple reports."""

    summary = summarize_reports(reports)

    prompt = f"""Analyze these {len(reports)} health reports for patterns:

    {summary}

    Identify:
    1. Recurring problems across facilities
    2. Systemic issues
    3. Best practices
    4. Emerging trends
    5. Intervention opportunities

    Return JSON with insights."""

    insights = ai_client.analyze(prompt)
    return insights
```

---

## Data Flow (AI-Powered)

### Single Document Processing

```
1. Upload DOCX/PDF
   ↓
2. Extract Text (python-docx, PyPDF2, Tesseract)
   ↓
3. AI Analysis (Claude/Local LLM)
   - Understands context
   - Extracts all fields
   - Handles any language
   - Returns structured JSON
   ↓
4. Schema Validation
   - Verify JSON structure
   - Fix common issues
   - Add confidence scores
   ↓
5. Rule Engine Evaluation
   - Apply compliance rules
   - Generate findings
   - Assign risk levels
   ↓
6. Storage (PostgreSQL JSONB)
   ↓
7. Dashboard Update
```

**Time**: 15-60 seconds per document (depending on AI backend)

### Batch Analytics

```
1. Query Reports (by facility/date/program)
   ↓
2. Aggregate Data
   ↓
3. AI Trend Analysis
   - Cross-facility patterns
   - Time-based trends
   - Risk prediction
   ↓
4. Generate Insights
   ↓
5. Dashboard Visualization
```

---

## Deployment Options

### Option 1: Cloud-Only (Fastest to Deploy)

```
User → AWS/GCP → FastAPI → Claude API → PostgreSQL
```

**Pros**: Quick setup, no AI infrastructure
**Cons**: API costs, data privacy concerns

**Cost**: ~$500/month (API + hosting for 1000 reports/month)

### Option 2: Local LM Studio (Government-Safe)

```
User → On-Premise Server → FastAPI → Local LLM → PostgreSQL
```

**Pros**: 100% offline, data privacy, no API costs
**Cons**: Requires GPU server

**Cost**: ~$5000 one-time (GPU server) + $100/month (hosting)

### Option 3: Hybrid (RECOMMENDED)

```
User → Cloud Load Balancer
        ├→ Local LLM (primary)
        └→ Cloud API (fallback if local fails)
```

**Pros**: Best of both, high availability
**Cons**: More complex setup

**Cost**: ~$5000 one-time + $300/month

---

## Technology Stack (Updated)

### AI Layer (NEW)
- **Cloud**: Anthropic Claude API (or OpenAI GPT-4)
- **Local**: LM Studio + Qwen/Llama models
- **Client**: `anthropic` or `openai` Python packages

### Backend (UNCHANGED)
- **Framework**: FastAPI
- **Database**: PostgreSQL (JSONB for flexible schema)
- **Cache**: Redis
- **Task Queue**: Celery
- **Storage**: S3/MinIO

### Frontend (FUTURE)
- **Dashboard**: React/Vue
- **Visualization**: Chart.js, D3.js

---

## Schema Design (AI-Friendly)

**Key Change**: Schema must be **AI-friendly** - clear field names and descriptions

### Example: PPC Schema with AI Hints

```python
PPC_SCHEMA = {
    "type": "object",
    "description": "Preconception and Maternal Health Clinic report",
    "properties": {
        "facility": {
            "type": "object",
            "description": "Healthcare facility information",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Facility name (CHC, PHC, etc.)"
                },
                "location": {
                    "type": "object",
                    "description": "Facility location details",
                    "properties": {
                        "block": {"type": "string", "description": "Block name"},
                        "district": {"type": "string", "description": "District name"},
                        "state": {"type": "string", "description": "State name"}
                    }
                }
            },
            "required": ["name"]
        },

        "beneficiaries": {
            "type": "object",
            "description": "Beneficiary attendance and barriers",
            "properties": {
                "expected_count": {
                    "type": "integer",
                    "description": "Number of beneficiaries expected to attend"
                },
                "actual_count": {
                    "type": "integer",
                    "description": "Number who actually attended"
                },
                "attendance_barriers": {
                    "type": "array",
                    "description": "Reasons why beneficiaries did not attend",
                    "items": {
                        "type": "object",
                        "properties": {
                            "reason": {
                                "type": "string",
                                "description": "Specific reason for non-attendance (in worker's own words)"
                            },
                            "count": {
                                "type": "integer",
                                "description": "Number of beneficiaries with this reason"
                            },
                            "barrier_type": {
                                "type": "string",
                                "enum": ["communication", "cultural", "economic", "health", "logistical", "systemic", "other"],
                                "description": "Category of barrier"
                            },
                            "severity": {
                                "type": "string",
                                "enum": ["low", "medium", "high", "critical"],
                                "description": "Impact severity"
                            }
                        }
                    }
                }
            }
        }
    }
}
```

**AI Prompt includes schema** → AI follows structure

---

## Updated MVP Roadmap (AI-Powered)

### Week 1-2: AI Integration

1. **Choose AI backend** (Cloud vs Local vs Hybrid)
2. **Set up LM Studio** if using local
3. **Implement AI analysis function**
4. **Test with 10 sample reports**
5. **Tune prompts** for accuracy

### Week 3-4: Schema & Validation

1. **Finalize AI-friendly schema**
2. **Build validation layer**
3. **Create auto-fix utilities**
4. **Test edge cases**

### Week 5-6: Rule Engine Integration

1. **Integrate validated data with rules**
2. **Add confidence thresholds**
3. **Test compliance detection**

### Week 7-8: API & Dashboard

1. **Build API endpoints**
2. **Create simple dashboard**
3. **Add batch processing**

### Week 9-12: Testing & Deployment

1. **Test with real reports (100+)**
2. **Optimize AI prompts**
3. **Deploy to staging**
4. **Pilot with 5 facilities**

---

## Performance & Costs

### AI Processing Performance

| Backend | Time per Report | Cost per Report | Setup Cost |
|---------|----------------|-----------------|------------|
| Claude API | 15-30 sec | $0.10-0.30 | $0 |
| GPT-4 API | 20-40 sec | $0.15-0.40 | $0 |
| Local (Qwen 14B) | 30-90 sec | $0 | $5,000 |
| Local (Llama 70B) | 60-180 sec | $0 | $10,000 |

### Recommended for Government

**Start**: Cloud API (Claude) for pilot
**Scale**: Migrate to Local LLM for production

**Why**:
- Pilot proves concept quickly
- Production ensures data privacy
- No ongoing API costs at scale

---

## Security & Privacy

### Data Privacy with Local LLM

✅ **No data leaves facility**
✅ **No third-party API calls**
✅ **Government-compliant**
✅ **Audit-safe**

### Hybrid Model Security

- **Sensitive data**: Process locally only
- **Non-sensitive analytics**: Can use cloud
- **Always encrypt data at rest**
- **Complete audit logs**

---

## Success Metrics

### MVP Success (Same as Before)

- ✅ Process 100 documents with <5% error
- ✅ Data extraction accuracy >90%
- ✅ Processing time <60 seconds
- ✅ User satisfaction >4/5

### AI-Specific Metrics

- ✅ **Schema compliance**: >95% valid JSON
- ✅ **Field extraction**: >90% accuracy
- ✅ **Barrier identification**: >85% correct classification
- ✅ **Prompt stability**: <5% variation across runs

---

## Migration Path (From Pattern Matching to AI)

If you already built pattern matching:

1. **Keep existing pipeline** as backup
2. **Add AI layer in parallel**
3. **Compare outputs** (AI vs patterns)
4. **Gradually shift** to AI as confidence grows
5. **Deprecate patterns** once AI proves reliable

---

## Conclusion

**The paradigm shift**:

❌ **Old**: Try to predict every possible input → maintain huge dictionaries → fail on unexpected input

✅ **New**: Let AI understand anything → extract to schema → validate → apply rules

**Result**:
- Works with **ANY** input
- **Zero dictionary maintenance**
- **Handles typos, slang, code-switching**
- **Government-safe with local LLM**
- **Scales to new programs** without retraining

**This is the only architecture that will work in real-world government deployments.**

---

**Document Version**: 2.0 (AI-Powered)
**Supersedes**: ARCHITECTURE.md v1.0
**Date**: 2026-01-07
