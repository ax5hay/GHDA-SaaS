# Phrase Normalization Engine - Design Document

## Overview

The Phrase Normalization Engine is a critical component that maps noisy, multilingual phrases (Hinglish, Roman Hindi, broken English) to canonical intents WITHOUT performing full translation. This approach is faster, more deterministic, and preserves original phrasing for audit purposes.

## Why Not Translation?

1. **Roman Hindi/Hinglish doesn't translate cleanly**: Mixed language constructs lose meaning in translation
2. **Domain-specific terminology**: Health program terms have specific canonical forms
3. **Speed**: Pattern matching is faster than full NLP translation
4. **Deterministic**: Same input always produces same output
5. **Audit trail**: Preserves original text with mappings

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   Phrase Normalization Engine                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Preprocessing   │
                    │  - Lowercase     │
                    │  - Trim          │
                    │  - Remove punct  │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Token Matching  │
                    │  - Fuzzy match   │
                    │  - Levenshtein   │
                    │  - Token overlap │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Intent Mapping  │
                    │  - Best match    │
                    │  - Confidence    │
                    │  - Category      │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Output          │
                    │  - Intent code   │
                    │  - Confidence    │
                    │  - Category      │
                    │  - Original      │
                    └──────────────────┘
```

## Core Components

### 1. Phrase Dictionary

**Structure**: JSON-based dictionary with versioning

**Schema**:
```json
{
  "version": "1.0.0",
  "description": "Phrase dictionary for attendance barriers",
  "phrases": [
    {
      "id": "ATT_001",
      "raw_patterns": [
        "pti ka exident",
        "pati ka accident",
        "husband accident"
      ],
      "canonical_intent": "REASON_HUSBAND_ACCIDENT",
      "category": "PERSONAL_EMERGENCY",
      "severity": "high",
      "match_type": "fuzzy",
      "min_confidence": 0.7
    }
  ]
}
```

**Key Fields**:
- `raw_patterns`: List of known variations
- `canonical_intent`: Normalized intent code (UPPERCASE_WITH_UNDERSCORES)
- `category`: High-level grouping
- `severity`: Impact level
- `match_type`: exact, fuzzy, or semantic
- `min_confidence`: Minimum confidence threshold for this pattern

### 2. Preprocessor

**Purpose**: Normalize input text for matching

**Operations**:
```python
def preprocess(text: str) -> str:
    # Lowercase
    text = text.lower()

    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Remove special characters (keep alphanumeric + space)
    text = re.sub(r'[^a-z0-9\s]', '', text)

    # Normalize common variations
    text = text.replace('exident', 'accident')
    text = text.replace('pti', 'pati')
    text = text.replace('btaya', 'bataya')

    return text
```

**Character Normalization Table**:
```python
NORMALIZATION_MAP = {
    'exident': 'accident',
    'pti': 'pati',
    'btaya': 'bataya',
    'nai': 'nahi',
    'gyi': 'gayi',
    'kya': 'kiya',
    # Add more as discovered
}
```

### 3. Phrase Matcher

**Purpose**: Match input phrase against pattern dictionary

**Matching Algorithms**:

#### A. Exact Match
```python
def exact_match(input_phrase: str, pattern: str) -> float:
    """Return 1.0 if exact match, 0.0 otherwise."""
    return 1.0 if input_phrase == pattern else 0.0
```

#### B. Fuzzy Match (Levenshtein Distance)
```python
from rapidfuzz import fuzz

def fuzzy_match(input_phrase: str, pattern: str) -> float:
    """Calculate fuzzy match score using Levenshtein distance."""
    return fuzz.ratio(input_phrase, pattern) / 100.0
```

#### C. Token Overlap
```python
def token_overlap_match(input_phrase: str, pattern: str) -> float:
    """Calculate match score based on token overlap."""
    input_tokens = set(input_phrase.split())
    pattern_tokens = set(pattern.split())

    if not pattern_tokens:
        return 0.0

    intersection = input_tokens & pattern_tokens
    overlap_ratio = len(intersection) / len(pattern_tokens)

    return overlap_ratio
