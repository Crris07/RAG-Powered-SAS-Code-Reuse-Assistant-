"""OpenAI LLM provider"""

import os

from src.llm.llm_adapter import LLMProvider
from src.core.logger import get_logger

logger = get_logger(__name__)

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""

    def __init__(self, model: str = "gpt-4"):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")

        if not self.api_key:
            logger.warning("OPENAI_API_KEY not set")
            self.client = None
        else:
            try:
                if OpenAI is None:
                    raise ImportError("openai package not installed")
                self.client = OpenAI(api_key=self.api_key)
                logger.info(f"Initialized OpenAI provider with model: {model}")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI: {e}")
                self.client = None

    def is_available(self) -> bool:
        """Check if OpenAI is available"""
        return self.client is not None

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        """Generate text using OpenAI GPT"""
        if not self.is_available():
            raise RuntimeError("OpenAI client not initialized")

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise
