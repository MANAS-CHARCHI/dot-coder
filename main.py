#!/usr/bin/env python3
"""
.coder - Multi-Agent Software Factory

Main entry point for the autonomous multi-agent pipeline.
"""

from orchestrator import Orchestrator
from rich import print as rprint
from rich.panel import Panel
from rich.table import Table
from rich.console import Console
from pathlib import Path
import sys
import json

console = Console()


def check_existing_project():
    """Check if there's an existing project in .coder/"""
    coder_path = Path(".coder")
    
    if not coder_path.exists():
        return None
    
    # Check for pipeline state
    state_file = coder_path / "orchestrator" / "pipeline_state.json"
    memory_file = coder_path / "orchestrator" / "memory.json"
    
    if not state_file.exists() or not memory_file.exists():
        return None
    
    try:
        state = json.loads(state_file.read_text())
        memory = json.loads(memory_file.read_text())
        
        project_name = state.get("project_name") or memory.get("project_name") or "Unknown Project"
        status = state.get("status", "unknown")
        current_step = state.get("current_step")
        
        return {
            "name": project_name,
            "status": status,
            "current_step": current_step,
            "state": state,
            "memory": memory
        }
    except:
        return None


def show_project_menu(project_info):
    """Show menu for existing project"""
    console.print(Panel(
        f"[bold cyan]Existing Project Found[/bold cyan]\n\n"
        f"Project: [bold]{project_info['name']}[/bold]\n"
        f"Status: {project_info['status']}\n"
        f"Current Step: {project_info['current_step'] or 'Not started'}",
        title="📁 Project Detected",
        border_style="cyan"
    ))
    
    console.print("\n[bold]What would you like to do?[/bold]\n")
    
    table = Table(show_header=False, box=None)
    table.add_column("Option", style="cyan")
    table.add_column("Description", style="white")
    
    if project_info['status'] == 'running':
        table.add_row("1", "Resume - Continue from where it stopped")
    elif project_info['status'] == 'completed':
        table.add_row("1", "View - See the final report")
    else:
        table.add_row("1", "Resume - Try to continue the project")
    
    table.add_row("2", "Improve - Modify/enhance the existing project")
    table.add_row("3", "Regenerate Code - Re-run Coder with proper file names")
    table.add_row("4", "Chat - Ask questions or request changes")
    table.add_row("5", "Start Fresh - Delete and create new project")
    table.add_row("6", "Exit - Keep existing project and quit")
    
    console.print(table)
    console.print()


def handle_resume(orchestrator):
    """Resume an existing project"""
    rprint("\n[cyan]Resuming project...[/cyan]\n")
    orchestrator.print_status()
    
    response = input("\nContinue from where we left off? (yes/no): ").strip().lower()
    if response != "yes":
        rprint("[yellow]Cancelled.[/yellow]")
        return False
    
    return orchestrator.run_pipeline()


def handle_improve(orchestrator, project_info):
    """Improve/modify an existing project"""
    rprint("\n[bold cyan]🔧 Improvement Mode[/bold cyan]\n")
    
    console.print("What would you like to improve?\n")
    console.print("1. Add new features")
    console.print("2. Fix bugs/issues")
    console.print("3. Refactor code")
    console.print("4. Update dependencies")
    console.print("5. Custom improvement")
    
    choice = input("\nYour choice (1-5): ").strip()
    
    improvement_request = input("\nDescribe what you want to improve: ").strip()
    
    if not improvement_request:
        rprint("[yellow]No improvement specified. Cancelled.[/yellow]")
        return False
    
    # Create an improvement task
    rprint(f"\n[green]✓ Improvement request: {improvement_request}[/green]")
    rprint("\n[yellow]Note: Improvement mode will be implemented in a future version.[/yellow]")
    rprint("[yellow]For now, you can:[/yellow]")
    rprint("  1. Manually edit files in .coder/")
    rprint("  2. Run specific agents again")
    rprint("  3. Or start fresh with option 3")
    
    return False


def handle_view_report():
    """View the final report of a completed project"""
    report_path = Path(".coder/delivery/final_report.md")
    
    if not report_path.exists():
        rprint("[red]Final report not found.[/red]")
        return
    
    report = report_path.read_text()
    
    console.print(Panel(
        report[:2000] + ("..." if len(report) > 2000 else ""),
        title="📄 Final Report (Preview)",
        border_style="green"
    ))
    
    console.print(f"\n[cyan]Full report: {report_path}[/cyan]")
    console.print("[dim]Open this file to see the complete report[/dim]\n")


