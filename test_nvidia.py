#!/usr/bin/env python3
"""
Test NVIDIA API connection specifically
"""

import os
from dotenv import load_dotenv
from rich import print as rprint
from rich.panel import Panel

load_dotenv()

def test_nvidia_setup():
    """Test NVIDIA API setup"""
    rprint("\n[bold cyan]Testing NVIDIA API Setup[/bold cyan]\n")
    
    # Check API key
    nvidia_key = os.environ.get("NVIDIA_API_KEY")
    
    if not nvidia_key:
        rprint("[red]❌ NVIDIA_API_KEY not found in .env[/red]")
        rprint("\n[yellow]To fix:[/yellow]")
        rprint("1. Edit .env file")
        rprint("2. Add: NVIDIA_API_KEY=nvapi-your_key_here")
        return False
    
    if nvidia_key == "your_nvidia_api_key_here":
        rprint("[red]❌ NVIDIA_API_KEY is still the default placeholder[/red]")
        rprint("\n[yellow]To fix:[/yellow]")
        rprint("1. Get API key from: https://build.nvidia.com/")
        rprint("2. Edit .env and replace placeholder with actual key")
        return False
    
    rprint(f"✅ NVIDIA_API_KEY found: {nvidia_key[:15]}...")
    
    # Check openai package
    try:
        from openai import OpenAI
        rprint("✅ openai package installed")
    except ImportError:
        rprint("[red]❌ openai package not installed[/red]")
        rprint("\n[yellow]To fix:[/yellow]")
        rprint("Run: uv sync")
        return False
    
    # Test connection
    rprint("\n[cyan]Testing NVIDIA API connection...[/cyan]")
    
    try:
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=nvidia_key,
            timeout=30.0  # 30 second timeout
        )
        
        rprint("✅ Client created successfully")
        
        # Try a simple call
        rprint("\n[cyan]Sending test message (this may take 10-30 seconds)...[/cyan]")
        
        completion = client.chat.completions.create(
            model="meta/llama-3.1-8b-instruct",  # Try a different model that's known to work
            messages=[
                {"role": "user", "content": "Say 'NVIDIA API works!' and nothing else."}
            ],
            max_tokens=50,
            temperature=0.5,
            top_p=1,
            stream=False
        )
        
        response = completion.choices[0].message.content
        rprint(f"\n[green]✅ Response: {response}[/green]")
        
        rprint("\n[bold green]🎉 NVIDIA API is working correctly![/bold green]")
        rprint("\n[yellow]Note: Using meta/llama-3.1-8b-instruct for testing[/yellow]")
        rprint("[yellow]The z-ai/glm4.7 model may have different requirements[/yellow]")
        return True
        
    except Exception as e:
        rprint(f"\n[red]❌ API call failed: {e}[/red]")
        rprint("\n[yellow]Possible issues:[/yellow]")
        rprint("1. Invalid API key")
        rprint("2. Network connection problem")
        rprint("3. Model 'z-ai/glm4.7' may not be available")
        rprint("4. API rate limit reached")
        rprint("5. Timeout (API took too long to respond)")
        return False


def test_model_selection():
    """Test which model will be used by default"""
    rprint("\n[bold cyan]Testing Default Model Selection[/bold cyan]\n")
    
    try:
        from llm_call import DEFAULT_MODEL, MODELS
        
        rprint(f"Default model: [bold]{DEFAULT_MODEL}[/bold]")
        
        if DEFAULT_MODEL in MODELS:
            model_info = MODELS[DEFAULT_MODEL]
            rprint(f"Provider: {model_info['provider']}")
            rprint(f"Context: {model_info['context']} tokens")
            rprint(f"Cost: ${model_info['input_cost']}/token in, ${model_info['output_cost']}/token out")
            
            if model_info['provider'] == 'nvidia':
                rprint("\n✅ Default is set to NVIDIA")
                return True
            else:
                rprint(f"\n⚠️  Default is set to {model_info['provider']}, not NVIDIA")
                return False
        else:
            rprint(f"[red]❌ Default model '{DEFAULT_MODEL}' not found in MODELS[/red]")
            return False
            
    except Exception as e:
        rprint(f"[red]❌ Error: {e}[/red]")
        return False


def test_llm_integration():
    """Test the actual llm.py integration"""
    rprint("\n[bold cyan]Testing LLM Integration[/bold cyan]\n")
    
    try:
        from llm import call_llm, nvidia_client, gemini_client
        
        rprint(f"NVIDIA client: {'✅ Initialized' if nvidia_client else '❌ Not initialized'}")
        rprint(f"Gemini client: {'✅ Initialized' if gemini_client else '❌ Not initialized'}")
        
        if not nvidia_client:
            rprint("\n[yellow]⚠️  NVIDIA client not initialized[/yellow]")
            rprint("This means NVIDIA_API_KEY is not set in .env")
            return False
        
        rprint("\n[cyan]Testing call_llm() with NVIDIA...[/cyan]")
        
        result = call_llm(
            system="You are a test assistant.",
            history=[{"role": "user", "parts": [{"text": "Say 'Integration test passed!' and nothing else."}]}],
            agent="test_nvidia",
            model="meta/llama-3.1-8b-instruct"
        )
        
        if result.get("error"):
            rprint(f"[red]❌ Error: {result['error']}[/red]")
            return False
        
        rprint(f"\n[green]✅ Response: {result.get('reply', '')[:100]}[/green]")
        rprint(f"[dim]Model used: meta/llama-3.1-8b-instruct[/dim]")
        rprint(f"[dim]Tokens: {result.get('input_tokens', 0)} in / {result.get('output_tokens', 0)} out[/dim]")
        
        rprint("\n[bold green]🎉 LLM integration is working![/bold green]")
        return True
        
    except Exception as e:
        rprint(f"[red]❌ Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False


def main():
    rprint(Panel(
        "[bold]NVIDIA API Diagnostic Tool[/bold]\n\n"
        "This will test your NVIDIA API setup",
        title="🔍 Diagnostics",
        border_style="cyan"
    ))
    
    results = {
        "NVIDIA Setup": test_nvidia_setup(),
        "Model Selection": test_model_selection(),
        "LLM Integration": test_llm_integration(),
    }
    
    rprint("\n" + "="*50)
    rprint("\n[bold]Summary:[/bold]\n")
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        rprint(f"{status} - {test_name}")
    
    if all(results.values()):
        rprint("\n[bold green]All tests passed! NVIDIA API is ready to use.[/bold green]")
        rprint("\n[cyan]Next step: Run 'python main.py' and choose option 1 (NVIDIA for all)[/cyan]\n")
    else:
        rprint("\n[bold red]Some tests failed. Fix the issues above.[/bold red]\n")


if __name__ == "__main__":
    main()
