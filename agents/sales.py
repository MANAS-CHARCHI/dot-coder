# Task: SALES-AGENT
# File: agents/sales.py
# Description: Sales agent - gathers requirements from user
# Author: System

from rich import print as rprint
from rich.console import Console
from rich.table import Table
from .base_agent import BaseAgent

console = Console()


class SalesAgent(BaseAgent):
    """
    Sales Agent - Gathers requirements through conversation
    Asks questions ONE AT A TIME
    Writes requirements.md and model_selection.md
    """
    
    def get_system_prompt(self) -> str:
        return """You are the Sales Agent for the .coder multi-agent software factory.

Your job is to gather requirements from the user through a natural conversation.

RULES:
1. Ask ONE question at a time - never multiple questions in one message
2. Be friendly and conversational
3. After each answer, acknowledge it briefly and ask the next question
4. Never assume - always ask
5. Keep questions simple and clear
6. Maximum 8 exchanges total

CONVERSATION FLOW:
1. Greet and ask: What do you want to build?
2. Ask: Who will use this? (target users)
3. Ask: What are the main features?
4. Ask: Any features explicitly OUT OF SCOPE?
5. Ask: Expected scale? (users, data volume)
6. Ask: Frontend preference? (React / Vue / plain HTML / no preference)
7. Ask: Backend preference? (Python / Node / other / no preference)
8. Ask: What kind of data will you store? (suggests database type)
9. Ask: Need user authentication?
10. Ask: Any third-party services? (payments, email, file storage)

After gathering info, summarize everything and ask for confirmation.

When user confirms, respond with: REQUIREMENTS_COMPLETE

Keep responses short - 1-2 sentences max per message."""

    def run(self) -> bool:
        """Run the sales conversation"""
        rprint("\n[bold cyan]💼 Sales Agent Starting...[/bold cyan]\n")
        
        # Start conversation
        system_prompt = self.get_system_prompt()
        
        # Initial greeting
        response = self.call_llm(
            system_prompt,
            "Start the requirements gathering conversation. Greet the user and ask the first question."
        )
        
        if not response:
            return False
        
        console.print(f"[cyan]Sales Agent:[/cyan] {response}")
        
        # Conversation loop
        requirements_data = {
            "project_name": None,
            "description": None,
            "target_users": None,
            "features": [],
            "out_of_scope": [],
            "scale": None,
            "frontend_pref": None,
            "backend_pref": None,
            "data_type": None,
            "auth_needed": None,
            "third_party": []
        }
        
        conversation_count = 0
        max_exchanges = 10
        
        while conversation_count < max_exchanges:
            # Get user input
            user_input = input("\nYou: ").strip()
            
            if not user_input:
                console.print("[yellow]Please provide an answer[/yellow]")
                continue
            
            conversation_count += 1
            
            # Send to LLM
            response = self.call_llm(
                system_prompt,
                user_input
            )
            
            if not response:
                return False
            
            console.print(f"\n[cyan]Sales Agent:[/cyan] {response}")
            
            # Check if done
            if "REQUIREMENTS_COMPLETE" in response:
                break
        
        # Now ask for model selection
        rprint("\n[bold cyan]📊 Model Selection[/bold cyan]\n")
        
        model_table = Table(title="Recommended Models")
        model_table.add_column("Agent", style="cyan")
        model_table.add_column("Recommended", style="green")
        model_table.add_column("Budget", style="yellow")
        
        model_table.add_row("Manager", "Llama 3.1 8B", "Gemini 2.5 Flash-Lite")
        model_table.add_row("Architect", "Llama 3.1 8B", "Gemini 2.5 Flash-Lite")
        model_table.add_row("DB Engineer", "Llama 3.1 8B", "Gemini 2.5 Flash-Lite")
        model_table.add_row("Backend Eng.", "Llama 3.1 8B", "Gemini 2.5 Flash-Lite")
        model_table.add_row("Frontend Eng.", "Llama 3.1 8B", "Gemini 2.5 Flash-Lite")
        model_table.add_row("Coder", "Llama 3.1 8B", "Gemini 2.5 Flash-Lite")
        model_table.add_row("Reviewer", "Llama 3.1 8B", "Gemini 2.5 Flash-Lite")
        model_table.add_row("Tester", "Llama 3.1 8B", "Gemini 2.5 Flash-Lite")
        
        console.print(model_table)
        
        console.print("\n[yellow]Choose:[/yellow]")
        console.print("1. Use NVIDIA Llama 3.1 8B for all (recommended, free)")
        console.print("2. Use Gemini 2.5 Flash-Lite for all (free)")
        console.print("3. Mix: NVIDIA for planning, Gemini for coding")
        
        choice = input("\nYour choice (1/2/3): ").strip()
        
        model_selection = {}
        if choice == "1":
            # All use NVIDIA
            model_selection = {agent: "meta/llama-3.1-8b-instruct" for agent in [
                "manager", "architect", "db_engineer", "backend_engineer",
                "frontend_engineer", "coder_db", "coder_backend", "coder_frontend",
                "reviewer_backend", "reviewer_frontend", "tester_backend",
                "tester_frontend", "final_tester", "delivery"
            ]}
        elif choice == "2":
            # All use Gemini
            model_selection = {agent: "gemini-2.5-flash-lite" for agent in [
                "manager", "architect", "db_engineer", "backend_engineer",
                "frontend_engineer", "coder_db", "coder_backend", "coder_frontend",
                "reviewer_backend", "reviewer_frontend", "tester_backend",
                "tester_frontend", "final_tester", "delivery"
            ]}
        else:
            # Mix: NVIDIA for planning, Gemini for coding
            model_selection = {
                "manager": "meta/llama-3.1-8b-instruct",
                "architect": "meta/llama-3.1-8b-instruct",
                "db_engineer": "meta/llama-3.1-8b-instruct",
                "backend_engineer": "meta/llama-3.1-8b-instruct",
                "frontend_engineer": "meta/llama-3.1-8b-instruct",
                "coder_db": "gemini-2.5-flash-lite",
                "coder_backend": "gemini-2.5-flash-lite",
                "coder_frontend": "gemini-2.5-flash-lite",
                "reviewer_backend": "meta/llama-3.1-8b-instruct",
                "reviewer_frontend": "meta/llama-3.1-8b-instruct",
                "tester_backend": "gemini-2.5-flash-lite",
                "tester_frontend": "gemini-2.5-flash-lite",
                "final_tester": "meta/llama-3.1-8b-instruct",
                "delivery": "meta/llama-3.1-8b-instruct"
            }
        
        # Write requirements.md
        requirements_md = self._generate_requirements_doc()
        self.write_file("sales/requirements.md", requirements_md)
        
        # Write model_selection.md
        model_selection_md = self._generate_model_selection_doc(model_selection)
        self.write_file("sales/model_selection.md", model_selection_md)
        
        # Update memory
        self.update_memory({
            "model_selection": model_selection
        })
        
        rprint("\n[bold green]✅ Sales Agent Complete[/bold green]")
        return True
    
    def _generate_requirements_doc(self) -> str:
        """Generate requirements.md from conversation history"""
        # Extract key info from conversation
        conversation = "\n\n".join([
            f"**{msg['role'].upper()}:** {msg['parts'][0]['text']}"
            for msg in self.history
        ])
        
        return f"""# Requirements Document

## Conversation Summary

{conversation}

## Next Steps

This document will be read by the Manager Agent to create a project plan.

---
Generated by Sales Agent (.coder)
"""
    
    def _generate_model_selection_doc(self, selection: dict) -> str:
        """Generate model_selection.md"""
        lines = ["# Model Selection\n"]
        lines.append("| Agent | Model |")
        lines.append("|-------|-------|")
        
        for agent, model in selection.items():
            lines.append(f"| {agent} | {model} |")
        
        lines.append("\n---\nGenerated by Sales Agent (.coder)")
        
        return "\n".join(lines)
