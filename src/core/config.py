"""Configuration management for SAS RAG Assistant"""

import os
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent


class Config:
    """Application configuration"""

    def __init__(self, config_file: Optional[str] = None):
        """Initialize configuration from YAML and environment variables"""
        if config_file is None:
            config_file = PROJECT_ROOT / "config.yaml"

        with open(config_file, "r") as f:
            self.config = yaml.safe_load(f)

        # Override with environment variables
        self._apply_env_overrides()

    def _apply_env_overrides(self):
        """Apply environment variable overrides"""
        env_mapping = {
            "ENVIRONMENT": ["app", "environment"],
            "DEBUG": ["app", "debug"],
            "LOG_LEVEL": ["app", "log_level"],
            "OPENAI_API_KEY": ["llm", "openai", "api_key"],
            "ANTHROPIC_API_KEY": ["llm", "claude", "api_key"],
            "CODELLAMA_MODEL_PATH": ["llm", "codellama", "model_path"],
        }

        for env_var, config_path in env_mapping.items():
            if env_val := os.getenv(env_var):
                self._set_nested_value(config_path, env_val)

    def _set_nested_value(self, path: list, value: str):
        """Set a nested value in config dictionary"""
        current = self.config
        for key in path[:-1]:
            current = current.setdefault(key, {})
        current[path[-1]] = value

    def get(self, *keys, default=None):
        """Get nested config value"""
        current = self.config
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            else:
                return default
        return current if current is not None else default

    @property
    def app_environment(self) -> str:
        return self.get("app", "environment", default="development")

    @property
    def debug(self) -> bool:
        return self.get("app", "debug", default=False)

    @property
    def log_level(self) -> str:
        return self.get("app", "log_level", default="INFO")

    @property
    def corpus_path(self) -> Path:
        return Path(self.get("data", "corpus_path", default="./data/corpus/raw"))

    @property
    def vector_db_path(self) -> Path:
        return Path(self.get("data", "vector_db_path", default="./data/vector_db"))

    @property
    def llm_provider(self) -> str:
        return self.get("llm", "provider", default="openai")

    @property
    def chunk_size(self) -> int:
        return self.get("chunking", "chunk_size", default=500)


# Global config instance
_config = None


def get_config() -> Config:
    """Get or create global config instance"""
    global _config
    if _config is None:
        _config = Config()
    return _config
