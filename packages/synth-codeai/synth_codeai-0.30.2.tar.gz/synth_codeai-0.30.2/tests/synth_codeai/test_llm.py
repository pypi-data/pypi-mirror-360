import os
from dataclasses import dataclass
from unittest import mock
from unittest.mock import Mock, patch

import pytest
from langchain_anthropic.chat_models import ChatAnthropic
from langchain_core.messages import HumanMessage
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from langchain_openai.chat_models import ChatOpenAI

from synth_codeai.agent_backends.ciayn_agent import CiaynAgent
from synth_codeai.env import validate_environment
from synth_codeai.llm import (
    create_llm_client,
    get_available_openai_models,
    get_env_var,
    get_provider_config,
    initialize_expert_llm,
    initialize_llm,
    select_expert_model,
)


@pytest.fixture
def clean_env(monkeypatch):
    """Remove relevant environment variables before each test"""
    env_vars = [
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "OPENROUTER_API_KEY",
        "MAKEHUB_API_KEY",
        "OPENAI_API_BASE",
        "EXPERT_ANTHROPIC_API_KEY",
        "EXPERT_OPENAI_API_KEY",
        "EXPERT_OPENROUTER_API_KEY",
        "EXPERT_MAKEHUB_API_KEY",
        "EXPERT_OPENAI_API_BASE",
        "GEMINI_API_KEY",
        "EXPERT_GEMINI_API_KEY",
    ]
    for var in env_vars:
        monkeypatch.delenv(var, raising=False)


@pytest.fixture
def mock_openai():
    """
    Mock ChatOpenAI class for testing OpenAI provider initialization.
    Prevents actual API calls during testing.
    """
    with patch("synth_codeai.llm.ChatOpenAI") as mock:
        mock.return_value = Mock(spec=ChatOpenAI)
        yield mock


def test_initialize_expert_defaults(clean_env, mock_openai, monkeypatch):
    """Test expert LLM initialization with explicit parameters."""
    monkeypatch.setenv("EXPERT_OPENAI_API_KEY", "test-key")
    _llm = initialize_expert_llm("openai", "o1")

    mock_openai.assert_called_once_with(
        api_key="test-key",
        model="o1",
        reasoning_effort="high",
        timeout=180,
        max_retries=5,
        metadata={"model_name": "o1", "provider": "openai"},
    )


def test_initialize_expert_openai_custom(clean_env, mock_openai, monkeypatch):
    """Test expert OpenAI initialization with custom parameters."""
    monkeypatch.setenv("EXPERT_OPENAI_API_KEY", "test-key")
    _llm = initialize_expert_llm("openai", "gpt-4-preview")

    mock_openai.assert_called_once_with(
        api_key="test-key",
        model="gpt-4-preview",
        temperature=0,
        timeout=180,
        max_retries=5,
        metadata={"model_name": "gpt-4-preview", "provider": "openai"},
    )


def test_initialize_expert_gemini(clean_env, mock_gemini, monkeypatch):
    """Test expert Gemini initialization."""
    monkeypatch.setenv("EXPERT_GEMINI_API_KEY", "test-key")
    _llm = initialize_expert_llm("gemini", "gemini-2.0-flash-thinking-exp-1219")

    mock_gemini.assert_called_once_with(
        api_key="test-key",
        model="gemini-2.0-flash-thinking-exp-1219",
        temperature=0,
        timeout=180,
        max_retries=5,
        metadata={"model_name": "gemini-2.0-flash-thinking-exp-1219", "provider": "gemini"},
    )


def test_initialize_expert_anthropic(clean_env, mock_anthropic, monkeypatch):
    """Test expert Anthropic initialization."""
    monkeypatch.setenv("EXPERT_ANTHROPIC_API_KEY", "test-key")
    _llm = initialize_expert_llm("anthropic", "claude-3")

    # Check that mock_anthropic was called
    assert mock_anthropic.called

    # Verify essential parameters
    kwargs = mock_anthropic.call_args.kwargs
    assert kwargs["api_key"] == "test-key"
    assert kwargs["model_name"] == "claude-3"
    assert kwargs["temperature"] == 0
    assert kwargs["timeout"] == 180
    assert kwargs["max_retries"] == 5


