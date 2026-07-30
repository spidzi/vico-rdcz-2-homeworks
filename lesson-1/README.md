# Lesson 1 Homework

This project demonstrates an OpenAI Chat Completions flow that:

1. Sends a user question to the model.
2. Lets the model call a local Python tool function.
3. Sends the tool output back to the model.
4. Prints the final model answer.

## Requirements

- Python 3.12+
- OPENAI_API_KEY

## Setup

1. Create and activate a virtual environment (optional):

```bash
uv venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```bash
uv sync
```

3. Create your environment file:

```bash
copy .env.example .env
```

4. Add your API key to `.env`:

```env
OPENAI_API_KEY=your_key_here
```

## Run

```bash
uv run main.py
```

Custom prompt:

```bash
uv run main.py --prompt "Multiply 8 by 9 and then add 12"
```
