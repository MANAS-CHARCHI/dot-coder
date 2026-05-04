import os
import platform
import subprocess
from pathlib import Path
from rich import print as rprint

# ─────────────────────────────────────────────
# OS DETECTION
# ─────────────────────────────────────────────

IS_WINDOWS = platform.system() == "Windows"
IS_MAC     = platform.system() == "Darwin"
IS_LINUX   = platform.system() == "Linux"

# ─────────────────────────────────────────────
# TOOL 1 — READ FILE
# ─────────────────────────────────────────────

def read_file(path: str) -> dict:
    try:
        p = Path(path)
        if not p.exists():
            return {"success": False, "content": None, "error": f"File not found: {path}"}
        content = p.read_text(encoding="utf-8")
        return {"success": True, "content": content, "lines": len(content.splitlines()), "error": None}
    except Exception as e:
        return {"success": False, "content": None, "error": str(e)}

# ─────────────────────────────────────────────
# TOOL 2 — WRITE FILE
# ─────────────────────────────────────────────

def write_file(path: str, content: str) -> dict:
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return {"success": True, "path": str(p), "lines": len(content.splitlines()), "error": None}
    except Exception as e:
        return {"success": False, "path": path, "error": str(e)}

# ─────────────────────────────────────────────
# TOOL 3 — LIST FILES
# ─────────────────────────────────────────────

def list_files(directory: str = ".") -> dict:
    try:
        p = Path(directory)
        if not p.exists():
            return {"success": False, "files": [], "error": f"Directory not found: {directory}"}
        skip = {".git", "__pycache__", "node_modules", ".venv", "venv"}
        files = []
        for item in sorted(p.rglob("*")):
            if any(part in skip for part in item.parts):
                continue
            if item.is_file():
                files.append(str(item.relative_to(p)))
        return {"success": True, "files": files, "count": len(files), "error": None}
    except Exception as e:
        return {"success": False, "files": [], "error": str(e)}

# ─────────────────────────────────────────────
# TOOL 4 — CREATE FOLDER
# ─────────────────────────────────────────────

def create_folder(path: str) -> dict:
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return {"success": True, "path": path, "error": None}
    except Exception as e:
        return {"success": False, "path": path, "error": str(e)}

# ─────────────────────────────────────────────
# TOOL 5 — RUN COMMAND
# ─────────────────────────────────────────────

def run_command(command: str, working_dir: str = ".") -> dict:
    try:
        result = subprocess.run(
            command,
            shell      = True,
            capture_output = True,
            text       = True,
            timeout    = 30,
            cwd        = working_dir
        )
        return {
            "success":   result.returncode == 0,
            "stdout":    result.stdout.strip(),
            "stderr":    result.stderr.strip(),
            "exit_code": result.returncode,
            "error":     None
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "stdout": "", "stderr": "", "exit_code": 1, "error": "Timed out after 30s"}
    except Exception as e:
        return {"success": False, "stdout": "", "stderr": "", "exit_code": 1, "error": str(e)}

# ─────────────────────────────────────────────
# TOOL REGISTRY — maps names to functions
# ─────────────────────────────────────────────

TOOLS = {
    "read_file":     read_file,
    "write_file":    write_file,
    "list_files":    list_files,
    "create_folder": create_folder,
    "run_command":   run_command,
}

def execute_tool(tool_name: str, args: dict) -> dict:
    if tool_name not in TOOLS:
        return {"success": False, "error": f"Unknown tool: {tool_name}"}
    return TOOLS[tool_name](**args)


# ─────────────────────────────────────────────
# TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    rprint(f"OS: {'Windows' if IS_WINDOWS else 'Mac' if IS_MAC else 'Linux'}")

    rprint(write_file("test_output/hello.txt", "hello from .coder"))
    rprint(read_file("test_output/hello.txt"))
    rprint(list_files("."))
    rprint(run_command("echo tools are working"))