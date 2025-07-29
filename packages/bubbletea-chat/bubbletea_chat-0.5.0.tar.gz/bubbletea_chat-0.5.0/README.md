# BubbleTea Python SDK

Build AI chatbots for the BubbleTea platform with simple Python functions.

**Now with LiteLLM support!** 🎉 Easily integrate with OpenAI, Anthropic Claude, Google Gemini, and 100+ other LLMs.

**NEW: Vision & Image Generation!** 📸🎨 Build multimodal bots that can analyze images and generate new ones using AI.

## Installation

```bash
pip install bubbletea-chat
```

## Quick Start

Create a simple chatbot in `my_bot.py`:

```python
import bubbletea_chat as bt

@bt.chatbot
def my_chatbot(message: str):
    # Your bot logic here
    if "image" in message.lower():
        yield bt.Image("https://picsum.photos/400/300")
        yield bt.Text("Here's a random image for you!")
    else:
        yield bt.Text(f"You said: {message}")

if __name__ == "__main__":
    # Run the chatbot server
    bt.run_server(my_chatbot, port=8000, host="0.0.0.0")

```

Run it locally:

```bash
python my_bot.py
```

This will start a server at `http://localhost:8000` with your chatbot available at the `/chat` endpoint.


### Configuration with `@config` Decorator

BubbleTea provides a `@config` decorator to define and expose bot configurations via a dedicated endpoint. This is useful for setting up bot metadata, such as its name, URL, emoji, and initial greeting.

#### Example: Using the `@config` Decorator


```python
import bubbletea_chat as bt

# Define bot configuration
@bt.config()
def get_config():
    return bt.BotConfig(
        name="Weather Bot",
        url="http://localhost:8000",
        is_streaming=True,
        emoji="🌤️",
        initial_text="Hello! I can help you check the weather. Which city would you like to know about?"
    )

# Define the chatbot
@bt.chatbot(name="Weather Bot", stream=True)
def weather_bot(message: str):
    if "new york" in message.lower():
        yield bt.Text("🌤️ New York: Partly cloudy, 72°F")
    else:
        yield bt.Text("Please specify a city to check the weather.")
```

When the bot server is running, the configuration can be accessed at the `/config` endpoint. For example:

```bash
curl http://localhost:8000/config
```

This will return the bot's configuration as a JSON object.

#### Dynamic Bot Creation Using `/config`

BubbleTea agents can dynamically create new chatbots by utilizing the `/config` endpoint. For example, if you provide a command like:

```bash
create new bot 'bot-name' with url 'http://example.com'
```

The agent will automatically fetch the configuration from `http://example.com/config` and create a new chatbot based on the metadata defined in the configuration. This allows for seamless integration and creation of new bots without manual setup.

## Features

### 🤖 LiteLLM Integration

BubbleTea now includes built-in support for LiteLLM, allowing you to easily use any LLM provider. We use LiteLLM on the backend, which supports 100+ LLM models from various providers.

```python
from bubbletea_chat import LLM

# Use any model supported by LiteLLM
llm = LLM(model="gpt-4")
llm = LLM(model="claude-3-sonnet-20240229")
llm = LLM(model="gemini/gemini-pro")

# Simple completion
response = await llm.acomplete("Hello, how are you?")

# Streaming
async for chunk in llm.stream("Tell me a story"):
    yield bt.Text(chunk)
```

