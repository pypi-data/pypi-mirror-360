"""LLM provider implementations for the Agentic RAG library."""

import asyncio
import json
import os
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, AsyncGenerator

from pydantic import BaseModel, Field

from ..utils.exceptions import LLMError
from ..utils.logging import LoggerMixin


class LLMMessage(BaseModel):
    """Message for LLM conversation."""
    
    role: str = Field(description="Message role (system, user, assistant)")
    content: str = Field(description="Message content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Message metadata")


class LLMResponse(BaseModel):
    """Response from LLM provider."""

    content: str = Field(description="Generated content")
    model: Optional[str] = Field(default=None, description="Model used for generation")
    usage: Dict[str, Any] = Field(default_factory=dict, description="Token usage information")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")
    finish_reason: Optional[str] = Field(default=None, description="Reason for completion")


class BaseLLMProvider(ABC, LoggerMixin):
    """Abstract base class for LLM providers."""
    
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        timeout: int = 30,
        **kwargs
    ):
        self.model = model
        self.api_key = api_key or self._get_api_key()
        self.base_url = base_url
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.kwargs = kwargs
    
    @abstractmethod
    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment or configuration."""
        pass
    
    @abstractmethod
    async def generate(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """Generate response from messages."""
        pass
    
    @abstractmethod
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response from messages."""
        pass
    
    async def chat(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Simple chat interface."""
        messages = []
        
        if system_message:
            messages.append(LLMMessage(role="system", content=system_message))
        
        messages.append(LLMMessage(role="user", content=prompt))
        
        return await self.generate(messages, **kwargs)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider implementation."""
    
    def __init__(self, model: str = "gpt-3.5-turbo", **kwargs):
        super().__init__(model=model, **kwargs)
        self._client = None
        self._initialize_client()
    
    def _get_api_key(self) -> Optional[str]:
        """Get OpenAI API key from environment."""
        return os.getenv("OPENAI_API_KEY")
    
    def _initialize_client(self) -> None:
        """Initialize OpenAI client."""
        try:
            from openai import AsyncOpenAI
            
            if not self.api_key:
                raise LLMError("OpenAI API key not provided")
            
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout
            )
            
            self.logger.info(f"Initialized OpenAI client with model: {self.model}")
            
        except ImportError:
            raise LLMError("openai not installed. Install with: pip install openai")
        except Exception as e:
            raise LLMError(f"Failed to initialize OpenAI client: {e}")
    
    async def generate(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """Generate response using OpenAI."""
        if not self._client:
            raise LLMError("OpenAI client not initialized")
        
        try:
            # Convert messages to OpenAI format
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            # Merge kwargs with instance settings
            params = {
                "model": self.model,
                "messages": openai_messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                **{k: v for k, v in kwargs.items() if k not in ["temperature", "max_tokens"]}
            }
            
            response = await self._client.chat.completions.create(**params)
            
            return LLMResponse(
                content=response.choices[0].message.content,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                metadata={
                    "model": response.model,
                    "created": response.created
                },
                finish_reason=response.choices[0].finish_reason
            )
            
        except Exception as e:
            raise LLMError(f"OpenAI generation failed: {e}", provider="openai", model=self.model)
    
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> AsyncGenerator[LLMResponse, None]:
        """Generate streaming response using OpenAI with advanced features."""
        if not self._client:
            raise LLMError("OpenAI client not initialized")

        try:
            # Convert messages to OpenAI format
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]

            # Enhanced streaming parameters
            params = {
                "model": self.model,
                "messages": openai_messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "stream": True,
                "stream_options": {"include_usage": True} if kwargs.get("include_usage", True) else None,
                **{k: v for k, v in kwargs.items() if k not in ["temperature", "max_tokens", "stream", "include_usage"]}
            }

            stream = await self._client.chat.completions.create(**params)

            # Track streaming metrics
            accumulated_content = ""
            chunk_count = 0
            start_time = asyncio.get_event_loop().time()

            async for chunk in stream:
                chunk_count += 1
                current_time = asyncio.get_event_loop().time()

                # Handle content chunks
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    accumulated_content += content

                    yield LLMResponse(
                        content=content,
                        model=self.model,
                        usage={
                            "prompt_tokens": 0,  # Will be updated in final chunk
                            "completion_tokens": len(accumulated_content.split()),
                            "total_tokens": 0
                        },
                        metadata={
                            "streaming": True,
                            "chunk_index": chunk_count,
                            "accumulated_length": len(accumulated_content),
                            "generation_time": current_time - start_time,
                            "finish_reason": chunk.choices[0].finish_reason if chunk.choices else None,
                            "tokens_per_second": len(accumulated_content.split()) / max(current_time - start_time, 0.001)
                        }
                    )

                # Handle usage information (final chunk)
                if hasattr(chunk, 'usage') and chunk.usage:
                    yield LLMResponse(
                        content="",  # Empty content signals end with usage info
                        model=self.model,
                        usage={
                            "prompt_tokens": chunk.usage.prompt_tokens,
                            "completion_tokens": chunk.usage.completion_tokens,
                            "total_tokens": chunk.usage.total_tokens
                        },
                        metadata={
                            "streaming": True,
                            "stream_complete": True,
                            "total_chunks": chunk_count,
                            "total_generation_time": current_time - start_time,
                            "average_tokens_per_second": chunk.usage.completion_tokens / max(current_time - start_time, 0.001),
                            "full_response_length": len(accumulated_content)
                        }
                    )

        except Exception as e:
            raise LLMError(f"OpenAI streaming failed: {e}", provider="openai", model=self.model)


