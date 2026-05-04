# Contributing to .coder

Thanks for your interest in contributing! This guide will help you get started.

---

## Quick Links

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)

---

## Code of Conduct

Be respectful, constructive, and collaborative. We're all here to build something cool.

---

## How to Contribute

### Reporting Bugs

Open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version)
- Relevant logs from `.coder/orchestrator/event_log.json`

### Suggesting Features

Open an issue with:
- Clear description of the feature
- Why it's useful
- How it might work
- Any implementation ideas

### Improving Documentation

Documentation PRs are always welcome! Areas that need help:
- More examples
- Better explanations
- Fixing typos
- Adding diagrams

### Writing Code

See [Development Setup](#development-setup) below.

---

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/dot-coder.git
cd dot-coder
```

### 2. Install Dependencies

```bash
uv sync
```

### 3. Set Up Environment

```bash
cp .env.example .env
# Add your GEMINI_API_KEY
```

### 4. Run Tests

```bash
python test_setup.py
```

### 5. Make Changes

Create a branch:

```bash
git checkout -b feature/my-feature
```

### 6. Test Your Changes

```bash
# Run the full pipeline
python main.py

# Check logs
cat .coder/orchestrator/event_log.json
```

---

## Project Structure

```
dot-coder/
├── main.py                 # Entry point
├── orchestrator.py         # Pipeline orchestrator
├── llm.py                  # LLM API client
├── llm_call.py            # Model definitions
├── agents/                 # All agent implementations
│   ├── __init__.py        # Agent registry
│   ├── base_agent.py      # Base class
│   ├── sales.py           # Sales agent
│   ├── manager.py         # Manager agent
│   ├── architect.py       # Architect agent
│   ├── db_engineer.py     # DB Engineer agent
│   ├── backend_engineer.py # Backend Engineer agent
│   ├── frontend_engineer.py # Frontend Engineer agent
│   ├── coder.py           # Coder agent
│   ├── reviewer.py        # Reviewer agent
│   ├── tester.py          # Tester agent
│   └── delivery.py        # Delivery agent
├── .coder/                # Generated output (gitignored)
├── README.md              # Main documentation
├── QUICKSTART.md          # Quick start guide
├── ARCHITECTURE.md        # Architecture deep dive
└── CONTRIBUTING.md        # This file
```

---

## Key Concepts

### Orchestrator

- Python code (not an LLM)
- Manages pipeline state
- Runs agents in order
- Handles retries and errors

### Agents

- LLM-powered
- Inherit from `BaseAgent`
- Read from `.coder/`
- Write to `.coder/`
- Update `memory.json`

### Communication

- Agents never call each other
- All communication through files
- Shared memory for consistency

### Quality Gates

- Check output after each agent
- Retry up to 3 times
- Escalate if still failing

---

## Testing

### Manual Testing

```bash
# Run full pipeline
python main.py

# Check output
ls -la .coder/

# Check logs
cat .coder/orchestrator/event_log.json

# Check memory
cat .coder/orchestrator/memory.json
```

### Setup Testing

```bash
python test_setup.py
```

### Unit Tests (TODO)

We need unit tests! Contributions welcome.

Areas that need tests:
- Orchestrator logic
- Quality gates
- File parsing
- Memory updates
- Retry logic

---

## Adding a New Agent

### 1. Create Agent File

```python
# agents/my_agent.py

from .base_agent import BaseAgent
from rich import print as rprint


class MyAgent(BaseAgent):
    """
    My Agent - Does something cool
    """
    
    def get_system_prompt(self) -> str:
        return """You are My Agent.
        
Your job is to...

INPUT FILES:
- .coder/previous_agent/output.md

OUTPUT FILES YOU MUST CREATE:
- .coder/my_agent/result.md

RULES:
- Be specific
- Follow conventions from memory.json
"""
    
    def run(self) -> bool:
        """Run the agent"""
        rprint("\n[bold cyan]🎯 My Agent Starting...[/bold cyan]\n")
        
        # Read inputs
        input_data = self.read_file("previous_agent/output.md")
        
        if not input_data:
            rprint("[red]Error: Missing input[/red]")
            return False
        
        # Create prompt
        user_message = f"""Process this input:

{input_data}

MEMORY:
{self.memory}

Create result.md with your output."""
        
        # Call LLM
        response = self.call_llm(self.get_system_prompt(), user_message)
        
        if not response:
            return False
        
        # Write output
        self.write_file("my_agent/result.md", response)
        
        rprint("\n[bold green]✅ My Agent Complete[/bold green]")
        return True
```

### 2. Register Agent

```python
# agents/__init__.py

from .my_agent import MyAgent

AGENT_MAP = {
    # ... existing agents ...
    "my_agent": MyAgent,
}
```

### 3. Add to Pipeline

```python
# orchestrator.py

self.dependencies = {
    # ... existing dependencies ...
    "my_agent": ["previous_agent"],
}

self.quality_gates = {
    # ... existing gates ...
    "my_agent": ["my_agent/result.md"],
}
```

### 4. Update State

```python
# .coder/orchestrator/pipeline_state.json

"steps": {
    # ... existing steps ...
    "my_agent": {
        "status": "pending",
        "started_at": null,
        "completed_at": null,
        "retries": 0
    }
}
```

### 5. Test It

```bash
python main.py
```

---

## Adding a New Model Provider

### 1. Add Model Definitions

```python
# llm_call.py

MODELS = {
    # ... existing models ...
    "claude-3-opus": {
        "provider": "anthropic",
        "input_cost": 0.000015,
        "output_cost": 0.000075,
        "context": 200000
    },
}
```

### 2. Implement API Client

```python
# llm.py

def call_llm(system: str, history: list, agent: str, model: str = DEFAULT_MODEL) -> dict:
    model_info = MODELS[model]
    
    if model_info["provider"] == "google":
        return _call_gemini(system, history, agent, model)
    elif model_info["provider"] == "anthropic":
        return _call_claude(system, history, agent, model)
    else:
        return {"error": f"Unknown provider: {model_info['provider']}"}


def _call_claude(system: str, history: list, agent: str, model: str) -> dict:
    # Implement Claude API call
    pass
```

### 3. Update Model Selection

```python
# agents/sales.py

model_table.add_row("Manager", "Claude Opus", "Claude Sonnet")
# ... etc
```

---

## Code Style

### Python

- Follow PEP 8
- Use type hints where helpful
- Keep functions focused and small
- Add docstrings to classes and complex functions

### Naming

- `snake_case` for functions and variables
- `PascalCase` for classes
- `UPPER_CASE` for constants

### Comments

- Explain **why**, not **what**
- Use docstrings for public APIs
- Keep comments up to date

### Imports

```python
# Standard library
import json
from pathlib import Path

# Third-party
from rich import print as rprint

# Local
from .base_agent import BaseAgent
```

---

## Pull Request Process

### 1. Create PR

- Clear title describing the change
- Description explaining why and how
- Link to related issues

### 2. PR Checklist

- [ ] Code follows style guide
- [ ] Added/updated documentation
- [ ] Tested manually
- [ ] No breaking changes (or documented)
- [ ] Updated CHANGELOG (if exists)

### 3. Review Process

- Maintainer will review within a few days
- Address feedback
- Squash commits if requested

### 4. Merge

- Maintainer will merge when approved
- Delete your branch after merge

---

## Areas That Need Help

### High Priority

- [ ] Unit tests for orchestrator
- [ ] Unit tests for agents
- [ ] Actual code execution
- [ ] Bug fix loop (Coder ↔ Tester)
- [ ] Better file parsing from LLM responses

### Medium Priority

- [ ] Claude API support
- [ ] More tech stacks (Go, Rust, etc.)
- [ ] Web UI for monitoring
- [ ] Better error messages
- [ ] Progress indicators

### Low Priority

- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] More examples
- [ ] Video tutorials
- [ ] Benchmarks

---

## Questions?

- Open an issue
- Start a discussion
- Check existing issues first

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing!** 🎉
