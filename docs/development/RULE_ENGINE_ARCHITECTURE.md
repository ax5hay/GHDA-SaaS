# Rule Engine Architecture - Design Document

## Overview

The Rule Engine is the heart of the automated validation and compliance checking system. It replaces human coordinators by encoding their knowledge as explicit, versioned, explainable rules that can be automatically evaluated against parsed report data.

## Design Principles

1. **Explainability**: Every rule evaluation must be traceable
2. **Versioning**: Rules are versioned like code
3. **Editability**: Rules can be updated without code deployment
4. **Deterministic**: Same input + same rules = same output
5. **Performance**: Fast evaluation even with hundreds of rules

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Rule Engine                              │
└─────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
   ┌──────────┐        ┌──────────┐        ┌──────────┐
   │  Rule    │        │ Condition│        │ Evidence │
   │  Loader  │        │ Evaluator│        │Collector │
   └──────────┘        └──────────┘        └──────────┘
         │                    │                    │
         └────────────────────┴────────────────────┘
                              │
                              ▼
                      ┌──────────────┐
                      │   Findings   │
                      │  (Results)   │
                      └──────────────┘
```

## Core Components

### 1. Rule Definition Structure

**JSON Schema**:
```json
{
  "rule_id": "R_PPC_001",
  "version": "1.0",
  "name": "Human-readable rule name",
  "category": "PROTOCOL_VIOLATION | SYSTEM_FAILURE | ...",
  "severity": "low | medium | high | critical",
  "condition": {
    // Condition tree (see below)
  },
  "action": {
    "flag": "FLAG_CODE",
    "message": "Human-readable message",
    "remediation": "Recommended action"
  },
  "evidence_fields": ["field1", "field2"],
  "active": true,
  "created_at": "2025-01-07T00:00:00Z",
  "updated_at": "2025-01-07T00:00:00Z"
}
```

**Rule Categories**:
- `PROTOCOL_VIOLATION`: Violation of standard protocols
- `SYSTEM_FAILURE`: Systemic issues (ASHA, lab, etc.)
- `MOBILIZATION`: Beneficiary mobilization issues
- `INFRASTRUCTURE_GAP`: Physical infrastructure problems
- `STAFFING_ISSUE`: Staff-related problems
- `SUPPLY_SHORTAGE`: Supply/equipment shortages
- `PROCESS_DELAY`: Delays in processes
- `PROTOCOL_DEVIATION`: Minor deviations from protocol
- `QUALITY_ISSUE`: Quality problems
- `FOLLOW_UP`: Follow-up action required

**Severity Levels**:
- `low`: Minor issue, for information only
- `medium`: Moderate issue, should be addressed
- `high`: Significant issue, requires prompt action
- `critical`: Severe issue, immediate intervention required

### 2. Condition Expression Language

Rules use a simple but powerful expression language to specify conditions.

#### Simple Condition
```json
{
  "field": "beneficiaries.attendance_rate",
  "operator": "<",
  "value": 0.5
}
```

**Supported Operators**:
- `==`: Equal
- `!=`: Not equal
- `<`: Less than
- `<=`: Less than or equal
- `>`: Greater than
- `>=`: Greater than or equal
- `contains`: Array/string contains value
- `not_contains`: Array/string does not contain value
- `in`: Value in list
- `not_in`: Value not in list
- `is_null`: Field is null/missing
- `is_not_null`: Field exists and not null
- `matches_regex`: Field matches regex pattern

#### Compound Conditions

**AND**:
```json
{
  "and": [
    {"field": "beneficiaries.bmi", "operator": ">=", "value": 25},
    {"field": "counselling.exercise_provided", "operator": "!=", "value": true}
  ]
}
```

**OR**:
```json
{
  "or": [
    {"field": "staff.medical_officer_present", "operator": "==", "value": false},
    {"field": "staff.nurse_present", "operator": "==", "value": false}
  ]
}
```

**NOT**:
```json
{
  "not": {
    "field": "compliance.due_list_prepared",
    "operator": "==",
    "value": true
  }
}
```

**Nested**:
```json
{
  "and": [
    {"field": "laboratory.samples_collected", "operator": ">", "value": 0},
    {
      "or": [
        {"field": "laboratory.results_received", "operator": "==", "value": false},
        {"field": "laboratory.results_shared", "operator": "==", "value": false}
      ]
    }
  ]
}
```

#### Array Operations

**Contains Object**:
```json
{
  "field": "beneficiaries.attendance_barriers",
  "operator": "array_contains",
  "value": {
    "normalized_intent": "ASHA_COMMUNICATION_FAILURE"
  }
}
```

**Count Where**:
```json
{
  "field": "beneficiaries.attendance_barriers",
  "operator": "array_count_where",
  "condition": {
    "normalized_intent": "ASHA_COMMUNICATION_FAILURE"
  },
  "comparator": ">",
  "threshold": 2
}
```

**Any Match**:
```json
{
  "field": "clinical_services.staff_present",
  "operator": "array_any_match",
  "condition": {
    "designation": "Medical Officer",
    "present": false
  }
}
```

### 3. Rule Evaluator

**Core Evaluation Engine**:

```python
from typing import Any, Dict, List
from datetime import datetime


