# LM Studio Troubleshooting Guide

## Quick Fix Checklist

### Issue 1: "Invalid model identifier" Error

**Error Message:**
```
Error code: 400 - Invalid model identifier "local-model"
```

**Solution:**
1. Open LM Studio and check the loaded model name
2. Set the environment variable:
   ```bash
   set LM_STUDIO_MODEL=your-model-name-here
   ```
3. Common model names:
   - `phi-4-reasoning-plus`
   - `qwen2.5-14b-instruct`
   - `llama-3.1-8b-instruct`
   - `mistral-7b-instruct-v0.2`

**How to find your model name:**
- Look in LM Studio's UI at the top where it shows the loaded model
- Or check the error message - it often suggests valid names

---

### Issue 2: "Failed to parse AI response as JSON"

**Error Message:**
```
⚠️ WARNING: AI response wasn't valid JSON
```

**What's happening:**
The local AI model is returning text that isn't properly formatted as JSON.

**Solutions:**

#### Option 1: Try a different model
Some models are better at following JSON formatting instructions:
- ✅ **Best for JSON:** Qwen 2.5 (14B+), Mistral Instruct, Command-R
- ⚠️ **Sometimes works:** Llama 3.1, Phi-4
- ❌ **Avoid for JSON:** Base models, non-instruct models

#### Option 2: Adjust the prompt (for advanced users)
Edit the system prompt in the code to be more explicit:
```python
"You MUST respond with ONLY valid JSON. No explanations, no markdown, just pure JSON."
```

#### Option 3: Use the enhanced parser
Both scripts now have improved JSON parsing that tries multiple strategies:
1. Extract from ```json blocks
2. Extract from ``` blocks
3. Find JSON by pattern matching `{ ... }`
4. Auto-fix trailing commas

**The improved version will show diagnostics:**
```
📝 Raw AI response length: 1234 characters
⚠️ First parse attempt failed: ...
Response preview (first 500 chars): ...
✅ Successfully parsed after fixing trailing commas
```

#### Option 4: Increase temperature
If the model is being too creative, try lowering temperature:
```python
temperature=0.1  # More deterministic, better for JSON
```

---

### Issue 3: Model is too slow

**Solutions:**
1. **Use a smaller model:** Switch from 14B → 7B → 3B
2. **Use quantized models:** Look for models with `Q4_K_M` or `GGUF` (faster)
3. **Reduce max_tokens:** Change from 8000 to 4000 in the code
4. **Use GPU acceleration:** Make sure LM Studio is using your GPU

---

### Issue 4: Model output is poor quality

**Symptoms:**
- Missing data in the analysis
- Generic/vague recommendations
- Incorrect information extraction

**Solutions:**
1. **Use a larger model:** 14B+ models give better results than 7B
2. **Try Qwen 2.5:** Specifically good at structured data extraction
3. **Reduce complexity:** Simplify the JSON schema in the prompt
4. **Add examples:** Include a sample JSON response in the prompt

---

## Recommended Models for This Task

### Best Overall (Quality + Speed)
1. **Qwen 2.5 14B Instruct** - Excellent at JSON, fast, good analysis
2. **Qwen 2.5 32B Instruct** - Best quality (if you have 32GB+ RAM)

### Good Budget Options
3. **Mistral 7B Instruct v0.2** - Fast, decent JSON compliance
4. **Llama 3.1 8B Instruct** - Good all-rounder

### Avoid
- ❌ Base models (non-instruct)
- ❌ Models < 3B (too simple)
- ❌ Code-focused models (not trained for analysis)

---

## Debugging Commands

### Check if LM Studio is running
```bash
curl http://192.168.56.1:1234/v1/models
```

Should return a list of available models.

### Test the connection
```python
from openai import OpenAI
client = OpenAI(base_url="http://192.168.56.1:1234/v1", api_key="test")
response = client.chat.completions.create(
    model="phi-4-reasoning-plus",  # Your model name
    messages=[{"role": "user", "content": "Say 'Hello'"}],
    max_tokens=50
)
print(response.choices[0].message.content)
```

---

## Getting Help

If you're still stuck:
1. Check the raw AI response preview in the error message
2. Try running with a simpler document first
3. Verify your model is fully loaded in LM Studio (not just downloading)
4. Check LM Studio's console for error messages

---

## Environment Variables Reference

```bash
# Set model name (required if default doesn't work)
set LM_STUDIO_MODEL=phi-4-reasoning-plus

# Set custom LM Studio URL (if using different port/IP)
set LM_STUDIO_URL=http://localhost:1234/v1
```

---

## Common Model Names

Copy-paste these to try:

```bash
# Phi models
set LM_STUDIO_MODEL=phi-4-reasoning-plus
set LM_STUDIO_MODEL=phi-3-medium-instruct

# Qwen models
set LM_STUDIO_MODEL=qwen2.5-14b-instruct
set LM_STUDIO_MODEL=qwen2.5-7b-instruct
set LM_STUDIO_MODEL=qwen2.5

# Llama models
set LM_STUDIO_MODEL=llama-3.1-8b-instruct
set LM_STUDIO_MODEL=llama-3.1-70b-instruct

# Mistral models
set LM_STUDIO_MODEL=mistral-7b-instruct-v0.2
set LM_STUDIO_MODEL=mistral-nemo-instruct
```

---

**Last Updated:** 2026-01-07
