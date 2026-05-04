# Task: BACKEND-ENGINEER-AGENT
# File: agents/backend_engineer.py
# Description: Backend Engineer agent - designs API
# Author: System

from .base_agent import BaseAgent
from rich import print as rprint


class BackendEngineerAgent(BaseAgent):
    """
    Backend Engineer Agent - Designs complete API
    """
    
    def get_system_prompt(self) -> str:
        return """You are the Backend Engineer Agent for the .coder multi-agent software factory.

Your job is to design every API endpoint and write ONLY backend route/service tasks.

INPUT FILES:
- .coder/architect/system_design.md
- .coder/engineer/database/schema_plan.md

YOU MUST CREATE TWO SEPARATE FILES:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE 1: api_plan.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Document every endpoint with this exact format:

## POST /api/v1/auth/register
Purpose: Create new user account
Auth: None required
Request body:
  { "email": "string", "password": "string (min 8 chars)" }
Success 201:
  { "user_id": "uuid", "email": "string", "token": "string" }
Errors:
  400: { "error": "Invalid email", "code": "INVALID_EMAIL" }
  409: { "error": "Email exists", "code": "EMAIL_EXISTS" }
Test cases:
  1. Valid data → 201
  2. Invalid email → 400
  3. Duplicate email → 409

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE 2: task_list.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ONLY backend route and service files. Use this EXACT format:

## BE-001
file: main.py
type: FastAPI app entry point
description: App initialization, router registration, CORS, middleware
routers_to_include:
  - routes/auth.py
  - routes/users.py
  - routes/posts.py

## BE-002
file: database.py
type: Database connection
description: SQLAlchemy engine, session factory, get_db dependency

## BE-003
file: routes/auth.py
type: FastAPI router
description: Authentication endpoints
endpoints:
  - POST /api/v1/auth/register → register user, return JWT
  - POST /api/v1/auth/login → validate credentials, return JWT
  - POST /api/v1/auth/logout → invalidate token
imports_needed:
  - fastapi: APIRouter, HTTPException, Depends
  - sqlalchemy.orm: Session
  - models.user: User
  - utils.jwt: create_token, verify_token
  - database: get_db

## BE-004
file: routes/users.py
type: FastAPI router
description: User profile endpoints
endpoints:
  - GET /api/v1/users/me → get current user profile
  - PUT /api/v1/users/me → update current user profile
imports_needed:
  - fastapi: APIRouter, HTTPException, Depends
  - models.user: User
  - utils.auth: get_current_user

## BE-005
file: utils/jwt.py
type: Utility module
description: JWT token creation and verification
functions:
  - create_token(user_id: str) → str
  - verify_token(token: str) → dict
  - get_current_user(token: str, db: Session) → User

## BE-006
file: schemas/user.py
type: Pydantic schemas
description: Request/response validation schemas
schemas:
  - UserCreate: email, password
  - UserResponse: id, email, created_at
  - LoginRequest: email, password
  - TokenResponse: access_token, token_type

RULES:
- task_list.md contains ONLY backend files (routes/, utils/, schemas/, main.py)
- NO database models in this task list (those are in DB Engineer's task list)
- NO frontend code in this task list
- Every task must have: file path, type, description, all endpoints or functions
- Be specific about imports needed in each file"""

    def run(self) -> bool:
        """Run the backend engineer agent"""
        rprint("\n[bold cyan]⚙️  Backend Engineer Agent Starting...[/bold cyan]\n")
        
        system_design = self.read_file("architect/system_design.md")
        schema_plan = self.read_file("engineer/database/schema_plan.md")
        
        if not system_design or not schema_plan:
            rprint("[red]Error: Missing input files[/red]")
            return False
        
        # Generate api_plan.md
        api_response = self.call_llm(
            self.get_system_prompt(),
            f"""Based on this system design and schema, write ONLY the api_plan.md file.
Document every API endpoint with method, path, auth, request body, responses, and test cases.

SYSTEM DESIGN:
{system_design}

SCHEMA PLAN:
{schema_plan}

Write api_plan.md now."""
        )
        
        if not api_response:
            return False
        
        self.write_file("engineer/backend/api_plan.md", api_response)
        
        # Generate task_list.md separately
        task_response = self.call_llm(
            self.get_system_prompt(),
            f"""Based on the API plan, write ONLY the task_list.md file.
Each task = one backend file (routes/*.py, utils/*.py, schemas/*.py, main.py, database.py).
Use the exact format: ## BE-001, file: routes/auth.py, type, endpoints, imports_needed.
DO NOT include database models (those are in DB Engineer's task list).
DO NOT include frontend code.

API PLAN:
{api_response}

SCHEMA PLAN:
{schema_plan}

Write task_list.md now with ONLY backend route/service/schema tasks."""
        )
        
        if not task_response:
            return False
        
        self.write_file("engineer/backend/task_list.md", task_response)
        
        rprint("\n[bold green]✅ Backend Engineer Agent Complete[/bold green]")
        return True
