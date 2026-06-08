from fastapi import APIRouter

from app.services.conversation_service import (
    conversation_service
)

router = APIRouter()


@router.post("/conversations")
async def create_conversation():

    conversation = await (
        conversation_service
        .create_conversation()
    )

    return {
        "conversation_id":
            conversation["id"]
    }


@router.get("/conversations")
async def get_conversations():

    return await (
        conversation_service
        .get_conversations()
    )


@router.get(
    "/conversations/{conversation_id}/messages"
)
async def get_messages(
    conversation_id: int
):

    return await (
        conversation_service
        .get_messages(
            conversation_id
        )
    )