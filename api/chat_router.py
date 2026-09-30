import logging
from fastapi import APIRouter
from pydantic import BaseModel

from service.chat_service import ChatService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/chat",
    tags=["chat"],
)

chat_service = ChatService()


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    logger.info("Chat endpoint called")
    logger.info("Chat input: %s", request.message)
    response = await chat_service.chat(request.message)

    return ChatResponse(response=response)

