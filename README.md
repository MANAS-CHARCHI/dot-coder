# .coder — Multi-Agent Software Factory

**An autonomous multi-agent pipeline that takes your rough idea and delivers a complete, tested, working codebase.**

No human intervention needed after the initial conversation (except 3 checkpoints for approval).

---

## What Is This?

.coder is a fully autonomous software factory powered by 10 specialized AI agents:

1. **Sales Agent** — Gathers requirements through conversation
2. **Manager Agent** — Creates project plan and task distribution
3. **Architect Agent** — Makes all technical decisions
4. **DB Engineer Agent** — Designs complete database schema
5. **Backend Engineer Agent** — Designs complete API
6. **Frontend Engineer Agent** — Designs complete UI
7. **Coder Agent** — Writes actual code (3 phases: DB, Backend, Frontend)
8. **Reviewer Agent** — Fast quality gate before testing
9. **Tester Agent** — Writes and runs tests, reports bugs
10. **Delivery Agent** — Creates final report with setup instructions

All agents communicate through files in `.coder/` — a shared memory folder.

One **Orchestrator** (Python code, not an LLM) manages the entire pipeline.

---

## Features

✅ **Fully Autonomous** — Runs end-to-end with minimal human input  
✅ **3 Human Checkpoints** — Approve requirements, architecture, and final delivery  
✅ **Parallel Execution** — DB and Frontend planning run simultaneously  
✅ **Retry Logic** — Agents get 3 attempts before escalating  
✅ **Resume from Crash** — Pipeline state saved after every step  
✅ **Event Log** — Full audit trail of everything that happened  
✅ **Shared Memory** — All agents stay consistent (no contradictions)  
✅ **Quality Gates** — Nothing broken passes downstream  

---

## Quick Start

### 1. Install Dependencies

```bash
# Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync
```

### 2. Set Up API Key

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API key
# Option 1 (Recommended): NVIDIA API - Get free key at: https://build.nvidia.com/
# Option 2: Gemini API - Get free key at: https://aistudio.google.com/apikey
```

**Note:** You only need ONE API key. NVIDIA z-ai/glm4.7 is the default (free, with reasoning capabilities).

### 3. Run the Pipeline

```bash
python main.py
```

That's it! The Sales Agent will start asking you questions.

See [SETUP_NVIDIA.md](SETUP_NVIDIA.md) for detailed setup instructions.

---

## How It Works

### The Pipeline

```
User Input (terminal)
↓
[ORCHESTRATOR] ← Python code, not an LLM
↓
[SALES]        → human checkpoint 1
↓
[MANAGER]
↓
[ARCHITECT]    → human checkpoint 2
↓
┌─────────────────────┐
[DB ENGINEER]   [FRONTEND PREP]   ← parallel
└─────────────────────┘
↓
[CODER] → [REVIEWER] → [TESTER] ← backend loop
↓
[FRONTEND ENGINEER]
↓
[CODER] → [REVIEWER] → [TESTER] ← frontend loop
↓
[FINAL TESTER] → human checkpoint 3
↓
[DELIVERY] → User ✅
```

### The .coder Folder

All agents read from and write to `.coder/`:

```
.coder/
├── orchestrator/
│   ├── pipeline_state.json    ← live state of every step
│   ├── event_log.json         ← every event timestamped
│   └── memory.json            ← shared facts all agents read
├── sales/
│   ├── requirements.md
│   └── model_selection.md
├── manager/
│   ├── project_plan.md
│   └── task_distribution.md
├── architect/
│   ├── system_design.md
│   ├── data_flow.md
│   └── tech_requirements.md
├── engineer/
│   ├── database/
│   ├── backend/
│   └── frontend/
├── coder/
│   ├── db_code/
│   ├── backend_code/
│   └── frontend_code/
├── reviewer/
│   └── review_results.md
├── tester/
│   ├── test_results.md
│   └── bugs.md
└── delivery/
    └── final_report.md