def test_initialize_expert_openrouter(clean_env, mock_openai, monkeypatch):
    """Test expert OpenRouter initialization."""
    monkeypatch.setenv("EXPERT_OPENROUTER_API_KEY", "test-key")
    _llm = initialize_expert_llm("openrouter", "models/mistral-large")

    mock_openai.assert_called_once_with(
        api_key="test-key",
        base_url="https://openrouter.ai/api/v1",
        model="models/mistral-large",
        temperature=0,
        timeout=180,
        max_retries=5,
        default_headers={"HTTP-Referer": "https://synth-codeai.ai", "X-Title": "synth.codeai"},
        metadata={"model_name": "models/mistral-large", "provider": "openrouter"},
    )


def test_initialize_expert_makehub(clean_env, mock_openai, monkeypatch):
    """Test expert MakeHub initialization."""
    monkeypatch.setenv("EXPERT_MAKEHUB_API_KEY", "test-key")
    _llm = initialize_expert_llm("makehub", "anthropic/claude-4-sonnet")

    mock_openai.assert_called_once_with(
        api_key="test-key",
        base_url="https://api.makehub.ai/v1",
        model="anthropic/claude-4-sonnet",
        temperature=0,
        timeout=180,
        max_retries=5,
        default_headers={"HTTP-Referer": "https://synth-codeai.ai", "X-Title": "synth.codeai"},
        metadata={"model_name": "anthropic/claude-4-sonnet", "provider": "makehub"},
    )


