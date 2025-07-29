"""
FastAPI server implementation for BubbleTea chatbots
"""

import json
import asyncio
from typing import Optional, AsyncGenerator, List, Dict, Any
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from .decorators import ChatbotFunction
from . import decorators
from .schemas import ComponentChatRequest, ComponentChatResponse, BotConfig
from .components import Done


class BubbleTeaServer:
    """FastAPI server for hosting BubbleTea chatbots"""
    
    def __init__(self, chatbot: ChatbotFunction, port: int = 8000, cors: bool = True, cors_config: Optional[Dict[str, Any]] = None):
        self.app = FastAPI(title=f"BubbleTea Bot: {chatbot.name}")
        self.chatbot = chatbot
        self.port = port
        
        # Check if bot config has CORS settings
        if cors and not cors_config and decorators._config_function:
            config_func, _ = decorators._config_function
            try:
                # Try to get config to check for CORS settings
                if asyncio.iscoroutinefunction(config_func):
                    # Can't await here, so use default CORS
                    pass
                else:
                    config = config_func()
                    if hasattr(config, 'cors_config') and config.cors_config:
                        cors_config = config.cors_config
            except:
                pass
        
        # Setup CORS
        if cors:
            self._setup_cors(cors_config)
        
        self._setup_routes()
    
    def _setup_cors(self, cors_config: Optional[Dict[str, Any]] = None):
        """Setup CORS middleware with sensible defaults"""
        default_config = {
            "allow_origins": ["*"],  # Allow all origins in development
            "allow_credentials": True,
            "allow_methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["*"],
        }
        
        # Update with custom config if provided
        if cors_config:
            default_config.update(cors_config)
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            **default_config
        )
    
    def _setup_routes(self):
        """Setup the chat endpoint"""
        
        @self.app.post("/chat")
        async def chat_endpoint(request: ComponentChatRequest):
            """Handle chat requests"""
            response = await self.chatbot.handle_request(request)
            
            if self.chatbot.stream:
                # Streaming response
                async def stream_generator():
                    async for component in response:
                        # Convert component to JSON and wrap in SSE format
                        data = component.model_dump_json()
                        yield f"data: {data}\n\n"
                    # Send done signal
                    done = Done()
                    yield f"data: {done.model_dump_json()}\n\n"
                
                return StreamingResponse(
                    stream_generator(),
                    media_type="text/event-stream"
                )
            else:
                # Non-streaming response
                return response
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {
                "status": "healthy",
                "bot_name": self.chatbot.name,
                "streaming": self.chatbot.stream
            }
        
        # Register config endpoint if decorator was used
        if decorators._config_function:
            config_func, config_path = decorators._config_function
            
            @self.app.get(config_path, response_model=BotConfig)
            async def config_endpoint():
                """Get bot configuration"""
                # Check if config function is async
                if asyncio.iscoroutinefunction(config_func):
                    result = await config_func()
                else:
                    result = config_func()
                
                # Ensure result is a BotConfig instance
                if isinstance(result, BotConfig):
                    return result
                elif isinstance(result, dict):
                    return BotConfig(**result)
                else:
                    # Try to convert to BotConfig
                    return result
    
    def run(self, host: str = "0.0.0.0"):
        """Run the server"""
        uvicorn.run(self.app, host=host, port=self.port)


def run_server(chatbot: ChatbotFunction, port: int = 8000, host: str = "0.0.0.0", cors: bool = True, cors_config: Optional[Dict[str, Any]] = None):
    """
    Run a FastAPI server for the given chatbot
    
    Args:
        chatbot: The chatbot function decorated with @chatbot
        port: Port to run the server on
        host: Host to bind the server to
        cors: Enable CORS support (default: True)
        cors_config: Custom CORS configuration dict with keys:
            - allow_origins: List of allowed origins (default: ["*"])
            - allow_credentials: Allow credentials (default: True)
            - allow_methods: Allowed methods (default: ["GET", "POST", "OPTIONS"])
            - allow_headers: Allowed headers (default: ["*"])
    """
    server = BubbleTeaServer(chatbot, port, cors=cors, cors_config=cors_config)
    server.run(host)