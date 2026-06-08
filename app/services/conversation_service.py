from datetime import (
    datetime,
    timezone,
)

from app.db.supabase import (
    supabase
)


class ConversationService:

    async def create_conversation(
        self
    ):

        result = (
            supabase.table(
                "conversations"
            )
            .insert({
                "title":
                    "New Chat"
            })
            .execute()
        )

        return result.data[0]


    async def get_conversations(
        self
    ):

        result = (
            supabase.table(
                "conversations"
            )
            .select("*")
            .order(
                "updated_at",
                desc=True
            )
            .execute()
        )

        return result.data


    async def get_conversation(
        self,
        conversation_id: int
    ):

        result = (
            supabase.table(
                "conversations"
            )
            .select("*")
            .eq(
                "id",
                conversation_id
            )
            .execute()
        )

        return result.data[0] if result.data else None


    async def get_messages(
        self,
        conversation_id: int
    ):

        result = (
            supabase.table(
                "messages"
            )
            .select("*")
            .eq(
                "conversation_id",
                conversation_id
            )
            .order(
                "message_order"
            )
            .execute()
        )

        return result.data


    async def get_messages_count(
        self,
        conversation_id: int
    ):

        result = (
            supabase.table(
                "messages"
            )
            .select(
                "id",
                count="exact"
            )
            .eq(
                "conversation_id",
                conversation_id
            )
            .execute()
        )

        return result.count


    async def get_next_message_order(
        self,
        conversation_id: int
    ):

        result = (
            supabase.table(
                "messages"
            )
            .select("message_order")
            .eq(
                "conversation_id",
                conversation_id
            )
            .order(
                "message_order",
                desc=True
            )
            .limit(1)
            .execute()
        )

        if result.data:
            return result.data[0][
                "message_order"
            ] + 1

        return 1


    async def save_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        message_order: int
    ):

        result = (
            supabase.table(
                "messages"
            )
            .insert({
                "conversation_id":
                    conversation_id,
                "role": role,
                "content": content,
                "message_order":
                    message_order
            })
            .execute()
        )

        return result.data[0]


    async def update_conversation(
        self,
        conversation_id: int,
        title: str | None = None,
        summary: str | None = None
    ):

        updates = {}

        if title is not None:
            updates["title"] = title

        if summary is not None:
            updates["summary"] = summary

        updates["updated_at"] = (
            datetime.now(
                timezone.utc
            ).isoformat()
        )

        result = (
            supabase.table(
                "conversations"
            )
            .update(updates)
            .eq(
                "id",
                conversation_id
            )
            .execute()
        )

        return result.data[0] if result.data else None


conversation_service = (
    ConversationService()
)