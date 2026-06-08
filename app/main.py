from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)

from app.api.chat import (
    router as chat_router
)

from app.api.conversations import (
    router as conversations_router
)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "*",
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


app.include_router(chat_router)

app.include_router(
    conversations_router
)


@app.get("/")
async def root():

    return {
        "message": "API running"
    }