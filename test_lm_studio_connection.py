#!/usr/bin/env python3
"""
Quick diagnostic script to test LM Studio connection and model
"""

import os
from openai import OpenAI

print("="*80)
print("LM STUDIO CONNECTION TEST")
print("="*80)

# Configuration
base_url = os.environ.get("LM_STUDIO_URL", "http://192.168.56.1:1234/v1")
model_name = os.environ.get("LM_STUDIO_MODEL", "phi-4-reasoning-plus")

print(f"\n1. Testing connection to: {base_url}")
print(f"2. Using model: {model_name}")

try:
    client = OpenAI(base_url=base_url, api_key="test")

    # Test 1: Simple greeting
    print("\n" + "="*80)
    print("TEST 1: Simple greeting (low token count)")
    print("="*80)

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "user", "content": "Say 'Hello, I am working!' and nothing else."}
        ],
        max_tokens=50,
        temperature=0.7
    )

    response_text = response.choices[0].message.content
    print(f"✅ Response: {response_text}")
    print(f"✅ Length: {len(response_text)} characters")

    # Test 2: JSON generation
    print("\n" + "="*80)
    print("TEST 2: Simple JSON generation")
    print("="*80)

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that responds only with valid JSON."
            },
            {
                "role": "user",
                "content": """Return this exact JSON and nothing else:
{
  "status": "working",
  "message": "LM Studio is functioning correctly",
  "test": true
}"""
            }
        ],
        max_tokens=200,
        temperature=0.3
    )

    response_text = response.choices[0].message.content
    print(f"Response:\n{response_text}")
    print(f"\n✅ Length: {len(response_text)} characters")

    # Try to parse as JSON
    import json
    try:
        data = json.loads(response_text.strip().replace('```json', '').replace('```', ''))
        print(f"✅ Valid JSON! Parsed: {data}")
    except:
        print("⚠️  Response is not valid JSON, but model is responding")

    # Test 3: Check model info
    print("\n" + "="*80)
    print("TEST 3: Checking available models")
    print("="*80)

    try:
        models = client.models.list()
        print("Available models:")
        for model in models.data:
            print(f"  - {model.id}")
    except Exception as e:
        print(f"⚠️  Could not list models: {e}")

    # Test 4: Longer context test
    print("\n" + "="*80)
    print("TEST 4: Medium-length input (~500 chars)")
    print("="*80)

    test_text = """
    Patient Visit Report

    Facility: Sample Health Center
    Date: 2024-01-15

    Beneficiaries Expected: 25
    Beneficiaries Attended: 18

    Services Provided:
    - Blood pressure screening: 18 patients
    - Hemoglobin testing: 15 patients
    - Counseling: 12 patients

    Issues:
    - Equipment shortage
    - Staff absent

    Extract the key numbers from this report as JSON with fields: expected, attended, bp_tests, hb_tests.
    Return ONLY valid JSON.
    """

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "system",
                "content": "You are a data extraction assistant. Extract structured data and return only valid JSON."
            },
            {
                "role": "user",
                "content": test_text
            }
        ],
        max_tokens=500,
        temperature=0.3
    )

    response_text = response.choices[0].message.content
    print(f"Response:\n{response_text}")
    print(f"\n✅ Length: {len(response_text)} characters")

    if len(response_text) == 0:
        print("\n⚠️  WARNING: Empty response for medium-length input!")
        print("This suggests the model may have issues with context length or content filtering.")

    print("\n" + "="*80)
    print("DIAGNOSIS COMPLETE")
    print("="*80)

    print("\n✅ LM Studio is responding to requests")
    print(f"✅ Model '{model_name}' is working")

    print("\n💡 Next steps:")
    print("   1. If all tests passed: The model works, issue might be with long documents")
    print("   2. If Test 4 failed (empty response): Your document is too long for the model")
    print("   3. If JSON tests failed: Model doesn't follow JSON instructions well")

    print("\n💡 Recommendations:")
    print("   - Try a model with larger context window (Qwen 2.5, Llama 3.1)")
    print("   - Or chunk your document into smaller parts")
    print("   - Or use a cloud API for large documents")

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\n💡 Troubleshooting:")
    print("   1. Is LM Studio running?")
    print("   2. Is a model loaded?")
    print("   3. Is the local server started?")
    print(f"   4. Try accessing in browser: {base_url.replace('/v1', '')}")

    import traceback
    traceback.print_exc()

print("\n" + "="*80)
