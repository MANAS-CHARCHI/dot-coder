# Task: TESTER-AGENT
# File: agents/tester.py
# Description: Tester agent - writes and runs tests
# Author: System

from .base_agent import BaseAgent
from rich import print as rprint


class TesterAgent(BaseAgent):
    """
    Tester Agent - Writes tests, runs them, reports bugs
    """
    
    def get_system_prompt(self) -> str:
        return """You are the Tester Agent for the .coder multi-agent software factory.

Your job is to write tests, run them, and report bugs.

INPUT:
- Test cases from Engineer agent
- Code from Coder agent

OUTPUT FILES:
- .coder/tester/test_plan.md
- .coder/tester/[phase]_test_results.md
- .coder/tester/bugs.md (if bugs found)

TEST PLAN MUST INCLUDE:
- What will be tested
- Test framework used
- How to run tests

TEST RESULTS MUST INCLUDE:
- Total tests
- Passed
- Failed
- Execution time
- Coverage (if available)

BUGS.MD FORMAT (for each bug):
```
## BUG-001: [Title]

Severity: Critical / High / Medium / Low

File: path/to/file.py
Line: 45

Test: test_user_registration

Steps to Reproduce:
1. Call POST /api/v1/auth/register
2. With email "test@example.com"
3. With password "short"

Expected: 400 error "Password must be at least 8 characters"
Got: 500 error "Internal server error"

Suggested Fix:
Add password length validation before database insert
```

RULES:
- Write actual test code
- Run tests if possible (or simulate)
- Be specific about bugs
- Empty bugs.md means all tests passed

When all tests pass, output:
"All tests passing. No bugs found. bugs.md is empty."
"""

    def run(self) -> bool:
        """Run the tester agent"""
        # Determine phase
        if "backend" in self.name:
            phase = "backend"
            code_dir = "coder/backend_code"
            task_list_path = "engineer/backend/task_list.md"
            results_file = "tester/backend_test_results.md"
        elif "frontend" in self.name:
            phase = "frontend"
            code_dir = "coder/frontend_code"
            task_list_path = "engineer/frontend/task_list.md"
            results_file = "tester/frontend_test_results.md"
        elif "final" in self.name:
            phase = "final"
            code_dir = None
            task_list_path = None
            results_file = "tester/final_test_results.md"
        else:
            rprint("[red]Error: Unknown tester phase[/red]")
            return False
        
        rprint(f"\n[bold cyan]🧪 Tester Agent Starting ({phase})...[/bold cyan]\n")
        
        if phase == "final":
            # Final tester checks everything
            backend_results = self.read_file("tester/backend_test_results.md")
            frontend_results = self.read_file("tester/frontend_test_results.md")
            
            user_message = f"""Run final integration tests:

BACKEND RESULTS:
{backend_results}

FRONTEND RESULTS:
{frontend_results}

Run end-to-end tests and create final_test_results.md"""
        else:
            # Phase-specific testing
            task_list = self.read_file(task_list_path)
            
            user_message = f"""Write and run tests for this code:

TASK LIST (includes test cases):
{task_list}

MEMORY:
{self.memory}

Create:
1. test_plan.md - what you'll test
2. {results_file} - test results
3. bugs.md - any bugs found (empty if all pass)

Be thorough."""
        
        # Call LLM
        response = self.call_llm(self.get_system_prompt(), user_message)
        
        if not response:
            return False
        
        # Write results
        self.write_file("tester/test_plan.md", response)
        self.write_file(results_file, response)
        
        # Check if bugs found
        if "all tests passing" in response.lower() or "no bugs" in response.lower():
            self.write_file("tester/bugs.md", "# No Bugs Found\n\nAll tests passing.")
            rprint(f"\n[bold green]✅ All Tests Passed ({phase})[/bold green]")
        else:
            self.write_file("tester/bugs.md", response)
            rprint(f"\n[bold yellow]⚠️  Bugs Found ({phase})[/bold yellow]")
            # In production, would loop back to Coder
        
        return True
