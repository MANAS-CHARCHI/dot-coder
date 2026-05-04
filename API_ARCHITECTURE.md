# API Architecture - Multi-Provider Support

Visual guide to how the .coder system supports multiple LLM providers.

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    .coder SYSTEM                        │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  LLM ABSTRACTION LAYER                  │
│                     (llm.py)                            │
│                                                         │
│  call_llm(system, history, agent, model)                │
│         │                                               │
│         ├─→ Route to provider based on model            │
│         │                                               │
│         ├─→ _call_nvidia()   (OpenAI SDK)               │
│         ├─→ _call_gemini()   (Google SDK)               │
│         └─→ _call_claude()   (Future)                   │
└─────────────────────────┬───────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   NVIDIA     │  │   GOOGLE     │  │   FUTURE     │
│     API      │  │   GEMINI     │  │  PROVIDERS   │
│              │  │     API      │  │              │
│ z-ai/glm4.7  │  │ Flash-Lite   │  │ Claude, GPT  │
└──────────────┘  └──────────────┘  └──────────────┘
```

---

## Provider Routing Flow

```
Agent calls: call_llm(system, history, agent, "z-ai/glm4.7")
                          │
                          ▼
              ┌───────────────────────┐
              │ Look up model in      │
              │ MODELS dictionary     │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ Get provider:         │
              │ "nvidia"              │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ Route to:             │
              │ _call_nvidia()        │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ Call NVIDIA API       │
              │ with OpenAI SDK       │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ Stream response       │
              │ + reasoning           │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ Return to agent       │
              └───────────────────────┘
```

---

## NVIDIA API Flow

```
┌─────────────────────────────────────────────────────────┐
│                  _call_nvidia()                         │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 1. Convert history format                               │
│    Gemini format → OpenAI format                        │
│                                                         │
│    {"role": "user", "parts": [{"text": "..."}]}         │
│    ↓                                                    │
│    {"role": "user", "content": "..."}                   │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Create OpenAI client                                 │
│                                                         │
│    client = OpenAI(                                     │
│        base_url="https://integrate.api.nvidia.com/v1",  │
│        api_key=NVIDIA_API_KEY                           │
│    )                                                    │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Call API with streaming                              │
│                                                         │
│    completion = client.chat.completions.create(         │
│        model="z-ai/glm4.7",                             │
│        messages=messages,                               │
│        stream=True,                                     │
│        extra_body={                                     │
│            "chat_template_kwargs": {                    │
│                "enable_thinking": True                  │
│            }                                            │
│        }                                                │
│    )                                                    │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 4. Process stream                                       │
│                                                         │
│    for chunk in completion:                             │
│        delta = chunk.choices[0].delta                   │
│                                                         │
│        if delta.reasoning_content:                      │
│            print(dim_color + reasoning)                 │
│                                                         │
│        if delta.content:                                │
│            print(content)                               │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 5. Log and return                                       │
│                                                         │
│    return {                                             │
│        "reply": full_response,                          │
│        "input_tokens": estimated,                       │
│        "output_tokens": estimated,                      │
│        "cost": 0.00,                                    │
│        "error": None                                    │
│    }                                                    │
└─────────────────────────────────────────────────────────┘
```

---

## Gemini API Flow

```
┌─────────────────────────────────────────────────────────┐
│                  _call_gemini()                         │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 1. Use history as-is                                    │
│    (Already in Gemini format)                           │
│                                                         │
│    {"role": "user", "parts": [{"text": "..."}]}         │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 2. Call Gemini API                                      │
│                                                         │
│    response = client.models.generate_content(           │
│        model=model,                                     │
│        contents=history,                                │
│        config=GenerateContentConfig(                    │
│            system_instruction=system                    │
│        )                                                │
│    )                                                    │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Extract response                                     │
│                                                         │
│    reply = response.text                                │
│    input_tokens = response.usage_metadata.prompt_...    │
│    output_tokens = response.usage_metadata.candidates...│
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ 4. Log and return                                       │
│                                                         │
│    return {                                             │
│        "reply": reply,                                  │
│        "input_tokens": input_tokens,                    │
│        "output_tokens": output_tokens,                  │
│        "cost": calculated,                              │
│        "error": None                                    │
│    }                                                    │
└─────────────────────────────────────────────────────────┘
```

---

## Model Selection Flow

```
Sales Agent runs
      │
      ▼
┌─────────────────────────────────────────┐
│ Show model selection table:             │
│                                         │
│ 1. NVIDIA z-ai/glm4.7 for all          │
│ 2. Gemini 2.5 Flash-Lite for all       │
│ 3. Mix: NVIDIA + Gemini                │
└─────────────────┬───────────────────────┘
                  │
                  ▼
            User chooses
                  │
      ┌───────────┼───────────┐
      │           │           │
      ▼           ▼           ▼
   Option 1    Option 2    Option 3
      │           │           │
      ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ All use  │ │ All use  │ │ Planning:│
│ NVIDIA   │ │ Gemini   │ │ NVIDIA   │
│          │ │          │ │          │
│          │ │          │ │ Coding:  │
│          │ │          │ │ Gemini   │
└────┬─────┘ └────┬─────┘ └────┬─────┘
     │            │            │
     └────────────┼────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ Write to memory.json:                   │
