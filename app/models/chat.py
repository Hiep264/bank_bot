from pydantic import BaseModel
from typing import Literal


class Message(BaseModel):

    role: Literal[
        "user",
        "assistant",
        "system"
    ]

    content: str


class ChatRequest(BaseModel):

    conversation_id: int | None = None
    message: str