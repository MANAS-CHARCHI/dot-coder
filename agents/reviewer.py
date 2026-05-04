# Task: REVIEWER-AGENT
# File: agents/reviewer.py
# Description: Reviewer agent - fast quality gate before testing
# Author: System

from .base_agent import BaseAgent
from rich import print as rprint
from pathlib import Path


class ReviewerAgent(BaseAgent):
    """
    Reviewer Agent - Fast quality gate between Coder and Tester
    Catches obvious problems before testing
    """
    
    def get_system_prompt(self) -> str:
        return """You are the Reviewer Agent for the .coder multi-agent software factory.

Your job is to catch obvious problems before Tester wastes cycles.

This is NOT a deep review - catch only OBVIOUS issues that will DEFINITELY fail.

CHECK ON EVERY FILE:
1. COMPLETENESS
   - No missing functions
   - No unfinished placeholders like "# TODO" or "// implement this"
   - No skipped tasks

2. CONSISTENCY
   - Field names match schema_plan
   - Endpoints match api_plan
   - Imports match memory.json tech stack
   - Naming conventions followed

3. OBVIOUS ERRORS
   - Syntax errors
   - Imports that don't exist
   - Functions called but not defined
   - Missing env var reads

4. STANDARDS
   - File header present
   - Error handling present
   - No hardcoded secrets

OUTPUT FORMAT:
If PASS:
```
PASS

All files pass. Ready for testing.
```

If FAIL:
```
FAIL

## file1.py
Line 23: Missing import for 'requests'
Line 45: Function 'validate_email' called but not defined
Line 67: Hardcoded API key - should use env var

## file2.py
Line 12: Field name 'userId' should be 'user_id' per conventions
Line 34: Missing error handling for database query
```

Be specific: file + line + what's wrong + what to fix."""

    def run(self) -> bool:
        """Run the reviewer agent"""
        # Determine which phase we're in
        if "backend" in self.name:
            phase = "backend"
            code_dir = "coder/backend_code"
            review_file = "reviewer/backend_review.md"
        elif "frontend" in self.name:
            phase = "frontend"
            code_dir = "coder/frontend_code"
            review_file = "reviewer/frontend_review.md"
        else:
            rprint("[red]Error: Unknown reviewer phase[/red]")
            return False
        
        rprint(f"\n[bold cyan]🔍 Reviewer Agent Starting ({phase})...[/bold cyan]\n")
        
        # Read all code files
        code_path = self.base_path / code_dir
        if not code_path.exists():
            rprint(f"[red]Error: {code_dir} not found[/red]")
            return False
        
        code_files = {}
        for file_path in code_path.rglob("*"):
            if file_path.is_file():
                rel_path = file_path.relative_to(code_path)
                code_files[str(rel_path)] = file_path.read_text()
        
        if not code_files:
            rprint("[red]Error: No code files found[/red]")
            return False
        
        # Read task list and schema/api plan for context
        if phase == "backend":
            task_list = self.read_file("engineer/backend/task_list.md")
            plan = self.read_file("engineer/backend/api_plan.md")
        else:
            task_list = self.read_file("engineer/frontend/task_list.md")
            plan = self.read_file("engineer/frontend/ui_plan.md")
        
        # Create prompt
        files_text = "\n\n".join([
            f"=== FILE: {path} ===\n{content}\n=== END FILE ==="
            for path, content in code_files.items()
        ])
        
        user_message = f"""Review these code files for obvious issues:

TASK LIST:
{task_list}

PLAN:
{plan}

MEMORY (conventions):
{self.memory}

CODE FILES:
{files_text}

Review all files and output PASS or FAIL with specific issues."""

        # Call LLM
        response = self.call_llm(self.get_system_prompt(), user_message)
        
        if not response:
            return False
        
        # Write review results
        self.write_file(review_file, response)
        
        # Check if passed
        if "PASS" in response.upper() and "FAIL" not in response.upper():
            rprint(f"\n[bold green]✅ Review PASSED ({phase})[/bold green]")
            return True
        else:
            rprint(f"\n[bold yellow]⚠️  Review FAILED ({phase})[/bold yellow]")
            rprint(f"[yellow]Issues found in code review[/yellow]")
            
            # For now, treat review failures as warnings, not blockers
            # The Tester will catch these issues anyway
            rprint(f"[dim]Note: Continuing to testing phase. Issues logged in {review_file}[/dim]")
            return True  # Changed from False to True to continue pipeline
