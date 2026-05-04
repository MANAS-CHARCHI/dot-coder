# Task: ORCHESTRATOR
# File: orchestrator.py
# Description: Main orchestrator that manages the entire multi-agent pipeline
# Author: System

import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


class Orchestrator:
    """
    The Orchestrator manages the entire pipeline.
    It is NOT an LLM agent - it's Python code that coordinates all agents.
    """
    
    def __init__(self):
        self.base_path = Path(".coder")
        self.orchestrator_path = self.base_path / "orchestrator"
        self.state_file = self.orchestrator_path / "pipeline_state.json"
        self.memory_file = self.orchestrator_path / "memory.json"
        self.event_log_file = self.orchestrator_path / "event_log.json"
        
        self.state = self._load_state()
        self.memory = self._load_memory()
        self.events = self._load_events()
        
        # Add any missing steps from dependencies to state immediately
        self._ensure_all_steps_exist()
        
        # Dependency graph - defines what each step needs before it can run
        self.dependencies = {
            "sales": [],
            "manager": ["sales"],
            "architect": ["manager"],
            "setup": ["architect"],          # generates requirements.txt, package.json, etc.
            "db_engineer": ["architect"],
            "coder_db": ["db_engineer"],
            "backend_engineer": ["coder_db"],
            "coder_backend": ["backend_engineer"],
            "reviewer_backend": ["coder_backend"],
            "tester_backend": ["reviewer_backend"],
            "frontend_engineer": ["backend_engineer"],
            "coder_frontend": ["frontend_engineer"],
            "reviewer_frontend": ["coder_frontend"],
            "tester_frontend": ["reviewer_frontend"],
            "final_tester": ["tester_backend", "tester_frontend"],
            "delivery": ["final_tester"]
        }
        
        # Quality gates - what files each step must produce
        self.quality_gates = {
            "sales": [
                "sales/requirements.md",
                "sales/model_selection.md"
            ],
            "manager": [
                "manager/project_plan.md",
                "manager/task_distribution.md"
            ],
            "architect": [
                "architect/system_design.md",
                "architect/data_flow.md",
                "architect/tech_requirements.md"
            ],
            "setup": [
                "setup/backend/requirements.txt",
                "setup/frontend/package.json",
                "setup/docker-compose.yml",
                "setup/backend/.env.example",
                "setup/backend/alembic.ini",
                "setup/frontend/vite.config.js",
                "setup/.gitignore",
                "setup/README.md"
            ],
            "db_engineer": [
                "engineer/database/schema_plan.md",
                "engineer/database/task_list.md"
            ],
            "coder_db": [],
            "backend_engineer": [
                "engineer/backend/api_plan.md",
                "engineer/backend/task_list.md"
            ],
            "coder_backend": [],
            "reviewer_backend": ["reviewer/backend_review.md"],
            "tester_backend": [
                "tester/backend_test_results.md"
            ],
            "frontend_engineer": [
                "engineer/frontend/ui_plan.md",
                "engineer/frontend/task_list.md"
            ],
            "coder_frontend": [],
            "reviewer_frontend": ["reviewer/frontend_review.md"],
            "tester_frontend": [
                "tester/frontend_test_results.md"
            ],
            "final_tester": [
                "tester/final_test_results.md"
            ],
            "delivery": [
                "delivery/final_report.md"
            ]
        }
    
    def _load_state(self) -> dict:
        """Load pipeline state from disk"""
        if self.state_file.exists():
            return json.loads(self.state_file.read_text())
        return {}
    
    def _ensure_all_steps_exist(self):
        """Add any missing steps from dependency graph to state"""
        if not self.state or "steps" not in self.state:
            return
            
        steps = list(self.dependencies.keys())
        changed = False
        
        for step in steps:
            if step not in self.state["steps"]:
                self.state["steps"][step] = {
                    "status": "pending",
                    "started_at": None,
                    "completed_at": None,
                    "retries": 0
                }
                rprint(f"[dim]➕ Added missing step: {step}[/dim]")
                changed = True
        
        if changed:
            self._save_state()
    
    def _save_state(self):
        """Save pipeline state to disk"""
        self.orchestrator_path.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(self.state, indent=2))
    
    def _load_memory(self) -> dict:
        """Load shared memory from disk"""
        if self.memory_file.exists():
            return json.loads(self.memory_file.read_text())
        return {}
    
    def _save_memory(self):
        """Save shared memory to disk"""
        self.orchestrator_path.mkdir(parents=True, exist_ok=True)
        self.memory_file.write_text(json.dumps(self.memory, indent=2))
    
    def _load_events(self) -> list:
        """Load event log from disk"""
        if self.event_log_file.exists():
            return json.loads(self.event_log_file.read_text())
        return []
    
    def _log_event(self, event: str, detail: str):
        """Log an event to the event log"""
        entry = {
            "time": datetime.now().isoformat(),
            "event": event,
            "detail": detail
        }
        self.events.append(entry)
        self.orchestrator_path.mkdir(parents=True, exist_ok=True)
        self.event_log_file.write_text(json.dumps(self.events, indent=2))
        
        # Also print to console
        rprint(f"[dim]📝 {event}: {detail}[/dim]")
    
    def initialize_pipeline(self, project_name: str):
        """Initialize a new pipeline run"""
        project_id = f"proj_{uuid.uuid4().hex[:8]}"
        
        self.state = {
            "project_id": project_id,
            "project_name": project_name,
            "started_at": datetime.now().isoformat(),
            "current_step": None,
            "status": "running",
            "steps": {
                step: {
                    "status": "pending",
                    "started_at": None,
                    "completed_at": None,
                    "retries": 0
                }
                for step in self.dependencies.keys()
            }
        }
        
        # Initialize memory if it doesn't exist
        if not self.memory or not self.memory.get("project_name"):
            from llm_call import DEFAULT_MODEL
            self.memory = {
                "project_name": project_name,
                "target_users": None,
                "out_of_scope": [],
                "tech_stack": {
                    "frontend": None,
                    "backend": None,
                    "database": None,
                    "orm": None,
                    "auth": None,
                    "migrations": None
                },
                "conventions": {
                    "primary_keys": None,
                    "base_api_url": None,
                    "error_format": None,
                    "env_prefix": None
                },
                "model_selection": {
                    "sales": DEFAULT_MODEL
                }
            }
            self._save_memory()
        
        self._save_state()
        self._log_event("pipeline_started", project_name)
        
        rprint(Panel(
            f"[bold green]Pipeline Initialized[/bold green]\n"
            f"Project: {project_name}\n"
            f"ID: {project_id}",
            title="🚀 Orchestrator"
        ))
    
    def can_run_step(self, step: str) -> bool:
        """Check if a step's dependencies are all complete"""
        deps = self.dependencies.get(step, [])
        for dep in deps:
            if self.state["steps"][dep]["status"] != "done":
                return False
        return True
    
    def check_quality_gate(self, step: str) -> tuple[bool, List[str]]:
        """
        Check if a step produced all required files.
        Returns (passed, missing_files)
        """
        required_files = self.quality_gates.get(step, [])
        missing = []
        
        for file_path in required_files:
            full_path = self.base_path / file_path
            if not full_path.exists():
                missing.append(file_path)
            elif full_path.stat().st_size == 0:
                missing.append(f"{file_path} (empty)")
        
        return len(missing) == 0, missing
    
    def run_agent(self, agent_name: str, retry_count: int = 0) -> bool:
        """
        Run a single agent. Returns True if successful, False if failed.
        This is a placeholder - actual implementation will import and call agent modules.
        """
        from agents import run_agent
        
        self.state["current_step"] = agent_name
        self.state["steps"][agent_name]["status"] = "running"
        self.state["steps"][agent_name]["started_at"] = datetime.now().isoformat()
        self._save_state()
        
        self._log_event("agent_started", agent_name)
        
        try:
            # Call the actual agent
            success = run_agent(agent_name, self.memory, retry_count)
            
            if success:
                self.state["steps"][agent_name]["status"] = "done"
                self.state["steps"][agent_name]["completed_at"] = datetime.now().isoformat()
                self._save_state()
                self._log_event("agent_completed", agent_name)
                return True
            else:
                return False
                
        except Exception as e:
            rprint(f"[red]❌ Agent {agent_name} crashed: {e}[/red]")
            self._log_event("agent_error", f"{agent_name}: {str(e)}")
            return False
    
    def retry_agent(self, agent_name: str, missing_files: List[str]) -> bool:
        """Retry an agent up to 3 times with specific feedback"""
        retry_count = self.state["steps"][agent_name]["retries"]
        
        if retry_count >= 3:
            rprint(f"[red]❌ Agent {agent_name} failed after 3 retries[/red]")
            self._log_event("agent_failed", f"{agent_name} exhausted retries")
            return False
        
        retry_count += 1
        self.state["steps"][agent_name]["retries"] = retry_count
        self._save_state()
        
        feedback = f"Retry {retry_count}/3: Missing files: {', '.join(missing_files)}"
        rprint(f"[yellow]🔄 {feedback}[/yellow]")
        self._log_event("agent_retry", f"{agent_name} - {feedback}")
        
        # Run agent again with retry context
        return self.run_agent(agent_name, retry_count)
    
    def human_checkpoint(self, checkpoint_name: str, message: str) -> bool:
        """
        Pause pipeline and wait for human approval.
        Returns True if approved, False if rejected.
        """
        self._log_event("checkpoint", checkpoint_name)
        
        console.print(Panel(
            f"[bold yellow]{message}[/bold yellow]\n\n"
            f"Type 'yes' to continue, 'no' to stop, or 'change' to modify:",
            title=f"🛑 Checkpoint: {checkpoint_name}"
        ))
        
        while True:
            response = input("> ").strip().lower()
            if response == "yes":
                self._log_event("checkpoint_approved", checkpoint_name)
                return True
            elif response == "no":
                self._log_event("checkpoint_rejected", checkpoint_name)
                return False
            elif response == "change":
                console.print("[yellow]Please make your changes and type 'yes' when ready[/yellow]")
            else:
                console.print("[red]Please type 'yes', 'no', or 'change'[/red]")
    
    def run_parallel(self, steps: List[str]) -> bool:
        """Run multiple independent steps in parallel"""
        self._log_event("parallel_start", ", ".join(steps))
        
        with ThreadPoolExecutor(max_workers=len(steps)) as executor:
            futures = {
                executor.submit(self.run_agent, step): step
                for step in steps
            }
            
            results = {}
            for future in as_completed(futures):
                step = futures[future]
                try:
                    results[step] = future.result()
                except Exception as e:
                    rprint(f"[red]Parallel execution error for {step}: {e}[/red]")
                    results[step] = False
        
        self._log_event("parallel_complete", ", ".join(steps))
        return all(results.values())
    
    def run_pipeline(self):
        """Main pipeline execution loop"""
        
        # Get all steps in order
        steps = list(self.dependencies.keys())
        
        # Ensure all steps from dependency graph exist in state.
        # This handles new steps added after a pipeline was already saved to disk.
        changed = False
        for step in steps:
            if step not in self.state["steps"]:
                self.state["steps"][step] = {
                    "status": "pending",
                    "started_at": None,
                    "completed_at": None,
                    "retries": 0
                }
                rprint(f"[dim]➕ Added missing step to state: {step}[/dim]")
                changed = True
        if changed:
            self._save_state()
        
        # Keep track of which steps we've attempted
        max_iterations = len(steps) * 2  # Prevent infinite loops
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            made_progress = False
            
            for step in steps:
                # Check if already done (resume case)
                if self.state["steps"][step]["status"] == "done":
                    continue
                
                # Check if currently running (shouldn't happen, but safety check)
                if self.state["steps"][step]["status"] == "running":
                    continue
                
                # Check dependencies
                if not self.can_run_step(step):
                    continue
                
                # This step is ready to run!
                made_progress = True
                
                # Run the agent
                rprint(f"\n[bold cyan]▶️  Running: {step}[/bold cyan]")
                success = self.run_agent(step, 0)
                
                if not success:
                    rprint(f"[red]❌ Pipeline stopped at {step}[/red]")
                    self.state["status"] = "failed"
                    self._save_state()
                    return False
                
                # Quality gate check
                passed, missing = self.check_quality_gate(step)
                
                if not passed:
                    rprint(f"[yellow]⚠️  Quality gate failed for {step}[/yellow]")
                    self._log_event("quality_gate_fail", f"{step}: {', '.join(missing)}")
                    
                    # Retry up to 3 times
                    retry_success = self.retry_agent(step, missing)
                    
                    if not retry_success:
                        rprint(f"[red]❌ Pipeline stopped - {step} failed quality gate[/red]")
                        self.state["status"] = "failed"
                        self._save_state()
                        return False
                    
                    # Re-check quality gate after retry
                    passed, missing = self.check_quality_gate(step)
                    if not passed:
                        rprint(f"[red]❌ Quality gate still failing after retries[/red]")
                        self.state["status"] = "failed"
                        self._save_state()
                        return False
                
                self._log_event("quality_gate_pass", step)
                
                # Human checkpoints
                if step == "sales":
                    if not self.human_checkpoint(
                        "Requirements Review",
                        "Review the requirements in .coder/sales/requirements.md"
                    ):
                        self.state["status"] = "cancelled"
                        self._save_state()
                        return False
                
                elif step == "architect":
                    if not self.human_checkpoint(
                        "Architecture Review",
                        "Review the system design in .coder/architect/"
                    ):
                        self.state["status"] = "cancelled"
                        self._save_state()
                        return False
                
                elif step == "final_tester":
                    if not self.human_checkpoint(
                        "Final Approval",
                        "All tests passing. Ready to deliver?"
                    ):
                        self.state["status"] = "cancelled"
                        self._save_state()
                        return False
            
            # Check if all steps are done
            all_done = all(
                self.state["steps"][step]["status"] == "done"
                for step in steps
            )
            
            if all_done:
                break
            
            # If we didn't make any progress this iteration, something is wrong
            if not made_progress:
                pending_steps = [
                    step for step in steps
                    if self.state["steps"][step]["status"] == "pending"
                ]
                rprint(f"[red]❌ Pipeline stuck. Pending steps: {', '.join(pending_steps)}[/red]")
                self.state["status"] = "failed"
                self._save_state()
                return False
        
        # Pipeline complete
        self.state["status"] = "completed"
        self.state["completed_at"] = datetime.now().isoformat()
        self._save_state()
        self._log_event("pipeline_completed", "All steps done")
        
        rprint(Panel(
            "[bold green]✅ Pipeline Complete![/bold green]\n"
            f"Check .coder/delivery/final_report.md for results",
            title="🎉 Success"
        ))
        
        return True
    
    def print_status(self):
        """Print current pipeline status"""
        table = Table(title="Pipeline Status")
        table.add_column("Step", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Retries", style="yellow")
        
        for step, info in self.state["steps"].items():
            status_emoji = {
                "pending": "⏳",
                "running": "▶️",
                "done": "✅",
                "failed": "❌"
            }.get(info["status"], "❓")
            
            table.add_row(
                step,
                f"{status_emoji} {info['status']}",
                str(info["retries"])
            )
        
        console.print(table)


def main():
    """Entry point for orchestrator"""
    orchestrator = Orchestrator()
    
    # Check if resuming
    if orchestrator.state.get("status") == "running":
        console.print("[yellow]Found existing pipeline. Resuming...[/yellow]")
        orchestrator.print_status()
    else:
        # New pipeline
        project_name = input("Enter project name: ").strip()
        if not project_name:
            project_name = "New Project"
        orchestrator.initialize_pipeline(project_name)
    
    # Run the pipeline
    orchestrator.run_pipeline()


if __name__ == "__main__":
    main()