```

#### D. Weighted Combination
```python
def calculate_match_score(
    input_phrase: str,
    pattern: str,
    weights: dict = None
) -> float:
    """Combine multiple matching strategies."""
    if weights is None:
        weights = {
            'fuzzy': 0.6,
            'token_overlap': 0.4
        }

    scores = {
        'fuzzy': fuzzy_match(input_phrase, pattern),
        'token_overlap': token_overlap_match(input_phrase, pattern)
    }

    weighted_score = sum(
        scores[method] * weight
        for method, weight in weights.items()
    )

    return weighted_score
```

### 4. Intent Mapper

**Purpose**: Map best match to canonical intent

**Algorithm**:
```python
class IntentMapper:
    def __init__(self, phrase_dictionary: dict):
        self.phrases = phrase_dictionary['phrases']

    def map_intent(self, input_phrase: str) -> dict:
        """Map input phrase to canonical intent."""
        preprocessed = self.preprocess(input_phrase)

        best_match = {
            'canonical_intent': None,
            'confidence': 0.0,
            'category': None,
            'severity': None,
            'matched_pattern': None
        }

        for phrase_entry in self.phrases:
            for pattern in phrase_entry['raw_patterns']:
                score = calculate_match_score(preprocessed, pattern)

                if score > best_match['confidence']:
                    if score >= phrase_entry['min_confidence']:
                        best_match = {
                            'canonical_intent': phrase_entry['canonical_intent'],
                            'confidence': score,
                            'category': phrase_entry['category'],
                            'severity': phrase_entry['severity'],
                            'matched_pattern': pattern
                        }

        return best_match
```

### 5. Confidence Scorer

**Purpose**: Calculate and adjust confidence scores

**Factors Affecting Confidence**:

1. **String Similarity** (60%)
   - Levenshtein distance
   - Handles typos and minor variations

2. **Token Overlap** (40%)
   - Shared words between input and pattern
   - Robust to word order changes

**Confidence Adjustment**:
```python
def adjust_confidence(
    base_confidence: float,
    input_length: int,
    pattern_length: int
) -> float:
    """Adjust confidence based on length similarity."""
    length_diff = abs(input_length - pattern_length)
    max_length = max(input_length, pattern_length)

    length_penalty = length_diff / max_length
    adjusted = base_confidence * (1 - (length_penalty * 0.2))

    return max(0.0, min(1.0, adjusted))
```

## Implementation

### Core Class: `PhraseNormalizer`

```python
from typing import Dict, List, Optional
from rapidfuzz import fuzz
import json
import re


class PhraseNormalizer:
    """Normalize noisy multilingual phrases to canonical intents."""

    def __init__(self, dictionary_path: str):
        """Initialize with phrase dictionary."""
        with open(dictionary_path, 'r', encoding='utf-8') as f:
            self.dictionary = json.load(f)

        self.phrases = self.dictionary['phrases']

    def preprocess(self, text: str) -> str:
        """Preprocess input text."""
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^a-z0-9\s]', '', text)

        # Apply character normalizations
        for old, new in NORMALIZATION_MAP.items():
            text = text.replace(old, new)

        return text

    def calculate_match_score(
        self,
        input_phrase: str,
        pattern: str
    ) -> float:
        """Calculate match score between input and pattern."""
        fuzzy_score = fuzz.ratio(input_phrase, pattern) / 100.0

        input_tokens = set(input_phrase.split())
        pattern_tokens = set(pattern.split())

        if pattern_tokens:
            overlap = len(input_tokens & pattern_tokens) / len(pattern_tokens)
        else:
            overlap = 0.0

        # Weighted combination
        final_score = (fuzzy_score * 0.6) + (overlap * 0.4)

        return final_score

    def normalize(self, input_phrase: str) -> Dict:
        """
        Normalize input phrase to canonical intent.

        Returns:
            {
                'raw_phrase': str,
                'canonical_intent': str | None,
                'confidence': float,
                'category': str | None,
                'severity': str | None,
                'matched_pattern': str | None
            }
        """
        preprocessed = self.preprocess(input_phrase)

        best_match = {
            'raw_phrase': input_phrase,
            'canonical_intent': None,
            'confidence': 0.0,
            'category': None,
            'severity': None,
            'matched_pattern': None
        }

        for phrase_entry in self.phrases:
            for pattern in phrase_entry['raw_patterns']:
                preprocessed_pattern = self.preprocess(pattern)
                score = self.calculate_match_score(
                    preprocessed,
                    preprocessed_pattern
                )

                if score > best_match['confidence']:
                    if score >= phrase_entry['min_confidence']:
                        best_match.update({
                            'canonical_intent': phrase_entry['canonical_intent'],
                            'confidence': round(score, 3),
                            'category': phrase_entry['category'],
                            'severity': phrase_entry['severity'],
                            'matched_pattern': pattern
                        })

        return best_match

    def normalize_batch(
        self,
        phrases: List[str]
    ) -> List[Dict]:
        """Normalize multiple phrases."""
        return [self.normalize(phrase) for phrase in phrases]
