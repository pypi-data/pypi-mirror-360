"""
LiteLLM integration for easy LLM calls in BubbleTea bots
"""

from typing import List, Dict, Optional, AsyncGenerator, Union
import litellm
from litellm import acompletion, completion, image_generation, aimage_generation
from .schemas import ImageInput


class LLM:
    """
    Simple wrapper around LiteLLM for easy LLM calls
    
    Example:
        llm = LLM(model="gpt-3.5-turbo")
        response = llm.complete("Hello, how are you?")
        
        # Streaming
        async for chunk in llm.stream("Tell me a story"):
            yield Text(chunk)
    """
    
    def __init__(self, model: str = "gpt-3.5-turbo", **kwargs):
        self.model = model
        self.default_params = kwargs
    
    def _format_message_with_images(self, content: str, images: Optional[List[ImageInput]] = None) -> Union[str, List[Dict]]:
        """Format message content with images for multimodal models"""
        if not images:
            return content
        
        # Create multimodal content array
        content_parts = [{"type": "text", "text": content}]
        
        for img in images:
            if img.url:
                content_parts.append({
                    "type": "image_url",
                    "image_url": {"url": img.url}
                })
            elif img.base64:
                if img.base64.startswith("data:"):
                    # If base64 already starts with 'data:', use it directly
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {"url": img.base64}
                    })
                else:
                    # Format base64 image with proper data URI
                    mime_type = img.mime_type or "image/jpeg"
                    image_url = f"data:{mime_type};base64,{img.base64}"
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    })
        
        return content_parts
    
    def complete(self, prompt: str, **kwargs) -> str:
        """
        Get a completion from the LLM
        
        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional parameters to pass to litellm
            
        Returns:
            The LLM's response as a string
        """
        params = {**self.default_params, **kwargs}
        messages = [{"role": "user", "content": prompt}]
        
        response = completion(
            model=self.model,
            messages=messages,
            **params
        )
        
        return response.choices[0].message.content
    
    async def acomplete(self, prompt: str, **kwargs) -> str:
        """
        Async version of complete()
        """
        params = {**self.default_params, **kwargs}
        messages = [{"role": "user", "content": prompt}]
        
        response = await acompletion(
            model=self.model,
            messages=messages,
            **params
        )
        
        return response.choices[0].message.content
    
    async def stream(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        """
        Stream a completion from the LLM
        
        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional parameters to pass to litellm
            
        Yields:
            Chunks of the LLM's response
        """
        params = {**self.default_params, **kwargs}
        messages = [{"role": "user", "content": prompt}]
        
        response = await acompletion(
            model=self.model,
            messages=messages,
            stream=True,
            **params
        )
        
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def with_messages(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Get a completion with full message history
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters to pass to litellm
            
        Returns:
            The LLM's response as a string
        """
        params = {**self.default_params, **kwargs}
        
        response = completion(
            model=self.model,
            messages=messages,
            **params
        )
        
        return response.choices[0].message.content
    
    async def astream_with_messages(self, messages: List[Dict[str, str]], **kwargs) -> AsyncGenerator[str, None]:
        """
        Stream a completion with full message history
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters to pass to litellm
            
        Yields:
            Chunks of the LLM's response
        """
        params = {**self.default_params, **kwargs}
        
        response = await acompletion(
            model=self.model,
            messages=messages,
            stream=True,
            **params
        )
        
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
    
    def complete_with_images(self, prompt: str, images: List[ImageInput], **kwargs) -> str:
        """
        Get a completion from the LLM with images
        
        Args:
            prompt: The text prompt
            images: List of ImageInput objects (URLs or base64)
            **kwargs: Additional parameters
            
        Returns:
            The LLM's response as a string
        """
        params = {**self.default_params, **kwargs}
        
        # Format message with images
        content = self._format_message_with_images(prompt, images)
        messages = [{"role": "user", "content": content}]
        
        response = completion(
            model=self.model,
            messages=messages,
            **params
        )
        
        return response.choices[0].message.content
    
    async def acomplete_with_images(self, prompt: str, images: List[ImageInput], **kwargs) -> str:
        """
        Async version of complete_with_images()
        """
        params = {**self.default_params, **kwargs}
        
        # Format message with images
        content = self._format_message_with_images(prompt, images)
        messages = [{"role": "user", "content": content}]
        
        response = await acompletion(
            model=self.model,
            messages=messages,
            **params
        )
        
        return response.choices[0].message.content
    
    async def stream_with_images(self, prompt: str, images: List[ImageInput], **kwargs) -> AsyncGenerator[str, None]:
        """
        Stream a completion from the LLM with images
        
        Args:
            prompt: The text prompt
            images: List of ImageInput objects
            **kwargs: Additional parameters
            
        Yields:
            Chunks of the LLM's response
        """
        params = {**self.default_params, **kwargs}
        
        # Format message with images
        content = self._format_message_with_images(prompt, images)
        messages = [{"role": "user", "content": content}]
        
        response = await acompletion(
            model=self.model,
            messages=messages,
            stream=True,
            **params
        )
        
        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def generate_image(self, prompt: str, **kwargs) -> str:
        """
        Generate an image using an image generation model like DALL·E.
        Returns the image URL.
        """
        params = {**self.default_params, **kwargs}
        response = image_generation(prompt=prompt, **params)
        return response.data[0].url

    async def agenerate_image(self, prompt: str, **kwargs) -> str:
        """
        Async version of generate_image.
        """
        params = {**self.default_params, **kwargs}
        response = await aimage_generation(prompt=prompt, **params)
        return response.data[0].url