from datetime import datetime
from pydantic import BaseModel

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    prompt: str
    response: str
    created_at: datetime