from llm import call_llm
from rich import print as rprint

def run_agent(agent_name: str, system: str, task: str, max_steps: int = 10) -> dict:

    history = []
    total_input_tokens  = 0
    total_output_tokens = 0
    total_cost          = 0

    # add the first task as user message
    history.append({
        "role":  "user",
        "parts": [{"text": task}]
    })

    rprint(f"\n[bold cyan]═══ {agent_name.upper()} AGENT STARTING ═══[/bold cyan]")
    rprint(f"[dim]Task: {task[:80]}...[/dim]\n")

    for step in range(1, max_steps + 1):

        rprint(f"[yellow]Step {step}/{max_steps}[/yellow]")

        # call the LLM
        result = call_llm(
            system  = system,
            history = history,
            agent   = agent_name
        )

        # if LLM call failed
        if result["error"]:
            rprint(f"[red]Error on step {step}: {result['error']}[/red]")
            break

        reply = result["reply"]

        # track totals
        total_input_tokens  += result["input_tokens"]
        total_output_tokens += result["output_tokens"]
        total_cost          += result["cost"]

        rprint(f"[green]Reply:[/green] {reply[:200]}")

        # add reply to history
        history.append({
            "role":  "model",
            "parts": [{"text": reply}]
        })

        # check if agent says it is done
        if "DONE" in reply.upper():
            rprint(f"\n[bold green]✓ {agent_name} finished in {step} steps[/bold green]")
            break

        # feed back to continue
        history.append({
            "role":  "user",
            "parts": [{"text": "continue"}]
        })

    # summary
    rprint(f"\n[bold]━━━ {agent_name.upper()} SUMMARY ━━━[/bold]")
    rprint(f"Steps:         {step}")
    rprint(f"Input tokens:  {total_input_tokens}")
    rprint(f"Output tokens: {total_output_tokens}")
    rprint(f"Cost:          ${total_cost:.6f}")

    return {
        "agent":         agent_name,
        "steps":         step,
        "history":       history,
        "input_tokens":  total_input_tokens,
        "output_tokens": total_output_tokens,
        "cost":          total_cost
    }


if __name__ == "__main__":
    run_agent(
        agent_name = "counter",
        system     = "You are a counting agent. Count from 1 upward, one number per reply. When you reach 5 say DONE.",
        task       = "start counting",
        max_steps  = 10
    )