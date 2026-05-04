# NVIDIA API Fix - Model Update

## Problem

The original integration used `z-ai/glm4.7` model which:
- Was hanging/timing out on API calls
- Had special reasoning parameters that may not be widely supported
- May not be available on all NVIDIA API accounts

## Solution

Switched to **Meta Llama 3.1 8B Instruct** (`meta/llama-3.1-8b-instruct`) which is:
- ✅ Widely available on NVIDIA API
- ✅ Well-tested and stable
- ✅ Free to use
- ✅ 128K context window (much larger than the original 16K)
- ✅ Standard OpenAI-compatible API (no special parameters needed)

## Changes Made

### 1. Model Definition (llm_call.py)

**Changed from:**
```python
"z-ai/glm4.7": {
    "provider": "nvidia",
    "context": 16384
}
DEFAULT_MODEL = "z-ai/glm4.7"
```

**To:**
```python
"meta/llama-3.1-8b-instruct": {
    "provider": "nvidia",
    "context": 128000
}
DEFAULT_MODEL = "meta/llama-3.1-8b-instruct"
```

### 2. API Call Simplification (llm.py)

**Removed:**
- `extra_body` with reasoning parameters
- Reasoning content collection
- Complex streaming logic

**Added:**
- 60-second timeout for reliability
- Simplified streaming (content only)
- Standard OpenAI parameters

### 3. Model Selection (agents/sales.py)

**Updated display:**
- "NVIDIA Llama 3.1 8B" instead of "z-ai/glm4.7"
- All references updated to use `meta/llama-3.1-8b-instruct`

### 4. Test Script (test_nvidia.py)

**Added:**
- 30-second timeout
- Better error messages
- Uses `meta/llama-3.1-8b-instruct` for testing

## How to Test

```bash
# Test NVIDIA API connection
python test_nvidia.py

# Should see:
# ✅ NVIDIA_API_KEY found
# ✅ openai package installed
# ✅ Client created successfully
# ✅ Response: NVIDIA API works!
```

## How to Use

```bash
# Run the pipeline
python main.py

# When prompted, choose:
# 1. Use NVIDIA Llama 3.1 8B for all (recommended, free)
```

## Alternative Models Available

If you want to try other NVIDIA models, you can add them to `llm_call.py`:

```python
# High-quality model (70B parameters)
"nvidia/llama-3.1-nemotron-70b-instruct": {
    "provider": "nvidia",
    "input_cost": 0.000,
    "output_cost": 0.000,
    "context": 32768
}

# Other popular models on NVIDIA
"mistralai/mixtral-8x7b-instruct-v0.1": {
    "provider": "nvidia",
    "input_cost": 0.000,
    "output_cost": 0.000,
    "context": 32768
}
```

Check https://build.nvidia.com/ for the full list of available models.

## Benefits of Llama 3.1 8B

1. **Larger Context**: 128K tokens vs 16K
2. **More Stable**: Widely used and tested
3. **Better Compatibility**: Standard OpenAI API
4. **Good Performance**: 8B parameters is a sweet spot
5. **Free**: No cost on NVIDIA API

## Troubleshooting

### Still hanging?

1. **Check your API key**: Make sure it's valid
   ```bash
   cat .env | grep NVIDIA_API_KEY
   ```

2. **Test with curl**:
   ```bash
   curl -X POST "https://integrate.api.nvidia.com/v1/chat/completions" \
     -H "Authorization: Bearer $NVIDIA_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{
       "model": "meta/llama-3.1-8b-instruct",
       "messages": [{"role":"user","content":"Hello"}],
       "max_tokens": 50
     }'
   ```

3. **Check network**: Make sure you can reach NVIDIA API
   ```bash
   ping integrate.api.nvidia.com
   ```

4. **Try different model**: Edit `llm_call.py` and change DEFAULT_MODEL

### Want to go back to Gemini?

Just choose option 2 during model selection, or edit `.env` to remove `NVIDIA_API_KEY`.

---

**Status**: ✅ Fixed and tested  
**Date**: May 4, 2026  
**Version**: 2.1.1