│                                         │
│ {                                       │
│   "model_selection": {                  │
│     "manager": "z-ai/glm4.7",           │
│     "architect": "z-ai/glm4.7",         │
│     "coder_db": "gemini-2.5-flash-lite",│
│     ...                                 │
│   }                                     │
│ }                                       │
└─────────────────┬───────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│ All agents read model from memory       │
│ and use it for their LLM calls          │
└─────────────────────────────────────────┘
```

---

## Environment Configuration

```
.env file
    │
    ├─→ NVIDIA_API_KEY=nvapi-xxx...
    │   │
    │   └─→ Used by: nvidia_client = OpenAI(...)
    │
    └─→ GEMINI_API_KEY=AIza...
        │
        └─→ Used by: gemini_client = genai.Client(...)


At startup:
    │
    ├─→ setup_nvidia()
    │   │
    │   ├─→ Check NVIDIA_API_KEY
    │   ├─→ If exists: create OpenAI client
    │   └─→ If missing: return None
    │
    └─→ setup_gemini()
        │
        ├─→ Check GEMINI_API_KEY
        ├─→ If exists: create Gemini client
        └─→ If missing: return None


At runtime:
    │
    ├─→ If model provider is "nvidia":
    │   │
    │   ├─→ Check if nvidia_client exists
    │   ├─→ If yes: use it
    │   └─→ If no: return error
    │
    └─→ If model provider is "google":
        │
        ├─→ Check if gemini_client exists
        ├─→ If yes: use it
        └─→ If no: return error
```

---

## Error Handling

```
call_llm() called
      │
      ▼
┌─────────────────────┐
│ Model in MODELS?    │
└──────┬──────────────┘
       │
   ┌───┴───┐
   │       │
  Yes     No
   │       │
   │       └─→ Return {"error": "Unknown model"}
   │
   ▼
┌─────────────────────┐
│ Get provider        │
└──────┬──────────────┘
       │
   ┌───┴───┐
   │       │
nvidia  google
   │       │
   ▼       ▼
┌──────┐ ┌──────┐
│Client│ │Client│
│exists│ │exists│
└──┬───┘ └──┬───┘
   │        │
┌──┴──┐  ┌─┴───┐
│     │  │     │
Yes  No  Yes  No
│     │  │     │
│     └──┴─────└─→ Return {"error": "API key not set"}
│
▼
┌─────────────────────┐
│ Call API            │
└──────┬──────────────┘
       │
   ┌───┴───┐
   │       │
Success  Error
   │       │
   │       └─→ Catch exception
   │           Return {"error": str(e)}
   │
   ▼
Return success response
```

---

## Adding New Providers

### Step 1: Add Model Definition

```python
# llm_call.py

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

### Step 2: Add Client Setup

```python
# llm.py

def setup_openai():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

openai_client = setup_openai()
```

### Step 3: Add Provider Function

```python
# llm.py

def _call_openai(system, history, agent, model, model_info):
    if not openai_client:
        return {"error": "OPENAI_API_KEY not set"}
    
    # Convert history format
    messages = [{"role": "system", "content": system}]
    for msg in history:
        # ... conversion logic
    
    # Call API
    response = openai_client.chat.completions.create(
        model=model,
        messages=messages
    )
    
    # Return formatted response
    return {
        "reply": response.choices[0].message.content,
        "input_tokens": response.usage.prompt_tokens,
        "output_tokens": response.usage.completion_tokens,
        "cost": calculated_cost,
        "error": None
    }
```

### Step 4: Add to Router

```python
# llm.py

def call_llm(system, history, agent, model=DEFAULT_MODEL):
    model_info = MODELS[model]
    provider = model_info["provider"]
    
    if provider == "nvidia":
        return _call_nvidia(...)
    elif provider == "google":
        return _call_gemini(...)
    elif provider == "openai":
        return _call_openai(...)  # NEW
    else:
        return {"error": f"Unknown provider: {provider}"}
```

### Step 5: Update Environment

```bash
# .env.example

OPENAI_API_KEY=sk-...
```

### Step 6: Update Model Selection

```python
# agents/sales.py

model_table.add_row("Manager", "GPT-4", "z-ai/glm4.7")
# ... etc
```

---

## Provider Comparison

| Feature | NVIDIA | Gemini | Future (OpenAI) |
|---------|--------|--------|-----------------|
| **SDK** | OpenAI | Google | OpenAI |
| **Streaming** | ✅ Yes | ❌ No | ✅ Yes |
| **Reasoning** | ✅ Yes | ❌ No | ❌ No |
| **Free Tier** | ✅ Yes | ✅ Yes | ❌ No |
| **Context** | 16K | 1M | 8K-128K |
| **Cost** | $0 | $0-$5/1M | $3-$60/1M |
| **Setup** | Easy | Easy | Easy |

---

## Best Practices

### 1. Always Check Client Exists

```python
if not nvidia_client:
    return {"error": "NVIDIA_API_KEY not set"}
```

### 2. Handle API Errors Gracefully

```python
try:
    response = client.chat.completions.create(...)
except Exception as e:
    return {"error": str(e)}
```

### 3. Log All Calls

```python
entry = {
    "timestamp": datetime.now().isoformat(),
    "agent": agent,
    "model": model,
    "input_tokens": input_tokens,
    "output_tokens": output_tokens,
    "cost_usd": cost,
    "duration_ms": duration
}
log_call(entry)
```

### 4. Estimate Tokens When Unavailable

```python
# NVIDIA doesn't provide usage in streaming
input_tokens = len(system.split()) + sum(len(str(m).split()) for m in history)
output_tokens = len(reply.split())
```

### 5. Maintain Consistent Interface

All provider functions return the same format:

```python
{
    "reply": str,
    "input_tokens": int,
    "output_tokens": int,
    "cost": float,
    "duration_ms": int,
    "error": str | None
}
```

---

This architecture makes it easy to add new providers while maintaining a clean, consistent interface for all agents!
