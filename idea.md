# .coder — Multi-Agent Software Factory
## Master System Design Document — Version 2

---

## WHAT IS THIS?

A fully autonomous multi-agent pipeline that takes a user's rough idea and
delivers a complete, tested, working codebase — with no human intervention
after the initial conversation.

Every agent reads from and writes to `.coder/` — a shared memory folder.
No agent talks directly to another. They communicate through files.
One entity watches over everything — the Orchestrator.

---

## WHAT CHANGED FROM V1

- Added Orchestrator layer — manages the entire pipeline in Python code
- Added Reviewer agent — catches bad code before Tester wastes cycles
- Added shared memory (memory.json) — all agents stay consistent
- Added pipeline state (pipeline_state.json) — resume from any crash point
- Added event log — full audit trail of everything that happened
- Added parallel execution — DB and Frontend planning run simultaneously
- Added 3 human checkpoints — wrong assumptions caught early
- Added retry logic — agents get 3 attempts before escalating

---

## THE BIG PICTURE

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

---

## FOLDER STRUCTURE

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
│   │   ├── schema_plan.md
│   │   └── task_list.md
│   ├── backend/
│   │   ├── api_plan.md
│   │   └── task_list.md
│   └── frontend/
│       ├── ui_plan.md
│       └── task_list.md
├── coder/
│   ├── db_code/
│   ├── backend_code/
│   └── frontend_code/
├── reviewer/
│   └── review_results.md
├── tester/
│   ├── test_plan.md
│   ├── test_results.md
│   └── bugs.md
└── delivery/
    └── final_report.md
```

---

## THE ORCHESTRATION LAYER

The Orchestrator is NOT an LLM agent. It is Python code.
It runs the entire pipeline. Every agent is called by the Orchestrator.
No agent ever calls another agent directly.

### 1 — Pipeline State

Saved to `.coder/orchestrator/pipeline_state.json` after every step.
If pipeline crashes at step 12 of 20 — restart and resume from step 12.

```json
{
  "project_id": "proj_abc123",
  "started_at": "2026-05-04T10:00:00",
  "current_step": "backend_engineer",
  "status": "running",
  "steps": {
    "sales":             { "status": "done",    "completed_at": "..." },
    "manager":           { "status": "done",    "completed_at": "..." },
    "architect":         { "status": "done",    "completed_at": "..." },
    "db_engineer":       { "status": "done",    "completed_at": "..." },
    "coder_db":          { "status": "done",    "completed_at": "..." },
    "backend_engineer":  { "status": "running", "started_at":   "..." },
    "coder_backend":     { "status": "pending" },
    "tester_backend":    { "status": "pending" },
    "frontend_engineer": { "status": "pending" },
    "coder_frontend":    { "status": "pending" },
    "tester_frontend":   { "status": "pending" },
    "final_tester":      { "status": "pending" },
    "delivery":          { "status": "pending" }
  }
}
```

### 2 — Dependency Graph

The Orchestrator never starts an agent before its dependencies are complete.

```
sales              → no dependencies
manager            → needs: sales
architect          → needs: manager
db_engineer        → needs: architect
coder_db           → needs: db_engineer
backend_engineer   → needs: coder_db
coder_backend      → needs: backend_engineer
tester_backend     → needs: coder_backend
frontend_engineer  → needs: backend_engineer (api_plan.md)
coder_frontend     → needs: frontend_engineer
tester_frontend    → needs: coder_frontend
final_tester       → needs: tester_backend + tester_frontend
delivery           → needs: final_tester
```

### 3 — Quality Gates

After every agent finishes, Orchestrator checks the output before continuing.
Verifies: all required files exist, files are non-empty, content is correct format.

If quality gate fails:
- Retry agent up to 3 times with specific feedback on what was missing
- If still failing after 3 retries → escalate to Manager to re-plan

### 4 — Retry Logic

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

### 5 — Human Checkpoints

Pipeline pauses at 3 points and waits for user approval.

Checkpoint 1 — After Sales:
"Here is what I understood. Is this correct? (yes / no / change something)"

Checkpoint 2 — After Architect:
"Here is the system design. Happy with this? (yes / no / change something)"

Checkpoint 3 — After Final Tester:
"All tests passing. Ready to deliver? (yes / no)"

### 6 — Parallel Execution

Orchestrator runs independent agents simultaneously using Python threads.

Parallel pairs:
- DB Engineer + Frontend initial prep (both need Architect, not each other)
- Multiple Coder subtasks in same phase (writing 3 model files simultaneously)

Saves roughly 30-40% of total pipeline time.

### 7 — Event Log

Every event written to `.coder/orchestrator/event_log.json`.

```json
[
  { "time": "10:00:01", "event": "pipeline_started",  "detail": "todo app" },
  { "time": "10:00:02", "event": "agent_started",     "detail": "sales" },
  { "time": "10:02:14", "event": "agent_completed",   "detail": "sales" },
  { "time": "10:02:14", "event": "checkpoint",        "detail": "user approved" },
  { "time": "10:08:12", "event": "quality_gate_fail", "detail": "architect missing data_flow.md" },
  { "time": "10:08:12", "event": "agent_retry",       "detail": "architect retry 1/3" },
  { "time": "10:11:44", "event": "quality_gate_pass", "detail": "architect verified" },
  { "time": "10:11:44", "event": "parallel_start",    "detail": "db_engineer + frontend_prep" }
]
```

---

## SHARED MEMORY

File: `.coder/orchestrator/memory.json`

Key facts written early and read by every agent downstream.
Prevents contradictions — if Architect chose PostgreSQL, no agent later suggests MongoDB.

Who writes:
- Sales → project name, target users, out of scope
- Manager → timeline, priorities, high level tech direction
- Architect → exact framework, database, auth method, conventions
- DB Engineer → table names, primary key style
- Backend → base URL, auth header, error format

```json
{
  "project_name":   "TodoApp",
  "target_users":   "small teams",
  "out_of_scope":   ["payments", "mobile app"],
  "tech_stack": {
    "frontend":     "React 18 + Tailwind",
    "backend":      "FastAPI + Python 3.11",
    "database":     "PostgreSQL 15",
    "orm":          "SQLAlchemy 2.0",
    "auth":         "JWT Bearer tokens",
    "migrations":   "Alembic"
  },
  "conventions": {
    "primary_keys": "UUID",
    "base_api_url": "/api/v1",
    "error_format": "{ error: string, code: string }",
    "env_prefix":   "APP_"
  }
}
```

---

## AGENT 0 — ORCHESTRATOR (Python code, not LLM)

Runs the pipeline. Manages state, dependencies, retries, gates, checkpoints.
Does NOT write project files. Does NOT make technical decisions.

Core loop:
```
load pipeline_state.json
find first incomplete step

