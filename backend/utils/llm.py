"""Drop-in replacement for emergentintegrations.llm.chat using OpenAI SDK directly"""
from openai import AsyncOpenAI
import logging

logger = logging.getLogger(__name__)

class UserMessage:
    def __init__(self, text: str):
        self.text = text

class LlmChat:
    def __init__(self, api_key: str, session_id: str = None, system_message: str = None):
        self.api_key = api_key
        self.session_id = session_id
        self.system_message = system_message
        self.model_provider = "openai"
        self.model_name = "gpt-4o-mini"

    def with_model(self, provider: str, model_name: str):
        self.model_provider = provider
        self.model_name = model_name
        return self

    async def send_message(self, message: UserMessage) -> str:
        try:
            client = AsyncOpenAI(api_key=self.api_key)
            messages = []
            if self.system_message:
                messages.append({"role": "system", "content": self.system_message})
            messages.append({"role": "user", "content": message.text})

            response = await client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"LLM error: {e}")
            raise
