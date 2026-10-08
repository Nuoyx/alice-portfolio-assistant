import logging
import secrets
import os
import redis.asyncio as redis
from fastapi import APIRouter, Cookie, Response, Request
from pydantic import BaseModel, Field

from memory.redis_memory import RedisConversationMemory
from service.chat_service import ChatService
from service.rate_limiter import RateLimiter
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)


redis_client = redis.from_url(
    os.getenv("REDIS_URL"),
    decode_responses=True,
)


memory = RedisConversationMemory(
    redis_client=redis_client,
    ttl=int(os.getenv("SESSION_TTL", "86400")),
)
rate_limiter = RateLimiter(
    redis_client=redis_client
)
chat_service = ChatService(memory)


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=1000,
    )


class ChatResponse(BaseModel):
    response: str


@router.post("", response_model=ChatResponse)
async def chat(
        request: Request,
        chat_request: ChatRequest,
        response: Response,
        session_id: str | None = Cookie(default=None, alias="sessionId"),
) -> ChatResponse:
    logger.info("Chat input: %s", chat_request.message)
    client_ip = request.client.host if request.client else "unknown"
    allowed = await rate_limiter.is_allowed(client_ip)
    if not allowed:
        return ChatResponse(
            response="You've reached today's chatbot usage limit. Please come back tomorrow."
        )

    if session_id is None:
        session_id = secrets.token_urlsafe(32)

        response.set_cookie(
            key="sessionId",
            value=session_id,
            max_age=int(os.getenv("SESSION_TTL", "86400")),
        )

    response = await chat_service.chat(
        conversation_id=session_id,
        user_message=chat_request.message,
    )

    return ChatResponse(
        response=response,
    )
