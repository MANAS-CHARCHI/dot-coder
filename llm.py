import os
import json
import time
import sys
from datetime import datetime
from pathlib import Path

from google import genai
from openai import OpenAI
from rich import print as rprint
from dotenv import load_dotenv
load_dotenv()

from llm_call import MODELS, DEFAULT_MODEL

# Color codes for reasoning output
_USE_COLOR = sys.stdout.isatty() and os.getenv("NO_COLOR") is None
_REASONING_COLOR = "\033[90m" if _USE_COLOR else ""
_RESET_COLOR = "\033[0m" if _USE_COLOR else ""

def setup_gemini():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

def setup_nvidia():
    api_key = os.environ.get("NVIDIA_API_KEY")
    if not api_key:
        return None
    return OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=api_key,
        timeout=60.0  # 60 second timeout
    )

# Initialize clients
gemini_client = setup_gemini()
nvidia_client = setup_nvidia()

def log_call(entry: dict):
    log_dir = Path(".coder/logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "calls.json"

    existing = []
    if log_file.exists():
        try:
            existing = json.loads(log_file.read_text())
        except:
            existing = []

    existing.append(entry)
    log_file.write_text(json.dumps(existing, indent=2))

def call_llm(system: str, history: list, agent: str, model: str = DEFAULT_MODEL) -> dict:

    if model not in MODELS:
        return {"error": f"Unknown model: {model}"}

    model_info = MODELS[model]
    provider = model_info["provider"]
    
    if provider == "nvidia":
        return _call_nvidia(system, history, agent, model, model_info)
    elif provider == "google":
        return _call_gemini(system, history, agent, model, model_info)
    else:
        return {"error": f"Unknown provider: {provider}"}


def _call_nvidia(system: str, history: list, agent: str, model: str, model_info: dict) -> dict:
    """Call NVIDIA API (OpenAI-compatible)"""
    
    if not nvidia_client:
        return {"error": "NVIDIA_API_KEY not set. Add it to .env file"}
    
    start = time.time()
    
    try:
        # Convert history format to OpenAI format
        messages = [{"role": "system", "content": system}]
        
        for msg in history:
            role = msg.get("role")
            if role == "user":
                content = msg.get("parts", [{}])[0].get("text", "")
                messages.append({"role": "user", "content": content})
            elif role == "model":
                content = msg.get("parts", [{}])[0].get("text", "")
                messages.append({"role": "assistant", "content": content})
        
        # Call NVIDIA API with streaming
        completion = nvidia_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.5,
            top_p=1,
            max_tokens=4096,
            stream=True
        )
        
        # Collect response
        reply_parts = []
        
        for chunk in completion:
            if not getattr(chunk, "choices", None):
                continue
            if len(chunk.choices) == 0 or getattr(chunk.choices[0], "delta", None) is None:
                continue
            
            delta = chunk.choices[0].delta
            
            # Collect actual content
            if getattr(delta, "content", None) is not None:
                reply_parts.append(delta.content)
                print(delta.content, end="", flush=True)
        
        print()  # New line after streaming
        
        reply = "".join(reply_parts)
        
        duration_ms = int((time.time() - start) * 1000)
        
        # Estimate tokens (NVIDIA doesn't provide usage in streaming)
        input_tokens = len(system.split()) + sum(len(str(m).split()) for m in history)
        output_tokens = len(reply.split())
        
        input_cost = input_tokens * model_info["input_cost"]
        output_cost = output_tokens * model_info["output_cost"]
        total_cost = input_cost + output_cost
        
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(total_cost, 6),
            "duration_ms": duration_ms,
            "user_message": history[-1] if history else "",
            "reply": reply
        }
        
        log_call(entry)
        
        rprint(f"[dim]↳ {agent} | {model} | ~{input_tokens} in / ~{output_tokens} out | {duration_ms}ms[/dim]")
        
        return {
            "reply": reply,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": round(total_cost, 6),
            "duration_ms": duration_ms,
            "error": None
        }
    
    except Exception as e:
        rprint(f"[red]NVIDIA API ERROR ({agent}): {e}[/red]")
        return {
            "reply": None,
            "input_tokens": 0,
            "output_tokens": 0,
            "cost": 0,
            "duration_ms": 0,
            "error": str(e)
        }


def _call_gemini(system: str, history: list, agent: str, model: str, model_info: dict) -> dict:
    """Call Google Gemini API"""
    
    if not gemini_client:
        return {"error": "GEMINI_API_KEY not set. Add it to .env file"}
    
    start = time.time()
    
    try:
        response = gemini_client.models.generate_content(
            model=model,
            contents=history,
            config=genai.types.GenerateContentConfig(
                system_instruction=system
            )
        )

        duration_ms = int((time.time() - start) * 1000)
        input_tokens = response.usage_metadata.prompt_token_count
        output_tokens = response.usage_metadata.candidates_token_count
        input_cost = input_tokens * model_info["input_cost"]
        output_cost = output_tokens * model_info["output_cost"]
        total_cost = input_cost + output_cost
        reply = response.text

        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent,
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost_usd": round(total_cost, 6),
            "duration_ms": duration_ms,
            "user_message": history[-1] if history else "",
            "reply": reply
        }

        log_call(entry)

        rprint(f"[dim]↳ {agent} | {model} | {input_tokens} in / {output_tokens} out | {duration_ms}ms[/dim]")

        return {
            "reply": reply,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": round(total_cost, 6),
            "duration_ms": duration_ms,
            "error": None
        }

    except Exception as e:
        rprint(f"[red]GEMINI API ERROR ({agent}): {e}[/red]")
        return {
            "reply": None,
            "input_tokens": 0,
            "output_tokens": 0,
            "cost": 0,
            "duration_ms": 0,
            "error": str(e)
        }
    

if __name__ == "__main__":
    result = call_llm(
        system="you are a helpful assistant",
        history=[{"role": "user", "parts": [{"text": "say hello in one sentence"}]}],
        agent="test"
    )
    rprint(result)