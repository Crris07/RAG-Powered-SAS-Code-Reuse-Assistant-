"""CodeLlama LLM provider"""

import os
from typing import Optional

from src.llm.llm_adapter import LLMProvider
from src.core.logger import get_logger

logger = get_logger(__name__)

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    import torch
except ImportError:
    AutoTokenizer = None
    AutoModelForCausalLM = None
    pipeline = None
    torch = None


class CodeLlamaProvider(LLMProvider):
    """CodeLlama local model provider"""

    def __init__(self, model_path: str = "./models/codellama-34b-instruct"):
        self.model_path = model_path
        self.device = "cuda" if torch and torch.cuda.is_available() else "cpu"
        self.pipeline = None

        # Check if model exists locally
        if not os.path.exists(model_path):
            logger.warning(f"CodeLlama model not found at {model_path}. "
                          "Please download the model first.")
            return

        try:
            if AutoTokenizer is None or AutoModelForCausalLM is None:
                raise ImportError("transformers package not installed")

            logger.info(f"Loading CodeLlama from {model_path} on {self.device}")

            # Load tokenizer and model
            tokenizer = AutoTokenizer.from_pretrained(model_path)
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
                low_cpu_mem_usage=True,
            )

            # Create pipeline
            self.pipeline = pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device=0 if self.device == "cuda" else -1,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            )

            logger.info(f"Initialized CodeLlama provider with model: {model_path}")

        except Exception as e:
            logger.error(f"Failed to initialize CodeLlama: {e}")
            self.pipeline = None

    def is_available(self) -> bool:
        """Check if CodeLlama is available"""
        return self.pipeline is not None

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.2,
        max_tokens: int = 1024,
    ) -> str:
        """Generate text using CodeLlama"""
        if not self.is_available():
            raise RuntimeError("CodeLlama pipeline not initialized")

        try:
            # Combine system and user prompts
            full_prompt = f"<s>[INST] <<SYS>>\n{system_prompt}\n<</SYS>>\n\n{user_prompt} [/INST]"

            # Generate response
            outputs = self.pipeline(
                full_prompt,
                max_new_tokens=max_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                top_p=0.9,
                num_return_sequences=1,
                pad_token_id=self.pipeline.tokenizer.eos_token_id,
            )

            # Extract generated text (remove the input prompt)
            generated_text = outputs[0]["generated_text"]
            response = generated_text[len(full_prompt):].strip()

            return response

        except Exception as e:
            logger.error(f"CodeLlama generation failed: {e}")
            raise