"""Claude LLM provider"""

import os

from src.llm.llm_adapter import LLMProvider
from src.core.logger import get_logger

logger = get_logger(__name__)

try:
    import anthropic
except ImportError:
    anthropic = None


class ClaudeProvider(LLMProvider):
    """Anthropic Claude provider"""

    def __init__(self, model: str = "claude-3-sonnet-20240229"):
        self.model = model
        self.api_key = os.getenv("ANTHROPIC_API_KEY")

        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not set")
            self.client = None
        else:
            try:
                if anthropic is None:
                    raise ImportError("anthropic package not installed")
                self.client = anthropic.Anthropic(api_key=self.api_key)
                logger.info(f"Initialized Claude provider with model: {model}")
            except Exception as e:
                logger.error(f"Failed to initialize Claude: {e}")
                self.client = None

    def is_available(self) -> bool:
        """Check if Claude is available"""
        return self.client is not None

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        """Generate text using Claude"""
        if not self.is_available():
            raise RuntimeError("Claude client not initialized")

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude generation failed: {e}")
            raise
