# Setup Guide - NVIDIA API Integration

The .coder system now supports **NVIDIA z-ai/glm4.7** as the default model, with Gemini as a fallback option.

---

## Why NVIDIA z-ai/glm4.7?

- **Free to use** (like Gemini)
- **Reasoning capabilities** - Shows its thinking process
- **16K context window** - Good for complex tasks
- **OpenAI-compatible API** - Easy to integrate

---

## Quick Setup

### 1. Install Dependencies

```bash
uv sync
```

This will install:
- `openai` - For NVIDIA API
- `google-genai` - For Gemini API (optional)
- `python-dotenv` - Environment variables
- `rich` - Terminal UI

### 2. Get NVIDIA API Key

1. Go to https://build.nvidia.com/
2. Sign in with your NVIDIA account (or create one)
3. Navigate to the z-ai/glm4.7 model page
4. Click "Get API Key"
5. Copy your API key

### 3. Configure Environment

```bash
# Copy example file
cp .env.example .env

# Edit .env and add your NVIDIA API key
nano .env  # or use any text editor
```

Your `.env` should look like:

```bash
# NVIDIA API Key (Default - z-ai/glm4.7 model)
NVIDIA_API_KEY=nvapi-your_actual_key_here

# Google Gemini API Key (Optional)
GEMINI_API_KEY=your_gemini_api_key_here
```

**Note:** You only need ONE API key to run the system. NVIDIA is recommended as default.

### 4. Test Setup

```bash
python test_setup.py
```

This will verify:
- ✅ All dependencies installed
- ✅ API key configured
- ✅ LLM connection works

### 5. Run the Pipeline

```bash
python main.py
```

---

## Model Selection

When you run the pipeline, the Sales Agent will ask you to choose models:

```
Choose:
1. Use NVIDIA z-ai/glm4.7 for all (recommended, free)
2. Use Gemini 2.5 Flash-Lite for all (free)
3. Mix: NVIDIA for planning, Gemini for coding
```

**Recommended:** Option 1 (NVIDIA for all agents)

---

## What Changed?

### New Files Modified

1. **llm_call.py**
   - Added `z-ai/glm4.7` model definition
   - Set as default model

2. **llm.py**
   - Added NVIDIA API client setup
   - Added `_call_nvidia()` function with streaming support
   - Shows reasoning in dim color during generation
   - Kept `_call_gemini()` for backward compatibility

3. **agents/sales.py**
   - Updated model selection table
   - Added 3 options: NVIDIA only, Gemini only, or Mix

4. **.env.example**
   - Added NVIDIA_API_KEY
   - Made GEMINI_API_KEY optional

5. **pyproject.toml**
   - Added `openai>=1.0.0` dependency

6. **test_setup.py**
   - Tests both API keys
   - Passes if at least one is configured

---

## Features of NVIDIA Integration

### Reasoning Display

The NVIDIA model shows its thinking process in real-time:

```
[dim gray text] - Model's internal reasoning
[normal text] - Actual response
```

This helps you understand how the model is approaching the task.

### Streaming Output

Responses stream in real-time, so you see progress as the model generates.

### OpenAI-Compatible

Uses the standard OpenAI client, making it easy to swap models or add other providers.

---

## Fallback to Gemini

If you prefer Gemini or want to use both:

1. Add both API keys to `.env`
2. Choose option 3 during model selection
3. NVIDIA handles planning (Manager, Architect, Engineers)
4. Gemini handles coding (Coder agents)

This gives you the best of both worlds:
- NVIDIA's reasoning for complex planning
- Gemini's speed for code generation

---

## Troubleshooting

### "NVIDIA_API_KEY not set"

Make sure:
1. You created `.env` file (not `.env.example`)
2. You added your actual API key
3. No spaces around the `=` sign
4. Key starts with `nvapi-`

### "Module 'openai' not found"

Run:
```bash
uv sync
```

### Want to use only Gemini?

1. Remove or comment out `NVIDIA_API_KEY` in `.env`
2. Add your `GEMINI_API_KEY`
3. Choose option 2 during model selection

### API Rate Limits

Both NVIDIA and Gemini have free tier rate limits:
- NVIDIA: Check https://build.nvidia.com/ for current limits
- Gemini: 15 requests/minute on free tier

If you hit limits, the system will show an error. Wait a minute and resume with `python main.py`.

---

## Cost Comparison

| Model | Provider | Cost | Context | Notes |
|-------|----------|------|---------|-------|
| z-ai/glm4.7 | NVIDIA | Free | 16K | Reasoning enabled |
| gemini-2.5-flash-lite | Google | Free | 1M | Fast, large context |
| gemini-1.5-flash | Google | $0.075/1M | 1M | Paid tier |
| gemini-1.5-pro | Google | $1.25/1M | 2M | Highest quality |

**Recommendation:** Use free models (NVIDIA or Gemini Flash-Lite) for development and testing.

---

## Advanced: Adding More Models

Want to add Claude, GPT-4, or other models?

1. Add model definition to `llm_call.py`:

```python
MODELS = {
    "gpt-4": {
        "provider": "openai",
        "input_cost": 0.00003,
        "output_cost": 0.00006,
        "context": 8192
    },
    # ... existing models
}
```

2. Add provider handler in `llm.py`:

```python
def _call_openai(system, history, agent, model, model_info):
    # Implementation here
    pass
```

3. Update model selection in `agents/sales.py`

---

## Next Steps

1. ✅ Setup complete? Run `python main.py`
2. 📖 Read QUICKSTART.md for usage guide
3. 🏗️ Read ARCHITECTURE.md for system details
4. 🤝 Read CONTRIBUTING.md to add features

---

**Questions?** Open an issue on GitHub.

**Happy building!** 🚀
