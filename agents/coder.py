# Task: CODER-AGENT
# File: agents/coder.py
# Description: Coder agent - writes actual code
# Author: System

from .base_agent import BaseAgent
from rich import print as rprint
import re


class CoderAgent(BaseAgent):
    """
    Coder Agent - Writes actual code files
    """
    
    def get_system_prompt(self) -> str:
        return """You are the Coder Agent for the .coder multi-agent software factory.

Your job is to write complete, working code files with proper filenames and extensions.

⚠️ CRITICAL: You MUST use proper file extensions (.py, .js, .jsx, .tsx, .css, .html, etc.)
⚠️ NEVER use .txt files for code!

OUTPUT FORMAT - Use this EXACT format for EVERY file:

=== FILE: folder/filename.ext ===
[complete file content with all imports]
=== END FILE ===

EXAMPLES OF CORRECT FORMAT:

=== FILE: models/user.py ===
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
=== END FILE ===

=== FILE: routes/auth.py ===
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models.user import User
from database import get_db
import bcrypt

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register")
async def register(email: str, password: str, db: Session = Depends(get_db)):
    # Check if user exists
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already exists")
    
    # Hash password
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    
    # Create user
    user = User(email=email, password_hash=hashed.decode())
    db.add(user)
    db.commit()
    
    return {"message": "User created", "user_id": user.id}
=== END FILE ===

=== FILE: components/App.jsx ===
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        fetchUser();
    }, []);
    
    const fetchUser = async () => {
        try {
            const response = await axios.get('/api/v1/user/me');
            setUser(response.data);
        } catch (error) {
            console.error('Failed to fetch user:', error);
        } finally {
            setLoading(false);
        }
    };
    
    if (loading) return <div>Loading...</div>;
    
    return (
        <div className="app">
            <h1>Welcome {user?.email}</h1>
        </div>
    );
}

export default App;
=== END FILE ===

FILE NAMING RULES:
1. Python files: .py (models/user.py, routes/auth.py, utils/jwt.py)
2. React components: .jsx or .tsx (components/App.jsx, pages/Home.tsx)
3. TypeScript: .ts or .tsx (types/user.ts, hooks/useAuth.tsx)
4. Stylesheets: .css (styles/main.css, components/Button.css)
5. Config files: .json, .yaml, .toml (package.json, config.yaml)
6. Use proper folder structure: models/, routes/, components/, utils/, etc.

MANDATORY REQUIREMENTS:
✅ Include ALL imports at the top of each file
✅ Use proper file extensions (NEVER .txt)
✅ Use proper folder structure
✅ Complete implementations (NO TODOs or placeholders)
✅ Include error handling
✅ Add type hints (Python) or types (TypeScript)
✅ Follow conventions from memory.json

❌ NEVER:
- Use .txt extension for code files
- Leave functions unimplemented
- Skip imports
- Use generic names like "file_0", "file_1"
- Forget the === FILE: === markers

Write ALL files for the task list using the === FILE: folder/filename.ext === format."""

    def run(self) -> bool:
        """Run the coder agent"""
        # Determine which phase we're in based on agent name
        if "db" in self.name:
            phase = "database"
            output_dir = "coder/db_code"
            task_list_path = "engineer/database/task_list.md"
            phase_label = "DATABASE MODELS ONLY"
            file_types = "Python SQLAlchemy model files (.py) in models/ folder"
        elif "backend" in self.name:
            phase = "backend"
            output_dir = "coder/backend_code"
            task_list_path = "engineer/backend/task_list.md"
            phase_label = "BACKEND API ONLY"
            file_types = "Python FastAPI files (.py) in routes/, utils/, schemas/ folders"
        elif "frontend" in self.name:
            phase = "frontend"
            output_dir = "coder/frontend_code"
            task_list_path = "engineer/frontend/task_list.md"
            phase_label = "FRONTEND ONLY"
            file_types = "React files (.jsx, .tsx, .js, .css) in src/ folder"
        else:
            rprint("[red]Error: Unknown coder phase[/red]")
            return False
        
        rprint(f"\n[bold cyan]💻 Coder Agent Starting ({phase})...[/bold cyan]\n")
        
        # Read task list
        task_list = self.read_file(task_list_path)
        
        if not task_list:
            rprint(f"[red]Error: {task_list_path} not found[/red]")
            return False
        
        # Create prompt
        user_message = f"""You are writing {phase_label} code.

TASK LIST:
{task_list}

MEMORY (tech stack):
{self.memory}

INSTRUCTIONS:
- Write ONLY {file_types}
- Use the EXACT === FILE: path/filename.ext === format
- Include ALL imports in every file
- Write complete, working code

OUTPUT EACH FILE LIKE THIS:

=== FILE: models/user.py ===
from sqlalchemy import Column, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
=== END FILE ===

Now write ALL files from the task list above."""

        # Call LLM
        response = self.call_llm(self.get_system_prompt(), user_message)
        
        if not response:
            return False
        
        # Parse response and extract files
        files = self._parse_files_from_response(response)
        
        if not files:
            rprint("[yellow]Warning: No files parsed from response[/yellow]")
            self.write_file(f"{output_dir}/raw_output.txt", response)
            return False
        
        # Validate that files have proper extensions
        valid_files = {}
        for file_path, content in files.items():
            if file_path.endswith('.txt') and len(files) > 1:
                rprint(f"[yellow]Warning: Skipping .txt file: {file_path}[/yellow]")
                continue
            valid_files[file_path] = content
        
        if not valid_files:
            rprint("[red]Error: No valid code files generated[/red]")
            return False
        
        # Write files
        for file_path, content in valid_files.items():
            self.write_file(f"{output_dir}/{file_path}", content)
        
        rprint(f"[green]✓ Wrote {len(valid_files)} files[/green]")
        
        rprint(f"\n[bold green]✅ Coder Agent Complete ({phase})[/bold green]")
        return True
    
    def _parse_files_from_response(self, response: str) -> dict:
        """Parse files from LLM response"""
        files = {}
        
        # Method 1: Try to find file markers (=== FILE: path ===)
        pattern = r"===\s*FILE:\s*(.+?)\s*===\s*\n(.*?)\n===\s*END FILE\s*==="
        matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)
        
        for file_path, content in matches:
            files[file_path.strip()] = content.strip()
        
        if files:
            rprint(f"[green]✓ Parsed {len(files)} files using FILE markers[/green]")
            return files
        
        # Method 2: Try to find markdown code blocks with filenames in comments
        # Look for patterns like: # File: models/user.py or // File: components/App.tsx
        pattern = r"```(?:python|javascript|typescript|jsx|tsx)?\n(?:#|//)\s*(?:File|file|FILE):\s*(.+?)\n(.*?)```"
        matches = re.findall(pattern, response, re.DOTALL)
        
        for file_path, content in matches:
            files[file_path.strip()] = content.strip()
        
        if files:
            rprint(f"[green]✓ Parsed {len(files)} files from code block comments[/green]")
            return files
        
        # Method 2.5: Look for filename in first few lines of code blocks
        pattern = r"```(?:python|javascript|typescript|jsx|tsx)?\n(.*?)```"
        matches = re.findall(pattern, response, re.DOTALL)
        
        for content in matches:
            lines = content.strip().split('\n')
            filename = None
            
            # Check first 3 lines for filename patterns
            for line in lines[:3]:
                # Look for # File: path or // File: path
                match = re.search(r'(?:#|//)\s*(?:File|file|FILE):\s*(.+)', line)
                if match:
                    filename = match.group(1).strip()
                    break
                # Look for # Task: ... File: path
                match = re.search(r'(?:#|//)\s*Task:.*File:\s*(.+)', line)
                if match:
                    filename = match.group(1).strip()
                    break
            
            if filename:
                files[filename] = content.strip()
        
        if files:
            rprint(f"[green]✓ Parsed {len(files)} files from content comments[/green]")
            return files
        
        # Method 3: Try to find code blocks with language hints and extract filenames from preceding text
        lines = response.split('\n')
        current_filename = None
        in_code_block = False
        code_content = []
        
        for i, line in enumerate(lines):
            # Check if this line mentions a filename
            if not in_code_block:
                # Look for patterns like "models/user.py:", "File: app.py", "Creating main.py"
                filename_match = re.search(r'(?:File:|Creating|Writing|file:)\s*([a-zA-Z0-9_/\-\.]+\.(py|js|jsx|tsx|ts|css|html|json))', line, re.IGNORECASE)
                if filename_match:
                    current_filename = filename_match.group(1)
                # Also check for just a filename followed by colon
                elif re.match(r'^([a-zA-Z0-9_/\-\.]+\.(py|js|jsx|tsx|ts|css|html|json)):\s*$', line.strip()):
                    current_filename = line.strip().rstrip(':')
            
            # Check for code block start
            if line.strip().startswith('```'):
                if not in_code_block:
                    in_code_block = True
                    code_content = []
                else:
                    # End of code block
                    in_code_block = False
                    if current_filename and code_content:
                        files[current_filename] = '\n'.join(code_content).strip()
                        current_filename = None
            elif in_code_block:
                code_content.append(line)
        
        if files:
            rprint(f"[green]✓ Parsed {len(files)} files from context[/green]")
            return files
        
        # Method 4: Last resort - extract all code blocks and try to infer filenames
        pattern = r"```(?:python|javascript|typescript|jsx|tsx)?\n(.*?)```"
        matches = re.findall(pattern, response, re.DOTALL)
        
        if matches:
            rprint(f"[yellow]⚠️  Found {len(matches)} code blocks but no filenames. Using generic names.[/yellow]")
            
            for i, content in enumerate(matches):
                # Try to infer file extension from content
                content_stripped = content.strip()
                
                # Check for Python
                if 'import ' in content_stripped or 'def ' in content_stripped or 'class ' in content_stripped:
                    ext = 'py'
                # Check for React/JSX
                elif 'import React' in content_stripped or 'export default' in content_stripped or '<' in content_stripped and '>' in content_stripped:
                    ext = 'jsx'
                # Check for TypeScript
                elif 'interface ' in content_stripped or ': string' in content_stripped or ': number' in content_stripped:
                    ext = 'tsx' if '<' in content_stripped else 'ts'
                # Check for CSS
                elif '{' in content_stripped and '}' in content_stripped and ':' in content_stripped and ';' in content_stripped:
                    ext = 'css'
                else:
                    ext = 'txt'
                
                files[f"file_{i}.{ext}"] = content_stripped
        
        return files