class RuleEvaluator:
    """Evaluate rules against document data."""

    def evaluate_condition(
        self,
        condition: Dict,
        data: Dict
    ) -> bool:
        """
        Recursively evaluate condition tree.

        Args:
            condition: Condition dictionary
            data: Document data to evaluate against

        Returns:
            True if condition is met, False otherwise
        """
        # Handle compound conditions
        if 'and' in condition:
            return all(
                self.evaluate_condition(sub_cond, data)
                for sub_cond in condition['and']
            )

        if 'or' in condition:
            return any(
                self.evaluate_condition(sub_cond, data)
                for sub_cond in condition['or']
            )

        if 'not' in condition:
            return not self.evaluate_condition(condition['not'], data)

        # Handle simple conditions
        return self._evaluate_simple_condition(condition, data)

    def _evaluate_simple_condition(
        self,
        condition: Dict,
        data: Dict
    ) -> bool:
        """Evaluate a simple condition."""
        field_path = condition['field']
        operator = condition['operator']
        expected_value = condition.get('value')

        # Get field value from data
        actual_value = self._get_nested_field(data, field_path)

        # Evaluate based on operator
        return self._apply_operator(
            actual_value,
            operator,
            expected_value,
            condition
        )

    def _get_nested_field(
        self,
        data: Dict,
        field_path: str
    ) -> Any:
        """
        Get value from nested dictionary using dot notation.

        Example: "beneficiaries.attendance_rate" -> data['beneficiaries']['attendance_rate']
        """
        keys = field_path.split('.')
        value = data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None

        return value

    def _apply_operator(
        self,
        actual: Any,
        operator: str,
        expected: Any,
        condition: Dict
    ) -> bool:
        """Apply comparison operator."""
        if operator == '==':
            return actual == expected

        elif operator == '!=':
            return actual != expected

        elif operator == '<':
            return actual is not None and actual < expected

        elif operator == '<=':
            return actual is not None and actual <= expected

        elif operator == '>':
            return actual is not None and actual > expected

        elif operator == '>=':
            return actual is not None and actual >= expected

        elif operator == 'contains':
            return expected in actual if actual is not None else False

        elif operator == 'not_contains':
            return expected not in actual if actual is not None else True

        elif operator == 'in':
            return actual in expected if actual is not None else False

        elif operator == 'not_in':
            return actual not in expected if actual is not None else True

        elif operator == 'is_null':
            return actual is None

        elif operator == 'is_not_null':
            return actual is not None

        elif operator == 'array_contains':
            return self._array_contains(actual, expected)

        elif operator == 'array_any_match':
            return self._array_any_match(
                actual,
                condition.get('condition', {})
            )

        elif operator == 'array_count_where':
            count = self._array_count_where(
                actual,
                condition.get('condition', {})
            )
            comparator = condition.get('comparator', '>')
            threshold = condition.get('threshold', 0)

            if comparator == '>':
                return count > threshold
            elif comparator == '>=':
                return count >= threshold
            elif comparator == '<':
                return count < threshold
            elif comparator == '<=':
                return count <= threshold
            elif comparator == '==':
                return count == threshold
            else:
                return False

        else:
            raise ValueError(f"Unknown operator: {operator}")

    def _array_contains(self, array: List, expected: Dict) -> bool:
        """Check if array contains object matching expected properties."""
        if not isinstance(array, list):
            return False

        for item in array:
            if self._object_matches(item, expected):
                return True

        return False

    def _array_any_match(self, array: List, condition: Dict) -> bool:
        """Check if any array item matches condition."""
        if not isinstance(array, list):
            return False

        for item in array:
            if self._object_matches(item, condition):
                return True

        return False

    def _array_count_where(self, array: List, condition: Dict) -> int:
        """Count array items matching condition."""
        if not isinstance(array, list):
            return 0

        count = 0
        for item in array:
            if self._object_matches(item, condition):
                count += 1

        return count

    def _object_matches(self, obj: Dict, condition: Dict) -> bool:
        """Check if object matches all properties in condition."""
        if not isinstance(obj, dict):
            return False

        for key, expected_value in condition.items():
            if obj.get(key) != expected_value:
                return False

        return True
