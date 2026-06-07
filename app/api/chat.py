from fastapi import APIRouter

from app.models.chat import (
    ChatRequest
)

from app.services.llm_service import (
    llm_service
)

router = APIRouter()


@router.post("/chat")
async def chat(
    payload: ChatRequest
):

    reply = await (
        llm_service.generate_reply(
            payload.messages
        )
    )

    return {
        "reply": reply
    }