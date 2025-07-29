"""
Decorators for creating BubbleTea chatbots
"""

import asyncio
import inspect
from typing import Callable, List, AsyncGenerator, Generator, Union, Tuple, Optional
from functools import wraps

from .components import Component, Done
from .schemas import ComponentChatRequest, ComponentChatResponse, ImageInput, BotConfig

# Module-level registry for config function
_config_function: Optional[Tuple[Callable, str]] = None


class ChatbotFunction:
    """Wrapper for chatbot functions"""
    
    def __init__(self, func: Callable, name: str = None, stream: bool = None):
        self.func = func
        self.name = name or func.__name__
        self.is_async = inspect.iscoroutinefunction(func)
        self.is_generator = inspect.isgeneratorfunction(func) or inspect.isasyncgenfunction(func)
        self.stream = stream if stream is not None else self.is_generator
        
    async def __call__(self, message: str, images: List[ImageInput] = None) -> Union[List[Component], AsyncGenerator[Component, None]]:
        """Execute the chatbot function"""
        # Check function signature to determine if it accepts images
        sig = inspect.signature(self.func)
        params = list(sig.parameters.keys())
        
        if len(params) > 1 and 'images' in params:
            # Function accepts images parameter
            if self.is_async:
                result = await self.func(message, images=images)
            else:
                result = self.func(message, images=images)
        else:
            # Backward compatibility: function only accepts message
            if self.is_async:
                result = await self.func(message)
            else:
                result = self.func(message)
            
        # Handle different return types
        if self.is_generator:
            # Generator functions yield components
            if inspect.isasyncgen(result):
                return result
            else:
                # Convert sync generator to async
                async def async_wrapper():
                    for item in result:
                        yield item
                return async_wrapper()
        else:
            # Non-generator functions return list of components
            if not isinstance(result, list):
                result = [result]
            return result
    
    async def handle_request(self, request: ComponentChatRequest):
        """Handle incoming chat request and return appropriate response"""
        components = await self(request.message, images=request.images)
        
        if self.stream:
            # Return async generator for streaming
            return components
        else:
            # Return list for non-streaming
            if inspect.isasyncgen(components):
                # Collect all components from generator
                collected = []
                async for component in components:
                    if not isinstance(component, Done):
                        collected.append(component)
                return ComponentChatResponse(responses=collected)
            else:
                return ComponentChatResponse(responses=components)


def chatbot(name: str = None, stream: bool = None):
    """
    Decorator to create a BubbleTea chatbot from a function
    
    Args:
        name: Optional name for the chatbot (defaults to function name)
        stream: Whether to stream responses (auto-detected from generator functions)
    
    Example:
        @chatbot()
        def my_bot(message: str):
            yield Text("Hello!")
            yield Image("https://example.com/image.jpg")
    """
    def decorator(func: Callable) -> ChatbotFunction:
        return ChatbotFunction(func, name=name, stream=stream)
    
    # Allow using @chatbot without parentheses
    if callable(name):
        func = name
        return ChatbotFunction(func)
    
    return decorator


def config(path: str = "/config"):
    """
    Decorator to define bot configuration endpoint
    
    Args:
        path: Optional path for the config endpoint (defaults to "/config")
    
    Example:
        @config()
        def get_config():
            return BotConfig(
                name="My Bot",
                url="https://mybot.example.com",
                is_streaming=True,
                emoji="🤖",
                initial_text="Hello! How can I help?"
            )
    """
    def decorator(func: Callable) -> Callable:
        global _config_function
        _config_function = (func, path)
        return func
    
    # Allow using @config without parentheses
    if callable(path):
        func = path
        _config_function = (func, "/config")
        return func
    
    return decorator