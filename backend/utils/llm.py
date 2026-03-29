"""Drop-in replacement for emergentintegrations.llm.chat using OpenAI SDK directly"""
from openai import AsyncOpenAI
import httpx
import aiohttp
import json
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

    async def _send_via_sdk(self, messages: list) -> str:
        """Try OpenAI SDK with explicit httpx client"""
        http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0, connect=15.0),
            follow_redirects=True,
            http2=False,
        )
        try:
            client = AsyncOpenAI(
                api_key=self.api_key,
                http_client=http_client,
                max_retries=2,
                timeout=60.0,
            )
            response = await client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )
            return response.choices[0].message.content or ""
        finally:
            await http_client.aclose()

    async def _send_via_aiohttp(self, messages: list) -> str:
        """Fallback: direct API call via aiohttp"""
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": 2000,
            "temperature": 0.7,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise Exception(f"OpenAI API {resp.status}: {body[:200]}")
                data = await resp.json()
                return data["choices"][0]["message"]["content"] or ""

    async def send_message(self, message: UserMessage) -> str:
        messages = []
        if self.system_message:
            messages.append({"role": "system", "content": self.system_message})
        messages.append({"role": "user", "content": message.text})

        # Try SDK first, fallback to aiohttp
        try:
            result = await self._send_via_sdk(messages)
            logger.info("OpenAI call succeeded (SDK)")
            return result
        except Exception as e:
            logger.warning(f"OpenAI SDK failed ({type(e).__name__}: {e}), trying aiohttp fallback...")

        try:
            result = await self._send_via_aiohttp(messages)
            logger.info("OpenAI call succeeded (aiohttp fallback)")
            return result
        except Exception as e:
            logger.error(f"OpenAI aiohttp fallback also failed ({type(e).__name__}): {e}")
            raise
