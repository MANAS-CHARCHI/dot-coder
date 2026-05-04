# Task: FRONTEND-ENGINEER-AGENT
# File: agents/frontend_engineer.py
# Description: Frontend Engineer agent - designs UI
# Author: System

from .base_agent import BaseAgent
from rich import print as rprint


class FrontendEngineerAgent(BaseAgent):
    """
    Frontend Engineer Agent - Designs complete UI
    """
    
    def get_system_prompt(self) -> str:
        return """You are the Frontend Engineer Agent for the .coder multi-agent software factory.

Your job is to design every page and component and write ONLY frontend tasks.

INPUT FILES:
- .coder/architect/system_design.md
- .coder/engineer/backend/api_plan.md

YOU MUST CREATE TWO SEPARATE FILES:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE 1: ui_plan.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Document every page with this exact format:

## Page: /login
Purpose: User login form
Components: LoginForm, ErrorMessage, LoadingSpinner
API calls:
  - POST /api/v1/auth/login (on form submit)
State:
  - email: string
  - password: string
  - loading: boolean
  - error: string | null
On success: store token in localStorage, redirect to /dashboard
On error: show error message, keep form filled

## Page: /dashboard
Purpose: Main user dashboard
Components: Header, Sidebar, ContentArea, UserStats
API calls:
  - GET /api/v1/users/me (on mount)
  - GET /api/v1/posts (on mount)
State:
  - user: User | null
  - posts: Post[]
  - loading: boolean
On success: render user data and posts
On error: show error toast

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE 2: task_list.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ONLY frontend files. Use this EXACT format:

## FE-001
file: src/main.jsx
type: React app entry point
description: App initialization, router setup, global providers

## FE-002
file: src/App.jsx
type: React root component
description: Route definitions using React Router
routes:
  - / → pages/Home.jsx
  - /login → pages/Login.jsx
  - /register → pages/Register.jsx
  - /dashboard → pages/Dashboard.jsx (protected)
imports_needed:
  - react-router-dom: BrowserRouter, Routes, Route
  - pages/Home: Home
  - pages/Login: Login
  - context/AuthContext: AuthProvider

## FE-003
file: src/pages/Login.jsx
type: React page component
description: Login form with email/password
api_calls:
  - POST /api/v1/auth/login
state:
  - email: string (useState)
  - password: string (useState)
  - loading: boolean (useState)
  - error: string | null (useState)
on_success: save token to localStorage, navigate to /dashboard
on_error: display error message
imports_needed:
  - react: React, useState
  - react-router-dom: useNavigate
  - axios: axios
  - components/Button: Button
  - components/Input: Input

## FE-004
file: src/components/Button.jsx
type: React component
description: Reusable button with loading state
props:
  - children: ReactNode
  - onClick: function
  - loading: boolean
  - disabled: boolean
  - variant: 'primary' | 'secondary' | 'danger'

## FE-005
file: src/context/AuthContext.jsx
type: React context
description: Authentication state management
provides:
  - user: User | null
  - token: string | null
  - login(token): void
  - logout(): void
  - isAuthenticated: boolean

## FE-006
file: src/utils/api.js
type: Utility module
description: Axios instance with base URL and auth headers
exports:
  - api: axios instance with baseURL and interceptors
  - setAuthToken(token): void

RULES:
- task_list.md contains ONLY frontend files (src/pages/, src/components/, src/utils/, src/context/)
- NO Python files, NO backend routes, NO database models
- Every task must have: file path, type, description
- Specify exact imports needed in each file
- Use .jsx for React components, .js for utilities, .css for styles"""

    def run(self) -> bool:
        """Run the frontend engineer agent"""
        rprint("\n[bold cyan]🎨 Frontend Engineer Agent Starting...[/bold cyan]\n")
        
        system_design = self.read_file("architect/system_design.md")
        api_plan = self.read_file("engineer/backend/api_plan.md")
        
        if not system_design or not api_plan:
            rprint("[red]Error: Missing input files[/red]")
            return False
        
        # Generate ui_plan.md
        ui_response = self.call_llm(
            self.get_system_prompt(),
            f"""Based on this system design and API plan, write ONLY the ui_plan.md file.
Document every page with route, purpose, components, API calls, state, and behavior.

SYSTEM DESIGN:
{system_design}

API PLAN:
{api_plan}

Write ui_plan.md now."""
        )
        
        if not ui_response:
            return False
        
        self.write_file("engineer/frontend/ui_plan.md", ui_response)
        
        # Generate task_list.md separately
        task_response = self.call_llm(
            self.get_system_prompt(),
            f"""Based on the UI plan, write ONLY the task_list.md file.
Each task = one frontend file (src/pages/*.jsx, src/components/*.jsx, src/utils/*.js, etc.).
Use the exact format: ## FE-001, file: src/pages/Login.jsx, type, description, imports_needed.
DO NOT include Python files, backend routes, or database models.

UI PLAN:
{ui_response}

API PLAN:
{api_plan}

Write task_list.md now with ONLY frontend React/JS/CSS tasks."""
        )
        
        if not task_response:
            return False
        
        self.write_file("engineer/frontend/task_list.md", task_response)
        
        rprint("\n[bold green]✅ Frontend Engineer Agent Complete[/bold green]")
        return True
