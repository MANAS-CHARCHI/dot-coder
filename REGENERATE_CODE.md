# Regenerate Code Feature

## What is it?

The **Regenerate Code** feature lets you re-run the Coder agents while keeping all your planning intact. This is useful when:
- ❌ Code was generated with wrong file extensions (.txt instead of .py)
- ❌ File names are generic (file_0.txt, file_1.txt)
- ❌ Folder structure is incorrect
- ✅ But the planning (requirements, architecture, designs) is good

## How to Use

### From Main Menu

```bash
python main.py
```

When you have an existing project, choose option **3. Regenerate Code**

### What It Does

1. ✅ **Keeps** all planning:
   - Sales requirements
   - Manager project plan
   - Architect system design
   - Engineer task lists (DB, Backend, Frontend)

2. ❌ **Deletes** only code outputs:
   - `.coder/coder/` (all generated code)
   - `.coder/reviewer/` (review results)
   - `.coder/tester/` (test results)

3. 🔄 **Re-runs** from Coder phase:
   - Coder (DB) - with improved prompts
   - Coder (Backend) - with improved prompts
   - Coder (Frontend) - with improved prompts
   - Reviewer
   - Tester
   - Delivery

### Improved File Naming

The Coder agent now has **enhanced prompts** that ensure:
- ✅ Proper file extensions (.py, .jsx, .tsx, .css, etc.)
- ✅ Proper folder structure (models/, routes/, components/)
- ✅ Descriptive filenames (user.py, auth.py, App.jsx)
- ✅ Complete imports in every file
- ❌ No more .txt files!
- ❌ No more generic names like file_0, file_1

## Example

### Before Regeneration

```
.coder/coder/backend_code/
├── file_0.txt    ❌ Wrong extension
├── file_1.txt    ❌ Wrong extension
├── file_2.txt    ❌ Wrong extension
└── output.txt    ❌ Wrong extension
```

### After Regeneration

```
.coder/coder/backend_code/
├── models/
│   ├── user.py          ✅ Proper name & extension
│   ├── game.py          ✅ Proper name & extension
│   └── score.py         ✅ Proper name & extension
├── routes/
│   ├── auth.py          ✅ Proper name & extension
│   ├── game.py          ✅ Proper name & extension
│   └── user.py          ✅ Proper name & extension
├── utils/
│   ├── jwt.py           ✅ Proper name & extension
│   └── database.py      ✅ Proper name & extension
└── main.py              ✅ Proper name & extension
```

## When to Use

### ✅ Use Regenerate Code When:
- Files have wrong extensions (.txt instead of .py)
- File names are generic (file_0, file_1)
- Missing imports in files
- Code structure is messy
- But planning is correct

### ❌ Don't Use When:
- Requirements are wrong → Use "Start Fresh"
- Architecture needs changes → Use "Start Fresh"
- Tech stack is wrong → Use "Start Fresh"

## Step-by-Step

1. **Run main.py**
   ```bash
   python main.py
   ```

2. **Choose option 3**
   ```
   Your choice (1-6): 3
   ```

3. **Confirm**
   ```
   🔄 Regenerate Code

   This will:
     ✓ Keep all planning (requirements, architecture, designs)
     ✓ Delete existing code
     ✓ Re-run Coder agents with improved file naming
     ✓ Generate proper .py, .jsx, .tsx files (not .txt)

   Continue? (yes/no): yes
   ```

4. **Wait for completion**
   - Coder agents will re-run
   - Files will be generated with proper names
   - Pipeline continues to testing and delivery

5. **Check results**
   ```bash
   ls -la .coder/coder/backend_code/
   ```

## What Gets Reset

| Component | Status |
|-----------|--------|
| Sales requirements | ✅ Kept |
| Manager plan | ✅ Kept |
| Architect design | ✅ Kept |
| DB Engineer schema | ✅ Kept |
| Backend Engineer API | ✅ Kept |
| Frontend Engineer UI | ✅ Kept |
| **Coder output** | ❌ **Deleted & Regenerated** |
| **Reviewer results** | ❌ **Deleted & Regenerated** |
| **Tester results** | ❌ **Deleted & Regenerated** |
| **Delivery report** | ❌ **Deleted & Regenerated** |

## Pipeline State

The pipeline state is reset for these steps:
- `coder_db` → pending
- `coder_backend` → pending
- `coder_frontend` → pending
- `reviewer_backend` → pending
- `reviewer_frontend` → pending
- `tester_backend` → pending
- `tester_frontend` → pending
- `final_tester` → pending
- `delivery` → pending

All other steps remain "done".

## Improved Coder Prompts

The Coder agent now has **explicit instructions** for:

### File Extensions
- Python: `.py`
- React: `.jsx` or `.tsx`
- TypeScript: `.ts` or `.tsx`
- Styles: `.css`
- Config: `.json`, `.yaml`, `.toml`

### Folder Structure
- Python: `models/`, `routes/`, `utils/`, `services/`
- React: `components/`, `pages/`, `hooks/`, `utils/`
- Shared: `config/`, `tests/`, `docs/`

### File Format
Every file must use:
```
=== FILE: folder/filename.ext ===
[complete code with imports]
=== END FILE ===
```

### Mandatory Requirements
- ✅ All imports included
- ✅ Complete implementations
- ✅ Error handling
- ✅ Type hints/types
- ❌ No TODOs
- ❌ No placeholders

## Troubleshooting

### Still getting .txt files?

The Coder agent has multiple fallback parsers. If the LLM doesn't use the `=== FILE: ===` format, it tries to:
1. Find filenames in code block comments
2. Extract filenames from context
3. Infer extensions from content

If still getting .txt files, the LLM might not be following instructions. Try:
- Running regenerate again
- Checking if a different model works better
- Manually editing the task lists to be more explicit

### Files in wrong folders?

Check the Engineer task lists:
- `.coder/engineer/database/task_list.md`
- `.coder/engineer/backend/task_list.md`
- `.coder/engineer/frontend/task_list.md`

Make sure they specify proper file paths.

### Missing imports?

The Reviewer should catch this. If not, the improved Coder prompt now emphasizes including all imports.

## Future Enhancements

Coming soon:
- 🔧 Regenerate specific phases only (just backend, just frontend)
- 📝 Edit task lists before regenerating
- 🎯 Target specific files to regenerate
- 🔄 Automatic retry if file naming fails

---

**Version:** 2.1  
**Status:** ✅ Available  
**Command:** `python main.py` → option 3
