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

    messages: list[Message]