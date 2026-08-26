from datetime import datetime
from pydantic import BaseModel

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    id: int
    prompt: str
    response: str
    created_at: datetime