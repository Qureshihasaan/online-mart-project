from pydantic import BaseModel
from typing import Optional, Any


class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    response: str
    raw_result: Optional[Any] = None