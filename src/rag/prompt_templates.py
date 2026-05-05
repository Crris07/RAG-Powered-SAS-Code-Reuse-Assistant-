"""Prompt templates for code adaptation"""

from typing import Optional


class PromptTemplates:
    """Collection of prompt templates"""

    SYSTEM_PROMPT = """You are an expert SAS programmer specializing in clinical trial data analysis.
Your task is to adapt existing SAS code for new requirements while maintaining code quality and best practices.

Guidelines:
- Preserve the original structure and logic
- Update variable names to reflect the new study context
- Modify dataset references as needed
- Ensure the code is production-ready
- Include clear, concise comments
- Handle edge cases appropriately"""

    ADAPTATION_PROMPT = """Given the following existing SAS code as reference:

{context}

Adapt this code to meet the new requirement:
{requirement}

Provide:
1. The adapted SAS code
2. Brief comments explaining key modifications
3. Any assumptions made about the new study parameters

Ensure the output is ready to run with minimal modifications."""

    REVIEW_PROMPT = """Review the following SAS code for:
1. Syntax correctness
2. Best practices compliance
3. Potential issues or improvements

Code:
{code}

Provide a brief assessment and any recommendations."""

    @classmethod
    def get_system_prompt(cls) -> str:
        """Get system prompt"""
        return cls.SYSTEM_PROMPT

    @classmethod
    def get_adaptation_prompt(cls, context: str, requirement: str) -> str:
        """Get adaptation prompt with filled context"""
        return cls.ADAPTATION_PROMPT.format(context=context, requirement=requirement)

    @classmethod
    def get_review_prompt(cls, code: str) -> str:
        """Get code review prompt"""
        return cls.REVIEW_PROMPT.format(code=code)

    @classmethod
    def get_custom_prompt(
        cls,
        template: str,
        **kwargs,
    ) -> str:
        """Get custom prompt with variable substitution"""
        return template.format(**kwargs)
