import logging

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)

from model.chat_model import create_chat_model
from prompts.system_prompt import build_system_prompt
from memory.redis_memory import (
    MemoryUnavailableError,
    RedisConversationMemory,
)

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(
        self,
        memory: RedisConversationMemory,
    ):
        self.model = create_chat_model()
        self.system_prompt = build_system_prompt()
        self.memory = memory

    async def chat(
        self,
        conversation_id: str,
        user_message: str,
    ) -> str:
        message = user_message.strip()

        if not message:
            raise ValueError("Message must not be empty.")

        logger.info(
            "Received chat message for conversation %s",
            conversation_id,
        )

        try:
            stored_messages = await self.memory.load(conversation_id)
            history = self._to_messages(stored_messages)

            messages = [
                SystemMessage(content=self.system_prompt),
                *history,
                HumanMessage(content=message),
            ]

            response = await self.model.ainvoke(messages)

            response_text = self._extract_text(response)

            await self.memory.append_many(
                conversation_id,
                [
                    {
                        "type": "human",
                        "content": message,
                    },
                    {
                        "type": "ai",
                        "content": response_text,
                    },
                ],
            )
        except MemoryUnavailableError:
            logger.exception(
                "Conversation memory unavailable for %s",
                conversation_id,
            )
            raise

        return response_text

    @staticmethod
    def _to_messages(
        messages: list[dict],
    ) -> list:
        history = []

        for message in messages:
            if message["type"] == "human":
                history.append(
                    HumanMessage(
                        content=message["content"]
                    )
                )
            elif message["type"] == "ai":
                history.append(
                    AIMessage(
                        content=message["content"]
                    )
                )

        return history

    @staticmethod
    def _extract_text(response) -> str:
        content = response.content

        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):
            parts = []

            for item in content:
                if isinstance(item, str):
                    parts.append(item)
                elif (
                    isinstance(item, dict)
                    and item.get("text")
                ):
                    parts.append(item["text"])

            return "".join(parts).strip()

        return str(content).strip()