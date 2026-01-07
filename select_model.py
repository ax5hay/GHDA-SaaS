#!/usr/bin/env python3
"""
Interactive model selector for LM Studio
Queries /v1/models endpoint to show available models and their capabilities
"""

import os
import sys
from openai import OpenAI

def format_bytes(bytes_size):
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"

def get_model_recommendation(model_id: str) -> str:
    """Get recommendation based on model name."""
    model_lower = model_id.lower()

    # Check for reasoning models
    if 'reasoning' in model_lower or 'o1' in model_lower or 'think' in model_lower:
        return "⚠️  SLOW - Reasoning model (avoid for data extraction)"

    # Check for recommended models
    if 'qwen' in model_lower and ('14b' in model_lower or '32b' in model_lower):
        return "⭐ EXCELLENT - Best for structured data extraction"
    if 'qwen' in model_lower:
        return "✅ GOOD - Good for JSON and analysis"
    if 'llama' in model_lower and ('8b' in model_lower or '70b' in model_lower):
        return "✅ GOOD - Solid all-rounder"
    if 'mistral' in model_lower and 'instruct' in model_lower:
        return "✅ GOOD - Fast and reliable"
    if 'phi' in model_lower and 'reasoning' not in model_lower:
        return "✅ OK - Small and fast"

    # Check for base models (not instruct)
    if 'instruct' not in model_lower and 'chat' not in model_lower:
        return "⚠️  NOT RECOMMENDED - Base model (not fine-tuned for instructions)"

    return "ℹ️  Unknown - Test before using"

def main():
    """Main interactive model selector."""

    print("="*80)
    print("LM STUDIO MODEL SELECTOR")
    print("="*80)

    base_url = os.environ.get("LM_STUDIO_URL", "http://192.168.56.1:1234/v1")

    print(f"\n🔌 Connecting to LM Studio: {base_url}")

    try:
        client = OpenAI(base_url=base_url, api_key="test")

        # Query available models
        print("📡 Querying /v1/models endpoint...")
        models_response = client.models.list()

        if not models_response.data:
            print("\n❌ No models found!")
            print("💡 Make sure:")
            print("   1. LM Studio is running")
            print("   2. At least one model is downloaded")
            print("   3. The local server is started")
            sys.exit(1)

        print(f"\n✅ Found {len(models_response.data)} available model(s)\n")
        print("="*80)
        print("AVAILABLE MODELS")
        print("="*80)

        # Display models with recommendations
        models_list = []
        for idx, model in enumerate(models_response.data, 1):
            model_id = model.id
            models_list.append(model_id)

            recommendation = get_model_recommendation(model_id)

            print(f"\n[{idx}] {model_id}")
            print(f"    {recommendation}")

            # Show additional info if available
            if hasattr(model, 'owned_by') and model.owned_by:
                print(f"    Owner: {model.owned_by}")
            if hasattr(model, 'created'):
                from datetime import datetime
                created_date = datetime.fromtimestamp(model.created).strftime('%Y-%m-%d')
                print(f"    Created: {created_date}")

        print("\n" + "="*80)
        print("RECOMMENDATIONS FOR YOUR TASK")
        print("="*80)

        # Find and highlight best models
        qwen_models = [m for m in models_list if 'qwen' in m.lower()]
        llama_models = [m for m in models_list if 'llama' in m.lower() and 'reasoning' not in m.lower()]
        reasoning_models = [m for m in models_list if 'reasoning' in m.lower() or 'o1' in m.lower()]

        print("\n🎯 For Government Health Data Analysis:")

        if qwen_models:
            print(f"\n   ⭐ BEST CHOICE: {qwen_models[0]}")
            print("      → Excellent JSON compliance, large context, fast")
        elif llama_models:
            print(f"\n   ✅ RECOMMENDED: {llama_models[0]}")
            print("      → Good all-rounder, reliable")

        if reasoning_models:
            print(f"\n   ⚠️  AVOID: {', '.join(reasoning_models)}")
            print("      → Too slow for data extraction (5-30 min per document)")

        # Interactive selection
        print("\n" + "="*80)
        print("SELECT MODEL")
        print("="*80)

        while True:
            try:
                choice = input(f"\nEnter model number (1-{len(models_list)}) or 'q' to quit: ").strip()

                if choice.lower() == 'q':
                    print("Exiting...")
                    sys.exit(0)

                idx = int(choice) - 1
                if 0 <= idx < len(models_list):
                    selected_model = models_list[idx]
                    break
                else:
                    print(f"❌ Invalid choice. Please enter 1-{len(models_list)}")
            except ValueError:
                print("❌ Invalid input. Please enter a number.")

        print("\n" + "="*80)
        print(f"✅ SELECTED: {selected_model}")
        print("="*80)

        # Test the model
        print("\n🧪 Testing model with simple query...")

        try:
            response = client.chat.completions.create(
                model=selected_model,
                messages=[
                    {"role": "user", "content": "Say 'Model is working!' and nothing else."}
                ],
                max_tokens=50,
                temperature=0.7,
                timeout=30.0
            )

            test_response = response.choices[0].message.content

            if test_response and len(test_response) > 0:
                print(f"✅ Model test successful!")
                print(f"   Response: {test_response}")
            else:
                print("⚠️  Model returned empty response - might have issues")

        except Exception as e:
            print(f"⚠️  Model test failed: {e}")
            print("   Model might still work for your task, but be cautious")

        # Show commands to use this model
        print("\n" + "="*80)
        print("HOW TO USE THIS MODEL")
        print("="*80)

        print(f"\n💡 Set as environment variable (Windows):")
        print(f"   set LM_STUDIO_MODEL={selected_model}")

        print(f"\n💡 Or on Linux/Mac:")
        print(f"   export LM_STUDIO_MODEL={selected_model}")

        print(f"\n💡 Then run your analyzer:")
        print(f"   python poc_analyzer_local.py SAMPLE_REPORT.txt")
        print(f"   python poc_analyzer_local_enhanced.py \"C:\\Users\\admin\\Desktop\\DOC-20251204-WA0056.docx\"")

        # Auto-set for this session if on Windows
        try:
            if sys.platform == 'win32':
                print(f"\n🔧 Auto-setting for current session...")
                os.environ['LM_STUDIO_MODEL'] = selected_model
                print(f"✅ LM_STUDIO_MODEL set to: {selected_model}")
                print("   This will work for the rest of this terminal session")
            else:
                print(f"\n💡 Run this command to set for current session:")
                print(f"   export LM_STUDIO_MODEL={selected_model}")
        except:
            pass

        print("\n" + "="*80)
        print("READY TO ANALYZE!")
        print("="*80)

        print(f"\n🎯 Your selected model: {selected_model}")
        print(f"📊 Document to analyze: ~30,000 characters")

        if 'reasoning' in selected_model.lower():
            print("\n⚠️  WARNING: This is a reasoning model - it will be VERY SLOW")
            print("   Expected time: 5-30 minutes per document")
            print("   Consider selecting a different model")
        else:
            print("\n✅ Good choice! This should work well.")
            print("   Expected time: 1-3 minutes per document")

        print("\n")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Is LM Studio running?")
        print("   2. Is the local server started in LM Studio?")
        print(f"   3. Can you access: {base_url}")
        print("   4. Try opening in browser: " + base_url.replace('/v1', ''))

        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
