# Model Selection Guide

## The Problem You Had

Your `phi-4-reasoning-plus` model was:
- ✅ Connecting to LM Studio successfully
- ✅ Starting to generate output (`{`)
- ❌ But taking 10+ minutes (reasoning models "think" step-by-step)
- ❌ Python client timing out and disconnecting
- ❌ Returning empty response

**Reasoning models are NOT suitable for data extraction tasks!**

---

## Quick Solutions (Choose One)

### Option 1: Interactive Model Selector ⭐ EASIEST

```bash
python select_model.py
```

This will:
1. Show all your available models in LM Studio
2. Recommend which ones are best for data extraction
3. Warn you about reasoning models
4. Let you test the model
5. Auto-configure your environment

**Just run it and follow the prompts!**

---

### Option 2: Smart Analyzer (Auto-Detects Best Model)

```bash
python poc_analyzer_smart.py "C:\Users\admin\Desktop\DOC-20251204-WA0056.docx"
```

This version:
- Automatically selects the best available model
- Warns if you're using a reasoning model
- Handles timeouts gracefully
- Simplifies the analysis for faster results

---

### Option 3: Manual Model Selection

```bash
# First, check what models you have
python select_model.py

# Then set the model
set LM_STUDIO_MODEL=qwen2.5-14b-instruct

# Run analyzer
python poc_analyzer_local_enhanced.py "C:\Users\admin\Desktop\DOC-20251204-WA0056.docx"
```

---

## Understanding Your Models

### Good Models for Data Extraction ✅

| Model | Speed | Quality | Context | Best For |
|-------|-------|---------|---------|----------|
| **Qwen 2.5 14B** | Fast (1-3 min) | Excellent | 32K+ tokens | ⭐ Best choice |
| **Qwen 2.5 7B** | Very Fast (30-90 sec) | Good | 32K+ tokens | Quick analysis |
| **Llama 3.1 8B** | Fast (1-2 min) | Good | 128K tokens | Large docs |
| **Mistral 7B Instruct** | Very Fast (30-60 sec) | Good | 32K tokens | Speed priority |

### Bad Models for This Task ❌

| Model | Problem |
|-------|---------|
| **phi-4-reasoning-plus** | Takes 10-30 minutes, often times out |
| **Any model with "reasoning"** | Too slow for data extraction |
| **Base models (no "instruct")** | Don't follow instructions well |
| **Models < 3B** | Too simple for complex analysis |

---

## Tools I Created For You

### 1. `select_model.py` - Interactive Model Chooser
```bash
python select_model.py
```

**Features:**
- Lists all LM Studio models via `/v1/models` API
- Shows recommendations for each
- Tests selected model
- Auto-configures environment

**When to use:** When you want to see all options and choose manually

---

### 2. `poc_analyzer_smart.py` - Auto-Selecting Analyzer
```bash
python poc_analyzer_smart.py report.docx
```

**Features:**
- Automatically picks best model
- Warns about reasoning models
- Simplified prompt for faster results
- Better timeout handling

**When to use:** Quick analysis without worrying about model selection

---

### 3. `test_lm_studio_connection.py` - Diagnostic Tool
```bash
python test_lm_studio_connection.py
```

**Features:**
- Tests if LM Studio is working
- Tests different input sizes
- Tests JSON generation
- Shows what your model can handle

**When to use:** When something isn't working

---

### 4. `check_model_context.py` - Context Window Tester
```bash
python check_model_context.py
```

**Features:**
- Tests different document sizes
- Finds your model's limit
- Recommends better models if needed

**When to use:** To see if your model can handle large documents

---

## Recommended Workflow

### First Time Setup

1. **Check what models you have:**
   ```bash
   python select_model.py
   ```

2. **If you don't have Qwen 2.5:**
   - Open LM Studio
   - Search: "qwen2.5-14b-instruct"
   - Download Q4_K_M version (~8GB)

3. **Select and test model:**
   ```bash
   python select_model.py
   # Choose the recommended model
   ```

4. **Run analysis:**
   ```bash
   python poc_analyzer_local_enhanced.py "your_report.docx"
   ```

---

### Daily Usage

**Option A - Let it auto-select:**
```bash
python poc_analyzer_smart.py report.docx
```

**Option B - Use your preferred model:**
```bash
set LM_STUDIO_MODEL=qwen2.5-14b-instruct
python poc_analyzer_local_enhanced.py report.docx
```

---

## Why Qwen 2.5 is Recommended

1. **Excellent JSON compliance** - Trained specifically for structured output
2. **Large context window** - 32K-128K tokens (vs Phi-4's 4K-8K)
3. **Fast** - 1-3 minutes for your 30K character documents
4. **Good analysis** - Better than Phi at understanding complex reports
5. **Reliable** - Doesn't timeout or crash
6. **Open source** - Free to use

**Your document**: ~30,740 characters = ~7,500 tokens

- ❌ Phi-4 context: 4K-8K tokens (doesn't fit with system prompt + output)
- ✅ Qwen 2.5 context: 32K tokens (fits easily with room to spare)

---

## Quick Reference Commands

```bash
# See all models and choose
python select_model.py

# Auto-select and analyze
python poc_analyzer_smart.py report.docx

# Use specific model
set LM_STUDIO_MODEL=qwen2.5-14b-instruct
python poc_analyzer_local_enhanced.py report.docx

# Test connection
python test_lm_studio_connection.py

# Check model limits
python check_model_context.py
```

---

## Troubleshooting

### Model takes forever / times out
→ You're using a reasoning model. Switch to Qwen/Llama/Mistral

### Empty response
→ Document too large for model's context. Use Qwen 2.5 or Llama 3.1

### Bad JSON / Parse errors
→ Model not good at structured output. Use Qwen 2.5

### Connection errors
→ Run `test_lm_studio_connection.py` to diagnose

---

## Next Steps

1. **Right now:** Run `python select_model.py`
2. **Choose:** A non-reasoning model (Qwen recommended)
3. **Analyze:** Your document should work in 1-3 minutes!

If you don't have Qwen 2.5, download it in LM Studio - it's specifically designed for tasks like yours!
