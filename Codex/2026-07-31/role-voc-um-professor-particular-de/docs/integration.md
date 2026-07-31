# ERP integration and network notes

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/health` | Availability and configured provider |
| POST | `/api/v1/chat` | Send a learner message |

Example request:

```json
{"message":"O que é uma variável?", "student_level":1, "conversation_id":"student-42"}
```

The response returns `reply`, `conversation_id`, and `provider`. Your ERP should use the `conversation_id` as its own stable learner/session key and persist chat history in its existing database. This starter deliberately has no database, authentication, or cross-origin access because those policies must match your ERP's security model.

## Provider setup

The full English instruction set is in `prompts/system_prompt.md`. The application starts in safe `mock` mode so it never makes unplanned external requests or requires a key. It includes an `openai_compatible` adapter using Python's standard library: set `LLM_PROVIDER=openai_compatible`, `LLM_MODEL`, and `LLM_API_KEY` in `.env`. `LLM_API_URL` is optional for an OpenAI-compatible gateway. Do not put provider keys in source control.

## Network and ports

- Container port: `8000` (private Docker network)
- Host port: `8017` by default, configurable through `HOST_PORT`
- Binding: `127.0.0.1`, so no LAN exposure or host-port collision with services outside the machine

Before starting, check the chosen host port in PowerShell:

```powershell
Get-NetTCPConnection -LocalPort 8017 -ErrorAction SilentlyContinue
```

If it returns a listener, choose another unallocated port (for example `8018`) in `.env`. Then run `docker compose up --build -d` and verify:

```powershell
Invoke-RestMethod http://127.0.0.1:8017/api/v1/health
docker compose ps
```

Or run `.\scripts\start-local.ps1`, which selects the first free port between 8017 and 8037, writes it to the ignored local `.env`, starts Docker Compose, and performs the health check.

For ERP on a different machine, do not simply change the binding to `0.0.0.0`. Place the API behind your ERP's authenticated reverse proxy/TLS gateway and restrict access by firewall/network policy.

## Windows without Docker

Run `.\scripts\start-windows.ps1`. It starts a background server using only the Python standard library, bound to `127.0.0.1`, and checks `/api/v1/health` before reporting success. Stop it with `.\scripts\stop-windows.ps1`.