```

## Usage Examples

### Example 1: Single Phrase
```python
normalizer = PhraseNormalizer('data/phrase_dictionaries/ppc_attendance_barriers.json')

result = normalizer.normalize("pti ka exident ho gya")

print(result)
# {
#     'raw_phrase': 'pti ka exident ho gya',
#     'canonical_intent': 'REASON_HUSBAND_ACCIDENT',
#     'confidence': 0.89,
#     'category': 'PERSONAL_EMERGENCY',
#     'severity': 'high',
#     'matched_pattern': 'pti ka accident ho gya'
# }
```

### Example 2: Batch Processing
```python
phrases = [
    "asha nai btaya tha",
    "mayke gyi thi",
    "family emergency"
]

results = normalizer.normalize_batch(phrases)

for result in results:
    print(f"{result['raw_phrase']} -> {result['canonical_intent']} ({result['confidence']})")

# Output:
# asha nai btaya tha -> ASHA_COMMUNICATION_FAILURE (0.89)
# mayke gyi thi -> REASON_BENEFICIARY_AT_MATERNAL_HOME (0.93)
# family emergency -> REASON_FAMILY_EMERGENCY (0.95)
```

### Example 3: Low Confidence / No Match
```python
result = normalizer.normalize("completely unknown phrase xyz")

print(result)
# {
#     'raw_phrase': 'completely unknown phrase xyz',
#     'canonical_intent': None,
#     'confidence': 0.0,
#     'category': None,
#     'severity': None,
#     'matched_pattern': None
# }
```

## Dictionary Management

### Adding New Phrases

1. **Identify New Pattern**:
   - Review unmatched phrases from processing logs
   - Cluster similar unmatched phrases

2. **Create Entry**:
```json
{
  "id": "ATT_013",
  "raw_patterns": [
    "new pattern 1",
    "new pattern 2"
  ],
  "canonical_intent": "NEW_INTENT_CODE",
  "category": "APPROPRIATE_CATEGORY",
  "severity": "medium",
  "match_type": "fuzzy",
  "min_confidence": 0.75
}
```

3. **Test**:
   - Test against known examples
   - Verify confidence scores
   - Check for collisions with existing patterns

4. **Version Control**:
   - Increment dictionary version
   - Document changes in changelog
   - Deploy new version

### Dictionary Versioning

```json
{
  "version": "1.1.0",
  "changelog": [
    {
      "version": "1.1.0",
      "date": "2025-01-15",
      "changes": [
        "Added 5 new attendance barrier patterns",
        "Improved confidence thresholds for ASHA patterns"
      ]
    },
    {
      "version": "1.0.0",
      "date": "2025-01-07",
      "changes": [
        "Initial release"
      ]
    }
  ]
}
```

## Performance Optimization

### 1. Caching
```python
from functools import lru_cache

class CachedPhraseNormalizer(PhraseNormalizer):
    @lru_cache(maxsize=1000)
    def normalize(self, input_phrase: str) -> Dict:
        """Cached normalization for repeated phrases."""
        return super().normalize(input_phrase)
