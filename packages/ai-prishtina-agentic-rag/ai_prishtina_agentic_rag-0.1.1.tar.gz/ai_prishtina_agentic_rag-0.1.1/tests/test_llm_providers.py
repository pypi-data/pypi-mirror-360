"""Tests for LLM provider implementations."""

import asyncio
import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch

from agentic_rag.llm.providers import (
    BaseLLMProvider,
    OpenAIProvider,
    AnthropicProvider,
    LocalModelProvider,
    LLMMessage,
    LLMResponse
)
from agentic_rag.utils.exceptions import LLMError


class TestLLMMessage:
    """Test LLM message model."""
    
    def test_message_creation(self):
        """Test creating an LLM message."""
        message = LLMMessage(
            role="user",
            content="Hello, how are you?",
            metadata={"timestamp": "2024-01-01"}
        )
        
        assert message.role == "user"
        assert message.content == "Hello, how are you?"
        assert message.metadata["timestamp"] == "2024-01-01"


class TestLLMResponse:
    """Test LLM response model."""
    
    def test_response_creation(self):
        """Test creating an LLM response."""
        response = LLMResponse(
            content="Hello! I'm doing well, thank you.",
            usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25},
            metadata={"model": "gpt-3.5-turbo"},
            finish_reason="stop"
        )
        
        assert response.content == "Hello! I'm doing well, thank you."
        assert response.usage["total_tokens"] == 25
        assert response.metadata["model"] == "gpt-3.5-turbo"
        assert response.finish_reason == "stop"


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider for testing base functionality."""
    
    def _get_api_key(self):
        return "mock_api_key"
    
    async def generate(self, messages, **kwargs):
        return LLMResponse(
            content="Mock response",
            usage={"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
            metadata={"model": self.model}
        )
    
    async def generate_stream(self, messages, **kwargs):
        words = ["Mock", " streaming", " response"]
        for word in words:
            yield word


class TestBaseLLMProvider:
    """Test base LLM provider functionality."""
    
    def test_provider_initialization(self):
        """Test provider initialization."""
        provider = MockLLMProvider(
            model="test-model",
            temperature=0.8,
            max_tokens=500
        )
        
        assert provider.model == "test-model"
        assert provider.temperature == 0.8
        assert provider.max_tokens == 500
        assert provider.api_key == "mock_api_key"
    
    @pytest.mark.asyncio
    async def test_chat_interface(self):
        """Test simple chat interface."""
        provider = MockLLMProvider(model="test-model")
        
        response = await provider.chat(
            prompt="Hello",
            system_message="You are a helpful assistant"
        )
        
        assert isinstance(response, LLMResponse)
        assert response.content == "Mock response"
    
    @pytest.mark.asyncio
    async def test_generate_stream(self):
        """Test streaming generation."""
        provider = MockLLMProvider(model="test-model")
        messages = [LLMMessage(role="user", content="Hello")]
        
        chunks = []
        async for chunk in provider.generate_stream(messages):
            chunks.append(chunk)
        
        assert chunks == ["Mock", " streaming", " response"]


@pytest.mark.asyncio
class TestOpenAIProvider:
    """Test OpenAI provider implementation."""
    
    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client."""
        with patch('agentic_rag.llm.providers.AsyncOpenAI') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            yield mock_client
    
    def test_openai_initialization_without_key(self):
        """Test OpenAI initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(LLMError, match="OpenAI API key not provided"):
                OpenAIProvider()
    
    def test_openai_initialization_with_key(self, mock_openai_client):
        """Test OpenAI initialization with API key."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            provider = OpenAIProvider(model="gpt-4")
            
            assert provider.model == "gpt-4"
            assert provider.api_key == "test_key"
    
    async def test_openai_generate(self, mock_openai_client):
        """Test OpenAI text generation."""
        # Mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Generated response"
        mock_response.choices[0].finish_reason = "stop"
        mock_response.usage.prompt_tokens = 10
        mock_response.usage.completion_tokens = 5
        mock_response.usage.total_tokens = 15
        mock_response.model = "gpt-3.5-turbo"
        mock_response.created = 1234567890
        
        mock_openai_client.chat.completions.create.return_value = mock_response
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            provider = OpenAIProvider()
            provider._client = mock_openai_client
            
            messages = [LLMMessage(role="user", content="Hello")]
            response = await provider.generate(messages)
            
            assert isinstance(response, LLMResponse)
            assert response.content == "Generated response"
            assert response.usage["total_tokens"] == 15
            assert response.finish_reason == "stop"
    
    async def test_openai_generate_stream(self, mock_openai_client):
        """Test OpenAI streaming generation."""
        # Mock streaming response
        async def mock_stream():
            chunks = [
                MagicMock(choices=[MagicMock(delta=MagicMock(content="Hello"))]),
                MagicMock(choices=[MagicMock(delta=MagicMock(content=" world"))]),
                MagicMock(choices=[MagicMock(delta=MagicMock(content="!"))])
            ]
            for chunk in chunks:
                yield chunk
        
        mock_openai_client.chat.completions.create.return_value = mock_stream()
        
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
            provider = OpenAIProvider()
            provider._client = mock_openai_client
            
            messages = [LLMMessage(role="user", content="Hello")]
            chunks = []
            async for chunk in provider.generate_stream(messages):
                chunks.append(chunk)
            
            assert chunks == ["Hello", " world", "!"]


