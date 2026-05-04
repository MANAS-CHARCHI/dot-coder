# Pipeline Flow Visualization

Visual guide to how the .coder pipeline works.

---

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│                         USER                                │
│                    (Terminal Input)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                             │
│                   (Python Code)                             │
│                                                             │
│  • Manages pipeline state                                   │
│  • Checks dependencies                                      │
│  • Runs quality gates                                       │
│  • Handles retries                                          │
│  • Logs events                                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────┐
              │   AGENT LOOP     │
              │  (15 steps)      │
              └──────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FINAL REPORT                             │
│              (.coder/delivery/final_report.md)              │
└─────────────────────────────────────────────────────────────┘
```

---

## Detailed Pipeline

```
START
  │
  ▼
┌─────────────────────┐
│   1. SALES AGENT    │  ← Conversation with user
│                     │  → requirements.md
│                     │  → model_selection.md
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │ CHECKPOINT 1 │  ← User approves requirements
    └──────┬───────┘
           │
           ▼
┌─────────────────────┐
│  2. MANAGER AGENT   │  ← Reads requirements
│                     │  → project_plan.md
│                     │  → task_distribution.md
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 3. ARCHITECT AGENT  │  ← Reads project plan
│                     │  → system_design.md
│                     │  → data_flow.md
│                     │  → tech_requirements.md
│                     │  → Updates memory.json
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │ CHECKPOINT 2 │  ← User approves architecture
    └──────┬───────┘
           │
           ▼
┌──────────────────────────────────────┐
│  4. DB ENGINEER    5. FRONTEND PREP  │  ← PARALLEL
│                                      │
│  → schema_plan.md   → ui_plan.md     │
│  → task_list.md     → task_list.md   │
└──────────┬───────────────────────────┘
           │
           ▼
┌─────────────────────┐
│  6. CODER (DB)      │  ← Reads DB task list
│                     │  → Writes model files
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 7. BACKEND ENGINEER │  ← Reads DB models
│                     │  → api_plan.md
│                     │  → task_list.md
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 8. CODER (BACKEND)  │  ← Reads backend task list
│                     │  → Writes API code
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 9. REVIEWER (BE)    │  ← Reviews backend code
│                     │  → review_results.md
└──────────┬──────────┘
           │
           ▼
      ┌────┴────┐
      │  PASS?  │
      └────┬────┘
           │ Yes
           ▼
┌─────────────────────┐
│ 10. TESTER (BE)     │  ← Tests backend code
│                     │  → test_results.md
│                     │  → bugs.md
└──────────┬──────────┘
           │
           ▼
      ┌────┴────┐
      │  BUGS?  │
      └────┬────┘
           │ No
           ▼
┌─────────────────────┐
│ 11. FRONTEND ENG.   │  ← Reads API plan
│                     │  → ui_plan.md
│                     │  → task_list.md
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 12. CODER (FE)      │  ← Reads frontend task list
│                     │  → Writes UI code
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 13. REVIEWER (FE)   │  ← Reviews frontend code
│                     │  → review_results.md
└──────────┬──────────┘
           │
           ▼
      ┌────┴────┐
      │  PASS?  │
      └────┬────┘
           │ Yes
           ▼
┌─────────────────────┐
│ 14. TESTER (FE)     │  ← Tests frontend code
│                     │  → test_results.md
│                     │  → bugs.md
└──────────┬──────────┘
           │
           ▼
      ┌────┴────┐
      │  BUGS?  │
      └────┬────┘
           │ No
           ▼
┌─────────────────────┐
│ 15. FINAL TESTER    │  ← Integration tests
│                     │  → final_test_results.md
└──────────┬──────────┘
           │
           ▼
    ┌──────────────┐
    │ CHECKPOINT 3 │  ← User approves delivery
    └──────┬───────┘
           │
           ▼
┌─────────────────────┐
│ 16. DELIVERY AGENT  │  ← Reads everything
│                     │  → final_report.md
└──────────┬──────────┘
           │
           ▼
         DONE ✅
```

---

## Communication Flow

```
┌──────────────┐
│    AGENT     │
└──────┬───────┘
       │
       │ reads
       ▼
┌──────────────────────────────┐
│  .coder/previous_agent/      │
│  - output files              │
└──────────────────────────────┘
       │
       │ reads
       ▼
┌──────────────────────────────┐
│  .coder/orchestrator/        │
│  - memory.json               │
└──────────────────────────────┘
       │
       │ calls
       ▼
┌──────────────────────────────┐
│      LLM API                 │
│  (Gemini / Claude)           │
└──────────────────────────────┘
       │
       │ receives
       ▼
┌──────────────────────────────┐
│     RESPONSE                 │
└──────────────────────────────┘
       │
       │ writes
       ▼
┌──────────────────────────────┐
│  .coder/current_agent/       │
│  - output files              │
└──────────────────────────────┘
       │
       │ updates (if needed)
       ▼
┌──────────────────────────────┐
│  .coder/orchestrator/        │
│  - memory.json               │
└──────────────────────────────┘
```

---

## State Management

```
┌─────────────────────────────────────────┐
│         ORCHESTRATOR                    │
└─────────────────────────────────────────┘
                  │
      ┌───────────┼───────────┐
      │           │           │
      ▼           ▼           ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│ STATE    │ │ MEMORY   │ │ EVENTS   │
│          │ │          │ │          │
│ Current  │ │ Tech     │ │ Agent    │
│ step     │ │ stack    │ │ started  │
│          │ │          │ │          │
│ Status   │ │ Conven-  │ │ Agent    │
│ per step │ │ tions    │ │ done     │
│          │ │          │ │          │
│ Retry    │ │ Model    │ │ Quality  │
│ counts   │ │ selection│ │ gate     │
│          │ │          │ │          │
│ Times    │ │ Project  │ │ Retry    │
│          │ │ metadata │ │          │
└──────────┘ └──────────┘ └──────────┘
     │             │             │
     ▼             ▼             ▼
