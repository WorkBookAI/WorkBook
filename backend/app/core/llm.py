import httpx
import asyncio
from typing import Optional, List, AsyncGenerator
import openai
import anthropic
from app.core.config import ConfigManager
import logging

logger = logging.getLogger(__name__)

class LLMProvider:
    async def chat(
        self,
        messages: List[dict],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        raise NotImplementedError

    async def stream(
        self,
        messages: List[dict],
        system_prompt: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        raise NotImplementedError

class OllamaProvider(LLMProvider):
    def __init__(self, model: str, endpoint: str = "http://localhost:11434"):
        self.model = model
        self.endpoint = endpoint

    async def chat(self, messages: List[dict], system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.endpoint}/api/chat",
                json={"model": self.model, "messages": messages, "stream": False},
                timeout=60.0,
            )
            data = response.json()
            return data.get("message", {}).get("content", "")

    async def stream(self, messages: List[dict], system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.endpoint}/api/chat",
                json={"model": self.model, "messages": messages, "stream": True},
                timeout=60.0,
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        import json
                        data = json.loads(line)
                        if "message" in data:
                            yield data["message"].get("content", "")

class LMStudioProvider(LLMProvider):
    def __init__(self, model: str, endpoint: str = "http://localhost:1234"):
        self.model = model
        self.endpoint = endpoint

    async def chat(self, messages: List[dict], system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.endpoint}/v1/chat/completions",
                json={"model": self.model, "messages": messages, "stream": False},
                timeout=60.0,
            )
            data = response.json()
            return data["choices"][0]["message"]["content"]

    async def stream(self, messages: List[dict], system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.endpoint}/v1/chat/completions",
                json={"model": self.model, "messages": messages, "stream": True},
                timeout=60.0,
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        import json
                        data = json.loads(line[6:])
                        if data.get("choices"):
                            yield data["choices"][0]["delta"].get("content", "")

class OpenAIProvider(LLMProvider):
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model
        api_key = ConfigManager.get_api_key("openai")
        openai.api_key = api_key

    async def chat(self, messages: List[dict], system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content

    async def stream(self, messages: List[dict], system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            stream=True,
        )
        for chunk in response:
            yield chunk.choices[0].delta.get("content", "")

class AnthropicProvider(LLMProvider):
    def __init__(self, model: str = "claude-3-sonnet-20240229"):
        self.model = model
        api_key = ConfigManager.get_api_key("anthropic")
        self.client = anthropic.Anthropic(api_key=api_key)

    async def chat(self, messages: List[dict], system_prompt: Optional[str] = None, temperature: float = 0.7) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            system=system_prompt,
            messages=messages,
            temperature=temperature,
        )
        return response.content[0].text

    async def stream(self, messages: List[dict], system_prompt: Optional[str] = None) -> AsyncGenerator[str, None]:
        with self.client.messages.stream(
            model=self.model,
            max_tokens=2048,
            system=system_prompt,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                yield text

class LLMManager:
    @staticmethod
    def get_provider(provider: str, model: str, **kwargs) -> LLMProvider:
        """Get LLM provider instance."""
        if provider == "ollama":
            return OllamaProvider(model, kwargs.get("endpoint", "http://localhost:11434"))
        elif provider == "lm_studio":
            return LMStudioProvider(model, kwargs.get("endpoint", "http://localhost:1234"))
        elif provider == "openai":
            return OpenAIProvider(model)
        elif provider == "anthropic":
            return AnthropicProvider(model)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    @staticmethod
    async def detect_local_models() -> dict:
        """Auto-detect available local models."""
        models = {"ollama": [], "lm_studio": []}

        # Check Ollama
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:11434/api/tags", timeout=2.0)
                if response.status_code == 200:
                    data = response.json()
                    models["ollama"] = [m["name"] for m in data.get("models", [])]
        except Exception as e:
            logger.debug(f"Ollama not available: {e}")

        # Check LM Studio
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:1234/v1/models", timeout=2.0)
                if response.status_code == 200:
                    data = response.json()
                    models["lm_studio"] = [m["id"] for m in data.get("data", [])]
        except Exception as e:
            logger.debug(f"LM Studio not available: {e}")

        return models
