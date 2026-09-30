from langchain_core.messages import HumanMessage, SystemMessage
import logging
from model.chat_model import create_chat_model
from prompts.system_prompt import build_system_prompt

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self.model = create_chat_model()
        self.system_prompt = build_system_prompt()

    async def chat(self, user_message: str) -> str:
        logger.info("Received chat message: %s", user_message)

        message = user_message.strip()

        if not message:
            raise ValueError("Message must not be empty.")

        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=message),
        ]

        response = await self.model.ainvoke(messages)

        if isinstance(response.content, str):
            return response.content

        return "".join(
            block.get("text", "")
            for block in response.content
            if isinstance(block, dict) and block.get("type") == "text"
        )