class AnthropicProvider(BaseLLMProvider):
    """Anthropic LLM provider implementation."""
    
    def __init__(self, model: str = "claude-3-sonnet-20240229", **kwargs):
        super().__init__(model=model, **kwargs)
        self._client = None
        self._initialize_client()
    
    def _get_api_key(self) -> Optional[str]:
        """Get Anthropic API key from environment."""
        return os.getenv("ANTHROPIC_API_KEY")
    
    def _initialize_client(self) -> None:
        """Initialize Anthropic client."""
        try:
            from anthropic import AsyncAnthropic
            
            if not self.api_key:
                raise LLMError("Anthropic API key not provided")
            
            self._client = AsyncAnthropic(
                api_key=self.api_key,
                timeout=self.timeout
            )
            
            self.logger.info(f"Initialized Anthropic client with model: {self.model}")
            
        except ImportError:
            raise LLMError("anthropic not installed. Install with: pip install anthropic")
        except Exception as e:
            raise LLMError(f"Failed to initialize Anthropic client: {e}")
    
    async def generate(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """Generate response using Anthropic."""
        if not self._client:
            raise LLMError("Anthropic client not initialized")
        
        try:
            # Convert messages to Anthropic format
            system_message = None
            anthropic_messages = []
            
            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    anthropic_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            # Merge kwargs with instance settings
            params = {
                "model": self.model,
                "messages": anthropic_messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                **{k: v for k, v in kwargs.items() if k not in ["temperature", "max_tokens"]}
            }
            
            if system_message:
                params["system"] = system_message
            
            response = await self._client.messages.create(**params)
            
            return LLMResponse(
                content=response.content[0].text,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                },
                metadata={
                    "model": response.model,
                    "id": response.id
                },
                finish_reason=response.stop_reason
            )
            
        except Exception as e:
            raise LLMError(f"Anthropic generation failed: {e}", provider="anthropic", model=self.model)
    
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Generate streaming response using Anthropic."""
        if not self._client:
            raise LLMError("Anthropic client not initialized")
        
        try:
            # Convert messages to Anthropic format
            system_message = None
            anthropic_messages = []
            
            for msg in messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    anthropic_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            # Merge kwargs with instance settings
            params = {
                "model": self.model,
                "messages": anthropic_messages,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": kwargs.get("max_tokens", self.max_tokens),
                "stream": True,
                **{k: v for k, v in kwargs.items() if k not in ["temperature", "max_tokens", "stream"]}
            }
            
            if system_message:
                params["system"] = system_message
            
            stream = await self._client.messages.create(**params)
            
            async for chunk in stream:
                if chunk.type == "content_block_delta":
                    yield chunk.delta.text
                    
        except Exception as e:
            raise LLMError(f"Anthropic streaming failed: {e}", provider="anthropic", model=self.model)


class LocalModelProvider(BaseLLMProvider):
    """Local model provider using transformers."""
    
    def __init__(self, model: str = "microsoft/DialoGPT-medium", **kwargs):
        super().__init__(model=model, **kwargs)
        self.model_name = model  # Alias for consistency
        self.temperature = kwargs.get("temperature", 0.7)
        self.max_tokens = kwargs.get("max_tokens", 1000)
        self.max_length = kwargs.get("max_length", 2048)
        self._tokenizer = None
        self._model = None
        self._initialize_model()
    
    def _get_api_key(self) -> Optional[str]:
        """Local models don't need API keys."""
        return None
    
    def _initialize_model(self) -> None:
        """Initialize local model and tokenizer."""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            self._tokenizer = AutoTokenizer.from_pretrained(self.model)
            self._model = AutoModelForCausalLM.from_pretrained(self.model)
            
            # Add padding token if not present
            if self._tokenizer.pad_token is None:
                self._tokenizer.pad_token = self._tokenizer.eos_token
            
            self.logger.info(f"Initialized local model: {self.model}")
            
        except ImportError:
            raise LLMError("transformers not installed. Install with: pip install transformers torch")
        except Exception as e:
            raise LLMError(f"Failed to initialize local model: {e}")

    def _messages_to_prompt(self, messages: List[LLMMessage]) -> str:
        """Convert messages to a prompt string."""
        prompt_parts = []

        for message in messages:
            if message.role == "system":
                prompt_parts.append(f"System: {message.content}")
            elif message.role == "user":
                prompt_parts.append(f"Human: {message.content}")
            elif message.role == "assistant":
                prompt_parts.append(f"Assistant: {message.content}")

        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)
    
    async def generate(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """Generate response using local model."""
        if not self._model or not self._tokenizer:
            raise LLMError("Local model not initialized")
        
        try:
            import torch
            
            # Convert messages to text
            text = ""
            for msg in messages:
                if msg.role == "system":
                    text += f"System: {msg.content}\n"
                elif msg.role == "user":
                    text += f"User: {msg.content}\n"
                elif msg.role == "assistant":
                    text += f"Assistant: {msg.content}\n"
            
            text += "Assistant: "
            
            # Tokenize input
            inputs = self._tokenizer.encode(text, return_tensors="pt")
            
            # Generate response
            with torch.no_grad():
                outputs = self._model.generate(
                    inputs,
                    max_length=inputs.shape[1] + kwargs.get("max_tokens", self.max_tokens),
                    temperature=kwargs.get("temperature", self.temperature),
                    do_sample=True,
                    pad_token_id=self._tokenizer.eos_token_id
                )
            
            # Decode response
            response_text = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract only the new generated part
            generated_text = response_text[len(text):].strip()
            
            return LLMResponse(
                content=generated_text,
                usage={
                    "prompt_tokens": inputs.shape[1],
                    "completion_tokens": outputs.shape[1] - inputs.shape[1],
                    "total_tokens": outputs.shape[1]
                },
                metadata={
                    "model": self.model,
                    "local": True
                },
                finish_reason="stop"
            )
            
        except Exception as e:
            raise LLMError(f"Local model generation failed: {e}", provider="local", model=self.model)
    
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> AsyncGenerator[LLMResponse, None]:
        """Generate streaming response using local model with complex implementation."""
        if not self._model or not self._tokenizer:
            raise LLMError("Local model not initialized")

        try:
            import torch
            import threading
            import queue

            # Convert messages to prompt
            prompt = self._messages_to_prompt(messages)

            # Tokenize input
            inputs = self._tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=self.max_length - kwargs.get("max_tokens", self.max_tokens)
            )

            # Setup streaming parameters
            generation_kwargs = {
                "input_ids": inputs["input_ids"],
                "attention_mask": inputs["attention_mask"],
                "max_new_tokens": kwargs.get("max_tokens", self.max_tokens),
                "temperature": kwargs.get("temperature", self.temperature),
                "do_sample": True,
                "pad_token_id": self._tokenizer.eos_token_id,
                "eos_token_id": self._tokenizer.eos_token_id,
            }

            # Create custom streamer for real-time token generation
            class AsyncTextStreamer:
                def __init__(self, tokenizer, skip_prompt=True, timeout=None):
                    self.tokenizer = tokenizer
                    self.skip_prompt = skip_prompt
                    self.timeout = timeout
                    self.token_queue = queue.Queue()
                    self.stop_signal = False
                    self.prompt_length = 0

                def put(self, value):
                    """Called by the model for each generated token."""
                    if self.stop_signal:
                        return

                    if isinstance(value, torch.Tensor):
                        if value.dim() > 1:
                            value = value[0]  # Take first batch

                        # Skip prompt tokens if requested
                        if self.skip_prompt and len(value) <= self.prompt_length:
                            self.prompt_length = len(value)
                            return

                        # Decode new tokens only
                        if self.skip_prompt and self.prompt_length > 0:
                            new_tokens = value[self.prompt_length:]
                            if len(new_tokens) > 0:
                                text = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
                                if text:
                                    self.token_queue.put(text)
                        else:
                            text = self.tokenizer.decode(value, skip_special_tokens=True)
                            if text:
                                self.token_queue.put(text)

                def end(self):
                    """Called when generation is complete."""
                    self.token_queue.put(None)  # Signal end

                def stop(self):
                    """Stop the streaming."""
                    self.stop_signal = True
                    self.token_queue.put(None)

                async def __aiter__(self):
                    """Async iterator for streaming tokens."""
                    last_text = ""
                    while True:
                        try:
                            # Get token with timeout
                            token = await asyncio.get_event_loop().run_in_executor(
                                None,
                                lambda: self.token_queue.get(timeout=self.timeout or 30)
                            )

                            if token is None:  # End signal
                                break

                            # Yield incremental text
                            if token != last_text:
                                new_text = token[len(last_text):] if token.startswith(last_text) else token
                                if new_text:
                                    yield new_text
                                last_text = token

                        except queue.Empty:
                            break
                        except Exception as e:
                            # Log error without logger dependency
                            print(f"Streaming error: {e}")
                            break

            # Initialize streamer
            streamer = AsyncTextStreamer(
                self._tokenizer,
                skip_prompt=True,
                timeout=kwargs.get("stream_timeout", 30)
            )

            # Set prompt length for skipping
            streamer.prompt_length = len(inputs["input_ids"][0])

            # Start generation in background thread
            def generate_in_thread():
                try:
                    if self._model is None or self._tokenizer is None:
                        raise Exception("Model or tokenizer not initialized")

                    with torch.no_grad():
                        # Use model.generate with custom streamer
                        output_ids = self._model.generate(
                            **generation_kwargs,
                            streamer=streamer if hasattr(self._model, 'generate') else None
                        )

                        # If model doesn't support streaming, fall back to manual streaming
                        if not hasattr(self._model, 'generate') or streamer.token_queue.empty():
                            # Decode full output and stream manually
                            full_output = self._tokenizer.decode(
                                output_ids[0][len(inputs["input_ids"][0]):],
                                skip_special_tokens=True
                            )

                            # Stream word by word
                            words = full_output.split()
                            for i, word in enumerate(words):
                                if not streamer.stop_signal:
                                    partial_text = " ".join(words[:i+1])
                                    streamer.token_queue.put(partial_text)

                    streamer.end()

                except Exception as e:
                    self.logger.error(f"Generation thread error: {e}")
                    streamer.stop()

            # Start generation thread
            generation_thread = threading.Thread(target=generate_in_thread)
            generation_thread.daemon = True
            generation_thread.start()

            # Stream tokens as they're generated
            accumulated_text = ""
            token_count = 0
            start_time = asyncio.get_event_loop().time()

            async for token_text in streamer:
                if token_text:
                    accumulated_text += token_text
                    token_count += len(token_text.split())

                    current_time = asyncio.get_event_loop().time()

                    yield LLMResponse(
                        content=token_text,
                        model=self.model_name,
                        usage={
                            "prompt_tokens": len(prompt.split()),
                            "completion_tokens": token_count,
                            "total_tokens": len(prompt.split()) + token_count
                        },
                        metadata={
                            "streaming": True,
                            "chunk_index": token_count,
                            "accumulated_length": len(accumulated_text),
                            "generation_time": current_time - start_time,
                            "tokens_per_second": token_count / max(current_time - start_time, 0.001)
                        }
                    )

            # Wait for generation thread to complete
            generation_thread.join(timeout=kwargs.get("generation_timeout", 60))

            # Final response with complete metadata
            final_time = asyncio.get_event_loop().time()
            yield LLMResponse(
                content="",  # Empty content signals end of stream
                model=self.model_name,
                usage={
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": token_count,
                    "total_tokens": len(prompt.split()) + token_count
                },
                metadata={
                    "streaming": True,
                    "stream_complete": True,
                    "total_generation_time": final_time - start_time,
                    "average_tokens_per_second": token_count / max(final_time - start_time, 0.001),
                    "total_tokens_generated": token_count,
                    "full_response_length": len(accumulated_text)
                }
            )

        except Exception as e:
            raise LLMError(f"Local model streaming failed: {e}") from e


