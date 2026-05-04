# Task: MANAGER-AGENT
# File: agents/manager.py
# Description: Manager agent - creates project plan and task distribution
# Author: System

from .base_agent import BaseAgent
from rich import print as rprint


class ManagerAgent(BaseAgent):
    """
    Manager Agent - Breaks project into phases and identifies parallel work
    """
    
    def get_system_prompt(self) -> str:
        return """You are the Manager Agent for the .coder multi-agent software factory.

Your job is to read the requirements and create a detailed project plan.

INPUT FILES:
- .coder/sales/requirements.md

OUTPUT FILES YOU MUST CREATE:
- .coder/manager/project_plan.md
- .coder/manager/task_distribution.md

PROJECT PLAN MUST INCLUDE:
1. Project overview (1 paragraph)
2. High-level tech stack direction (frontend, backend, database)
3. Major phases (Database → Backend → Frontend)
4. What can run in parallel (DB Engineer + Frontend Prep)
5. Dependencies between phases
6. Timeline estimate

TASK DISTRIBUTION MUST INCLUDE:
1. Exact handoff chain: Sales → Manager → Architect → [DB Eng ‖ Frontend Prep] → etc.
2. What each agent must produce
3. Which agents can run in parallel
4. Critical path

RULES:
- No code, no low-level decisions
- Be explicit about what runs in parallel
- Ambiguous plans cause failed builds
- Think like a project manager, not an engineer

Output both files as markdown with clear sections."""

    def run(self) -> bool:
        """Run the manager agent"""
        rprint("\n[bold cyan]📋 Manager Agent Starting...[/bold cyan]\n")
        
        # Read requirements
        requirements = self.read_file("sales/requirements.md")
        if not requirements:
            rprint("[red]Error: requirements.md not found[/red]")
            return False
        
        # Create prompt
        user_message = f"""Read these requirements and create a project plan:

{requirements}

Create two files:
1. project_plan.md - overall project plan with phases and timeline
2. task_distribution.md - detailed agent handoff chain and parallel work

Be specific and detailed. Think through the entire pipeline."""

        # Call LLM
        response = self.call_llm(self.get_system_prompt(), user_message)
        
        if not response:
            return False
        
        # Parse response and extract files
        # For now, write the full response to both files
        # In production, would parse markdown sections
        
        self.write_file("manager/project_plan.md", response)
        self.write_file("manager/task_distribution.md", response)
        
        rprint("\n[bold green]✅ Manager Agent Complete[/bold green]")
        return True
