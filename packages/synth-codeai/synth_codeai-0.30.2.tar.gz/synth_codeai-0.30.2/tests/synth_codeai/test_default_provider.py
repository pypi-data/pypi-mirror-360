"""Tests for default provider and model configuration."""

from dataclasses import dataclass
from typing import Optional

import pytest

from synth_codeai.__main__ import parse_arguments
from synth_codeai.env import validate_environment


@dataclass
class MockArgs:
    """Mock arguments for testing."""

    provider: Optional[str] = None
    expert_provider: Optional[str] = None
    model: Optional[str] = None
    expert_model: Optional[str] = None
    message: Optional[str] = None
    research_only: bool = False
    chat: bool = False


@pytest.fixture
def clean_env(monkeypatch):
    """Remove all provider-related environment variables."""
    env_vars = [
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",  # Added this line
        "OPENROUTER_API_KEY",
        "OPENAI_API_BASE",
        "EXPERT_ANTHROPIC_API_KEY",
        "EXPERT_OPENAI_API_KEY",
        "EXPERT_OPENAI_API_BASE",
        "TAVILY_API_KEY",
        "ANTHROPIC_MODEL",
        "MAKEHUB_API_KEY",
    ]
    for var in env_vars:
        monkeypatch.delenv(var, raising=False)
    yield


def test_default_anthropic_provider(clean_env, monkeypatch):
    """Test that Anthropic is the default provider when no environment variables are set."""
    args = parse_arguments(["-m", "test message"])
    assert args.provider == "anthropic"
    assert (
        args.model == "claude-3-7-sonnet-20250219"
    )  # Updated to match current default


def test_default_openai_provider(clean_env, monkeypatch):
    """Test that OpenAI is the default provider when only OPENAI_API_KEY is set."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    args = parse_arguments(["-m", "test message"])
    assert args.provider == "openai"
    assert args.model == "o4-mini"  # Default OpenAI model

def test_default_openai_over_anthropic(clean_env, monkeypatch):
    """Test that OpenAI is prioritized over Anthropic when both keys are set (and Gemini is not)."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    # Ensure GEMINI_API_KEY is not set (handled by clean_env)
    args = parse_arguments(["-m", "test message"])
    assert args.provider == "openai"
    assert args.model == "o4-mini"


def test_default_gemini_provider(clean_env, monkeypatch):
    """Test that Gemini is the default provider when GEMINI_API_KEY is set."""
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")
    # Also set OpenAI key to ensure Gemini priority
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")
    args = parse_arguments(["-m", "test message"])
    assert args.provider == "gemini"
    assert args.model == "gemini-2.5-pro-preview-05-06" # Default Gemini model


def test_respects_user_specified_anthropic_model(clean_env):
    """Test that user-specified Anthropic models are respected."""
    args = parse_arguments(
        [
            "-m",
            "test message",
            "--provider",
            "anthropic",
            "--model",
            "claude-3-5-sonnet-20241022",
        ]
    )
    assert args.provider == "anthropic"
    assert args.model == "claude-3-5-sonnet-20241022"  # Should not be overridden


TEST_CASES = [
    pytest.param(
        "research_only_no_provider",
        MockArgs(research_only=True),
        {},
        "No provider specified",
        id="research_only_no_provider",
    ),
    pytest.param(
        "research_only_anthropic",
        MockArgs(research_only=True, provider="anthropic"),
        {},
        None,
        id="research_only_anthropic",
    ),
    pytest.param(
        "research_only_non_anthropic_no_model",
        MockArgs(research_only=True, provider="openai"),
        {},
        "Model is required for non-Anthropic providers",
        id="research_only_non_anthropic_no_model",
    ),
    pytest.param(
        "research_only_non_anthropic_with_model",
        MockArgs(research_only=True, provider="openai", model="gpt-4"),
        {},
        None,
        id="research_only_non_anthropic_with_model",
    ),
]


@pytest.mark.parametrize("test_name,args,env_vars,expected_error", TEST_CASES)
def test_research_only_provider_validation(
    test_name: str, args: MockArgs, env_vars: dict, expected_error: str, monkeypatch
):
    """Test provider and model validation in research-only mode."""
    # Set test environment variables
    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    if expected_error:
        with pytest.raises(SystemExit, match=expected_error):
            validate_environment(args)
    else:
        validate_environment(args)
