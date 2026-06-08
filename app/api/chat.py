from fastapi import APIRouter, HTTPException

from app.models.chat import (
    ChatRequest,
    Message
)

from app.services.llm_service import (
    llm_service
)

from app.services.conversation_service import (
    conversation_service
)

from app.services.summary_service import (
    summary_service
)

router = APIRouter()

SUMMARY_INTERVAL = 6


@router.post("/chat")
async def chat(
    payload: ChatRequest
):

    conversation_id = (
        payload.conversation_id
    )

    if conversation_id is None:

        conversation = await (
            conversation_service
            .create_conversation()
        )

        conversation_id = conversation[
            "id"
        ]

    else:

        conversation = await (
            conversation_service
            .get_conversation(
                conversation_id
            )
        )

        if conversation is None:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Conversation"
                    " not found"
                )
            )

    next_order = await (
        conversation_service
        .get_next_message_order(
            conversation_id
        )
    )

    await conversation_service.save_message(
        conversation_id=conversation_id,
        role="user",
        content=payload.message,
        message_order=next_order
    )

    existing_messages = await (
        conversation_service
        .get_messages(conversation_id)
    )

    summary = conversation.get(
        "summary"
    )

    recent_messages = [
        Message(
            role=msg["role"],
            content=msg["content"]
        )
        for msg in existing_messages[-10:]
    ]

    reply = await (
        llm_service.generate_reply(
            recent_messages,
            summary=summary
        )
    )

    await conversation_service.save_message(
        conversation_id=conversation_id,
        role="assistant",
        content=reply,
        message_order=next_order + 1
    )

    message_count = await (
        conversation_service
        .get_messages_count(
            conversation_id
        )
    )

    if (
        message_count <= 3
        and payload.message
    ):

        new_title = (
            payload.message[:50]
            + (
                "..."
                if len(
                    payload.message
                ) > 50
                else ""
            )
        )

        await (
            conversation_service
            .update_conversation(
                conversation_id=conversation_id,
                title=new_title
            )
        )

    if (
        message_count >= SUMMARY_INTERVAL
        and message_count
        % SUMMARY_INTERVAL
        == 0
    ):

        try:

            new_summary = await (
                summary_service
                .summarize(
                    existing_messages
                )
            )

            await (
                conversation_service
                .update_conversation(
                    conversation_id=conversation_id,
                    summary=new_summary
                )
            )

        except Exception:

            pass

    await conversation_service.update_conversation(
        conversation_id=conversation_id
    )

    return {
        "reply": reply,
        "conversation_id":
            conversation_id
    }
