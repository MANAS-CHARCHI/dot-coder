import json
import re
from tools import execute_tool
from rich import print as rprint


def parse_and_execute(reply: str) -> tuple[str, bool]:
    """
    Look for tool calls in the LLM reply.
    Run them and return the results.

    Returns:
        (tool_results_string, did_any_tools_run)
    """

    # LLM must wrap tool calls like this:
    # <tool_call>
    # {"tool": "read_file", "args": {"path": "somefile.md"}}
    # </tool_call>

    pattern = r"<tool_call>\s*(.*?)\s*</tool_call>"
    matches = re.findall(pattern, reply, re.DOTALL)

    if not matches:
        return "", False

    results = []

    for raw in matches:
        try:
            call      = json.loads(raw)
            tool_name = call.get("tool")
            args      = call.get("args", {})

            rprint(f"  [cyan]🔧 {tool_name}({args})[/cyan]")

            result = execute_tool(tool_name, args)

            rprint(f"  [green]✓ {str(result)[:100]}[/green]")

            results.append(f"[{tool_name} result]\n{json.dumps(result, indent=2)}")

        except json.JSONDecodeError as e:
            results.append(f"[tool parse error] {e}")
        except Exception as e:
            results.append(f"[tool error] {e}")

    return "\n\n".join(results), True


# ─────────────────────────────────────────────
# TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":

    # simulate what an LLM reply looks like with a tool call
    fake_reply = """
    I will write a test file now.

    <tool_call>
    {"tool": "write_file", "args": {"path": "test_output/from_parser.txt", "content": "tool parser works!"}}
    </tool_call>

    Done writing the file.
    """

    result, ran = parse_and_execute(fake_reply)
    rprint(f"\nTool ran: {ran}")
    rprint(f"Result: {result}")
    