# Task: DB-ENGINEER-AGENT
# File: agents/db_engineer.py
# Description: DB Engineer agent - designs database schema
# Author: System

from .base_agent import BaseAgent
from rich import print as rprint


class DBEngineerAgent(BaseAgent):
    """
    DB Engineer Agent - Designs complete database schema
    """
    
    def get_system_prompt(self) -> str:
        return """You are the DB Engineer Agent for the .coder multi-agent software factory.

Your job is to design the complete database schema and write ONLY database model tasks.

INPUT FILES:
- .coder/architect/system_design.md
- .coder/architect/data_flow.md

YOU MUST CREATE TWO SEPARATE FILES:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE 1: schema_plan.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Document every table with this exact format:

## Table: users
Purpose: Stores user accounts
Columns:
- id: UUID PRIMARY KEY DEFAULT gen_random_uuid()
- email: VARCHAR(255) UNIQUE NOT NULL
- password_hash: VARCHAR(255) NOT NULL
- created_at: TIMESTAMP DEFAULT NOW()
Indexes:
- idx_users_email ON users(email)
Foreign Keys: none

## Table: posts
Purpose: Stores blog posts
Columns:
- id: SERIAL PRIMARY KEY
- user_id: UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE
- title: VARCHAR(255) NOT NULL
- content: TEXT NOT NULL
- created_at: TIMESTAMP DEFAULT NOW()
Indexes:
- idx_posts_user_id ON posts(user_id)
Foreign Keys:
- user_id → users.id

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE 2: task_list.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ONLY database model files. Use this EXACT format:

## DB-001
file: models/user.py
type: SQLAlchemy ORM model
table: users
columns:
  - id: UUID, primary_key=True
  - email: String(255), unique=True, nullable=False
  - password_hash: String(255), nullable=False
  - created_at: DateTime, default=datetime.utcnow
relationships:
  - posts: one-to-many

## DB-002
file: models/post.py
type: SQLAlchemy ORM model
table: posts
columns:
  - id: Integer, primary_key=True, autoincrement=True
  - user_id: UUID, ForeignKey('users.id'), nullable=False
  - title: String(255), nullable=False
  - content: Text, nullable=False
  - created_at: DateTime, default=datetime.utcnow
relationships:
  - user: many-to-one

RULES:
- task_list.md contains ONLY model files (models/*.py)
- NO routes, NO API endpoints, NO frontend code in this task list
- Every task must have: file path, type, table name, all columns with types
- Use SQLAlchemy types: String, Integer, UUID, Text, DateTime, Boolean, Float, JSON
- Include all relationships (one-to-many, many-to-one, many-to-many)
- Also create: models/database.py (engine + session setup)"""

    def run(self) -> bool:
        """Run the DB engineer agent"""
        rprint("\n[bold cyan]🗄️  DB Engineer Agent Starting...[/bold cyan]\n")
        
        system_design = self.read_file("architect/system_design.md")
        data_flow = self.read_file("architect/data_flow.md")
        
        if not system_design or not data_flow:
            rprint("[red]Error: Missing input files[/red]")
            return False
        
        # Generate schema_plan.md
        schema_response = self.call_llm(
            self.get_system_prompt(),
            f"""Based on this system design, write ONLY the schema_plan.md file.
Document every database table with columns, types, constraints, indexes, and foreign keys.

SYSTEM DESIGN:
{system_design}

DATA FLOW:
{data_flow}

Write schema_plan.md now."""
        )
        
        if not schema_response:
            return False
        
        self.write_file("engineer/database/schema_plan.md", schema_response)
        
        # Generate task_list.md separately
        task_response = self.call_llm(
            self.get_system_prompt(),
            f"""Based on the schema plan, write ONLY the task_list.md file.
Each task = one SQLAlchemy model file in models/ folder.
Use the exact format: ## DB-001, file: models/user.py, type, columns, relationships.
DO NOT include routes, API endpoints, or frontend code.

SCHEMA PLAN:
{schema_response}

Write task_list.md now with ONLY database model tasks."""
        )
        
        if not task_response:
            return False
        
        self.write_file("engineer/database/task_list.md", task_response)
        
        rprint("\n[bold green]✅ DB Engineer Agent Complete[/bold green]")
        return True
