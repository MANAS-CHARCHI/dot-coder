#!/usr/bin/env python3
"""
Test script to verify .coder setup
"""

import sys
from pathlib import Path
from rich import print as rprint
from rich.console import Console
from rich.table import Table

console = Console()


def test_imports():
    """Test that all required packages are installed"""
    rprint("\n[bold cyan]Testing imports...[/bold cyan]")
    
    try:
        import google.genai
        rprint("✅ google-genai")
    except ImportError:
        rprint("❌ google-genai not installed")
        return False
    
    try:
        import dotenv
        rprint("✅ python-dotenv")
    except ImportError:
        rprint("❌ python-dotenv not installed")
        return False
    
    try:
        import rich
        rprint("✅ rich")
    except ImportError:
        rprint("❌ rich not installed")
        return False
    
    try:
        import openai
        rprint("✅ openai")
    except ImportError:
        rprint("❌ openai not installed")
        return False
    
    return True


def test_env():
    """Test that .env file exists and has API key"""
    rprint("\n[bold cyan]Testing environment...[/bold cyan]")
    
    env_file = Path(".env")
    if not env_file.exists():
        rprint("❌ .env file not found")
        rprint("[yellow]Run: cp .env.example .env[/yellow]")
        return False
    
    rprint("✅ .env file exists")
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    nvidia_key = os.environ.get("NVIDIA_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    has_nvidia = nvidia_key and nvidia_key != "your_nvidia_api_key_here"
    has_gemini = gemini_key and gemini_key != "your_gemini_api_key_here"
    
    if has_nvidia:
        rprint("✅ NVIDIA_API_KEY is set")
    else:
        rprint("⚠️  NVIDIA_API_KEY not set (default model won't work)")
    
    if has_gemini:
        rprint("✅ GEMINI_API_KEY is set")
    else:
        rprint("⚠️  GEMINI_API_KEY not set (Gemini models won't work)")
    
    if not has_nvidia and not has_gemini:
        rprint("❌ No API keys configured")
        rprint("[yellow]Edit .env and add at least one API key[/yellow]")
        return False
    
    return True


def test_llm():
    """Test that LLM connection works"""
    rprint("\n[bold cyan]Testing LLM connection...[/bold cyan]")
    
    try:
        from llm import call_llm
        
        result = call_llm(
            system="You are a test assistant.",
            history=[{"role": "user", "parts": [{"text": "Say 'test successful' and nothing else"}]}],
            agent="test_setup"
        )
        
        if result.get("error"):
            rprint(f"❌ LLM error: {result['error']}")
            rprint("[yellow]Make sure at least one API key is configured in .env[/yellow]")
            return False
        
        rprint("✅ LLM connection works")
        rprint(f"[dim]Response: {result.get('reply', '')[:50]}...[/dim]")
        return True
        
    except Exception as e:
        rprint(f"❌ LLM test failed: {e}")
        return False


def test_structure():
    """Test that required files exist"""
    rprint("\n[bold cyan]Testing project structure...[/bold cyan]")
    
    required_files = [
        "main.py",
        "orchestrator.py",
        "llm.py",
        "llm_call.py",
        "agents/__init__.py",
        "agents/base_agent.py",
        "agents/sales.py",
        "agents/manager.py",
        "agents/architect.py",
        "agents/db_engineer.py",
        "agents/backend_engineer.py",
        "agents/frontend_engineer.py",
        "agents/coder.py",
        "agents/reviewer.py",
        "agents/tester.py",
        "agents/delivery.py",
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            rprint(f"✅ {file_path}")
        else:
            rprint(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist


def main():
    """Run all tests"""
    console.print("\n[bold]🧪 .coder Setup Test[/bold]\n")
    
    results = {
        "Imports": test_imports(),
        "Environment": test_env(),
        "Project Structure": test_structure(),
        "LLM Connection": test_llm(),
    }
    
    # Summary table
    table = Table(title="\nTest Results")
    table.add_column("Test", style="cyan")
    table.add_column("Status", style="magenta")
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        table.add_row(test_name, status)
    
    console.print(table)
    
    if all(results.values()):
        rprint("\n[bold green]🎉 All tests passed! Ready to run .coder[/bold green]")
        rprint("[cyan]Run: python main.py[/cyan]\n")
        sys.exit(0)
    else:
        rprint("\n[bold red]❌ Some tests failed. Fix issues above.[/bold red]\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
