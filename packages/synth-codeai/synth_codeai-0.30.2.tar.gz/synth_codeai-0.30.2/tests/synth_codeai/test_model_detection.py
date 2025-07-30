"""Unit tests for model_detection.py."""

import pytest
from unittest.mock import MagicMock, patch
from langchain_core.language_models import BaseChatModel

from synth_codeai.model_detection import (
    is_claude_37,
    normalize_model_name,
    get_model_name_from_chat_model,
    should_use_react_agent,
    model_name_has_claude,
    is_anthropic_claude
)
from synth_codeai.models_params import AgentBackendType


def test_normalize_model_name():
    """Test normalize_model_name function with various model names."""
    # Test provider prefix removal
    assert normalize_model_name("anthropic/claude-3.7") == "claude-3.7"
    assert normalize_model_name("google/gemini-2.0-pro") == "gemini-2.0-pro"
    assert normalize_model_name("openai/gpt-4") == "gpt-4"
    
    # Test version suffix removal
    assert normalize_model_name("gemini-2.0-pro-exp-02-05:free") == "gemini-2.0-pro-exp-02-05"
    assert normalize_model_name("claude-3.5-sonnet:v1") == "claude-3.5-sonnet"
    
    # Test both prefix and suffix
    assert normalize_model_name("google/gemini-2.0-pro:free") == "gemini-2.0-pro"
    
    # Test no changes needed
    assert normalize_model_name("claude-3.7") == "claude-3.7"
    assert normalize_model_name("gpt-4") == "gpt-4"
    
    # Test empty string
    assert normalize_model_name("") == ""
    

def test_is_claude_37():
    """Test is_claude_37 function with various model names."""
    # Test positive cases
    assert is_claude_37("claude-3.7")
    assert is_claude_37("claude3.7")
    assert is_claude_37("claude-3-7")
    assert is_claude_37("anthropic/claude-3.7")
    assert is_claude_37("anthropic/claude3.7")
    assert is_claude_37("anthropic/claude-3-7")
    assert is_claude_37("claude-3.7-sonnet")
    assert is_claude_37("claude3.7-haiku")
    
    # Test negative cases
    assert not is_claude_37("claude-3")
    assert not is_claude_37("claude-3.5")
    assert not is_claude_37("claude3.5")
    assert not is_claude_37("claude-3-5")
    assert not is_claude_37("gpt-4")
    assert not is_claude_37("")


def test_get_model_name_from_chat_model():
    """Test get_model_name_from_chat_model function with various model instances."""
    # Test with model attribute
    model_with_model_attr = MagicMock(spec=BaseChatModel)
    model_with_model_attr.model = "claude-3.7-sonnet"
    assert get_model_name_from_chat_model(model_with_model_attr) == "claude-3.7-sonnet"
    
    # Test with model_name attribute
    model_with_model_name_attr = MagicMock(spec=BaseChatModel)
    model_with_model_name_attr.model_name = "gpt-4"
    assert get_model_name_from_chat_model(model_with_model_name_attr) == "gpt-4"
    
    # Test with no relevant attributes
    model_without_attrs = MagicMock(spec=BaseChatModel)
    from synth_codeai.config import DEFAULT_MODEL
    assert get_model_name_from_chat_model(model_without_attrs) == DEFAULT_MODEL
    
    # Test with None
    assert get_model_name_from_chat_model(None) == DEFAULT_MODEL


@patch('litellm.supports_function_calling')
@patch('synth_codeai.model_detection.get_config_repository')
def test_should_use_react_agent_function_calling(mock_get_config_repo, mock_supports_function_calling):
    """Test should_use_react_agent based on function calling support."""
    model = MagicMock(spec=BaseChatModel)
    model.model = "claude-3.7-sonnet"
    
    mock_repo = MagicMock()
    mock_repo.get.return_value = "anthropic"
    mock_get_config_repo.return_value = mock_repo
    
    # --- Test when model SUPPORTS function calling ---
    mock_supports_function_calling.return_value = True
    assert should_use_react_agent(model) is True
    # Check the call arguments for the first call
    mock_supports_function_calling.assert_called_with(model="claude-3.7-sonnet", custom_llm_provider=None)

    # --- Test when model DOES NOT support function calling ---
    mock_supports_function_calling.reset_mock() # Reset call history
    mock_supports_function_calling.return_value = False # Set mock to return False for this case
    assert should_use_react_agent(model) is False
    # Check the call arguments for the second call (optional, but good practice)
    mock_supports_function_calling.assert_called_with(model="claude-3.7-sonnet", custom_llm_provider=None)


