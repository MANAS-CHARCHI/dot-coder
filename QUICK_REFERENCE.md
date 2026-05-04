# Quick Reference Card

Fast lookup for common tasks and commands.

---

## Installation

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Setup environment
cp .env.example .env
# Edit .env and add API key
```

---

## Running

```bash
# Start pipeline
python main.py

# Test setup
python test_setup.py

# Test LLM connection
python llm.py
```

---

## API Keys

### NVIDIA (Recommended)
- Get at: https://build.nvidia.com/
- Add to `.env`: `NVIDIA_API_KEY=nvapi-xxx`
- Model: `z-ai/glm4.7`
- Cost: Free

### Gemini (Alternative)
- Get at: https://aistudio.google.com/apikey
- Add to `.env`: `GEMINI_API_KEY=AIza-xxx`
- Model: `gemini-2.5-flash-lite`
- Cost: Free

---

## Model Selection

During pipeline, choose:

1. **NVIDIA for all** (recommended)
   - Free, with reasoning
   - Good for all tasks

2. **Gemini for all**
   - Free, fast
   - Large context window

3. **Mix both**
   - NVIDIA for planning
   - Gemini for coding

---

## File Structure

```
.coder/
├── orchestrator/
│   ├── pipeline_state.json  ← Resume point
│   ├── memory.json          ← Shared facts
│   └── event_log.json       ← Audit trail
├── sales/                   ← Requirements
├── manager/                 ← Project plan
├── architect/               ← System design
├── engineer/                ← Task lists
├── coder/                   ← Generated code
├── reviewer/                ← Code reviews
├── tester/                  ← Test results
└── delivery/                ← Final report
```

---

## Key Files

| File | Purpose |
|------|---------|
| `main.py` | Entry point |
| `orchestrator.py` | Pipeline manager |
| `llm.py` | LLM API client |
| `llm_call.py` | Model definitions |
| `agents/*.py` | All 10 agents |
| `.env` | API keys (gitignored) |

---

## Commands

### Setup
```bash
uv sync                    # Install dependencies
cp .env.example .env       # Create env file
python test_setup.py       # Verify setup
```

### Run
```bash
python main.py             # Start pipeline
```

### Debug
```bash
cat .coder/orchestrator/event_log.json     # See events
cat .coder/orchestrator/pipeline_state.json # See state
cat .coder/orchestrator/memory.json        # See memory
```

### Clean
```bash
rm -rf .coder/             # Delete all output
python main.py             # Start fresh
```

---

## Checkpoints

Pipeline pauses 3 times:

1. **After Sales** - Approve requirements
2. **After Architect** - Approve design
3. **After Final Tester** - Approve delivery

At each checkpoint:
- `yes` - Continue
- `no` - Stop
- `change` - Edit files manually, then continue

---

## Agents

| # | Agent | Input | Output |
|---|-------|-------|--------|
| 1 | Sales | User conversation | requirements.md |
| 2 | Manager | requirements.md | project_plan.md |
| 3 | Architect | project_plan.md | system_design.md |
| 4 | DB Engineer | system_design.md | schema_plan.md |
| 5 | Backend Eng | schema_plan.md | api_plan.md |
| 6 | Frontend Eng | api_plan.md | ui_plan.md |
| 7 | Coder | task_list.md | code files |
| 8 | Reviewer | code files | review_results.md |
| 9 | Tester | code + tests | test_results.md |
| 10 | Delivery | everything | final_report.md |

---

## Troubleshooting

### "API key not set"
- Check `.env` file exists
- Check key is correct format
- No spaces around `=`

### "Module not found"
- Run `uv sync`

### Pipeline stuck
- Check `.coder/orchestrator/event_log.json`
- Look for last event
- Resume with `python main.py`

### Want to start over
```bash
rm -rf .coder/
python main.py
```

---

## Environment Variables

```bash
# Required (at least one)
NVIDIA_API_KEY=nvapi-xxx
GEMINI_API_KEY=AIza-xxx

# Optional
NO_COLOR=1              # Disable colors
```

---

## Models Available

| Model | Provider | Cost | Context |
|-------|----------|------|---------|
| z-ai/glm4.7 | NVIDIA | Free | 16K |
| gemini-2.5-flash-lite | Google | Free | 1M |
| gemini-2.0-flash-exp | Google | Free | 1M |
| gemini-1.5-flash | Google | $0.075/1M | 1M |
| gemini-1.5-pro | Google | $1.25/1M | 2M |

---

## Documentation

| File | Content |
|------|---------|
| README.md | Project overview |
| QUICKSTART.md | Quick start guide |
| SETUP_NVIDIA.md | NVIDIA setup |
| ARCHITECTURE.md | System design |
| API_ARCHITECTURE.md | API integration |
| PIPELINE_FLOW.md | Visual flows |
| CONTRIBUTING.md | How to contribute |
| CHANGELOG.md | Version history |

---

## Common Tasks

### Add new agent
1. Create `agents/my_agent.py`
2. Inherit from `BaseAgent`
3. Implement `get_system_prompt()` and `run()`
4. Add to `agents/__init__.py`
5. Add to orchestrator dependencies

### Add new model
1. Add to `llm_call.py` MODELS dict
2. Add provider function in `llm.py`
3. Update model selection in `agents/sales.py`

### Change default model
```python
# llm_call.py
DEFAULT_MODEL = "your-model-name"
```

---

## Support

- 📖 Read docs in this repo
- 🐛 Open issue on GitHub
- 💬 Check existing issues first

---

## Quick Links

- NVIDIA API: https://build.nvidia.com/
- Gemini API: https://aistudio.google.com/apikey
- uv installer: https://astral.sh/uv/
- Project repo: [Your GitHub URL]

---

**Version:** 2.1  
**Last Updated:** May 4, 2026
