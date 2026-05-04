#!/usr/bin/env python3
"""
.coder - Interactive Chat Mode

Chat with your project, ask questions, request changes.
"""

import json
from pathlib import Path
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from llm import call_llm
from llm_call import DEFAULT_MODEL

console = Console()


class ProjectChat:
    """Interactive chat with project context"""
    
    def __init__(self):
        self.base_path = Path(".coder")
        self.history = []
        self.context = self._load_project_context()
        self.model = DEFAULT_MODEL
    
    def _load_project_context(self) -> dict:
        """Load all project files as context"""
        context = {
            "project_exists": False,
            "project_name": None,
            "files": {},
            "memory": {},
            "state": {}
        }
        
        if not self.base_path.exists():
            return context
        
        context["project_exists"] = True
        
        # Load memory
        memory_file = self.base_path / "orchestrator" / "memory.json"
        if memory_file.exists():
            try:
                context["memory"] = json.loads(memory_file.read_text())
                context["project_name"] = context["memory"].get("project_name", "Unknown")
            except:
                pass
        
        # Load state
        state_file = self.base_path / "orchestrator" / "pipeline_state.json"
        if state_file.exists():
            try:
                context["state"] = json.loads(state_file.read_text())
            except:
                pass
        
        # Load key files
        key_files = [
            "sales/requirements.md",
            "manager/project_plan.md",
            "architect/system_design.md",
            "architect/data_flow.md",
            "engineer/database/schema_plan.md",
            "engineer/backend/api_plan.md",
            "engineer/frontend/ui_plan.md",
            "delivery/final_report.md"
        ]
        
        for file_path in key_files:
            full_path = self.base_path / file_path
            if full_path.exists():
                try:
                    context["files"][file_path] = full_path.read_text()
                except:
                    pass
        
        return context
    
    def _get_system_prompt(self) -> str:
        """Get system prompt with project context"""
        
        if not self.context["project_exists"]:
            return """You are a helpful assistant for the .coder multi-agent software factory.

There is no project loaded yet. Help the user understand how to:
- Start a new project: python main.py
- Learn about the system: Check README.md
- Get help with setup: python test_setup.py"""
        
        project_name = self.context["project_name"]
        files_summary = "\n".join([f"- {path}" for path in self.context["files"].keys()])
        
        return f"""You are a helpful assistant for the .coder multi-agent software factory.

You are currently helping with the project: {project_name}

AVAILABLE PROJECT FILES:
{files_summary}

PROJECT MEMORY:
{json.dumps(self.context["memory"], indent=2)}

YOUR CAPABILITIES:
1. Answer questions about the project
2. Explain design decisions
3. Suggest improvements
4. Help with specific changes
5. Explain how to regenerate parts

WHEN USER ASKS FOR CHANGES:
- Explain which files need to be modified
- Suggest which agents to re-run
- Provide step-by-step instructions

WHEN USER ASKS QUESTIONS:
- Reference specific files and sections
- Explain the architecture and decisions
- Be helpful and detailed

Be conversational and helpful. Use the project context to give accurate answers."""
    
    def chat(self):
        """Start interactive chat session"""
        
        if not self.context["project_exists"]:
            console.print(Panel(
                "[bold yellow]No Project Found[/bold yellow]\n\n"
                "There's no project in .coder/ yet.\n\n"
                "To start a new project, run: [cyan]python main.py[/cyan]",
                title="⚠️  No Project",
                border_style="yellow"
            ))
            return
        
        console.print(Panel(
            f"[bold cyan]Interactive Chat Mode[/bold cyan]\n\n"
            f"Project: [bold]{self.context['project_name']}[/bold]\n"
            f"Files loaded: {len(self.context['files'])}\n\n"
            f"Ask questions, request changes, or get help!\n"
            f"Type 'exit' to quit, 'help' for commands.",
            title="💬 Chat",
            border_style="cyan"
        ))
        
        while True:
            try:
                user_input = input("\n[You] ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    rprint("[cyan]Goodbye![/cyan]")
                    break
                
                if user_input.lower() == 'help':
                    self._show_help()
                    continue
                
                if user_input.lower() == 'context':
                    self._show_context()
                    continue
                
                if user_input.lower() == 'reload':
                    self.context = self._load_project_context()
                    rprint("[green]✓ Project context reloaded[/green]")
                    continue
                
                # Call LLM
                response = self._call_llm(user_input)
                
                if response:
                    console.print(f"\n[bold cyan][Assistant][/bold cyan]")
                    console.print(Markdown(response))
            
            except KeyboardInterrupt:
                rprint("\n[cyan]Goodbye![/cyan]")
                break
            except Exception as e:
                rprint(f"[red]Error: {e}[/red]")
    
    def _call_llm(self, user_message: str) -> str:
        """Call LLM with project context"""
        
        # Add relevant file content if user mentions specific files
        context_additions = []
        
        for file_path, content in self.context["files"].items():
            file_name = file_path.split('/')[-1]
            if file_name.lower() in user_message.lower() or file_path in user_message:
                context_additions.append(f"\n=== {file_path} ===\n{content[:2000]}\n")
        
        enhanced_message = user_message
        if context_additions:
            enhanced_message += "\n\nRELEVANT FILES:\n" + "\n".join(context_additions)
        
        self.history.append({
            "role": "user",
            "parts": [{"text": enhanced_message}]
        })
        
        result = call_llm(
            system=self._get_system_prompt(),
            history=self.history,
            agent="chat",
            model=self.model
        )
        
        if result.get("error"):
            rprint(f"[red]Error: {result['error']}[/red]")
            return None
        
        reply = result.get("reply")
        if reply:
            self.history.append({
                "role": "model",
                "parts": [{"text": reply}]
            })
        
        return reply
    
    def _show_help(self):
        """Show help commands"""
        console.print(Panel(
            """[bold]Available Commands:[/bold]

[cyan]help[/cyan] - Show this help message
[cyan]context[/cyan] - Show loaded project context
[cyan]reload[/cyan] - Reload project files
[cyan]exit[/cyan] - Exit chat mode

[bold]Example Questions:[/bold]

• "What does this project do?"
• "Explain the database schema"
• "How do I add a new API endpoint?"
• "What's the tech stack?"
• "Show me the user authentication flow"
• "How can I change the database from PostgreSQL to MongoDB?"
• "What files do I need to modify to add a new feature?"

[bold]Requesting Changes:[/bold]

• "I want to add user profiles"
• "Change the frontend from React to Vue"
• "Add email notifications"
• "Improve error handling"

The assistant will explain what needs to be changed and how to do it.""",
            title="💡 Help",
            border_style="cyan"
        ))
    
    def _show_context(self):
        """Show current project context"""
        console.print(Panel(
            f"""[bold]Project Context:[/bold]

Project Name: {self.context['project_name']}
Status: {self.context['state'].get('status', 'unknown')}

[bold]Loaded Files ({len(self.context['files'])}):[/bold]
{chr(10).join(['• ' + path for path in self.context['files'].keys()])}

[bold]Tech Stack:[/bold]
{json.dumps(self.context['memory'].get('tech_stack', {}), indent=2)}""",
            title="📋 Context",
            border_style="cyan"
        ))


def main():
    """Entry point for chat mode"""
    chat = ProjectChat()
    chat.chat()


if __name__ == "__main__":
    main()
