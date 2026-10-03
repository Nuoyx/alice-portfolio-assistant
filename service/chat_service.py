import logging

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)

from model.chat_model import create_chat_model
from prompts.system_prompt import build_system_prompt
from rag.retriever import retrieve_documents
from memory.redis_memory import (
    MemoryUnavailableError,
    RedisConversationMemory,
)
from skills.selector import get_skill, select_skill
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

            skill_name = await select_skill(self.model, message)
            skill = get_skill(skill_name)

            documents = retrieve_documents(message)
            context = "\n\n".join(
                document.page_content
                for document in documents
            )
            messages = [
                SystemMessage(content=f"""
                {self.system_prompt} 
                Current skill: {skill}
                """),
                *history,
                HumanMessage(
                    content=f"""
                    Relevant portfolio information:
                    {context}
                    User question:
                    {message}
                    """
                ),
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