class CohereProvider(BaseLLMProvider):
    """Cohere LLM provider implementation."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "command",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ):
        """
        Initialize Cohere provider.

        Args:
            api_key: Cohere API key
            model: Model name to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
        """
        super().__init__(model=model, **kwargs)
        self.api_key = api_key or os.getenv("COHERE_API_KEY")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = None
        self._initialize_client()

    def _get_api_key(self) -> Optional[str]:
        """Get Cohere API key from environment."""
        return os.getenv("COHERE_API_KEY")

    def _initialize_client(self) -> None:
        """Initialize Cohere client."""
        try:
            import cohere

            if not self.api_key:
                raise LLMError("Cohere API key not provided")

            self._client = cohere.Client(self.api_key)
            self.logger.info(f"Initialized Cohere client with model: {self.model}")

        except ImportError:
            raise LLMError("cohere not installed. Install with: pip install cohere")
        except Exception as e:
            raise LLMError(f"Failed to initialize Cohere: {e}")

    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """Generate response using Cohere."""
        if not self._client:
            raise LLMError("Cohere client not initialized")

        try:
            # Convert messages to Cohere format
            prompt = self._messages_to_prompt(messages)

            # Generate response
            response = self._client.generate(
                model=self.model,
                prompt=prompt,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                **kwargs
            )

            # Extract response text
            content = response.generations[0].text.strip()

            return LLMResponse(
                content=content,
                model=self.model,
                usage={
                    "prompt_tokens": len(prompt.split()),
                    "completion_tokens": len(content.split()),
                    "total_tokens": len(prompt.split()) + len(content.split())
                },
                metadata={
                    "finish_reason": "stop",
                    "temperature": temperature or self.temperature
                }
            )

        except Exception as e:
            raise LLMError(f"Cohere generation failed: {e}") from e

    async def generate_stream(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """Generate streaming response using Cohere."""
        if not self._client:
            raise LLMError("Cohere client not initialized")

        try:
            # Convert messages to prompt
            prompt = self._messages_to_prompt(messages)

            # Generate response and simulate streaming
            response = self._client.generate(
                model=self.model,
                prompt=prompt,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                **kwargs
            )

            # Simulate streaming by yielding chunks
            content = response.generations[0].text.strip()
            words = content.split()
            for word in words:
                yield LLMResponse(
                    content=word + " ",
                    model=self.model,
                    usage={},
                    metadata={"chunk": True}
                )
                await asyncio.sleep(0.01)

        except Exception as e:
            raise LLMError(f"Cohere streaming failed: {e}") from e

    def _messages_to_prompt(self, messages: List[LLMMessage]) -> str:
        """Convert messages to Cohere prompt format."""
        prompt_parts = []

        for message in messages:
            if message.role == "system":
                prompt_parts.append(f"System: {message.content}")
            elif message.role == "user":
                prompt_parts.append(f"Human: {message.content}")
            elif message.role == "assistant":
                prompt_parts.append(f"Assistant: {message.content}")

        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)
