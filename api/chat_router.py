import logging
import secrets
import os
from fastapi import APIRouter, Cookie, Response
from pydantic import BaseModel

from memory.redis_memory import RedisConversationMemory
from service.chat_service import ChatService
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)


memory = RedisConversationMemory(
    redis_url=os.getenv("REDIS_URL"),
    ttl=int(os.getenv("SESSION_TTL", "86400")),
)
chat_service = ChatService(memory)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post("", response_model=ChatResponse)
async def chat(
        request: ChatRequest,
        response: Response,
        session_id: str | None = Cookie(default=None, alias="sessionId"),
) -> ChatResponse:
    logger.info("Chat input: %s", request.message)

    if session_id is None:
        session_id = secrets.token_urlsafe(32)

        response.set_cookie(
            key="sessionId",
            value=session_id,
            max_age=int(os.getenv("SESSION_TTL", "86400")),
        )

    response = await chat_service.chat(
        conversation_id=session_id,
        user_message=request.message,
    )

    return ChatResponse(
        response=response,
    )
