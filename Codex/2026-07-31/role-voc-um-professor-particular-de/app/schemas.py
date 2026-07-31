from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12_000)
    student_level: int | None = Field(default=None, ge=1, le=3)
    conversation_id: str | None = Field(default=None, max_length=128)


class ChatResponse(BaseModel):
    reply: str
    conversation_id: str | None = None
    provider: str


class HealthResponse(BaseModel):
    status: str
    service: str
    provider: str
