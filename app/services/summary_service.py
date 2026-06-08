import asyncio

import google.generativeai as genai

from app.core.config import (
    settings
)

genai.configure(
    api_key=settings.GEMINI_API_KEY
)

model = genai.GenerativeModel(
    "gemini-1.5-flash"
)


SUMMARY_PROMPT = """
You are a conversation memory system.

Summarize the conversation.

Keep:
- important technical topics
- user goals
- decisions
- preferences
- important context

Do NOT include:
- greetings
- repeated content
- small talk

Keep summary concise but useful.
"""


class SummaryService:

    async def summarize(
        self,
        messages
    ) -> str:

        conversation_text = ""

        for msg in messages:

            conversation_text += (
                f"{msg['role']}: "
                f"{msg['content']}\n"
            )

        prompt = f"""
{SUMMARY_PROMPT}

Conversation:

{conversation_text}
"""

        response = await asyncio.to_thread(
            model.generate_content,
            prompt
        )

        return response.text


summary_service = SummaryService()