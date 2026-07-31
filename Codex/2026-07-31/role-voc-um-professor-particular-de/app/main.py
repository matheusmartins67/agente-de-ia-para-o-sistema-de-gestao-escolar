import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from app.schemas import ChatRequest, ChatResponse, HealthResponse
from app.tutor import TutorService

app = FastAPI(title="School Management Assistant", version="1.0.0")
tutor = TutorService(os.getenv("LLM_PROVIDER", "mock"))
WEB_DIR = Path(__file__).parent / "web"


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/v1/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", service="school-management-assistant", provider=tutor.provider)


@app.post("/api/v1/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        reply = tutor.reply(request.message, request.student_level)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return ChatResponse(reply=reply, conversation_id=request.conversation_id, provider=tutor.provider)
