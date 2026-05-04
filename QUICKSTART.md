# Quick Start Guide

Get .coder running in 5 minutes.

---

## Step 1: Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

## Step 2: Install Dependencies

```bash
uv sync
```

This installs:
- `google-genai` — Gemini API client
- `python-dotenv` — Environment variable management
- `rich` — Beautiful terminal output

---

## Step 3: Get Gemini API Key

1. Go to https://aistudio.google.com/apikey
2. Click "Create API Key"
3. Copy the key

---

## Step 4: Configure Environment

```bash
# Copy example file
cp .env.example .env

# Edit .env and paste your API key
# GEMINI_API_KEY=your_actual_key_here
```

---

## Step 5: Run It!

```bash
python main.py
```

---

## What Happens Next?

1. **Sales Agent** asks you questions about what you want to build
2. You answer one question at a time (max 8-10 exchanges)
3. **Checkpoint 1**: Review requirements, approve or modify
4. **Manager** creates project plan
5. **Architect** makes all technical decisions
6. **Checkpoint 2**: Review architecture, approve or modify
7. **DB Engineer** designs database schema
8. **Backend Engineer** designs API
9. **Frontend Engineer** designs UI
10. **Coder** writes all the code (3 phases)
11. **Reviewer** checks code quality
12. **Tester** writes and runs tests
13. **Checkpoint 3**: Review final tests, approve delivery
14. **Delivery** creates final report

Total time: 10-30 minutes depending on project complexity.

---

## Example Conversation

```
$ python main.py

.coder - Multi-Agent Software Factory

Let's build something!

Enter project name: Todo App

💼 Sales Agent Starting...

Sales Agent: Hi! What do you want to build?

You: A simple todo app with user authentication

Sales Agent: Great! Who will use this app?

You: Small teams, 5-10 people per team

Sales Agent: What are the main features you need?

You: Users can create, edit, delete todos. Mark as complete. Filter by status.

Sales Agent: Any features explicitly OUT OF SCOPE?

You: No mobile app, no payments, no file attachments

Sales Agent: Expected scale - how many users and how much data?

You: Maybe 100 users total, a few thousand todos

Sales Agent: Frontend preference? React, Vue, plain HTML, or no preference?

You: React

Sales Agent: Backend preference? Python, Node, or other?

You: Python with FastAPI

Sales Agent: What kind of data will you store?

You: User accounts, todos with title/description/status/due date

Sales Agent: Need user authentication?

You: Yes, JWT tokens

Sales Agent: Any third-party services? Payments, email, file storage?

You: No

Sales Agent: Perfect! Here's what I understood:
- Todo app for small teams
- React frontend + Python FastAPI backend
- User auth with JWT
- CRUD operations on todos
- No mobile, payments, or files

Is this correct?

You: yes

[Model selection screen appears]

Choose:
1. Use recommended models (higher quality)
2. Use budget models (lower cost)
3. Use Gemini 2.5 Flash-Lite for all (free)

Your choice (1/2/3): 3

✅ Sales Agent Complete

🛑 Checkpoint: Requirements Review
Review the requirements in .coder/sales/requirements.md
Type 'yes' to continue, 'no' to stop, or 'change' to modify:

> yes

📋 Manager Agent Starting...
[... continues ...]
```

---

## Troubleshooting

### "GEMINI_API_KEY not set"

Make sure:
1. You created `.env` file (not `.env.example`)
2. You added your actual API key
3. No spaces around the `=` sign

### "Module not found"

Run `uv sync` again to install dependencies.

### Pipeline stuck or crashed

The pipeline saves state after every step. Just run `python main.py` again and it will ask if you want to resume.

### Want to start over?

Delete the `.coder/` folder:

```bash
rm -rf .coder/
python main.py
```

---

## What You Get

After the pipeline completes, check `.coder/delivery/final_report.md`.

It includes:
- Complete project summary
- All code files organized by layer
- Exact setup instructions
- How to run the application
- Test results
- Next steps

All code is in:
- `.coder/coder/db_code/` — Database models
- `.coder/coder/backend_code/` — API endpoints
- `.coder/coder/frontend_code/` — React components

---

## Next Steps

1. Copy code from `.coder/coder/` to your actual project
2. Follow setup instructions in `final_report.md`
3. Run tests
4. Deploy!

Or run the pipeline again with a different project idea.

---

## Tips

- **Be specific** in your answers to the Sales Agent
- **Review carefully** at checkpoints — wrong assumptions caught early save time
- **Use "change"** at checkpoints to manually edit files if needed
- **Check event log** (`.coder/orchestrator/event_log.json`) to see exactly what happened
- **Check memory.json** to see all shared decisions

---

## Need Help?

- Check the full README.md for architecture details
- Check `.coder/orchestrator/event_log.json` for what went wrong
- Open an issue on GitHub

---

Happy building! 🚀
