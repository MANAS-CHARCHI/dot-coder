# Task: ARCHITECT-AGENT
# File: agents/architect.py
# Description: Architect agent - creates system design
# Author: System

from .base_agent import BaseAgent
from rich import print as rprint


class ArchitectAgent(BaseAgent):
    """
    Architect Agent - Makes ALL technical decisions
    """
    
    def get_system_prompt(self) -> str:
        return """You are the Architect Agent for the .coder multi-agent software factory.

You make ALL technical decisions. You will be called 3 times to produce 3 separate files.
Each call will ask for ONE specific file. Write ONLY that file.

RULES:
- ONE choice per decision — never "you could use X or Y"
- Exact versions, not "latest"
- Junior developer must be able to follow this design
- Do NOT repeat content from other files
- Do NOT include JSON blobs or memory.json content in your output"""

    def _write_system_design(self, requirements: str, project_plan: str) -> str:
        return self.call_llm(
            self.get_system_prompt(),
            f"""Write system_design.md for this project.

REQUIREMENTS:
{requirements}

PROJECT PLAN:
{project_plan}

Write a clean markdown document covering:
1. Project overview (2-3 sentences)
2. Frontend: exact framework + version + why
3. Backend: exact framework + version + why
4. Database: exact DB + version + why
5. ORM: exact ORM + version + why
6. Auth method: JWT/OAuth/sessions + why
7. Migrations: tool + version
8. Folder structure (show the tree)
9. All environment variables needed (name + description)
10. Key architectural decisions

Write ONLY system_design.md content. Clean markdown, no JSON blobs."""
        )

    def _write_data_flow(self, system_design: str) -> str:
        return self.call_llm(
            self.get_system_prompt(),
            f"""Write data_flow.md for this project.

SYSTEM DESIGN:
{system_design}

Write a clean markdown document covering every major user flow as numbered steps:

## User Registration
1. User submits POST /api/v1/auth/register with email + password
2. Backend validates input (email format, password length)
3. Check if email already exists in users table
4. Hash password with bcrypt
5. Insert new user into database
6. Generate JWT token with user_id
7. Return 201 with token

## User Login
1. ...

## [Every other flow in the system]

Write ONLY data_flow.md content. Clean markdown, numbered steps per flow."""
        )

    def _write_tech_requirements(self, system_design: str) -> str:
        return self.call_llm(
            self.get_system_prompt(),
            f"""Write tech_requirements.md for this project.

SYSTEM DESIGN:
{system_design}

Write a clean markdown document with EXACT dependency versions:

## Backend Dependencies (requirements.txt)
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
pydantic==2.4.2
pydantic-settings==2.0.3
```

## Frontend Dependencies (package.json)
```json
{{
  "dependencies": {{
    "react": "18.2.0",
    "react-dom": "18.2.0",
    "react-router-dom": "6.18.0",
    "axios": "1.6.0"
  }},
  "devDependencies": {{
    "vite": "4.5.0",
    "@vitejs/plugin-react": "4.1.0"
  }}
}}
```

## Environment Variables (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
JWT_SECRET=your-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
APP_HOST=0.0.0.0
APP_PORT=8000
```

## Naming Conventions
- Python: snake_case for variables/functions, PascalCase for classes
- React: PascalCase for components, camelCase for variables
- Database: snake_case for tables and columns
- API: /api/v1/resource-name (kebab-case)
- Primary keys: UUID
- Error format: {{ "error": "message", "code": "ERROR_CODE" }}

Write ONLY tech_requirements.md content. Include exact pip package names and versions."""
        )

    def run(self) -> bool:
        """Run the architect agent"""
        rprint("\n[bold cyan]🏗️  Architect Agent Starting...[/bold cyan]\n")
        
        requirements = self.read_file("sales/requirements.md")
        project_plan = self.read_file("manager/project_plan.md")
        
        if not requirements or not project_plan:
            rprint("[red]Error: Missing input files[/red]")
            return False
        
        # Step 1: system_design.md
        rprint("[cyan]Writing system_design.md...[/cyan]")
        system_design = self._write_system_design(requirements, project_plan)
        if not system_design:
            return False
        self.write_file("architect/system_design.md", system_design)
        
        # Step 2: data_flow.md
        rprint("[cyan]Writing data_flow.md...[/cyan]")
        data_flow = self._write_data_flow(system_design)
        if not data_flow:
            return False
        self.write_file("architect/data_flow.md", data_flow)
        
        # Step 3: tech_requirements.md
        rprint("[cyan]Writing tech_requirements.md...[/cyan]")
        tech_req = self._write_tech_requirements(system_design)
        if not tech_req:
            return False
        self.write_file("architect/tech_requirements.md", tech_req)
        
        # Update memory with tech decisions
        self.update_memory({
            "tech_stack": {
                "frontend": "React 18.2.0",
                "backend": "FastAPI 0.104.1",
                "database": "PostgreSQL 15.3",
                "orm": "SQLAlchemy 2.0.23",
                "auth": "JWT",
                "migrations": "Alembic 1.12.1"
            },
            "conventions": {
                "primary_keys": "UUID",
                "base_api_url": "/api/v1",
                "error_format": "{ error: string, code: string }",
                "env_prefix": "APP_"
            }
        })
        
        rprint("\n[bold green]✅ Architect Agent Complete[/bold green]")
        return True
