# Task: DELIVERY-AGENT
# File: agents/delivery.py
# Description: Delivery agent - creates final report
# Author: System

from .base_agent import BaseAgent
from rich import print as rprint


class DeliveryAgent(BaseAgent):
    """
    Delivery Agent - Creates final report and confirms delivery
    """
    
    def get_system_prompt(self) -> str:
        return """You are the Delivery Agent for the .coder multi-agent software factory.

Your job is to create a comprehensive final report.

INPUT:
- Everything in .coder/

OUTPUT:
- .coder/delivery/final_report.md

FINAL REPORT MUST INCLUDE:

1. STATUS
   - All passing OR known issues
   - If bugs.md not empty, flag at top with warning

2. WHAT WAS BUILT
   - Project summary (2-3 paragraphs)
   - Features implemented
   - Tech stack used

3. FILES DELIVERED
   - List all code files with descriptions
   - Organized by layer (database, backend, frontend)

4. SETUP INSTRUCTIONS
   - Exact commands to install dependencies
   - How to configure (env vars)
   - How to run migrations
   - How to seed data (if applicable)
   - How to start the application

5. TEST SUMMARY
   - Total tests written
   - Pass rate
   - Coverage (if available)

6. OUT OF SCOPE
   - What was explicitly not built
   - From original requirements

7. SUGGESTED NEXT STEPS
   - What to build next
   - Improvements to consider
   - Known limitations

RULES:
- Check bugs.md first - if not empty, flag prominently
- Be comprehensive but concise
- Include exact commands (copy-pasteable)
- Assume reader is a developer who knows nothing about this project

Output as detailed markdown."""

    def run(self) -> bool:
        """Run the delivery agent"""
        rprint("\n[bold cyan]📦 Delivery Agent Starting...[/bold cyan]\n")
        
        # Read all key files
        requirements = self.read_file("sales/requirements.md")
        system_design = self.read_file("architect/system_design.md")
        bugs = self.read_file("tester/bugs.md")
        final_tests = self.read_file("tester/final_test_results.md")
        
        # Check for bugs
        has_bugs = bugs and "no bugs" not in bugs.lower()
        
        # Create prompt
        user_message = f"""Create a comprehensive final report:

REQUIREMENTS:
{requirements}

SYSTEM DESIGN:
{system_design}

BUGS:
{bugs}

FINAL TEST RESULTS:
{final_tests}

MEMORY:
{self.memory}

Create final_report.md with all sections:
- Status (flag if bugs exist)
- What was built
- Files delivered
- Setup instructions
- Test summary
- Out of scope
- Next steps

Be thorough and professional."""

        # Call LLM
        response = self.call_llm(self.get_system_prompt(), user_message)
        
        if not response:
            return False
        
        # Add warning if bugs exist
        if has_bugs:
            warning = """# ⚠️ WARNING: KNOWN ISSUES

This delivery has known bugs. See bugs.md for details.

---

"""
            response = warning + response
        
        # Write final report
        self.write_file("delivery/final_report.md", response)
        
        rprint("\n[bold green]✅ Delivery Agent Complete[/bold green]")
        rprint(f"\n[bold cyan]📄 Final report: .coder/delivery/final_report.md[/bold cyan]")
        
        return True