pipeline_state  memory.json  event_log.json
```

---

## Quality Gate Flow

```
Agent completes
      │
      ▼
┌─────────────────┐
│ Quality Gate    │
│                 │
│ Check:          │
│ • Files exist   │
│ • Non-empty     │
│ • Valid format  │
└────────┬────────┘
         │
    ┌────┴────┐
    │  PASS?  │
    └────┬────┘
         │
    ┌────┴────┐
    │         │
   Yes       No
    │         │
    │         ▼
    │    ┌────────────┐
    │    │ Retry < 3? │
    │    └────┬───────┘
    │         │
    │    ┌────┴────┐
    │    │         │
    │   Yes       No
    │    │         │
    │    ▼         ▼
    │  ┌─────┐  ┌──────────┐
    │  │Retry│  │ Escalate │
    │  └──┬──┘  └──────────┘
    │     │
    │     └──────┐
    │            │
    ▼            ▼
Continue    Try Again
```

---

## Retry Logic

```
Attempt 1
   │
   ▼
Run Agent
   │
   ▼
Quality Gate
   │
   ├─ PASS → Continue
   │
   └─ FAIL
      │
      ▼
   Attempt 2
   (with feedback: "Missing: X")
      │
      ▼
   Run Agent
      │
      ▼
   Quality Gate
      │
      ├─ PASS → Continue
      │
      └─ FAIL
         │
         ▼
      Attempt 3
      (with feedback: "Still missing X. Focus ONLY on X.")
         │
         ▼
      Run Agent
         │
         ▼
      Quality Gate
         │
         ├─ PASS → Continue
         │
         └─ FAIL
            │
            ▼
         ESCALATE
         (Manual intervention needed)
```

---

## Parallel Execution

```
Architect completes
        │
        ▼
┌───────────────────────────────┐
│   Check Dependencies          │
│                               │
│   DB Engineer needs:          │
│   ✅ Architect done           │
│                               │
│   Frontend Prep needs:        │
│   ✅ Architect done           │
│                               │
│   No dependency between them  │
└───────────┬───────────────────┘
            │
            ▼
    ┌───────────────┐
    │ Run in Parallel│
    └───────┬────────┘
            │
    ┌───────┴───────┐
    │               │
    ▼               ▼
┌─────────┐   ┌─────────┐
│   DB    │   │Frontend │
│Engineer │   │  Prep   │
└────┬────┘   └────┬────┘
     │             │
     └──────┬──────┘
            │
            ▼
    Both complete
            │
            ▼
    Continue pipeline
```

---

## File Structure

```
.coder/
│
├── orchestrator/
│   ├── pipeline_state.json  ← Current state
│   ├── memory.json          ← Shared facts
│   └── event_log.json       ← Audit trail
│
├── sales/
│   ├── requirements.md
│   └── model_selection.md
│
├── manager/
│   ├── project_plan.md
│   └── task_distribution.md
│
├── architect/
│   ├── system_design.md
│   ├── data_flow.md
│   └── tech_requirements.md
│
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
│
├── coder/
│   ├── db_code/
│   │   └── [generated files]
│   ├── backend_code/
│   │   └── [generated files]
│   └── frontend_code/
│       └── [generated files]
│
├── reviewer/
│   ├── backend_review.md
│   └── frontend_review.md
│
├── tester/
│   ├── test_plan.md
│   ├── backend_test_results.md
│   ├── frontend_test_results.md
│   ├── final_test_results.md
│   └── bugs.md
│
└── delivery/
    └── final_report.md
```

---

## Agent Interaction Pattern

```
┌──────────────────────────────────────────┐
│              AGENT N                     │
│                                          │
│  1. Read inputs from Agent N-1           │
│  2. Read memory.json                     │
│  3. Call LLM with:                       │
│     - System prompt (role)               │
│     - User message (task + inputs)       │
│  4. Parse LLM response                   │
│  5. Write output files                   │
│  6. Update memory.json (if needed)       │
│  7. Return success/failure               │
└──────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────┐
│           ORCHESTRATOR                   │
│                                          │
│  1. Check quality gate                   │
│  2. If pass: continue to Agent N+1       │
│  3. If fail: retry Agent N               │
│  4. Log event                            │
│  5. Save state                           │
└──────────────────────────────────────────┘
```

---

## Human Checkpoint Pattern

```
Agent completes
      │
      ▼
Is this a checkpoint step?
      │
  ┌───┴───┐
  │       │
 No      Yes
  │       │
  │       ▼
  │   ┌─────────────────────┐
  │   │ Show checkpoint UI  │
  │   │                     │
  │   │ "Review X"          │
  │   │ "yes/no/change"     │
  │   └──────────┬──────────┘
  │              │
  │         ┌────┴────┐
  │         │  Input  │
  │         └────┬────┘
  │              │
  │         ┌────┴────┐
  │         │         │
  │        yes    no/change
  │         │         │
  │         │         ▼
  │         │    ┌─────────┐
  │         │    │  Stop   │
  │         │    │   or    │
  │         │    │  Wait   │
  │         │    └─────────┘
  │         │
  └─────────┤
            │
            ▼
      Continue
```

---

## Error Recovery

```
Pipeline running
      │
      ▼
   Crash!
      │
      ▼
State saved to disk
      │
      ▼
User runs: python main.py
      │
      ▼
Load pipeline_state.json
      │
      ▼
Find current_step
      │
      ▼
Resume from that step
      │
      ▼
Continue pipeline
```

---

This visualization shows how all the pieces fit together!