for each step:
  check dependencies → complete? proceed : wait
  log: agent_started
  call agent
  run quality gate
  if fail: retry up to 3x, then escalate
  log: agent_completed
  save pipeline_state.json
  if checkpoint: pause, ask user
  if parallel possible: thread it
```

---

## AGENT 1 — SALES AGENT

Reads: user terminal input
Writes: requirements.md, model_selection.md, memory.json (initial)

Conversation flow:
1. Greet + get the big idea
2. Ask clarifying questions ONE AT A TIME — problem, users, features, scale, timeline
3. Ask tech questions ONE AT A TIME — frontend, backend, databases, auth, third-party services
4. Confirm understanding — show summary, ask for approval
5. Model selection — show table, let user pick per agent or one for all
6. Write files + hand off

Tech questions to cover:
- Frontend preference? (React / Vue / plain HTML / no preference)
- Backend preference? (Python / Node / other / no preference)
- What kind of data? → suggests database type
- Need multiple databases? (PostgreSQL + Redis? PostgreSQL + S3?)
- Need user authentication?
- Any third-party services? (payments, email, files)

Model selection table:
| Agent           | Recommended    | Budget                |
|----------------|----------------|-----------------------|
| Manager         | Claude Opus    | Claude Sonnet         |
| Architect       | Claude Opus    | Gemini 2.5 Pro        |
| DB Engineer     | Claude Sonnet  | Gemini 2.5 Flash      |
| Backend Eng.    | Claude Sonnet  | Gemini 2.5 Flash      |
| Frontend Eng.   | Claude Sonnet  | Gemini 2.5 Flash      |
| Coder           | Claude Sonnet  | Gemini 2.5 Flash-Lite |
| Reviewer        | Claude Haiku   | Gemini 2.5 Flash-Lite |
| Tester          | Claude Haiku   | Gemini 2.5 Flash-Lite |

Rules:
- One question at a time, max 8 exchanges
- Never assume tech stack — always ask
- Never start planning — Sales gathers only

---

## AGENT 2 — MANAGER AGENT

Reads: requirements.md, model_selection.md, memory.json
Writes: project_plan.md, task_distribution.md, memory.json (tech direction)

Job: Break project into phases. Identify what runs in parallel.
Define dependencies. Set what each agent must produce.

Key addition vs V1: explicitly identifies parallel opportunities in the plan.

Handoff chain to document:
Sales → Manager → Architect → [DB Eng ‖ Frontend Prep] →
Coder(DB) → Backend Eng → Coder(BE) ↔ Tester(BE) →
Frontend Eng → Coder(FE) ↔ Tester(FE) → Final Tester → Delivery

Rules:
- No code, no low-level decisions
- Must explicitly list what can run in parallel
- Ambiguous plans cause failed builds — be explicit

---

## AGENT 3 — ARCHITECT AGENT

Reads: requirements.md, project_plan.md, memory.json
Writes: system_design.md, data_flow.md, tech_requirements.md, memory.json (all tech decisions)

Key addition vs V1: writes ALL decisions to memory.json so downstream agents never contradict.

Must decide and document:
- Exact framework + version for frontend, backend
- Exact database(s) + ORM + migration tool
- Auth method
- Folder structure for each layer
- Every major data flow (user registers, user logs in, etc.)
- All environment variables needed
- Exact dependency versions

Rules:
- ONE choice per decision — never "you could use X or Y"
- Justify every decision in one sentence
- Write exact versions, not "latest"
- Junior developer must be able to follow this design

---

## AGENT 4 — DB ENGINEER AGENT

Reads: system_design.md, data_flow.md, memory.json
Writes: schema_plan.md, task_list.md, memory.json (table names, conventions)

Designs: every table, every field, every type, every constraint, every index, every relationship.
Zero ambiguity — Coder must write models with no questions.

Task list format for Coder:
- Exact file path
- Exact fields with types and constraints
- Reference to schema_plan.md section
- One task per model file

---

## AGENT 5 — BACKEND ENGINEER AGENT

Reads: system_design.md, schema_plan.md, memory.json
Writes: api_plan.md, task_list.md, memory.json (API conventions)

Designs: every endpoint, exact request/response shapes, HTTP status codes, error formats.
Writes coding tasks for Coder AND test cases for Tester.
Manages the Coder ↔ Tester bug loop until bugs.md is empty.

Every endpoint must have:
- Purpose
- Auth required (yes/no)
- Request body (exact JSON shape)
- All possible responses with status codes
- At least 3 test cases

---

## AGENT 6 — FRONTEND ENGINEER AGENT

Reads: system_design.md, api_plan.md, memory.json
Writes: ui_plan.md, task_list.md

Designs: every page, every component, every API call mapped to every page.
Writes coding tasks for Coder AND integration test cases for Tester.

Every page must have:
- Route and purpose
- Components used
- Exact API calls (method + endpoint + when)
- State variables with types
- On success behaviour
- On error behaviour

---

## AGENT 7 — REVIEWER AGENT (NEW)

Reads: task list Coder just completed, code files Coder just wrote
Writes: reviewer/review_results.md

Purpose: Fast quality gate between Coder and Tester.
Not a deep review — catches obvious problems that will definitely cause failures.

Checks on every file:
1. COMPLETENESS — no missing functions, no unfinished placeholders, no skipped tasks
2. CONSISTENCY — field names match schema_plan, endpoints match api_plan, imports match memory.json tech stack
3. OBVIOUS ERRORS — syntax errors, imports that don't exist, functions called but not defined, missing env var reads
4. STANDARDS — file header present, error handling present, no hardcoded secrets

Output:
- PASS → "All files pass. Ready for testing."
- FAIL → list every issue with file + line, what is wrong, what Coder must fix

After Coder fixes → Reviewer re-checks before passing to Tester.

---

## AGENT 8 — CODER AGENT

Reads: assigned task list, memory.json, reviewer/review_results.md (if fixing)
Writes: actual code files to .coder/coder/[db|backend|frontend]_code/

Key addition vs V1: reads memory.json first every session to use correct tech stack.

File header on every file:
```
# Task: [TASK-ID]
# File: [filename]
# Description: [one sentence]
# Author: Coder Agent (.coder)
```

Rules:
- Complete files only — no placeholders or TODOs
- If unclear: add comment AMBIGUOUS: [what] and make a reasonable choice, never stop
- After every file: "Task [ID] complete. File: [path]. Lines: [N]."

---

## AGENT 9 — TESTER AGENT

Reads: test cases from Engineer task list, code from .coder/coder/
Writes: test_plan.md, test_results.md, bugs.md

Bug report format (every bug):
- Title
- Severity: Critical / High / Medium / Low
- File + line number
- Test that caught it
- Steps to reproduce (numbered)
- Expected vs got
- Suggested fix (if obvious)

When all pass: "All tests passing. No bugs found. bugs.md is empty."

---

## AGENT 10 — DELIVERY AGENT

Reads: everything in .coder/
Writes: delivery/final_report.md

Confirms bugs.md is empty before writing report.
If bugs remain → flags at top of report with warning.

Report must include:
- Status (all passing or known issues)
- What was built (summary)
- All files delivered with descriptions
- Exact commands to install, configure, migrate, seed, start
- Test summary
- Out of scope items
- Suggested next steps

---

## KEY PRINCIPLES

1. Orchestrator runs everything — agents never call each other
2. Files are the communication bus — agents share info only through .md files
3. Memory.json is the shared brain — early decisions respected by all
4. Quality gates before every handoff — nothing broken passes downstream
5. Reviewer catches issues before Tester — saves tokens and time
6. Parallel where possible — cuts pipeline time 30-40%
7. Human checkpoints at critical moments — wrong assumptions caught early
8. Resume from any step — pipeline_state.json makes crashes recoverable
9. Event log is the audit trail — replay exactly what happened
10. Retry before escalate — 3 chances before Manager is called in