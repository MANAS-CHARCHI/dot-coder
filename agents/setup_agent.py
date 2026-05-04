# Task: SETUP-AGENT
# File: agents/setup_agent.py
# Description: Generates all project config and dependency files
# Author: System

from .base_agent import BaseAgent
from rich import print as rprint
import re


class SetupAgent(BaseAgent):
    """
    Setup Agent - Generates all project scaffolding files:
    requirements.txt, package.json, .env, docker-compose.yml,
    alembic.ini, vite.config.js, README.md, etc.
    """

    def get_system_prompt(self) -> str:
        return """You are the Setup Agent for the .coder multi-agent software factory.

Your job is to generate ALL project configuration and dependency files.
These files must be complete and immediately usable — no placeholders.

You will be given the tech stack and must produce real, working config files.

RULES:
- Use exact pinned versions (no ^ or ~ in package.json, no >= in requirements.txt)
- Include every package that the code actually needs
- .env files use placeholder values but correct variable names
- All files must be immediately usable after filling in secrets
- Output each file using: === FILE: filename === ... === END FILE ==="""

    def run(self) -> bool:
        rprint("\n[bold cyan]⚙️  Setup Agent Starting...[/bold cyan]\n")

        tech_req  = self.read_file("architect/tech_requirements.md")
        sys_design = self.read_file("architect/system_design.md")
        memory    = self.memory

        if not tech_req or not sys_design:
            rprint("[red]Error: Missing architect files[/red]")
            return False

        response = self.call_llm(
            self.get_system_prompt(),
            f"""Generate ALL project setup files for this tech stack.

TECH REQUIREMENTS:
{tech_req}

SYSTEM DESIGN:
{sys_design}

MEMORY:
{memory}

Generate these files using === FILE: path === ... === END FILE === format:

1. backend/requirements.txt
   - All Python packages with pinned versions
   - Must include: fastapi, uvicorn, sqlalchemy, alembic, psycopg2-binary,
     python-jose[cryptography], passlib[bcrypt], python-dotenv, pydantic,
     pydantic-settings, python-multipart

2. backend/.env.example
   - All env vars with placeholder values
   - DATABASE_URL, JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES, etc.

3. backend/alembic.ini
   - Full alembic config pointing to migrations/ folder

4. backend/alembic/env.py
   - Alembic env.py that imports all models and uses DATABASE_URL from env

5. frontend/package.json
   - All npm packages with pinned versions
   - scripts: dev, build, preview, lint
   - Must include: react, react-dom, react-router-dom, axios
   - devDependencies: vite, @vitejs/plugin-react, eslint

6. frontend/vite.config.js
   - Vite config with React plugin and proxy to backend /api

7. frontend/.env.example
   - VITE_API_URL=http://localhost:8000

8. docker-compose.yml
   - Services: backend, frontend, postgres, (redis if needed)
   - Correct ports, volumes, env_file references
   - depends_on with health checks

9. .gitignore
   - Python: __pycache__, .env, *.pyc, venv/, .venv/
   - Node: node_modules/, dist/, .env
   - General: .DS_Store, *.log

10. README.md
    - Project name and description
    - Prerequisites
    - Setup steps (clone, install, configure .env, migrate, run)
    - How to run with docker-compose
    - API base URL

Write ALL files now with complete, real content."""
        )

        if not response:
            return False

        files = self._parse_files(response)

        if not files:
            rprint("[yellow]Warning: No files parsed from setup agent response[/yellow]")
            self.write_file("setup/raw_output.txt", response)
            return False

        for path, content in files.items():
            self.write_file(f"setup/{path}", content)
            rprint(f"[green]✓ {path}[/green]")

        rprint(f"\n[bold green]✅ Setup Agent Complete — {len(files)} files generated[/bold green]")
        return True

    def _parse_files(self, response: str) -> dict:
        files = {}

        # Primary: === FILE: path === ... === END FILE ===
        pattern = r"===\s*FILE:\s*(.+?)\s*===\s*\n(.*?)\n===\s*END FILE\s*==="
        for path, content in re.findall(pattern, response, re.DOTALL | re.IGNORECASE):
            files[path.strip()] = content.strip()

        if files:
            return files

        # Fallback: markdown code blocks preceded by a filename line
        lines = response.split('\n')
        current_name = None
        in_block = False
        block_lines = []

        for line in lines:
            if not in_block:
                m = re.search(
                    r'(?:File:|Creating|Writing|###|##|`)\s*'
                    r'([a-zA-Z0-9_./@-]+\.'
                    r'(?:txt|json|yml|yaml|ini|py|js|jsx|ts|tsx|env|md|cfg|toml))',
                    line, re.IGNORECASE
                )
                if m:
                    current_name = m.group(1).lstrip('`').strip()
            if line.strip().startswith('```'):
                if not in_block:
                    in_block = True
                    block_lines = []
                else:
                    in_block = False
                    if current_name and block_lines:
                        files[current_name] = '\n'.join(block_lines).strip()
                    current_name = None
            elif in_block:
                block_lines.append(line)

        return files