**📚 Supported Models**: Check out the full list of supported models and providers at [LiteLLM Providers Documentation](https://docs.litellm.ai/docs/providers)

**💡 DIY Alternative**: You can also implement your own LLM connections using the LiteLLM library directly in your bots if you need more control over the integration.

### 📸 Vision/Image Analysis

BubbleTea supports multimodal interactions! Your bots can receive and analyze images:

```python
from bubbletea_chat import chatbot, Text, LLM, ImageInput

@chatbot
async def vision_bot(prompt: str, images: list = None):
    """A bot that can see and analyze images"""
    if images:
        llm = LLM(model="gpt-4-vision-preview")
        response = await llm.acomplete_with_images(prompt, images)
        yield Text(response)
    else:
        yield Text("Send me an image to analyze!")
```

**Supported Image Formats:**
- URL images: Direct links to images
- Base64 encoded images: For local/uploaded images
- Multiple images: Analyze multiple images at once

**Compatible Vision Models:**
- OpenAI: GPT-4 Vision (`gpt-4-vision-preview`)
- Anthropic: Claude 3 models (Opus, Sonnet, Haiku)
- Google: Gemini Pro Vision (`gemini/gemini-pro-vision`)
- And more vision-enabled models via LiteLLM

### 🎨 Image Generation

Generate images from text descriptions using AI models:

```python
from bubbletea_chat import chatbot, Image, LLM

@chatbot
async def art_bot(prompt: str):
    """Generate images from descriptions"""
    llm = LLM(model="dall-e-3")  # or any image generation model
    
    # Generate an image
    image_url = await llm.agenerate_image(prompt)
    yield Image(image_url)
```

**Image Generation Features:**
- Text-to-image generation
- Support for DALL-E, Stable Diffusion, and other models
- Customizable parameters (size, quality, style)

### 📦 Components

BubbleTea supports rich components for building engaging chatbot experiences:

- **Text**: Plain text messages
- **Image**: Images with optional alt text  
- **Markdown**: Rich formatted text

### 🔄 Streaming Support

BubbleTea automatically detects generator functions and streams responses:

```python
@bt.chatbot
async def streaming_bot(message: str):
    yield bt.Text("Processing your request...")
    
    # Simulate some async work
    import asyncio
    await asyncio.sleep(1)
    
    yield bt.Markdown("## Here's your response")
    yield bt.Image("https://example.com/image.jpg")
    yield bt.Text("All done!")
```

## Examples

### AI-Powered Bots with LiteLLM

#### OpenAI GPT Bot

```python
import bubbletea_chat as bt
from bubbletea_chat import LLM

@bt.chatbot
async def gpt_assistant(message: str):
    # Make sure to set OPENAI_API_KEY environment variable
    llm = LLM(model="gpt-4")
    
    # Stream the response
    async for chunk in llm.stream(message):
        yield bt.Text(chunk)
```

#### Claude Bot

```python
@bt.chatbot
async def claude_bot(message: str):
    # Set ANTHROPIC_API_KEY environment variable
    llm = LLM(model="claude-3-sonnet-20240229")
    
    response = await llm.acomplete(message)
    yield bt.Text(response)
```

#### Gemini Bot

```python
@bt.chatbot
async def gemini_bot(message: str):
    # Set GEMINI_API_KEY environment variable
    llm = LLM(model="gemini/gemini-pro")
    
    async for chunk in llm.stream(message):
        yield bt.Text(chunk)
```

### Vision-Enabled Bot

Build bots that can analyze images using multimodal LLMs:

```python
from bubbletea_chat import chatbot, Text, Markdown, LLM, ImageInput

@chatbot
async def vision_bot(prompt: str, images: list = None):
    """
    A vision-enabled bot that can analyze images
    """
    llm = LLM(model="gpt-4-vision-preview", max_tokens=1000)
    
    if images:
        yield Text("I can see you've shared some images. Let me analyze them...")
        response = await llm.acomplete_with_images(prompt, images)
        yield Markdown(response)
    else:
        yield Markdown("""
## 📸 Vision Bot

I can analyze images! Try sending me:
- Screenshots to explain
- Photos to describe
- Diagrams to interpret
- Art to analyze

Just upload an image along with your question!

**Supported formats**: JPEG, PNG, GIF, WebP
        """)
```

**Key Features:**
- Accepts images along with text prompts
- Supports both URL and base64-encoded images
- Works with multiple images at once
- Compatible with various vision models

### Image Generation Bot

Create images from text descriptions:

```python
from bubbletea_chat import chatbot, Text, Markdown, LLM, Image

@chatbot
async def image_generator(prompt: str):
    """
    Generate images from text descriptions
    """
    llm = LLM(model="dall-e-3")  # Default image generation model
    
    if prompt:
        yield Text(f"🎨 Creating: {prompt}")
        # Generate image from the text prompt
        image_url = await llm.agenerate_image(prompt)
        yield Image(image_url)
        yield Text("✨ Your image is ready!")
    else:
        yield Markdown("""
## 🎨 AI Image Generator

I can create images from your text prompts!

Try prompts like:
- *"A futuristic cityscape at sunset"*
- *"A cute robot playing guitar in a forest"*
- *"An ancient map with fantasy landmarks"*

👉 Just type your description and I'll generate an image for you!
        """)
```

### Simple Echo Bot

```python
import bubbletea_chat as bt

@bt.chatbot
def echo_bot(message: str):
    return bt.Text(f"Echo: {message}")
```

### Multi-Modal Bot

```python
import bubbletea_chat as bt

@bt.chatbot
def multimodal_bot(message: str):
    yield bt.Markdown("# Welcome to the Multi-Modal Bot!")
    
    yield bt.Text("I can show you different types of content:")
    
    yield bt.Markdown("""
    - 📝 **Text** messages
    - 🖼️ **Images** with descriptions  
    - 📊 **Markdown** formatting
    """)
    
    yield bt.Image(
        "https://picsum.photos/400/300",
        alt="A random beautiful image"
    )
    
    yield bt.Text("Pretty cool, right? 😎")
```

### Streaming Bot

```python
import bubbletea_chat as bt
import asyncio

@bt.chatbot
async def streaming_bot(message: str):
    yield bt.Text("Hello! Let me process your message...")
    await asyncio.sleep(1)
    
    words = message.split()
    yield bt.Text("You said: ")
    for word in words:
        yield bt.Text(f"{word} ")
        await asyncio.sleep(0.3)
    
    yield bt.Markdown("## Analysis Complete!")
```

## API Reference

### Decorators

- `@bt.chatbot` - Create a chatbot from a function
- `@bt.chatbot(name="custom-name")` - Set a custom bot name
- `@bt.chatbot(stream=False)` - Force non-streaming mode

**Image Support**: Functions can accept an optional `images` parameter:
```python
@bt.chatbot
async def my_bot(message: str, images: list = None):
    # images will contain ImageInput objects if provided
    pass
```

### Components

- `bt.Text(content: str)` - Plain text message
- `bt.Image(url: str, alt: str = None)` - Image component
- `bt.Markdown(content: str)` - Markdown formatted text

### LLM Class

- `LLM(model: str, **kwargs)` - Initialize an LLM client
  - `model`: Any model supported by LiteLLM (e.g., "gpt-4", "claude-3-sonnet-20240229")
  - `**kwargs`: Additional parameters (temperature, max_tokens, etc.)

#### Text Generation Methods:
- `complete(prompt: str, **kwargs) -> str` - Get a completion
- `acomplete(prompt: str, **kwargs) -> str` - Async completion
- `stream(prompt: str, **kwargs) -> AsyncGenerator[str, None]` - Stream a completion
- `with_messages(messages: List[Dict], **kwargs) -> str` - Use full message history
- `astream_with_messages(messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]` - Stream with messages

#### Vision/Image Analysis Methods:
- `complete_with_images(prompt: str, images: List[ImageInput], **kwargs) -> str` - Completion with images
- `acomplete_with_images(prompt: str, images: List[ImageInput], **kwargs) -> str` - Async with images
- `stream_with_images(prompt: str, images: List[ImageInput], **kwargs) -> AsyncGenerator` - Stream with images

#### Image Generation Methods:
- `generate_image(prompt: str, **kwargs) -> str` - Generate image (sync), returns URL
- `agenerate_image(prompt: str, **kwargs) -> str` - Generate image (async), returns URL

### ImageInput Class

Represents an image input that can be either a URL or base64 encoded:
```python
from bubbletea_chat import ImageInput

# URL image
ImageInput(url="https://example.com/image.jpg")

# Base64 image
ImageInput(
    base64="iVBORw0KGgoAAAANS...",
    mime_type="image/jpeg"  # Optional
)
```

### Server
```
if __name__ == "__main__":
    # Run the chatbot server
    bt.run_server(my_bot, port=8000, host="0.0.0.0")
```

- Runs a chatbot server on port 8000 and binds to host 0.0.0.0
  - Automatically creates a `/chat` endpoint for your bot
  - The `/chat` endpoint accepts POST requests with chat messages
  - Supports both streaming and non-streaming responses

## Environment Variables

To use different LLM providers, set the appropriate API keys:

```bash
# OpenAI
export OPENAI_API_KEY=your-openai-api-key

# Anthropic Claude
export ANTHROPIC_API_KEY=your-anthropic-api-key

# Google Gemini
export GEMINI_API_KEY=your-gemini-api-key

# Or use a .env file with python-dotenv
```

For more providers and configuration options, see the [LiteLLM documentation](https://docs.litellm.ai/docs/providers).

## Custom LLM Integration

While BubbleTea provides the `LLM` class for convenience, you can also use LiteLLM directly in your bots for more control:

```python
import bubbletea_chat as bt
from litellm import acompletion

@bt.chatbot
async def custom_llm_bot(message: str):
    # Direct LiteLLM usage
    response = await acompletion(
        model="gpt-4",
        messages=[{"role": "user", "content": message}],
        temperature=0.7,
        # Add any custom parameters
        api_base="https://your-custom-endpoint.com",  # Custom endpoints
        custom_llm_provider="openai",  # Custom providers
    )
    
    yield bt.Text(response.choices[0].message.content)
```

This approach gives you access to:
- Custom API endpoints
- Advanced parameters
- Direct response handling
- Custom error handling
- Any LiteLLM feature

## Testing Your Bot

Start your bot:

```bash
python my_bot.py
```

Your bot will automatically create a `/chat` endpoint that accepts POST requests. This is the standard endpoint for all BubbleTea chatbots.

Test with curl:

```bash
# Text only
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"type": "user", "message": "Hello bot!"}'

# With image URL
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "user",
    "message": "What is in this image?",
    "images": [{"url": "https://example.com/image.jpg"}]
  }'

# With base64 image
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "user",
    "message": "Describe this",
    "images": [{"base64": "iVBORw0KGgoAAAANS...", "mime_type": "image/png"}]
  }'
```

## 🌐 CORS Support

BubbleTea includes automatic CORS (Cross-Origin Resource Sharing) support out of the box! This means your bots will work seamlessly with web frontends without any additional configuration.

### Default Behavior
```python
# CORS is enabled by default with permissive settings for development
bt.run_server(my_bot, port=8000)
```

### Custom CORS Configuration
```python
# For production - restrict to specific origins
bt.run_server(my_bot, port=8000, cors_config={
    "allow_origins": ["https://bubbletea.app", "https://yourdomain.com"],
    "allow_credentials": True,
    "allow_methods": ["GET", "POST"],
    "allow_headers": ["Content-Type", "Authorization"]
})
```

### Disable CORS
```python
# Not recommended, but possible
bt.run_server(my_bot, port=8000, cors=False)
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.