@patch('litellm.supports_function_calling')
@patch('synth_codeai.model_detection.get_config_repository')
@patch('synth_codeai.model_detection.models_params')
def test_should_use_react_agent_config_override(mock_models_params, mock_get_config_repo, mock_supports_function_calling):
    """Test should_use_react_agent with config override."""
    # Setup
    model = MagicMock(spec=BaseChatModel)
    model.model = "claude-3.7-sonnet"
    
    # Mock config repository
    mock_repo = MagicMock()
    mock_repo.get.return_value = "anthropic"
    mock_get_config_repo.return_value = mock_repo
    
    # Mock models_params
    mock_models_params.get.return_value = {
        "claude-3.7-sonnet": {
            "default_backend": AgentBackendType.CREATE_REACT_AGENT
        }
    }
    
    # Test when config overrides to use REACT agent
    mock_supports_function_calling.return_value = False  # Would normally use CIAYN
    assert should_use_react_agent(model) is True  # But config overrides to REACT
    
    # Change config to use CIAYN
    mock_models_params.get.return_value = {
        "claude-3.7-sonnet": {
            "default_backend": AgentBackendType.CIAYN
        }
    }
    
    # Test when config overrides to use CIAYN agent
    mock_supports_function_calling.return_value = True  # Would normally use REACT
    assert should_use_react_agent(model) is False  # But config overrides to CIAYN


@patch('litellm.supports_function_calling')
def test_should_use_react_agent_error_handling(mock_supports_function_calling):
    """Test should_use_react_agent error handling."""
    # Setup
    model = MagicMock(spec=BaseChatModel)
    model.model = "claude-3.7-sonnet"
    
    # Test when litellm raises an exception
    mock_supports_function_calling.side_effect = Exception("API error")
    
    # Should default to False when there's an error checking function calling support
    assert should_use_react_agent(model) is False


def test_model_name_has_claude():
    """Test model_name_has_claude function."""
    # Test positive cases
    assert model_name_has_claude("claude-3.7")
    assert model_name_has_claude("claude-3.5-sonnet")
    assert model_name_has_claude("anthropic/claude-3-opus")
    assert model_name_has_claude("CLAUDE-3")  # Case insensitive
    
    # Test negative cases
    assert not model_name_has_claude("gpt-4")
    assert not model_name_has_claude("gemini-pro")
    assert not model_name_has_claude("")
    assert not model_name_has_claude(None)


def test_is_anthropic_claude():
    """Test is_anthropic_claude function."""
    # Test positive cases - Anthropic provider
    assert is_anthropic_claude({"provider": "anthropic", "model": "claude-3.7"})
    assert is_anthropic_claude({"provider": "Anthropic", "model": "claude-3.5-sonnet"})
    
    # Test positive cases - OpenRouter with Anthropic model
    assert is_anthropic_claude({"provider": "openrouter", "model": "anthropic/claude-3.7"})
    
    # Test positive cases - MakeHub with Anthropic model
    assert is_anthropic_claude({"provider": "makehub", "model": "anthropic/claude-4-sonnet"})
    
    # Test negative cases
    assert not is_anthropic_claude({"provider": "openai", "model": "gpt-4"})
    assert not is_anthropic_claude({"provider": "anthropic", "model": "gpt-4"})  # Wrong model for provider
    assert not is_anthropic_claude({"provider": "openrouter", "model": "openai/gpt-4"})
    assert not is_anthropic_claude({"provider": "anthropic", "model": ""})
    assert not is_anthropic_claude({"provider": "", "model": "claude-3.7"})
    assert not is_anthropic_claude({})