def test_initialize_expert_openai_compatible(clean_env, mock_openai, monkeypatch):
    """Test expert OpenAI-compatible initialization."""
    monkeypatch.setenv("EXPERT_OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("EXPERT_OPENAI_API_BASE", "http://test-url")
    _llm = initialize_expert_llm("openai-compatible", "local-model")

    mock_openai.assert_called_once_with(
        api_key="test-key",
        base_url="http://test-url",
        model="local-model",
        temperature=0,
        timeout=180,
        max_retries=5,
        metadata={"model_name": "local-model", "provider": "openai-compatible"},
    )


def test_initialize_expert_unsupported_provider(clean_env):
    """Test error handling for unsupported provider in expert mode."""
    with pytest.raises(ValueError, match=r"Unsupported provider: unknown"):
        initialize_expert_llm("unknown", "model")


def test_estimate_tokens():
    """Test token estimation functionality."""
    # Test empty/None cases
    assert CiaynAgent._estimate_tokens(None) == 0
    assert CiaynAgent._estimate_tokens("") == 0

    # Test string content
    assert CiaynAgent._estimate_tokens("test") == 2  # 4 bytes
    assert CiaynAgent._estimate_tokens("hello world") == 5  # 11 bytes
    assert CiaynAgent._estimate_tokens("🚀") == 2  # 4 bytes

    # Test message content
    msg = HumanMessage(content="test message")
    assert CiaynAgent._estimate_tokens(msg) == 6  # 11 bytes


def test_initialize_openai(clean_env, mock_openai):
    """Test OpenAI provider initialization"""
    os.environ["OPENAI_API_KEY"] = "test-key"
    _model = initialize_llm("openai", "gpt-4", temperature=0.7)

    mock_openai.assert_called_once_with(
        api_key="test-key",
        model="gpt-4",
        temperature=0.7,
        timeout=180,
        max_retries=5,
        metadata={"model_name": "gpt-4", "provider": "openai"},
    )


def test_initialize_gemini(clean_env, mock_gemini):
    """Test Gemini provider initialization"""
    os.environ["GEMINI_API_KEY"] = "test-key"
    _model = initialize_llm(
        "gemini", "gemini-2.0-flash-thinking-exp-1219", temperature=0.7
    )

    mock_gemini.assert_called_with(
        api_key="test-key",
        model="gemini-2.0-flash-thinking-exp-1219",
        temperature=0.7,
        timeout=180,
        max_retries=5,
        metadata={"model_name": "gemini-2.0-flash-thinking-exp-1219", "provider": "gemini" },
    )


def test_initialize_anthropic(clean_env, mock_anthropic):
    """Test Anthropic provider initialization"""
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    _model = initialize_llm("anthropic", "claude-3", temperature=0.7)

    # Check that mock_anthropic was called
    assert mock_anthropic.called

    # Verify essential parameters
    kwargs = mock_anthropic.call_args.kwargs
    assert kwargs["api_key"] == "test-key"
    assert kwargs["model_name"] == "claude-3"
    assert kwargs["temperature"] == 0.7
    assert kwargs["timeout"] == 180
    assert kwargs["max_retries"] == 5


def test_initialize_openrouter(clean_env, mock_openai):
    """Test OpenRouter provider initialization"""
    os.environ["OPENROUTER_API_KEY"] = "test-key"
    _model = initialize_llm("openrouter", "mistral-large", temperature=0.7)

    mock_openai.assert_called_with(
        api_key="test-key",
        base_url="https://openrouter.ai/api/v1",
        model="mistral-large",
        temperature=0.7,
        timeout=180,
        max_retries=5,
        default_headers={"HTTP-Referer": "https://synth-codeai.ai", "X-Title": "synth.codeai"},
        metadata={"model_name": "mistral-large", "provider": "openrouter"},
    )


def test_initialize_makehub(clean_env, mock_openai):
    """Test MakeHub provider initialization"""
    os.environ["MAKEHUB_API_KEY"] = "test-key"
    _model = initialize_llm("makehub", "anthropic/claude-4-sonnet", temperature=0.7)

    mock_openai.assert_called_with(
        api_key="test-key",
        base_url="https://api.makehub.ai/v1",
        model="anthropic/claude-4-sonnet",
        temperature=0.7,
        timeout=180,
        max_retries=5,
        default_headers={"HTTP-Referer": "https://synth-codeai.ai", "X-Title": "synth.codeai"},
        metadata={"model_name": "anthropic/claude-4-sonnet", "provider": "makehub"},
    )


def test_initialize_openai_compatible(clean_env, mock_openai):
    """Test OpenAI-compatible provider initialization"""
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["OPENAI_API_BASE"] = "https://custom-endpoint/v1"
    _model = initialize_llm("openai-compatible", "local-model", temperature=0.3)

    mock_openai.assert_called_with(
        api_key="test-key",
        base_url="https://custom-endpoint/v1",
        model="local-model",
        temperature=0.3,
        timeout=180,
        max_retries=5,
        metadata={"model_name": "local-model", "provider": "openai-compatible"},
    )


def test_initialize_unsupported_provider(clean_env):
    """Test initialization with unsupported provider raises ValueError"""
    with pytest.raises(ValueError, match=r"Unsupported provider: unknown"):
        initialize_llm("unknown", "model")


def test_temperature_defaults(clean_env, mock_openai, mock_anthropic, mock_gemini):
    """Test default temperature behavior for different providers."""
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    os.environ["OPENAI_API_BASE"] = "http://test-url"
    os.environ["GEMINI_API_KEY"] = "test-key"

    # Test openai-compatible default temperature
    initialize_llm("openai-compatible", "test-model", temperature=0.3)
    mock_openai.assert_called_with(
        api_key="test-key",
        base_url="http://test-url",
        model="test-model",
        temperature=0.3,
        timeout=180,
        max_retries=5,
        metadata={"model_name": "test-model", "provider": "openai-compatible"},
    )

    # Test default temperature when none is provided for models that support it
    initialize_llm("openai", "test-model")
    mock_openai.assert_called_with(
        api_key="test-key",
        model="test-model",
        temperature=0.7,
        timeout=180,
        max_retries=5,
        metadata={"model_name": "test-model", "provider": "openai"},
    )

    initialize_llm("anthropic", "test-model")

    # Verify essential parameters for Anthropic
    kwargs = mock_anthropic.call_args.kwargs
    assert kwargs["api_key"] == "test-key"
    assert kwargs["model_name"] == "test-model"
    assert kwargs["temperature"] == 0.7
    assert kwargs["timeout"] == 180
    assert kwargs["max_retries"] == 5

    initialize_llm("gemini", "test-model")
    mock_gemini.assert_called_with(
        api_key="test-key",
        model="test-model",
        temperature=0.7,
        timeout=180,
        max_retries=5,
        metadata={"model_name": "test-model", "provider": "gemini"},
    )

    # Test expert models don't require temperature
    initialize_expert_llm("openai", "o1")
    mock_openai.assert_called_with(
        api_key="test-key",
        model="o1",
        reasoning_effort="high",
        timeout=180,
        max_retries=5,
        metadata={"model_name": "o1", "provider": "openai"},
    )

    initialize_expert_llm("openai", "o1-mini")
    mock_openai.assert_called_with(
        api_key="test-key",
        model="o1-mini",
        reasoning_effort="high",
        timeout=180,
        max_retries=5,
        metadata={"model_name": "o1-mini", "provider": "openai"},
    )


def test_explicit_temperature(clean_env, mock_openai, mock_anthropic, mock_gemini):
    """Test explicit temperature setting for each provider."""
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["ANTHROPIC_API_KEY"] = "test-key"
    os.environ["OPENROUTER_API_KEY"] = "test-key"
    os.environ["MAKEHUB_API_KEY"] = "test-key"
    os.environ["GEMINI_API_KEY"] = "test-key"

    test_temp = 0.7

    # Test OpenAI
    initialize_llm("openai", "test-model", temperature=test_temp)
    mock_openai.assert_called_with(
        api_key="test-key",
        model="test-model",
        temperature=test_temp,
        timeout=180,
        max_retries=5,
        metadata={"model_name": "test-model", "provider": "openai"},
    )

    # Test Gemini
    initialize_llm("gemini", "test-model", temperature=test_temp)
    mock_gemini.assert_called_with(
        api_key="test-key",
        model="test-model",
        temperature=test_temp,
        timeout=180,
        max_retries=5,
        metadata={"model_name": "test-model", "provider": "gemini"},
    )

    # Test Anthropic
    initialize_llm("anthropic", "test-model", temperature=test_temp)

    # Verify essential parameters for Anthropic
    kwargs = mock_anthropic.call_args.kwargs
    assert kwargs["api_key"] == "test-key"
    assert kwargs["model_name"] == "test-model"
    assert kwargs["temperature"] == test_temp
    assert kwargs["timeout"] == 180
    assert kwargs["max_retries"] == 5

    # Test OpenRouter
    initialize_llm("openrouter", "test-model", temperature=test_temp)
    mock_openai.assert_called_with(
        api_key="test-key",
        base_url="https://openrouter.ai/api/v1",
        model="test-model",
        temperature=test_temp,
        timeout=180,
        max_retries=5,
        default_headers={"HTTP-Referer": "https://synth-codeai.ai", "X-Title": "synth.codeai"},
        metadata={"model_name": "test-model", "provider": "openrouter"},
    )

    # Test MakeHub
    initialize_llm("makehub", "test-model", temperature=test_temp)
    mock_openai.assert_called_with(
        api_key="test-key",
        base_url="https://api.makehub.ai/v1",
        model="test-model",
        temperature=test_temp,
        timeout=180,
        max_retries=5,
        default_headers={"HTTP-Referer": "https://synth-codeai.ai", "X-Title": "synth.codeai"},
        metadata={"model_name": "test-model", "provider": "makehub"},
    )


def test_get_available_openai_models_success():
    """Test successful retrieval of OpenAI models."""
    mock_model = Mock()
    mock_model.id = "gpt-4"
    mock_models = Mock()
    mock_models.data = [mock_model]

    with mock.patch("synth_codeai.llm.OpenAI") as mock_client:
        mock_client.return_value.models.list.return_value = mock_models
        models = get_available_openai_models()
        assert models == ["gpt-4"]
        mock_client.return_value.models.list.assert_called_once()


def test_get_available_openai_models_failure():
    """Test graceful handling of model retrieval failure."""
    with mock.patch("synth_codeai.llm.OpenAI") as mock_client:
        mock_client.return_value.models.list.side_effect = Exception("API Error")
        models = get_available_openai_models()
        assert models == []
        mock_client.return_value.models.list.assert_called_once()


def test_select_expert_model_explicit():
    """Test model selection with explicitly specified model."""
    model = select_expert_model("openai", "gpt-4")
    assert model == "gpt-4"


def test_select_expert_model_non_openai():
    """Test model selection for non-OpenAI provider."""
    model = select_expert_model("anthropic", None)
    assert model is None


def test_select_expert_model_priority():
    """Test model selection follows priority order (o3 first)."""
    available_models = ["gpt-4", "o3", "o1"]

    with mock.patch(
        "synth_codeai.llm.get_available_openai_models", return_value=available_models
    ):
        model = select_expert_model("openai")
        assert model == "o3"


def test_select_expert_model_priority_fallback_fails():
    """Test that selection returns None if 'o3' is not available."""
    available_models = ["gpt-4", "o1", "o1-preview"] # Does not contain 'o3'

    with mock.patch(
        "synth_codeai.llm.get_available_openai_models", return_value=available_models
    ):
        model = select_expert_model("openai")
        assert model is None # Should be None as 'o3' is the only priority


def test_initialize_llm_default_expert_openai_selects_o3(clean_env, mock_openai, monkeypatch):
    """Test that initialize_llm selects 'o3' as default expert if available."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key") # Use base key
    available_models = ["gpt-4", "o3", "o4-mini"] # Mock 'o3' as available

    with mock.patch(
        "synth_codeai.llm.get_available_openai_models", return_value=available_models
    ):
        # Call initialize_expert_llm without specifying an expert model.
        # It should default to 'o3' because it's available.
        # initialize_expert_llm implicitly calls create_llm_client with is_expert=True
        _llm = initialize_expert_llm(provider="openai", model_name=None)

        # Assert that ChatOpenAI was called with 'o3'
        mock_openai.assert_called_once()
        call_args, call_kwargs = mock_openai.call_args
        assert call_kwargs.get("model") == "o3"
        assert call_kwargs.get("api_key") == "test-key" # Should use base key if expert not set
        # Expert models should default to temperature 0 / high reasoning effort
        assert "temperature" not in call_kwargs or call_kwargs.get("temperature") == 0
        assert call_kwargs.get("reasoning_effort") == "high"


def test_temperature_validation(clean_env, mock_openai):
    """Test temperature validation in command line arguments."""
    from synth_codeai.__main__ import parse_arguments

    # Test temperature below minimum
    with pytest.raises(SystemExit):
        parse_arguments(["--message", "test", "--temperature", "-0.1"])

    # Test temperature above maximum
    with pytest.raises(SystemExit):
        parse_arguments(["--message", "test", "--temperature", "2.1"])

    # Test valid temperature
    args = parse_arguments(["--message", "test", "--temperature", "0.7"])
    assert args.temperature == 0.7


def test_provider_name_validation():
    """Test provider name validation and normalization."""
    # Test all supported providers
    providers = ["openai", "anthropic", "openrouter", "openai-compatible", "gemini"]
    for provider in providers:
        try:
            with patch("synth_codeai.llm.ChatOpenAI"), patch("synth_codeai.llm.ChatAnthropic"):
                initialize_llm(provider, "test-model", temperature=0.7)
        except ValueError as e:
            if "Temperature must be provided" not in str(e):
                pytest.fail(
                    f"Valid provider {provider} raised unexpected ValueError: {e}"
                )


def test_initialize_llm_cross_provider(
    clean_env, mock_openai, mock_anthropic, mock_gemini, monkeypatch
):
    """Test initializing different providers in sequence."""
    # Initialize OpenAI
    monkeypatch.setenv("OPENAI_API_KEY", "openai-key")
    _llm1 = initialize_llm("openai", "gpt-4", temperature=0.7)
    mock_openai.assert_called_with(
        api_key="openai-key",
        model="gpt-4",
        temperature=0.7,
        timeout=180,
        max_retries=5,
        metadata={"model_name": "gpt-4", "provider": "openai"},
    )

    # Initialize Anthropic
    monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-key")
    _llm2 = initialize_llm("anthropic", "claude-3", temperature=0.7)

    # Verify essential parameters for Anthropic
    kwargs = mock_anthropic.call_args.kwargs
    assert kwargs["api_key"] == "anthropic-key"
    assert kwargs["model_name"] == "claude-3"
    assert kwargs["temperature"] == 0.7
    assert kwargs["timeout"] == 180
    assert kwargs["max_retries"] == 5

    # Initialize Gemini
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-key")
    _llm3 = initialize_llm("gemini", "gemini-pro", temperature=0.7)
    mock_gemini.assert_called_with(
        api_key="gemini-key",
        model="gemini-pro",
        temperature=0.7,
        timeout=180,
        max_retries=5,
        metadata={"model_name": "gemini-pro", "provider": "gemini"},
    )

    # Initialize MakeHub
    monkeypatch.setenv("MAKEHUB_API_KEY", "makehub-key")
    _llm4 = initialize_llm("makehub", "anthropic/claude-4-sonnet", temperature=0.7)
    mock_openai.assert_called_with(
        api_key="makehub-key",
        base_url="https://api.makehub.ai/v1",
        model="anthropic/claude-4-sonnet",
        temperature=0.7,
        timeout=180,
        max_retries=5,
        default_headers={"HTTP-Referer": "https://synth-codeai.ai", "X-Title": "synth.codeai"},
        metadata={"model_name": "anthropic/claude-4-sonnet", "provider": "makehub"},
    )


@dataclass
class Args:
    """Test arguments class."""

    provider: str
    expert_provider: str
    model: str = None
    expert_model: str = None


def test_environment_variable_precedence(clean_env, mock_openai, monkeypatch):
    """Test environment variable precedence and fallback."""
    # Test get_env_var helper with fallback
    monkeypatch.setenv("TEST_KEY", "base-value")
    monkeypatch.setenv("EXPERT_TEST_KEY", "expert-value")

    assert get_env_var("TEST_KEY") == "base-value"
    assert get_env_var("TEST_KEY", expert=True) == "expert-value"

    # Test fallback when expert value not set
    monkeypatch.delenv("EXPERT_TEST_KEY", raising=False)
    assert get_env_var("TEST_KEY", expert=True) == "base-value"

    # Test provider config
    monkeypatch.setenv("EXPERT_OPENAI_API_KEY", "expert-key")
    config = get_provider_config("openai", is_expert=True)
    assert config["api_key"] == "expert-key"

    # Test LLM client creation with expert mode
    _llm = create_llm_client("openai", "o1", is_expert=True)
    mock_openai.assert_called_with(
        api_key="expert-key",
        model="o1",
        reasoning_effort="high",
        timeout=180,
        max_retries=5,
        metadata={"model_name": "o1", "provider": "openai"},
    )

    # Test environment validation
    monkeypatch.setenv("EXPERT_OPENAI_API_KEY", "")
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("TAVILY_API_KEY", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "anthropic-key")
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-key")
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")

    args = Args(provider="anthropic", expert_provider="openai")
    expert_enabled, expert_missing, web_enabled, web_missing = validate_environment(
        args
    )
    assert not expert_enabled
    assert expert_missing
    assert not web_enabled
    assert web_missing


@pytest.fixture
def mock_anthropic():
    """
    Mock ChatAnthropic class for testing Anthropic provider initialization.
    Prevents actual API calls during testing.
    """
    with patch("synth_codeai.llm.ChatAnthropic") as mock:
        mock.return_value = Mock(spec=ChatAnthropic)
        yield mock


@pytest.fixture
def mock_gemini():
    """Mock ChatGoogleGenerativeAI class for testing Gemini provider initialization."""
    with patch("synth_codeai.llm.ChatGoogleGenerativeAI") as mock:
        mock.return_value = Mock(spec=ChatGoogleGenerativeAI)
        yield mock


@pytest.fixture
def mock_deepseek_reasoner():
    """Mock ChatDeepseekReasoner for testing DeepSeek provider initialization."""
    with patch("synth_codeai.llm.ChatDeepseekReasoner") as mock:
        mock.return_value = Mock()
        yield mock


@pytest.fixture
def mock_deepseek():
    """Mock ChatDeepSeek for testing DeepSeek provider initialization."""
    with patch("synth_codeai.llm.ChatDeepSeek") as mock:
        mock.return_value = Mock()
        yield mock


def test_reasoning_effort_only_passed_to_supported_models(
    clean_env, mock_openai, monkeypatch
):
    """Test that reasoning_effort is only passed to supported models."""
    monkeypatch.setenv("EXPERT_OPENAI_API_KEY", "test-key")

    # Initialize expert LLM with GPT-4 (which doesn't support reasoning_effort)
    _llm = initialize_expert_llm("openai", "gpt-4")

    # Verify reasoning_effort was not included in kwargs
    mock_openai.assert_called_with(
        api_key="test-key",
        model="gpt-4",
        temperature=0,
        timeout=180,
        max_retries=5,
        metadata={"model_name": "gpt-4", "provider": "openai"},
    )


def test_reasoning_effort_passed_to_supported_models(
    clean_env, mock_openai, monkeypatch
):
    """Test that reasoning_effort is passed to models that support it."""
    monkeypatch.setenv("EXPERT_OPENAI_API_KEY", "test-key")

    # Initialize expert LLM with o1 (which supports reasoning_effort)
    _llm = initialize_expert_llm("openai", "o1")

    # Verify reasoning_effort was included in kwargs
    mock_openai.assert_called_with(
        api_key="test-key",
        model="o1",
        reasoning_effort="high",
        timeout=180,
        max_retries=5,
        metadata={"model_name": "o1", "provider": "openai"},
    )


def test_initialize_deepseek(
    clean_env, mock_openai, mock_deepseek_reasoner, mock_deepseek, monkeypatch
):
    """Test DeepSeek provider initialization with different models."""
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    # Test with reasoner model
    _model = initialize_llm("deepseek", "deepseek-reasoner", temperature=0.7)
    mock_deepseek_reasoner.assert_called_with(
        api_key="test-key",
        base_url="https://api.deepseek.com",
        model="deepseek-reasoner",
        temperature=0.7,
        timeout=180,
        max_retries=5,
        metadata={"model_name": "deepseek-reasoner", "provider": "deepseek"},
    )

    # Test with deepseek-chat model (should use ChatDeepSeek)
    _model = initialize_llm("deepseek", "deepseek-chat", temperature=0.7)
    mock_deepseek.assert_called_with(
        api_key="test-key",
        model="deepseek-chat",
        temperature=0.7,
        timeout=180,
        max_retries=5,
        metadata={"model_name": "deepseek-chat", "provider": "deepseek"},
    )

    # Test with OpenAI-compatible model (non-deepseek-chat)
    _model = initialize_llm("deepseek", "other-model", temperature=0.7)
    mock_openai.assert_called_with(
        api_key="test-key",
        base_url="https://api.deepseek.com",
        model="other-model",
        temperature=0.7,
        timeout=180,
        max_retries=5,
        metadata={"model_name": "other-model", "provider": "deepseek"},
    )


def test_initialize_openrouter_deepseek(
    clean_env, mock_openai, mock_deepseek_reasoner, monkeypatch
):
    """Test OpenRouter DeepSeek model initialization."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    # Test with DeepSeek R1 model
    _model = initialize_llm("openrouter", "deepseek/deepseek-r1", temperature=0.7)
    mock_deepseek_reasoner.assert_called_with(
        api_key="test-key",
        base_url="https://openrouter.ai/api/v1",
        model="deepseek/deepseek-r1",
        temperature=0.7,
        timeout=180,
        max_retries=5,
        default_headers={"HTTP-Referer": "https://synth-codeai.ai", "X-Title": "synth.codeai"},
        metadata={"model_name": "deepseek/deepseek-r1", "provider": "openrouter"},
    )


def test_makehub_price_performance_ratio(clean_env, mock_openai, monkeypatch):
    """Test MakeHub price_performance_ratio configuration."""
    from unittest.mock import Mock
    
    # Mock config repository
    mock_config_repo = Mock()
    mock_config_repo.get.return_value = 0.8  # Mock price_performance_ratio value
    
    with patch("synth_codeai.llm.get_config_repository", return_value=mock_config_repo):
        monkeypatch.setenv("MAKEHUB_API_KEY", "test-key")
        _model = initialize_llm("makehub", "anthropic/claude-4-sonnet", temperature=0.7)

        # Verify that the price-performance ratio header is included
        expected_headers = {
            "HTTP-Referer": "https://synth-codeai.ai",
            "X-Title": "synth.codeai",
            "X-Price-Performance-Ratio": "0.8"
        }
        
        mock_openai.assert_called_with(
            api_key="test-key",
            base_url="https://api.makehub.ai/v1",
            model="anthropic/claude-4-sonnet",
            temperature=0.7,
            timeout=180,
            max_retries=5,
            default_headers=expected_headers,
            metadata={"model_name": "anthropic/claude-4-sonnet", "provider": "makehub"},
        )


def test_makehub_no_price_performance_ratio(clean_env, mock_openai, monkeypatch):
    """Test MakeHub without price_performance_ratio configuration."""
    from unittest.mock import Mock
    
    # Mock config repository with no price_performance_ratio
    mock_config_repo = Mock()
    mock_config_repo.get.return_value = None
    
    with patch("synth_codeai.llm.get_config_repository", return_value=mock_config_repo):
        monkeypatch.setenv("MAKEHUB_API_KEY", "test-key")
        _model = initialize_llm("makehub", "anthropic/claude-4-sonnet", temperature=0.7)

        # Verify that no price-performance ratio header is included
        expected_headers = {
            "HTTP-Referer": "https://synth-codeai.ai",
            "X-Title": "synth.codeai"
        }
        
        mock_openai.assert_called_with(
            api_key="test-key",
            base_url="https://api.makehub.ai/v1",
            model="anthropic/claude-4-sonnet",
            temperature=0.7,
            timeout=180,
            max_retries=5,
            default_headers=expected_headers,
            metadata={"model_name": "anthropic/claude-4-sonnet", "provider": "makehub"},
        )
