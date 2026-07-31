# School Management Assistant

Local, Portuguese-speaking virtual assistant for a School Management System. It provides a browser interface and REST API for ERP integration, with data protection and action-confirmation guidance built in.

## Run on Windows (no Docker)

1. Copy `.env.example` to `.env`.
2. Run `./scripts/start-windows.ps1` in PowerShell.
3. Open `http://127.0.0.1:8017`.

The server binds only to `127.0.0.1` and chooses the next available port if 8017 is in use. Stop it with `./scripts/stop-windows.ps1`.

## API

- `GET /api/v1/health`
- `POST /api/v1/chat` with `{"message":"Como cadastro um aluno?"}`

The local `mock` mode provides safe guidance for common school-system tasks. For LLM-generated answers, set `LLM_PROVIDER=openai_compatible`, `LLM_MODEL`, and `LLM_API_KEY` in the ignored `.env` file. The full agent instruction is in `prompts/school_system_prompt.md`.

## GitHub

`.env`, virtual environments, temporary files, and logs are ignored. Do not commit API keys or student data. Create an empty GitHub repository, then add it as `origin` and push this repository.