```

### 4. Rule Engine

**Main Orchestrator**:

```python
class RuleEngine:
    """Main rule engine that orchestrates rule evaluation."""

    def __init__(self, rules: List[Dict]):
        """
        Initialize rule engine.

        Args:
            rules: List of rule definitions
        """
        self.rules = [r for r in rules if r.get('active', True)]
        self.evaluator = RuleEvaluator()

    def evaluate_all(self, document_data: Dict) -> List[Dict]:
        """
        Evaluate all rules against document data.

        Args:
            document_data: Parsed report data (canonical JSON)

        Returns:
            List of findings (rule violations)
        """
        findings = []

        for rule in self.rules:
            try:
                if self.evaluator.evaluate_condition(
                    rule['condition'],
                    document_data
                ):
                    finding = self._create_finding(rule, document_data)
                    findings.append(finding)

            except Exception as e:
                # Log error but continue with other rules
                print(f"Error evaluating rule {rule['rule_id']}: {e}")

        return findings

    def _create_finding(self, rule: Dict, data: Dict) -> Dict:
        """Create finding object from rule and data."""
        return {
            'rule_id': rule['rule_id'],
            'rule_version': rule['version'],
            'rule_name': rule['name'],
            'category': rule['category'],
            'severity': rule['severity'],
            'flag': rule['action']['flag'],
            'message': rule['action']['message'],
            'remediation': rule['action'].get('remediation'),
            'evidence': self._collect_evidence(
                rule['evidence_fields'],
                data
            ),
            'evaluated_at': datetime.utcnow().isoformat()
        }

    def _collect_evidence(
        self,
        evidence_fields: List[str],
        data: Dict
    ) -> Dict:
        """Collect evidence values for finding."""
        evidence = {}

        for field_path in evidence_fields:
            value = self.evaluator._get_nested_field(data, field_path)
            evidence[field_path] = value

        return evidence

    def evaluate_single_rule(
        self,
        rule_id: str,
        document_data: Dict
    ) -> Dict | None:
        """Evaluate a single rule by ID."""
        rule = next((r for r in self.rules if r['rule_id'] == rule_id), None)

        if not rule:
            return None

        if self.evaluator.evaluate_condition(rule['condition'], document_data):
            return self._create_finding(rule, document_data)

        return None
```

### 5. Rule Loader

**Load Rules from Database or Files**:

```python
import json
from typing import List, Dict


