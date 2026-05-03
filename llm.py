import os
import json
import time
from datetime import datetime
from pathlib import Path

from google import genai
from rich import print as rprint
from dotenv import load_dotenv
load_dotenv()

from llm_call import MODELS, DEFAULT_MODEL

def setup():
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        rprint("[red]ERROR: GEMINI_API_KEY not set. Run: export GEMINI_API_KEY=your_key[/red]")
        exit(1)
    return genai.Client(api_key=api_key)

client = setup()

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
    start      = time.time()

    try:
        response = client.models.generate_content(
            model    = model,
            contents = history,
            config   = genai.types.GenerateContentConfig(
                system_instruction = system
            )
        )

        duration_ms   = int((time.time() - start) * 1000)
        input_tokens  = response.usage_metadata.prompt_token_count
        output_tokens = response.usage_metadata.candidates_token_count
        input_cost    = input_tokens  * model_info["input_cost"]
        output_cost   = output_tokens * model_info["output_cost"]
        total_cost    = input_cost + output_cost
        reply         = response.text

        entry = {
            "timestamp":    datetime.now().isoformat(),
            "agent":        agent,
            "model":        model,
            "input_tokens": input_tokens,
            "output_tokens":output_tokens,
            "cost_usd":     round(total_cost, 6),
            "duration_ms":  duration_ms,
            "user_message": history[-1] if history else "",
            "reply":        reply
        }

        log_call(entry)

        rprint(f"[dim]↳ {agent} | {model} | {input_tokens} in / {output_tokens} out | {duration_ms}ms[/dim]")

        return {
            "reply":         reply,
            "input_tokens":  input_tokens,
            "output_tokens": output_tokens,
            "cost":          round(total_cost, 6),
            "duration_ms":   duration_ms,
            "error":         None
        }

    except Exception as e:
        rprint(f"[red]LLM ERROR ({agent}): {e}[/red]")
        return {
            "reply":         None,
            "input_tokens":  0,
            "output_tokens": 0,
            "cost":          0,
            "duration_ms":   0,
            "error":         str(e)
        }
    

if __name__ == "__main__":
    result = call_llm(
        system  = "you are a helpful assistant",
        history = [{"role": "user", "parts": [{"text": "say hello in one sentence"}]}],
        agent   = "test"
    )
    rprint(result)


# if __name__ == "__main__":
#     for m in client.models.list():
#         print(m.name)