```

### 2. Indexing
```python
# Build inverted index for faster lookup
class IndexedPhraseNormalizer(PhraseNormalizer):
    def __init__(self, dictionary_path: str):
        super().__init__(dictionary_path)
        self._build_index()

    def _build_index(self):
        """Build token-based index for faster lookup."""
        self.token_index = {}

        for phrase_entry in self.phrases:
            for pattern in phrase_entry['raw_patterns']:
                tokens = self.preprocess(pattern).split()
                for token in tokens:
                    if token not in self.token_index:
                        self.token_index[token] = []
                    self.token_index[token].append(phrase_entry)
```

### 3. Batch Processing
- Process multiple phrases in parallel
- Use multiprocessing for large batches

## Quality Assurance

### 1. Unit Tests
```python
def test_exact_match():
    normalizer = PhraseNormalizer('test_dictionary.json')
    result = normalizer.normalize("exact pattern match")
    assert result['confidence'] == 1.0

def test_fuzzy_match():
    normalizer = PhraseNormalizer('test_dictionary.json')
    result = normalizer.normalize("exect pattern match")  # typo
    assert result['confidence'] > 0.8
    assert result['canonical_intent'] == 'EXPECTED_INTENT'
```

### 2. Confidence Distribution Analysis
```python
# Analyze confidence scores across test set
def analyze_confidence_distribution(test_cases):
    results = [normalizer.normalize(tc) for tc in test_cases]

    high_confidence = [r for r in results if r['confidence'] > 0.9]
    medium_confidence = [r for r in results if 0.7 <= r['confidence'] <= 0.9]
    low_confidence = [r for r in results if r['confidence'] < 0.7]

    print(f"High confidence: {len(high_confidence)}")
    print(f"Medium confidence: {len(medium_confidence)}")
    print(f"Low confidence: {len(low_confidence)}")
```

### 3. Collision Detection
```python
# Check for pattern collisions
def detect_collisions(dictionary):
    patterns_seen = {}
    collisions = []

    for phrase_entry in dictionary['phrases']:
        for pattern in phrase_entry['raw_patterns']:
            if pattern in patterns_seen:
                collisions.append({
                    'pattern': pattern,
                    'intent1': patterns_seen[pattern],
                    'intent2': phrase_entry['canonical_intent']
                })
            else:
                patterns_seen[pattern] = phrase_entry['canonical_intent']

    return collisions
```

## Monitoring & Improvement

### 1. Log Unmatched Phrases
```python
class LoggingPhraseNormalizer(PhraseNormalizer):
    def normalize(self, input_phrase: str) -> Dict:
        result = super().normalize(input_phrase)

        if result['canonical_intent'] is None:
            # Log for future dictionary expansion
            log_unmatched_phrase(input_phrase)

        return result
```

### 2. Confidence Analytics
- Track average confidence by category
- Identify patterns with consistently low confidence
- Refine patterns based on confidence distributions

### 3. Dictionary Evolution
- Weekly review of unmatched phrases
- Monthly dictionary updates
- Quarterly confidence threshold adjustments

## Limitations

1. **New Domains**: Requires new dictionary for each domain
2. **Evolving Language**: Slang and new terms need manual addition
3. **Context-Free**: Doesn't understand semantic context
4. **Homonyms**: Can't disambiguate words with multiple meanings

## Future Enhancements

1. **Semantic Matching**: Add embeddings-based matching for better semantic understanding
2. **Context Awareness**: Use surrounding text for disambiguation
3. **Auto-Discovery**: ML-based clustering of unmatched phrases
4. **Multi-Dictionary**: Support multiple dictionaries simultaneously
5. **Real-time Learning**: Semi-automated pattern discovery

## Conclusion

The Phrase Normalization Engine provides a fast, deterministic, and audit-safe way to handle noisy multilingual input. By focusing on pattern matching rather than translation, it achieves high accuracy while maintaining explainability—critical for government applications.
