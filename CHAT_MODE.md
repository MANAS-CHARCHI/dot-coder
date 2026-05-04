# Chat Mode - Interactive Project Assistant

## What is Chat Mode?

Chat Mode lets you **interact with your project** through natural conversation. You can:
- ✅ Ask questions about the project
- ✅ Request changes or improvements
- ✅ Get explanations of design decisions
- ✅ Learn how to modify specific parts
- ✅ Understand the codebase

## How to Use

### Option 1: From Main Menu

```bash
python main.py
```

When you have an existing project, choose option **3. Chat**

### Option 2: Direct Chat

```bash
python chat.py
```

This starts chat mode directly.

---

## Example Conversations

### Asking Questions

```
[You] What does this project do?

[Assistant] This is a Snake Game project. Based on the requirements, 
it's a classic snake game where players control a snake that grows 
longer as it eats food. The game includes:
- Real-time snake movement
- Food generation
- Collision detection
- Score tracking
...
```

```
[You] Explain the database schema

[Assistant] The database schema includes 3 main tables:

1. **users** - Stores player accounts
   - id (UUID, primary key)
   - username (string, unique)
   - email (string, unique)
   - created_at (timestamp)

2. **games** - Records each game session
   - id (UUID, primary key)
   - user_id (foreign key to users)
   - score (integer)
   - duration (integer, seconds)
   - played_at (timestamp)
...
```

### Requesting Changes

```
[You] I want to add multiplayer support

[Assistant] To add multiplayer support, you'll need to modify several parts:

**1. Database Changes:**
- Add a `game_sessions` table for multiplayer games
- Add a `game_players` junction table
- Modify in: `.coder/engineer/database/schema_plan.md`

**2. Backend Changes:**
- Add WebSocket support for real-time communication
- Create multiplayer game endpoints
- Modify: `.coder/engineer/backend/api_plan.md`

**3. Frontend Changes:**
- Add lobby/matchmaking UI
- Implement WebSocket client
- Modify: `.coder/engineer/frontend/ui_plan.md`

**How to regenerate:**
1. Edit the requirements to include multiplayer
2. Re-run specific agents:
   - DB Engineer
   - Backend Engineer
   - Frontend Engineer
   - Coder (all phases)

Would you like me to help you draft the updated requirements?
```

```
[You] How do I change from PostgreSQL to MongoDB?

[Assistant] To switch from PostgreSQL to MongoDB:

**1. Update Memory:**
Edit `.coder/orchestrator/memory.json`:
```json
{
  "tech_stack": {
    "database": "MongoDB",
    "orm": "Mongoose"  // instead of SQLAlchemy
  }
}
```

**2. Regenerate Database Layer:**
- Delete `.coder/engineer/database/`
- Delete `.coder/coder/db_code/`
- Re-run: DB Engineer agent
- Re-run: Coder (DB phase)

**3. Update Backend:**
- The backend will need to use Mongoose instead of SQLAlchemy
- Re-run: Backend Engineer
- Re-run: Coder (Backend phase)

**Commands:**
```bash
# Delete old database code
rm -rf .coder/engineer/database .coder/coder/db_code

# Re-run agents (feature coming soon)
# For now, start fresh with updated requirements
```
```

### Understanding the Code

```
[You] Show me the user authentication flow

[Assistant] The user authentication flow works like this:

**1. Registration (POST /api/v1/auth/register):**
```
User submits email + password
  ↓
Backend validates input
  ↓
Hash password with bcrypt
  ↓
Store in database (users table)
  ↓
Generate JWT token
  ↓
Return token to user
```

**2. Login (POST /api/v1/auth/login):**
```
User submits email + password
  ↓
Backend finds user by email
  ↓
Compare password hash
  ↓
If valid: generate JWT token
  ↓
Return token
```

**3. Protected Routes:**
```
User sends request with JWT in header
  ↓
Backend validates JWT
  ↓
Extract user_id from token
  ↓
Allow access to resource
```

**Files involved:**
- Auth routes: `.coder/coder/backend_code/routes/auth.py`
- User model: `.coder/coder/backend_code/models/user.py`
- JWT utils: `.coder/coder/backend_code/utils/jwt.py`
```

---

## Available Commands

While in chat mode:

| Command | Description |
|---------|-------------|
| `help` | Show help message |
| `context` | Show loaded project files |
| `reload` | Reload project files from disk |
| `exit` | Exit chat mode |

---

## What Chat Mode Can Do

### ✅ Answer Questions
- "What's the tech stack?"
- "How does feature X work?"
- "What files were generated?"
- "Explain the API endpoints"

### ✅ Explain Architecture
- "Why was PostgreSQL chosen?"
- "How is the frontend structured?"
- "What's the data flow for user registration?"

### ✅ Guide Changes
- "How do I add a new feature?"
- "What needs to change to support X?"
- "Which agents do I need to re-run?"

### ✅ Provide Instructions
- "How to deploy this?"
- "How to run tests?"
- "How to add a new API endpoint?"

### ❌ What It Can't Do (Yet)
- Actually modify files (you need to do that manually)
- Re-run agents automatically (coming soon)
- Execute code or tests

---

## Tips for Best Results

1. **Be Specific**
   - ❌ "Change the database"
   - ✅ "How do I change from PostgreSQL to MongoDB?"

2. **Reference Files**
   - "Explain the api_plan.md"
   - "What's in the system_design?"

3. **Ask Follow-ups**
   - Chat maintains conversation history
   - Build on previous questions

4. **Use Context Command**
   - Type `context` to see what files are loaded
   - Type `reload` after making manual changes

---

## Future Enhancements

Coming soon:
- 🔧 **Auto-apply changes** - Chat can modify files directly
- 🔄 **Re-run agents** - Chat can trigger specific agents
- 📝 **Generate code** - Chat can write new features
- 🧪 **Run tests** - Chat can execute and debug
- 💾 **Save conversations** - Export chat history

---

## Example Session

```bash
$ python chat.py

╭─────────────────────────────────────────╮
│ 💬 Chat                                 │
│                                         │
│ Interactive Chat Mode                   │
│                                         │
│ Project: Snake Game                     │
│ Files loaded: 8                         │
│                                         │
│ Ask questions, request changes, or get  │
│ help!                                   │
│ Type 'exit' to quit, 'help' for        │
│ commands.                               │
╰─────────────────────────────────────────╯

[You] What's the tech stack?

[Assistant] The tech stack for this project is:

**Frontend:**
- React 18.2.0
- Tailwind CSS for styling
- Axios for API calls

**Backend:**
- FastAPI 0.104.1 (Python)
- SQLAlchemy 2.0.23 (ORM)
- Alembic for migrations
- JWT for authentication

**Database:**
- PostgreSQL 15.3

**Development:**
- Python 3.11+
- Node.js 18+
- npm/yarn for frontend packages

[You] How do I add a leaderboard feature?

[Assistant] To add a leaderboard feature, here's what you need to do:

[... detailed explanation ...]

[You] exit

Goodbye!
```

---

**Version:** 2.1  
**Status:** ✅ Available  
**Command:** `python chat.py` or `python main.py` → option 3
