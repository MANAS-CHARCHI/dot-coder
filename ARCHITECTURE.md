# Architecture Documentation

Deep dive into how .coder works internally.

---

## Table of Contents

1. [Overview](#overview)
2. [Core Principles](#core-principles)
3. [The Orchestrator](#the-orchestrator)
4. [Agent System](#agent-system)
5. [Communication Layer](#communication-layer)
6. [State Management](#state-management)
7. [Quality Control](#quality-control)
8. [Error Recovery](#error-recovery)
9. [Parallel Execution](#parallel-execution)
10. [Extension Points](#extension-points)

---

## Overview

.coder is a **multi-agent system** where:

- **One orchestrator** (Python code) manages everything
- **10 specialized agents** (LLM-powered) do the work
- **Files** are the communication bus
- **Shared memory** keeps everyone consistent
- **Quality gates** prevent bad outputs from propagating
- **Human checkpoints** catch wrong assumptions early

```
┌─────────────────────────────────────────┐
│           ORCHESTRATOR                  │
│  (Python - not an LLM)                  │
│                                         │
│  - Manages pipeline state               │
│  - Checks dependencies                  │
│  - Runs quality gates                   │
│  - Handles retries                      │
│  - Logs everything                      │
└─────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        │                       │
        ▼                       ▼
┌──────────────┐        ┌──────────────┐
│   AGENTS     │◄──────►│    FILES     │
│ (LLM-powered)│        │ (.coder/)    │
└──────────────┘        └──────────────┘
        │                       │
        └───────────┬───────────┘
                    ▼
            ┌──────────────┐
            │   MEMORY     │
            │ (memory.json)│
            └──────────────┘
```

---

## Core Principles

### 1. No Direct Agent Communication

Agents **never** call each other directly. They only communicate through files.

**Why?**
- Simpler debugging (just read the files)
- Easy to resume from any point
- Clear audit trail
- Agents can be swapped/upgraded independently

### 2. Orchestrator is Not an Agent

The orchestrator is **Python code**, not an LLM agent.

**Why?**
- Deterministic control flow
- No hallucinations in pipeline logic
- Fast execution (no LLM calls for coordination)
- Reliable state management

### 3. Shared Memory for Consistency

All agents read from `memory.json` before doing work.

**Why?**
- Prevents contradictions (Architect picks PostgreSQL, Coder doesn't use MongoDB)
- Reduces token usage (don't repeat tech stack in every prompt)
- Single source of truth

### 4. Quality Gates Before Handoff

After every agent, check output before continuing.

**Why?**
- Catch problems early
- Don't waste downstream agents' time
- Clear failure points

### 5. Retry Before Escalate

Give agents 3 chances with specific feedback before giving up.

**Why?**
- LLMs are non-deterministic (might work on retry)
- Specific feedback helps (not just "try again")
- Escalation is expensive (requires re-planning)

---

## The Orchestrator

**File:** `orchestrator.py`

### Responsibilities

1. **Pipeline Management**
   - Initialize new pipelines
   - Resume crashed pipelines
   - Track current step
   - Save state after every step

2. **Dependency Resolution**
   - Check if step's dependencies are complete
   - Block steps until dependencies ready
   - Enable parallel execution when safe

3. **Quality Control**
   - Run quality gates after each agent
   - Verify required files exist and are non-empty
   - Trigger retries on failure

4. **Error Handling**
   - Retry agents up to 3 times
   - Provide specific feedback on each retry
   - Escalate to Manager after 3 failures

5. **Human Interaction**
   - Pause at 3 checkpoints
   - Wait for user approval
   - Allow manual file edits

6. **Event Logging**
   - Log every event with timestamp
   - Create audit trail
   - Enable debugging

### Key Data Structures

#### Pipeline State

```json
{
  "project_id": "proj_abc123",
  "started_at": "2026-05-04T10:00:00",
  "current_step": "backend_engineer",
  "status": "running",
  "steps": {
    "sales": {
      "status": "done",
      "started_at": "...",
      "completed_at": "...",
      "retries": 0
    },
    "manager": {
      "status": "running",
      "started_at": "...",
      "completed_at": null,
      "retries": 1
    }
  }
}
```

#### Dependency Graph

```python
dependencies = {
    "sales": [],
    "manager": ["sales"],
    "architect": ["manager"],
    "db_engineer": ["architect"],
    "coder_db": ["db_engineer"],
    "backend_engineer": ["coder_db"],
    # ... etc
}
```

#### Quality Gates

```python
quality_gates = {
    "sales": [
        "sales/requirements.md",
        "sales/model_selection.md"
    ],
    "manager": [
        "manager/project_plan.md",
        "manager/task_distribution.md"
    ],
    # ... etc
}
```

### Main Loop

```python
for step in steps:
    # Skip if already done (resume case)
    if state["steps"][step]["status"] == "done":
        continue
    
    # Check dependencies
    if not can_run_step(step):
        continue
    
    # Run agent
    success = run_agent(step)
    
    # Quality gate
    passed, missing = check_quality_gate(step)
    
    if not passed:
        # Retry up to 3 times
        retry_agent(step, missing)
    
    # Human checkpoints
    if step in ["sales", "architect", "final_tester"]:
        if not human_checkpoint(step):
            return False
```

---

## Agent System

**Directory:** `agents/`

### Base Agent Class

All agents inherit from `BaseAgent`:

```python
class BaseAgent:
    def __init__(self, name, memory, retry_count):
        self.name = name
        self.memory = memory
        self.retry_count = retry_count
        self.history = []
    
    def read_file(self, path) -> str
    def write_file(self, path, content)
    def update_memory(self, updates)
    def call_llm(self, system_prompt, user_message) -> str
    
    def get_system_prompt(self) -> str:
        # Override in subclass
        raise NotImplementedError
    
    def run(self) -> bool:
        # Override in subclass
        raise NotImplementedError
```

### Agent Lifecycle

1. **Initialization**
   - Load memory.json
   - Get model from memory
   - Initialize conversation history

2. **Execution**
   - Read input files
   - Call LLM with system prompt + user message
   - Parse response
   - Write output files
   - Update memory if needed

3. **Completion**
   - Return True if successful
   - Return False if failed

### Agent Types

#### 1. Conversational Agents

**Example:** Sales Agent

- Interactive conversation with user
- Multiple LLM calls in a loop
- Builds up conversation history
- Writes summary at end

#### 2. Planning Agents

**Example:** Manager, Architect, Engineers

- Read input files
- Single LLM call with detailed prompt
- Parse response into multiple output files
- Update shared memory

#### 3. Coding Agents

**Example:** Coder

- Read task lists
- Generate actual code
- Parse code blocks from response
- Write multiple code files

#### 4. Review Agents

**Example:** Reviewer, Tester

- Read code files
- Check for specific issues
- Generate pass/fail report
- List specific problems

#### 5. Summary Agents

**Example:** Delivery

- Read all pipeline outputs
- Generate comprehensive report
- No memory updates

---

## Communication Layer

### File-Based Communication

All inter-agent communication happens through files in `.coder/`.

**Advantages:**
- Transparent (just read the files)
- Debuggable (files persist)
- Resumable (state on disk)
- Versionable (can commit to git)

**Disadvantages:**
- Slower than in-memory
- Requires file parsing
- Disk I/O overhead

### File Naming Convention

```
.coder/
├── <agent_name>/
│   ├── <output_file>.md
│   └── <output_file>.md
```

Examples:
- `.coder/sales/requirements.md`
- `.coder/architect/system_design.md`
- `.coder/coder/backend_code/main.py`

### File Formats

Most files are **Markdown** for human readability.

Code files are in their native format (`.py`, `.js`, etc.).

---

## State Management

### Pipeline State

**File:** `.coder/orchestrator/pipeline_state.json`

Tracks:
- Current step
- Status of each step (pending/running/done/failed)
- Start/completion timestamps
- Retry counts

**Updated:** After every step

**Used for:** Resume from crash

### Shared Memory

**File:** `.coder/orchestrator/memory.json`

Stores:
- Project metadata (name, scope)
- Tech stack decisions (exact versions)
- Conventions (naming, formats)
- Model selection

**Updated:** By Sales, Manager, Architect, Engineers

**Read by:** All agents

### Event Log

**File:** `.coder/orchestrator/event_log.json`

Records:
- Every event with timestamp
- Agent starts/completions
- Quality gate results
- Retries and failures
- Checkpoint approvals

**Append-only:** Never modified, only appended

**Used for:** Debugging, audit trail

---

## Quality Control

### Quality Gates

After each agent completes, the orchestrator checks:

1. **File Existence**
   - All required files exist
   - No missing outputs

2. **File Content**
   - Files are non-empty
   - Files have minimum content

3. **Format Validation** (future)
   - Markdown has required sections
   - Code has required structure

### Retry Logic

```
Agent runs → output checked
↓
Quality gate fails
↓
Retry 1: "Missing: [specific files]. Create them."
↓ still fails?
Retry 2: "Still missing [files]. Focus ONLY on creating these files."
↓ still fails?
Retry 3: "Last attempt. Create [files] with [specific content]."
↓ still fails?
Escalate: "Agent failed 3 times. Manual intervention needed."
```

### Reviewer Agent

Special quality gate between Coder and Tester.

**Checks:**
- Completeness (no TODOs, no placeholders)
- Consistency (matches schema/API plans)
- Obvious errors (syntax, missing imports)
- Standards (headers, error handling)

**Why separate agent?**
- Faster than running tests
- Catches obvious issues early
- Saves Tester's time

---

## Error Recovery

### Resume from Crash

If pipeline crashes:

1. Load `pipeline_state.json`
2. Find first incomplete step
3. Continue from there

All previous work is preserved.

### Manual Intervention

At any checkpoint, user can:

1. Type `change`
2. Edit files in `.coder/` manually
3. Type `yes` to continue

Pipeline continues with modified files.

### Escalation

After 3 failed retries:

1. Log escalation event
2. Pause pipeline
3. Show error to user
4. Wait for manual fix

---

## Parallel Execution

### Parallel Opportunities

Some agents can run simultaneously:

- **DB Engineer + Frontend Prep** (both need Architect, not each other)
- **Multiple Coder tasks** (writing independent files)

### Implementation

```python
def run_parallel(steps: List[str]) -> bool:
    with ThreadPoolExecutor(max_workers=len(steps)) as executor:
        futures = {
            executor.submit(run_agent, step): step
            for step in steps
        }
        
        results = {}
        for future in as_completed(futures):
            step = futures[future]
            results[step] = future.result()
    
    return all(results.values())
```

### Safety

Only run in parallel if:
- No dependencies between steps
- No shared file writes
- Independent memory updates

---

## Extension Points

### Adding New Agents

1. Create `agents/my_agent.py`
2. Inherit from `BaseAgent`
3. Implement `get_system_prompt()` and `run()`
4. Add to `AGENT_MAP` in `agents/__init__.py`
5. Add to dependency graph in `orchestrator.py`
6. Add quality gate requirements

### Adding New Models

1. Add to `MODELS` in `llm_call.py`
2. Implement API client in `llm.py`
3. Update model selection in Sales agent

### Custom Quality Gates

Override `check_quality_gate()` in orchestrator:

```python
def check_quality_gate(self, step: str) -> tuple[bool, List[str]]:
    # Custom validation logic
    if step == "my_agent":
        return self._check_my_agent_output()
    
    # Default validation
    return super().check_quality_gate(step)
```

### Custom Checkpoints

Add to `run_pipeline()`:

```python
if step == "my_agent":
    if not self.human_checkpoint("My Review", "Check my_agent output"):
        return False
```

---

## Performance Considerations

### Token Usage

- Sales: ~1K-5K tokens (conversation)
- Manager: ~5K-10K tokens (planning)
- Architect: ~10K-20K tokens (detailed design)
- Engineers: ~10K-15K tokens each
- Coder: ~20K-50K tokens (code generation)
- Reviewer: ~10K-20K tokens (code review)
- Tester: ~15K-30K tokens (test generation)
- Delivery: ~5K-10K tokens (summary)

**Total:** ~100K-200K tokens per project

**Cost (Gemini Flash-Lite):** $0 (free tier)

### Execution Time

- Sales: 2-5 minutes (user conversation)
- Manager: 30-60 seconds
- Architect: 1-2 minutes
- Engineers: 1-2 minutes each
- Coder: 2-5 minutes per phase
- Reviewer: 1-2 minutes per phase
- Tester: 2-3 minutes per phase
- Delivery: 30-60 seconds

**Total:** 15-30 minutes for typical project

### Optimization Opportunities

1. **Parallel execution** — Save 30-40% time
2. **Caching** — Reuse similar designs
3. **Incremental updates** — Only regenerate changed parts
4. **Streaming** — Show progress in real-time
5. **Batch operations** — Multiple files in one LLM call

---

## Security Considerations

### API Keys

- Never commit `.env` to git
- Use environment variables only
- Rotate keys regularly

### Generated Code

- Review before running
- Scan for hardcoded secrets
- Check for malicious patterns
- Run in sandbox first

### File System

- All writes confined to `.coder/`
- No access to parent directories
- No arbitrary command execution

---

## Future Enhancements

### Planned Features

- [ ] Actual code execution and testing
- [ ] Bug fix loop (Coder ↔ Tester until all pass)
- [ ] Web UI for monitoring
- [ ] Claude API support
- [ ] More tech stacks (Go, Rust, etc.)
- [ ] Database migrations generation
- [ ] Docker containerization
- [ ] CI/CD pipeline generation
- [ ] Documentation generation
- [ ] API client generation

### Research Directions

- [ ] Multi-agent debate for better decisions
- [ ] Self-improving prompts
- [ ] Learned quality gates
- [ ] Automatic bug fixing
- [ ] Code optimization agent
- [ ] Security audit agent

---

## Conclusion

.coder is a **production-grade multi-agent system** that demonstrates:

- Clear separation of concerns
- Robust error handling
- Transparent communication
- Human-in-the-loop design
- Extensible architecture

The key insight: **Orchestration is code, not conversation.**

By keeping the orchestrator deterministic and agents specialized, we get the best of both worlds: reliable coordination + creative generation.

---

**Questions?** Open an issue on GitHub.
