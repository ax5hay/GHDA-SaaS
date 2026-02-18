# 🚀 QUICK REFERENCE CARD

## Run Analysis (Choose One)

### Option 1: Cloud (Anthropic Claude)
```bash
# Setup (one time)
pip install anthropic python-docx PyPDF2
export ANTHROPIC_API_KEY='sk-ant-...'  # Get from console.anthropic.com

# Run
python poc_analyzer.py your_report.docx
```

### Option 2: Local (LM Studio)
```bash
# Setup (one time)
# 1. Install LM Studio from https://lmstudio.ai
# 2. Load model (Qwen 2.5 14B recommended)
# 3. Click "Start Server"

pip install openai python-docx PyPDF2

# Run
python poc_analyzer_local.py your_report.docx
```

### Option 3: Enhanced Local (Beautiful PDFs) ⭐⭐ RECOMMENDED
```bash
# Setup (one time)
# 1-3. Same as Option 2
pip install openai python-docx PyPDF2 reportlab pillow

# Run
python poc_analyzer_local_enhanced.py your_report.docx

# Output: Organized folder with 4 files including beautiful PDF!
```

---

## What You Get

- `filename_ANALYSIS_REPORT.md` - 20-50 page comprehensive report
- `filename_ANALYSIS_REPORT.json` - Structured data

---

## Test with Sample

```bash
# Try the included Hinglish sample
python poc_analyzer_local.py SAMPLE_REPORT.txt

# View results
open SAMPLE_REPORT_ANALYSIS_REPORT.md
```

---

## Quick Comparison

| Feature | Cloud | Local |
|---------|-------|-------|
| **Cost** | ~$0.20/report | $0 |
| **Speed** | 15-30 sec | 30-90 sec |
| **Quality** | Best | Very Good |
| **Privacy** | ❌ Data sent to API | ✅ 100% offline |
| **Internet** | Required | Not needed |
| **Setup** | 2 minutes | 15 minutes |
| **Production** | ❌ API costs scale | ✅ Zero ongoing cost |

---

## LM Studio Models (for Local)

**Recommended** (best balance of speed/quality):
- **Qwen 2.5 14B** - Best for analysis
- **Llama 3.1 8B** - Fastest

**Advanced** (if you have powerful GPU):
- **Qwen 2.5 32B** - Best quality
- **Llama 3.1 70B** - Slowest but excellent

**Download in LM Studio**: Search model name → Click download

---

## Troubleshooting

### Cloud Version

**Error: ANTHROPIC_API_KEY not set**
```bash
# Set API key
export ANTHROPIC_API_KEY='your-key-here'

# Or Windows:
set ANTHROPIC_API_KEY=your-key-here
```

**Error: API key invalid**
- Get new key from https://console.anthropic.com/

### Local Version

**Error: Connection refused**
- Is LM Studio running?
- Is server started? (Click "Start Server" in LM Studio)
- Check URL matches (default: http://192.168.56.1:1234)

**Slow processing (>2 minutes)**
- Normal for larger models on CPU
- Consider smaller model (Llama 8B instead of 70B)
- Or use GPU

**Out of memory**
- Model too large for your RAM
- Use smaller model (8B instead of 14B)
- Or close other programs

---

## File Structure

```
GHDA-SaaS/
├── poc_analyzer.py          ← Cloud version
├── poc_analyzer_local.py    ← Local version ⭐
├── SAMPLE_REPORT.txt        ← Try this first
│
├── README_POST_POC.md       ← Start here
├── POC_QUICKSTART.md        ← Detailed setup
├── QUICK_REFERENCE.md       ← This file
│
└── ARCHITECTURE_V2_AI_POWERED.md  ← How it works
```

---

## Cost Calculator

### Cloud (Claude API)
- Small report (~2 pages): $0.10
- Medium report (~5 pages): $0.20
- Large report (~10 pages): $0.30

**1000 reports**: ~$100-300

### Local (LM Studio)
- Setup: $5,000 (GPU server) or $0.50/hour (rent GPU)
- Per report: **$0**

**1000 reports**: **$0**

**Breakeven**: ~25-50 reports (if buying GPU)

---

## Next Steps

### Just Testing?
```bash
python poc_analyzer_local.py SAMPLE_REPORT.txt
```

### Real Deployment?
1. Read [ARCHITECTURE_V2_AI_POWERED.md](ARCHITECTURE_V2_AI_POWERED.md)
2. Set up local LM Studio
3. Test with 10-20 real reports
4. Build web API (see [MVP_ROADMAP.md](MVP_ROADMAP.md))

---

## Support

- **Setup issues**: [POC_QUICKSTART.md](POC_QUICKSTART.md)
- **How it works**: [ARCHITECTURE_V2_AI_POWERED.md](ARCHITECTURE_V2_AI_POWERED.md)
- **Full platform**: [MVP_ROADMAP.md](MVP_ROADMAP.md)

---

## Key Insight

**This POC proves**: AI can handle **any** input, no matter how messy.

**No pattern matching needed.** 🎉

---

**Questions?** Run the sample report first, then read the docs above.