class RuleLoader:
    """Load rules from various sources."""

    @staticmethod
    def load_from_file(file_path: str) -> List[Dict]:
        """Load rules from JSON file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data.get('rules', [])

    @staticmethod
    def load_from_database(db_session, program: str = 'PPC') -> List[Dict]:
        """Load rules from database."""
        # Query active rules for program
        rules = db_session.query(Rule).filter(
            Rule.program == program,
            Rule.active == True
        ).all()

        return [rule.to_dict() for rule in rules]

    @staticmethod
    def load_by_version(
        db_session,
        program: str,
        version: str
    ) -> List[Dict]:
        """Load specific version of rules."""
        rules = db_session.query(Rule).filter(
            Rule.program == program,
            Rule.version == version
        ).all()

        return [rule.to_dict() for rule in rules]
```

## Usage Examples

### Example 1: Basic Rule Evaluation

```python
# Load rules
rules = RuleLoader.load_from_file('data/rules/ppc_rules_v1.json')

# Create engine
engine = RuleEngine(rules)

# Load document data
document_data = {
    "beneficiaries": {
        "expected_count": 8,
        "actual_count": 1,
        "attendance_rate": 0.125
    }
}

# Evaluate
findings = engine.evaluate_all(document_data)

for finding in findings:
    print(f"[{finding['severity']}] {finding['rule_name']}")
    print(f"  {finding['message']}")
    print(f"  Evidence: {finding['evidence']}")
```

### Example 2: Single Rule Evaluation

```python
finding = engine.evaluate_single_rule('R_PPC_003', document_data)

if finding:
    print(f"Rule triggered: {finding['flag']}")
else:
    print("Rule passed")
```

### Example 3: Custom Rule Addition

```python
# Add a new rule dynamically
new_rule = {
    "rule_id": "R_PPC_CUSTOM_001",
    "version": "1.0",
    "name": "Custom validation rule",
    "category": "CUSTOM",
    "severity": "medium",
    "condition": {
        "field": "some_field",
        "operator": ">",
        "value": 10
    },
    "action": {
        "flag": "CUSTOM_FLAG",
        "message": "Custom condition met"
    },
    "evidence_fields": ["some_field"],
    "active": True
}

engine.rules.append(new_rule)
findings = engine.evaluate_all(document_data)
```

## Rule Versioning Strategy

### Semantic Versioning

Rules follow semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (condition structure changes)
- **MINOR**: New fields or operators (backward compatible)
- **PATCH**: Message/remediation updates

### Version Storage

```sql
CREATE TABLE rules (
    id UUID PRIMARY KEY,
    rule_id VARCHAR(50) NOT NULL,
    version VARCHAR(20) NOT NULL,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    condition JSONB NOT NULL,
    action JSONB NOT NULL,
    evidence_fields JSONB NOT NULL,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(rule_id, version)
);

CREATE INDEX idx_rules_active ON rules(active) WHERE active = true;
CREATE INDEX idx_rules_category ON rules(category);
```

### Rule Audit Trail

```sql
CREATE TABLE rule_evaluations (
    id UUID PRIMARY KEY,
    report_id UUID REFERENCES reports(id),
    rule_id VARCHAR(50) NOT NULL,
    rule_version VARCHAR(20) NOT NULL,
    triggered BOOLEAN NOT NULL,
    finding JSONB,
    evaluated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_rule_eval_report ON rule_evaluations(report_id);
CREATE INDEX idx_rule_eval_rule ON rule_evaluations(rule_id);
```

## Performance Optimization

### 1. Rule Caching

```python
from functools import lru_cache

class CachedRuleEngine(RuleEngine):
    @lru_cache(maxsize=100)
    def _evaluate_condition_cached(
        self,
        condition_json: str,
        data_hash: str
    ) -> bool:
        """Cache rule evaluations."""
        condition = json.loads(condition_json)
        # Evaluate...
        return result
```

### 2. Parallel Evaluation

```python
from concurrent.futures import ThreadPoolExecutor

class ParallelRuleEngine(RuleEngine):
    def evaluate_all(self, document_data: Dict) -> List[Dict]:
        """Evaluate rules in parallel."""
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(self._evaluate_rule, rule, document_data)
                for rule in self.rules
            ]

            findings = []
            for future in futures:
                result = future.result()
                if result:
                    findings.append(result)

            return findings
```

### 3. Early Termination

```python
class OptimizedRuleEngine(RuleEngine):
    def evaluate_all(
        self,
        document_data: Dict,
        stop_on_critical: bool = False
    ) -> List[Dict]:
        """Optionally stop on first critical finding."""
        findings = []

        for rule in self.rules:
            if self.evaluator.evaluate_condition(rule['condition'], document_data):
                finding = self._create_finding(rule, document_data)
                findings.append(finding)

                if stop_on_critical and finding['severity'] == 'critical':
                    break

        return findings
```

## Testing Strategy

### Unit Tests

```python
def test_simple_condition():
    evaluator = RuleEvaluator()

    condition = {
        "field": "value",
        "operator": ">",
        "value": 10
    }

    data = {"value": 15}
    assert evaluator.evaluate_condition(condition, data) == True

    data = {"value": 5}
    assert evaluator.evaluate_condition(condition, data) == False


def test_compound_condition():
    evaluator = RuleEvaluator()

    condition = {
        "and": [
            {"field": "a", "operator": ">", "value": 10},
            {"field": "b", "operator": "<", "value": 20}
        ]
    }

    data = {"a": 15, "b": 15}
    assert evaluator.evaluate_condition(condition, data) == True
```

### Integration Tests

```python
def test_full_rule_evaluation():
    rules = RuleLoader.load_from_file('test_rules.json')
    engine = RuleEngine(rules)

    test_data = load_test_document()
    findings = engine.evaluate_all(test_data)

    assert len(findings) > 0
    assert any(f['rule_id'] == 'R_PPC_003' for f in findings)
```

## Monitoring & Observability

### Rule Execution Metrics

```python
from prometheus_client import Counter, Histogram

rule_evaluations = Counter(
    'rule_evaluations_total',
    'Total rule evaluations',
    ['rule_id', 'triggered']
)

rule_evaluation_duration = Histogram(
    'rule_evaluation_duration_seconds',
    'Rule evaluation duration',
    ['rule_id']
)
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

class LoggingRuleEngine(RuleEngine):
    def evaluate_all(self, document_data: Dict) -> List[Dict]:
        logger.info(f"Evaluating {len(self.rules)} rules")

        findings = super().evaluate_all(document_data)

        logger.info(
            f"Found {len(findings)} violations: "
            f"{sum(1 for f in findings if f['severity'] == 'critical')} critical, "
            f"{sum(1 for f in findings if f['severity'] == 'high')} high"
        )

        return findings
```

## Conclusion

The Rule Engine provides a powerful, flexible, and maintainable way to encode domain knowledge and automate validation. Its explainability and versioning make it suitable for government use cases where audit trails and transparency are critical.
