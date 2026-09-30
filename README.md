# FitBuddy — AI Fitness Plan Generator

FitBuddy is a FastAPI + Jinja2 + SQLite application that generates personalized 7-day workout plans and nutrition/recovery tips with Gemini. It also supports feedback-driven plan regeneration and an admin/coach dashboard.

## Project structure

```text
fitbuddy/
├── app/
│   ├── __init__.py
│   ├── ai.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── routes.py
│   └── schemas.py
├── static/css/style.css
├── templates/
│   ├── index.html
│   ├── result.html
│   └── all_users.html
├── tests/test_app.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## VS Code setup

1. Install Python 3.11+ and VS Code.
2. Extract/open the `fitbuddy` folder in VS Code.
3. Create a virtual environment:

Windows PowerShell:
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

4. Install packages:
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

5. Create environment file:
```text
Copy .env.example to .env
```

6. Put your Gemini API key in `.env`:
```env
GEMINI_API_KEY=your_real_key
```

For a no-key smoke test, use:
```env
MOCK_AI=true
```

## Run

```bash
uvicorn app.main:app --reload
```

Open:
- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/health
- http://127.0.0.1:8000/view-all-users

## Test

With the virtual environment active:
```bash
pytest -q
```

The included tests run in mock-AI mode so they do not consume Gemini quota. If a test database already exists, it can be removed with `rm test_fitbuddy.db` (or delete the file in Explorer) before rerunning.

## API

### POST /generate-workout
Form fields:
- name
- user_id
- age
- weight
- goal
- intensity

### POST /submit-feedback
Form fields:
- user_id
- feedback

### GET /view-all-users
Shows registered users and original/updated plans.

### POST /delete-user
Deletes a user and associated plans.

## Notes

The supplied project document specifies Gemini 1.5 Pro and Gemini Flash. Those model names are no longer the safest default for a new 2026 implementation, so this implementation uses the current Google GenAI SDK and configurable model names. Change `WORKOUT_MODEL` and `NUTRITION_MODEL` in `.env` if your Gemini account requires different models.

This application provides fitness-planning assistance, not medical diagnosis or treatment. Users should stop exercise if they experience pain or concerning symptoms and seek qualified professional advice when appropriate.
