import os
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv

load_dotenv()


def create_chat_model() -> ChatGoogleGenerativeAI:
    if not os.getenv("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY is required to initialize the chat model.")

    return ChatGoogleGenerativeAI(
        model=os.getenv("GEMINI_MODEL"),
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        max_output_tokens=1024,
    )