```

---

## Human Checkpoints

The pipeline pauses 3 times for your approval:

1. **After Sales** — "Is this what you want to build?"
2. **After Architect** — "Happy with the system design?"
3. **After Final Tester** — "All tests passing. Ready to deliver?"

At each checkpoint, you can:
- Type `yes` to continue
- Type `no` to stop
- Type `change` to modify files manually, then continue

---

## Resume from Crash

If the pipeline crashes or you stop it:

```bash
python main.py
```

It will detect the existing pipeline and ask if you want to resume.

All state is saved in `.coder/orchestrator/pipeline_state.json`.

---

## Model Selection

During the Sales conversation, you'll choose which AI models to use:

1. **NVIDIA z-ai/glm4.7 for all** — Recommended, free, with reasoning capabilities
2. **Gemini 2.5 Flash-Lite for all** — Free, fast, large context window
3. **Mix both** — NVIDIA for planning, Gemini for coding

Currently supports:
- **NVIDIA z-ai/glm4.7** (default) - Free with reasoning
- **Google Gemini** models - Free and paid tiers
- More providers coming soon (Claude, GPT-4)

---

## Example Session

```
$ python main.py

.coder - Multi-Agent Software Factory

Let's build something!

Enter project name: Todo App

💼 Sales Agent Starting...

Sales Agent: Hi! What do you want to build?

You: A simple todo app

Sales Agent: Great! Who will use this app?

You: Small teams

[... conversation continues ...]

🛑 Checkpoint: Requirements Review
Review the requirements in .coder/sales/requirements.md
Type 'yes' to continue, 'no' to stop, or 'change' to modify:

> yes

📋 Manager Agent Starting...
✅ Manager Agent Complete

🏗️  Architect Agent Starting...
✅ Architect Agent Complete

[... pipeline continues ...]

🎉 Pipeline completed successfully!
Check .coder/delivery/final_report.md for your project
```

---

## Architecture

### Orchestrator (Python)

The Orchestrator is **not an LLM agent** — it's Python code that:

- Manages pipeline state
- Checks dependencies before running each agent
- Runs quality gates after each agent
- Handles retries (up to 3 attempts)
- Runs parallel agents using threads
- Pauses for human checkpoints
- Logs every event

### Agents (LLM-powered)

Each agent:

- Reads from `.coder/` (previous agents' outputs)
- Reads from `memory.json` (shared facts)
- Calls an LLM with a specialized system prompt
- Writes output files to `.coder/`
- Updates `memory.json` if needed

Agents **never talk directly to each other** — only through files.

### Shared Memory

`memory.json` stores key decisions made early:

- Project name and scope
- Tech stack (exact versions)
- Conventions (naming, error formats, etc.)
- Model selection

All downstream agents read this to stay consistent.

### Quality Gates

After each agent runs, the Orchestrator checks:

- All required files exist
- Files are non-empty
- Content is in correct format

If quality gate fails → retry up to 3 times with specific feedback.

### Retry Logic

```
Agent runs → bad output
↓
Retry 1: "Your output was incomplete. Specifically: [X]. Try again."
↓ still bad?
Retry 2: "Still missing [X]. Focus only on producing [required output]."
↓ still bad?
Retry 3: last attempt with maximum specificity
↓ still bad?
Escalate to Manager: "Agent [X] failed 3 times. Re-plan this section."
```

---

## Development Status

**Current Version:** 2.1

**What Works:**
- ✅ Full pipeline orchestration
- ✅ All 10 agents implemented
- ✅ Shared memory system
- ✅ Quality gates and retries
- ✅ Human checkpoints
- ✅ Resume from crash
- ✅ Event logging
- ✅ NVIDIA API integration (z-ai/glm4.7 with reasoning)
- ✅ Gemini API integration
- ✅ Rich terminal UI

**Coming Soon:**
- ⏳ Parallel execution (threading)
- ⏳ Claude API support
- ⏳ Actual code execution and testing
- ⏳ Bug fix loop (Coder ↔ Tester)
- ⏳ Web UI for monitoring

---

## Contributing

This is an experimental project. Contributions welcome!

Key areas for improvement:
- Better prompt engineering for each agent
- More robust file parsing
- Actual test execution
- Support for more tech stacks
- Better error recovery

---

## License

MIT

---

## Credits

Built with:
- [NVIDIA AI](https://build.nvidia.com/) - z-ai/glm4.7 model
- [Google Gemini API](https://ai.google.dev/)
- [OpenAI Python Client](https://github.com/openai/openai-python) - For NVIDIA API
- [Rich](https://github.com/Textualize/rich) for terminal UI
- [uv](https://github.com/astral-sh/uv) for Python package management

---

**Built by AI, for building with AI.** 🤖
