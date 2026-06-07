from dotenv import load_dotenv
import os

load_dotenv()

class Settings:

    LLAMA_CPP_URL = os.getenv(
        "LLAMA_CPP_URL",
        "http://localhost:8080"
    )

    MODEL_NAME = os.getenv(
        "MODEL_NAME",
        "qwen"
    )

    FRONTEND_URL = os.getenv(
        "FRONTEND_URL",
        "http://localhost:5173"
    )

settings = Settings()