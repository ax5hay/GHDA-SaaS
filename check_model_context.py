#!/usr/bin/env python3
"""
Check what context length your LM Studio model can actually handle
"""

import os
from openai import OpenAI

print("="*80)
print("MODEL CONTEXT WINDOW TESTER")
print("="*80)

base_url = os.environ.get("LM_STUDIO_URL", "http://192.168.56.1:1234/v1")
model_name = os.environ.get("LM_STUDIO_MODEL", "phi-4-reasoning-plus")

print(f"\nTesting model: {model_name}")
print(f"LM Studio URL: {base_url}")

client = OpenAI(base_url=base_url, api_key="test")

# Test different input sizes
test_sizes = [
    (500, "Small"),
    (2000, "Medium"),
    (5000, "Large"),
    (10000, "Very Large"),
    (20000, "Huge"),
]

print("\n" + "="*80)
print("Testing different input sizes...")
print("="*80)

max_working_size = 0

for char_count, label in test_sizes:
    print(f"\n📝 Test: {label} input ({char_count} characters, ~{char_count//4} tokens)")

    # Generate test text
    test_text = "Sample health report data. " * (char_count // 28)
    test_text = test_text[:char_count]  # Trim to exact size

    # Ask for a simple response
    prompt = f"""Here is a health report:

{test_text}

Please respond with this exact JSON and nothing else:
{{"status": "received", "size": {char_count}}}
"""

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.3,
            timeout=60.0
        )

        response_text = response.choices[0].message.content

        if response_text and len(response_text) > 0:
            print(f"   ✅ SUCCESS - Model handled {char_count} characters")
            print(f"   Response: {response_text[:100]}")
            max_working_size = char_count
        else:
            print(f"   ❌ FAILED - Empty response at {char_count} characters")
            print(f"   💡 Your model's limit is around {max_working_size} characters")
            break

    except Exception as e:
        print(f"   ❌ ERROR at {char_count} characters: {e}")
        print(f"   💡 Your model's limit is around {max_working_size} characters")
        break

print("\n" + "="*80)
print("RESULTS")
print("="*80)

if max_working_size >= 15000:
    print(f"\n✅ EXCELLENT: Your model can handle {max_working_size}+ characters")
    print("   This is enough for most government health reports!")
    print(f"   Your document (30,740 chars) should work with this model.")
elif max_working_size >= 5000:
    print(f"\n⚠️  LIMITED: Your model can handle up to ~{max_working_size} characters")
    print(f"   Your document (30,740 chars) is TOO LARGE for this model.")
    print("\n💡 Solutions:")
    print("   1. Use a model with larger context (Qwen 2.5, Llama 3.1)")
    print("   2. Split your document into smaller sections")
    print("   3. Use cloud API for large documents")
elif max_working_size > 0:
    print(f"\n❌ VERY LIMITED: Your model can only handle ~{max_working_size} characters")
    print(f"   Your document (30,740 chars) is WAY TOO LARGE.")
    print("\n💡 Solutions:")
    print("   1. Switch to Qwen 2.5 14B (32K+ context)")
    print("   2. Use cloud API instead")
else:
    print("\n❌ MODEL NOT WORKING: All tests failed")
    print("\n💡 Check:")
    print("   1. Is the model fully loaded in LM Studio?")
    print("   2. Is the model name correct?")
    print("   3. Is LM Studio server running?")

print("\n" + "="*80)
print("RECOMMENDATIONS")
print("="*80)

print("\nFor your government health analysis project:")
print("\n📊 Your typical document size: ~30,000 characters")
print(f"📊 Your current model capacity: ~{max_working_size} characters")

if max_working_size < 20000:
    print("\n🎯 RECOMMENDED MODELS for large documents:")
    print("   1. Qwen 2.5 14B Instruct (32K-128K context) ⭐ BEST CHOICE")
    print("   2. Llama 3.1 8B Instruct (128K context)")
    print("   3. Mistral Nemo 12B (128K context)")
    print("\n   All available in LM Studio!")
else:
    print("\n✅ Your current model should work fine!")
    print("   The empty response might be due to a different issue.")
    print("   Try running: python test_lm_studio_connection.py")

print("\n" + "="*80)