@pytest.mark.asyncio
class TestAnthropicProvider:
    """Test Anthropic provider implementation."""
    
    @pytest.fixture
    def mock_anthropic_client(self):
        """Mock Anthropic client."""
        with patch('agentic_rag.llm.providers.AsyncAnthropic') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value = mock_client
            yield mock_client
    
    def test_anthropic_initialization_without_key(self):
        """Test Anthropic initialization without API key."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(LLMError, match="Anthropic API key not provided"):
                AnthropicProvider()
    
    def test_anthropic_initialization_with_key(self, mock_anthropic_client):
        """Test Anthropic initialization with API key."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"}):
            provider = AnthropicProvider(model="claude-3-sonnet-20240229")
            
            assert provider.model == "claude-3-sonnet-20240229"
            assert provider.api_key == "test_key"
    
    async def test_anthropic_generate(self, mock_anthropic_client):
        """Test Anthropic text generation."""
        # Mock response
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Generated response from Claude")]
        mock_response.usage.input_tokens = 10
        mock_response.usage.output_tokens = 8
        mock_response.model = "claude-3-sonnet-20240229"
        mock_response.id = "msg_123"
        mock_response.stop_reason = "end_turn"
        
        mock_anthropic_client.messages.create.return_value = mock_response
        
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"}):
            provider = AnthropicProvider()
            provider._client = mock_anthropic_client
            
            messages = [
                LLMMessage(role="system", content="You are helpful"),
                LLMMessage(role="user", content="Hello")
            ]
            response = await provider.generate(messages)
            
            assert isinstance(response, LLMResponse)
            assert response.content == "Generated response from Claude"
            assert response.usage["total_tokens"] == 18
            assert response.finish_reason == "end_turn"
    
    async def test_anthropic_generate_stream(self, mock_anthropic_client):
        """Test Anthropic streaming generation."""
        # Mock streaming response
        async def mock_stream():
            chunks = [
                MagicMock(type="content_block_delta", delta=MagicMock(text="Hello")),
                MagicMock(type="content_block_delta", delta=MagicMock(text=" from")),
                MagicMock(type="content_block_delta", delta=MagicMock(text=" Claude"))
            ]
            for chunk in chunks:
                yield chunk
        
        mock_anthropic_client.messages.create.return_value = mock_stream()
        
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"}):
            provider = AnthropicProvider()
            provider._client = mock_anthropic_client
            
            messages = [LLMMessage(role="user", content="Hello")]
            chunks = []
            async for chunk in provider.generate_stream(messages):
                chunks.append(chunk)
            
            assert chunks == ["Hello", " from", " Claude"]


@pytest.mark.asyncio
class TestLocalModelProvider:
    """Test local model provider implementation."""
    
    @pytest.fixture
    def mock_transformers(self):
        """Mock transformers components."""
        with patch('agentic_rag.llm.providers.AutoTokenizer') as mock_tokenizer_class, \
             patch('agentic_rag.llm.providers.AutoModelForCausalLM') as mock_model_class, \
             patch('agentic_rag.llm.providers.torch') as mock_torch:
            
            # Mock tokenizer
            mock_tokenizer = MagicMock()
            mock_tokenizer.pad_token = None
            mock_tokenizer.eos_token = "<eos>"
            mock_tokenizer.eos_token_id = 2
            mock_tokenizer.encode.return_value = mock_torch.tensor([[1, 2, 3, 4]])
            mock_tokenizer.decode.return_value = "User: Hello\nAssistant: Hello! How can I help you?"
            mock_tokenizer_class.from_pretrained.return_value = mock_tokenizer
            
            # Mock model
            mock_model = MagicMock()
            mock_model.generate.return_value = mock_torch.tensor([[1, 2, 3, 4, 5, 6, 7]])
            mock_model_class.from_pretrained.return_value = mock_model
            
            # Mock torch tensor
            mock_tensor = MagicMock()
            mock_tensor.shape = [1, 4]  # [batch_size, sequence_length]
            mock_torch.tensor.return_value = mock_tensor
            
            yield {
                'tokenizer': mock_tokenizer,
                'model': mock_model,
                'torch': mock_torch
            }
    
    def test_local_model_initialization(self, mock_transformers):
        """Test local model initialization."""
        provider = LocalModelProvider(model="microsoft/DialoGPT-medium")
        
        assert provider.model == "microsoft/DialoGPT-medium"
        assert provider._tokenizer is not None
        assert provider._model is not None
    
    async def test_local_model_generate(self, mock_transformers):
        """Test local model text generation."""
        provider = LocalModelProvider(model="microsoft/DialoGPT-medium")
        
        messages = [LLMMessage(role="user", content="Hello")]
        response = await provider.generate(messages)
        
        assert isinstance(response, LLMResponse)
        assert response.content == "Hello! How can I help you?"
        assert response.metadata["local"] is True
    
    async def test_local_model_generate_stream(self, mock_transformers):
        """Test local model streaming generation."""
        provider = LocalModelProvider(model="microsoft/DialoGPT-medium")
        
        messages = [LLMMessage(role="user", content="Hello")]
        chunks = []
        async for chunk in provider.generate_stream(messages):
            chunks.append(chunk)
        
        # Should simulate streaming by splitting words
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)


class TestLLMProviderErrors:
    """Test error handling in LLM providers."""
    
    def test_openai_import_error(self):
        """Test OpenAI import error handling."""
        with patch('openai.AsyncOpenAI', side_effect=ImportError):
            with patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"}):
                with pytest.raises(LLMError, match="openai not installed"):
                    OpenAIProvider()
    
    def test_anthropic_import_error(self):
        """Test Anthropic import error handling."""
        with patch('anthropic.AsyncAnthropic', side_effect=ImportError):
            with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test_key"}):
                with pytest.raises(LLMError, match="anthropic not installed"):
                    AnthropicProvider()
    
    def test_local_model_import_error(self):
        """Test local model import error handling."""
        with patch('agentic_rag.llm.providers.AutoTokenizer', side_effect=ImportError):
            with pytest.raises(LLMError, match="transformers not installed"):
                LocalModelProvider(model_path="test-model")
