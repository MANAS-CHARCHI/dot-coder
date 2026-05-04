# Task: BASE-AGENT
# File: agents/base_agent.py
# Description: Base class for all agents with common functionality
# Author: System

import json
from pathlib import Path
from typing import Dict, List, Optional
from rich import print as rprint

from llm import call_llm


class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self, name: str, memory: dict, retry_count: int = 0):
        self.name = name
        self.memory = memory
        self.retry_count = retry_count
        self.base_path = Path(".coder")
        self.history = []
        
        # Get model from memory or use default
        from llm_call import DEFAULT_MODEL
        self.model = memory.get("model_selection", {}).get(name, DEFAULT_MODEL)
    
    def read_file(self, path: str) -> Optional[str]:
        """Read a file from .coder directory"""
        full_path = self.base_path / path
        if full_path.exists():
            return full_path.read_text()
        return None
    
    def write_file(self, path: str, content: str):
        """Write a file to .coder directory"""
        full_path = self.base_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        rprint(f"[green]✓ Wrote {path}[/green]")
    
    def update_memory(self, updates: dict):
        """Update shared memory"""
        memory_file = self.base_path / "orchestrator" / "memory.json"
        
        # Create directory if it doesn't exist
        memory_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load current memory or create new
        if memory_file.exists():
            try:
                current = json.loads(memory_file.read_text())
            except:
                # If file is corrupted, start fresh
                current = self._get_default_memory()
        else:
            current = self._get_default_memory()
        
        # Deep merge
        def merge(d1, d2):
            for key, value in d2.items():
                if key in d1 and isinstance(d1[key], dict) and isinstance(value, dict):
                    merge(d1[key], value)
                else:
                    d1[key] = value
        
        merge(current, updates)
        memory_file.write_text(json.dumps(current, indent=2))
        self.memory = current
    
    def _get_default_memory(self) -> dict:
        """Get default memory structure"""
        return {
            "project_name": None,
            "target_users": None,
            "out_of_scope": [],
            "tech_stack": {
                "frontend": None,
                "backend": None,
                "database": None,
                "orm": None,
                "auth": None,
                "migrations": None
            },
            "conventions": {
                "primary_keys": None,
                "base_api_url": None,
                "error_format": None,
                "env_prefix": None
            },
            "model_selection": {}
        }
    
    def call_llm(self, system_prompt: str, user_message: str) -> Optional[str]:
        """Call LLM with system prompt and user message"""
        self.history.append({
            "role": "user",
            "parts": [{"text": user_message}]
        })
        
        result = call_llm(
            system=system_prompt,
            history=self.history,
            agent=self.name,
            model=self.model
        )
        
        if result.get("error"):
            rprint(f"[red]LLM Error: {result['error']}[/red]")
            return None
        
        reply = result.get("reply")
        if reply:
            self.history.append({
                "role": "model",
                "parts": [{"text": reply}]
            })
        
        return reply
    
    def get_system_prompt(self) -> str:
        """Override in subclass to provide agent-specific system prompt"""
        raise NotImplementedError
    
    def run(self) -> bool:
        """Override in subclass to implement agent logic"""
        raise NotImplementedError
