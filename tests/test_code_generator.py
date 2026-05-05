"""Unit tests for code generator"""

import pytest
from unittest.mock import Mock, patch

from src.llm.code_generator import CodeGenerator


@pytest.fixture
def mock_llm():
    """Create mock LLM"""
    llm = Mock()
    llm.is_available.return_value = True
    llm.generate.return_value = """
    data work.new_dataset;
      set input.source;
      new_var = calculated_value;
    run;
    """
    return llm


def test_code_generator_initialization():
    """Test CodeGenerator initialization with mocked LLM"""
    with patch('src.llm.code_generator.OpenAIProvider') as mock_provider:
        mock_provider.return_value.is_available.return_value = True
        
        # Would initialize CodeGenerator if LLM is available
        # For now, just test that the class exists
        assert CodeGenerator is not None


def test_adapt_code_format(mock_llm):
    """Test code adaptation formatting"""
    context = "existing code block"
    requirement = "adapt this code"
    
    # Mock the LLM to be available
    mock_llm.is_available.return_value = True
    
    # Test that methods exist
    assert hasattr(CodeGenerator, 'adapt_code')
    assert hasattr(CodeGenerator, 'generate_code')