def handle_regenerate_code():
    """Regenerate code while keeping all planning"""
    console.print("\n[bold cyan]🔄 Regenerate Code[/bold cyan]\n")
    console.print("This will:")
    console.print("  ✓ Keep all planning (requirements, architecture, designs)")
    console.print("  ✓ Delete existing code")
    console.print("  ✓ Re-run Coder agents with improved file naming")
    console.print("  ✓ Generate proper .py, .jsx, .tsx files (not .txt)")
    
    confirm = input("\nContinue? (yes/no): ").strip().lower()
    
    if confirm != "yes":
        rprint("[yellow]Cancelled.[/yellow]")
        return False
    
    import shutil
    coder_path = Path(".coder/coder")
    reviewer_path = Path(".coder/reviewer")
    tester_path = Path(".coder/tester")
    
    # Delete code, review, and test outputs
    if coder_path.exists():
        shutil.rmtree(coder_path)
        rprint("[green]✓ Deleted existing code[/green]")
    
    if reviewer_path.exists():
        shutil.rmtree(reviewer_path)
        rprint("[green]✓ Deleted review results[/green]")
    
    if tester_path.exists():
        shutil.rmtree(tester_path)
        rprint("[green]✓ Deleted test results[/green]")
    
    # Reset pipeline state for coder steps
    state_file = Path(".coder/orchestrator/pipeline_state.json")
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text())
            
            # Get all steps from dependencies (ensures new steps like 'setup' are included)
            steps_to_reset = [
                "setup",
                "coder_db", "coder_backend", "coder_frontend",
                "reviewer_backend", "reviewer_frontend",
                "tester_backend", "tester_frontend",
                "final_tester", "delivery"
            ]
            
            # Ensure steps dict exists
            if "steps" not in state:
                state["steps"] = {}
            
            # Add any missing steps to the state
            for step in steps_to_reset:
                if step not in state["steps"]:
                    state["steps"][step] = {
                        "status": "pending",
                        "started_at": None,
                        "completed_at": None,
                        "retries": 0
                    }
                else:
                    # Reset the step
                    state["steps"][step] = {
                        "status": "pending",
                        "started_at": None,
                        "completed_at": None,
                        "retries": 0
                    }
            
            state["status"] = "running"
            state["current_step"] = "setup"
            
            state_file.write_text(json.dumps(state, indent=2))
            rprint("[green]✓ Reset pipeline state[/green]")
        except Exception as e:
            rprint(f"[red]Error resetting state: {e}[/red]")
            return False
    
    rprint("\n[bold green]✅ Ready to regenerate code![/bold green]")
    rprint("[cyan]The pipeline will now re-run from the Coder phase.[/cyan]\n")
    
    return True


def handle_start_fresh():
    """Delete existing project and start fresh"""
    console.print("\n[bold red]⚠️  Warning: This will delete all existing project files![/bold red]")
    confirm = input("Type 'DELETE' to confirm: ").strip()
    
    if confirm != "DELETE":
        rprint("[yellow]Cancelled. Existing project preserved.[/yellow]")
        return False
    
    import shutil
    coder_path = Path(".coder")
    
    if coder_path.exists():
        shutil.rmtree(coder_path)
        rprint("[green]✓ Existing project deleted[/green]")
    
    return True


def main():
    """Main entry point"""
    rprint(Panel(
        "[bold cyan].coder[/bold cyan] - Multi-Agent Software Factory\n\n"
        "An autonomous pipeline that takes your idea and delivers\n"
        "a complete, tested, working codebase.\n\n"
        "[dim]Version 2.1[/dim]",
        title="🤖 Welcome",
        border_style="cyan"
    ))
    
    try:
        # Check for existing project
        project_info = check_existing_project()
        
        if project_info:
            # Show menu for existing project
            show_project_menu(project_info)
            
            choice = input("Your choice (1-6): ").strip()
            
            if choice == "1":
                # Resume
                orchestrator = Orchestrator()
                
                if project_info['status'] == 'completed':
                    handle_view_report()
                    return
                
                success = handle_resume(orchestrator)
                
            elif choice == "2":
                # Improve
                orchestrator = Orchestrator()
                success = handle_improve(orchestrator, project_info)
                
            elif choice == "3":
                # Regenerate code
                if handle_regenerate_code():
                    orchestrator = Orchestrator()
                    success = orchestrator.run_pipeline()
                else:
                    return
                
            elif choice == "4":
                # Chat mode
                from chat import ProjectChat
                chat = ProjectChat()
                chat.chat()
                return
                
            elif choice == "5":
                # Start fresh
                if handle_start_fresh():
                    # Continue to new project creation below
                    project_info = None
                else:
                    return
                    
            elif choice == "6":
                # Exit
                rprint("[cyan]Goodbye![/cyan]")
                return
            else:
                rprint("[red]Invalid choice.[/red]")
                return
        
        # New project or after deleting old one
        if not project_info:
            orchestrator = Orchestrator()
            
            rprint("\n[bold]Let's build something![/bold]\n")
            project_name = input("Enter project name: ").strip()
            
            if not project_name:
                project_name = "New Project"
            
            orchestrator.initialize_pipeline(project_name)
            
            # Run the pipeline
            success = orchestrator.run_pipeline()
        
        if success:
            rprint("\n[bold green]🎉 Pipeline completed successfully![/bold green]")
            rprint("[cyan]Check .coder/delivery/final_report.md for your project[/cyan]\n")
            sys.exit(0)
        else:
            rprint("\n[bold red]❌ Pipeline failed or was cancelled[/bold red]")
            rprint("[yellow]Check .coder/orchestrator/event_log.json for details[/yellow]\n")
            sys.exit(1)
    
    except KeyboardInterrupt:
        rprint("\n\n[yellow]Pipeline interrupted by user[/yellow]")
        rprint("[dim]Run again to resume from where you left off[/dim]\n")
        sys.exit(130)
    
    except Exception as e:
        rprint(f"\n[bold red]Fatal error: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
