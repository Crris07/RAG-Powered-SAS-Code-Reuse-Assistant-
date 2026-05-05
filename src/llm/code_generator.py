"""Code generation and adaptation"""

from typing import Optional

from src.core.config import get_config
from src.core.logger import get_logger
from src.llm.provider.openai_provider import OpenAIProvider
from src.llm.provider.claude_provider import ClaudeProvider
from src.llm.provider.codellama_provider import CodeLlamaProvider
from src.llm.provider.demo_provider import DemoProvider
from src.rag.prompt_templates import PromptTemplates

logger = get_logger(__name__)


class CodeGenerator:
    """Generate and adapt SAS code using LLMs"""

    def __init__(self, provider: Optional[str] = None):
        config = get_config()
        provider = provider or config.llm_provider

        if provider == "demo":
            self.llm = DemoProvider()
        elif provider == "openai":
            model = config.get("llm", "openai", "model", default="gpt-4")
            self.llm = OpenAIProvider(model=model)
        elif provider == "claude":
            model = config.get("llm", "claude", "model", default="claude-3-sonnet-20240229")
            self.llm = ClaudeProvider(model=model)
        elif provider == "codellama":
            model_path = config.get("llm", "codellama", "model_path", default="./models/codellama-34b-instruct")
            self.llm = CodeLlamaProvider(model_path=model_path)
        else:
            raise ValueError(
                f"Unknown LLM provider: {provider}. Supported: demo, openai, claude, codellama"
            )

        if not self.llm.is_available():
            raise RuntimeError(f"{provider} LLM provider is not available")

        logger.info(f"Initialized CodeGenerator with provider: {provider}")

    def adapt_code(
        self,
        context: str,
        requirement: str,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        """
        Adapt retrieved code to new requirement
        
        Args:
            context: Retrieved code examples with explanations
            requirement: New requirement/query
            temperature: LLM temperature parameter
            max_tokens: Maximum tokens in response
            
        Returns:
            Adapted SAS code
        """
        try:
            system_prompt = PromptTemplates.get_system_prompt()
            user_prompt = PromptTemplates.get_adaptation_prompt(context, requirement)

            adapted_code = self.llm.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            logger.info("Code adaptation completed")
            return adapted_code

        except Exception as e:
            logger.error(f"Code adaptation failed: {e}")
            raise

    def generate_code(
        self,
        requirement: str,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        """
        Generate SAS code from scratch (without retrieval)
        
        Args:
            requirement: Code requirement
            temperature: LLM temperature parameter
            max_tokens: Maximum tokens in response
            
        Returns:
            Generated SAS code
        """
        try:
            system_prompt = PromptTemplates.get_system_prompt()
            user_prompt = f"Generate SAS code for: {requirement}"

            generated_code = self.llm.generate(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            logger.info("Code generation completed")
            return generated_code

        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            raise
