import httpx

from app.core.config import settings

SYSTEM_PROMPT = """
You are a helpful AI assistant that provides information about Agribank.

Answer clearly and concisely.

Always answer in the same language
as the user.
"""

class LLMService:

    async def generate_reply(
        self,
        messages
    ) -> str:

        formatted_messages = [

            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },

            *[
                {
                    "role": msg.role,
                    "content": msg.content
                }
                for msg in messages
            ]
        ]

        payload = {

            "model": settings.MODEL_NAME,

            "messages":
                formatted_messages,

            "temperature": 0.7,

            "max_tokens": 512,

            "stream": False
        }

        async with httpx.AsyncClient(
            timeout=120.0
        ) as client:

            response = await client.post(
                f"{settings.LLAMA_CPP_URL}/v1/chat/completions",
                json=payload
            )

            response.raise_for_status()

            data = response.json()

            return (
                data["choices"][0]
                ["message"]["content"]
            )


llm_service = LLMService()