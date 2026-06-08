from pydantic import BaseModel


class CreateConversationResponse(
    BaseModel
):

    conversation_id: int


class ConversationResponse(
    BaseModel
):

    id: int

    title: str | None