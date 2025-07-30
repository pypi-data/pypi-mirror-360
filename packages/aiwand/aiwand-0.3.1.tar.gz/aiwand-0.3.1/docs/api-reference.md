# API Reference

Complete documentation for all AIWand functions and features.

## Core Functions

### `summarize(text, max_length=None, style="concise", model=None)`

Summarize text with customizable options.

**Parameters:**
- `text` (str): Text to summarize
- `max_length` (int, optional): Maximum words in summary
- `style` (str): Summary style - "concise", "detailed", or "bullet-points"
- `model` (str, optional): Specific model to use (auto-selected if not provided)

**Returns:** Summarized text (str)

**Raises:**
- `ValueError`: If text is empty
- `AIError`: If API call fails or no provider available

**Example:**
```python
import aiwand

# Basic summarization
summary = aiwand.summarize("Your long text here...")

# Customized summarization
summary = aiwand.summarize(
    text="Your text...",
    style="bullet-points",
    max_length=50,
    model="gpt-4"
)
```

### `chat(message, conversation_history=None, model=None, temperature=0.7)`

Have a conversation with AI.

**Parameters:**
- `message` (str): Your message
- `conversation_history` (list, optional): Previous conversation messages
- `model` (str, optional): Specific model to use (auto-selected if not provided)
- `temperature` (float): Response creativity (0.0-1.0)

**Returns:** AI response (str)

**Raises:**
- `ValueError`: If message is empty
- `AIError`: If API call fails or no provider available

**Example:**
```python
import aiwand

# Simple chat
response = aiwand.chat("What is machine learning?")

# Conversation with history
conversation = []
response1 = aiwand.chat("Hello!", conversation_history=conversation)
conversation.append({"role": "user", "content": "Hello!"})
conversation.append({"role": "assistant", "content": response1})

response2 = aiwand.chat("What did I just say?", conversation_history=conversation)
```

### `generate_text(prompt, max_tokens=500, temperature=0.7, model=None)`

Generate text from a prompt.

**Parameters:**
- `prompt` (str): Text prompt
- `max_tokens` (int): Maximum tokens to generate
- `temperature` (float): Response creativity (0.0-1.0)
- `model` (str, optional): Specific model to use (auto-selected if not provided)

**Returns:** Generated text (str)

**Raises:**
- `ValueError`: If prompt is empty
- `AIError`: If API call fails or no provider available

**Example:**
```python
import aiwand

# Basic generation
text = aiwand.generate_text("Write a poem about coding")

# Customized generation
text = aiwand.generate_text(
    prompt="Write a technical explanation of neural networks",
    max_tokens=300,
    temperature=0.3,
    model="gpt-4"
)
```

## Configuration Functions

### `setup_user_preferences()`

Interactive setup for user preferences (provider and model selection).

**Parameters:** None

**Returns:** None

**Example:**
```python
import aiwand

# Run interactive setup
aiwand.setup_user_preferences()
```

### `show_current_config()`

Display current configuration and available providers.

**Parameters:** None

**Returns:** None

**Example:**
```python
import aiwand

# Show current configuration
aiwand.show_current_config()
```

## Configuration

AIWand uses environment variables for configuration:

```bash
# Required: At least one API key
export OPENAI_API_KEY="your-openai-key"
export GEMINI_API_KEY="your-gemini-key"

# Optional: Default provider when both keys available
export AI_DEFAULT_PROVIDER="openai"  # or "gemini"
```

## Smart Model Selection

AIWand automatically selects the best available model:

| Available APIs | Default Model | Provider |
|----------------|---------------|----------|
| OpenAI only | `gpt-3.5-turbo` | OpenAI |
| Gemini only | `gemini-2.0-flash` | Gemini |
| Both available | Based on `AI_DEFAULT_PROVIDER` or preferences | Configurable |

### Supported Models

**OpenAI Models:**
- `gpt-4o`
- `gpt-4o-mini`
- `gpt-4-turbo`
- `gpt-4`
- `gpt-3.5-turbo` (default)

**Gemini Models:**
- `gemini-2.0-flash-exp`
- `gemini-2.0-flash` (default)
- `gemini-1.5-flash`
- `gemini-1.5-pro`

## Error Handling

### AIError

Custom exception for AI-related errors.

**Common scenarios:**
- No API keys configured
- API call failures
- Network issues
- Provider-specific errors

**Example:**
```python
import aiwand

try:
    summary = aiwand.summarize("Some text")
except aiwand.AIError as e:
    print(f"AI service error: {e}")
    # Handle API issues, missing keys, etc.
except ValueError as e:
    print(f"Input error: {e}")
    # Handle empty text, invalid parameters, etc.
```

## Best Practices

### Environment Setup
```python
# Use environment variables or .env file
import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env file

# AIWand will automatically pick up the keys
import aiwand
```

### Error Handling
```python
import aiwand

def safe_summarize(text):
    try:
        return aiwand.summarize(text)
    except aiwand.AIError as e:
        print(f"AI service unavailable: {e}")
        return None
    except ValueError as e:
        print(f"Invalid input: {e}")
        return None
```

### Model Selection
```python
import aiwand

# Let AIWand choose the best model
response = aiwand.chat("Hello")

# Or specify a model for specific needs
creative_response = aiwand.generate_text(
    "Write a creative story",
    model="gpt-4",
    temperature=0.9
)

factual_response = aiwand.generate_text(
    "Explain quantum physics",
    model="gpt-4",
    temperature=0.2
)
``` 