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

## Helper Functions

### `generate_random_number(length=6)`

Generate a random number with specified number of digits.

**Parameters:**
- `length` (int): Number of digits for the random number (default: 6)

**Returns:** Random number as string (preserves leading zeros)

**Raises:**
- `ValueError`: If length is less than 1

**Example:**
```python
import aiwand

# Default 6-digit number
number = aiwand.generate_random_number()
print(f"6-digit: {number}")  # e.g., "432875"

# Custom length
number = aiwand.generate_random_number(10)
print(f"10-digit: {number}")  # e.g., "9847382659"

# Single digit
number = aiwand.generate_random_number(1)
print(f"1-digit: {number}")  # e.g., "7"
```

### `generate_uuid(version=4, uppercase=False)`

Generate a UUID (Universally Unique Identifier).

**Parameters:**
- `version` (int): UUID version to generate (1 or 4, default: 4)
- `uppercase` (bool): Whether to return uppercase UUID (default: False)

**Returns:** Generated UUID string

**Raises:**
- `ValueError`: If version is not 1 or 4

**Example:**
```python
import aiwand

# Default UUID4
uuid = aiwand.generate_uuid()
print(f"UUID4: {uuid}")  # e.g., "f47ac10b-58cc-4372-a567-0e02b2c3d479"

# UUID4 uppercase
uuid = aiwand.generate_uuid(uppercase=True)
print(f"UUID4: {uuid}")  # e.g., "F47AC10B-58CC-4372-A567-0E02B2C3D479"

# UUID1 (includes timestamp and MAC address)
uuid = aiwand.generate_uuid(version=1)
print(f"UUID1: {uuid}")  # e.g., "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
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
| OpenAI only | `gpt-4o` | OpenAI |
| Gemini only | `gemini-2.0-flash` | Gemini |
| Both available | Based on `AI_DEFAULT_PROVIDER` or preferences | Configurable |

### Supported Models

**OpenAI Models:**
- `o3` (newest reasoning model, best performance)
- `o3-mini` (efficient reasoning model)
- `o1` (advanced reasoning model)
- `o1-mini` (compact reasoning model)
- `gpt-4.1` (1M context window, best for coding)
- `gpt-4.1-mini` (efficient large context model)
- `gpt-4o` (default - multimodal flagship)
- `gpt-4o-mini` (fast, capable, cost-effective)
- `gpt-4-turbo`
- `gpt-4`
- `gpt-3.5-turbo`

**Gemini Models:**
- `gemini-2.5-pro` (newest flagship model)
- `gemini-2.5-flash` (latest experimental model)
- `gemini-2.5-flash-lite` (efficient variant)
- `gemini-2.0-flash-exp` (experimental features)
- `gemini-2.0-flash` (default - stable, fast, capable)
- `gemini-2.0-pro`
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

### Using Helper Functions
```python
import aiwand

# Generate random data for testing
test_id = aiwand.generate_random_number(8)
session_id = aiwand.generate_uuid()

# Create unique identifiers
user_id = f"user_{aiwand.generate_random_number(6)}"
transaction_id = aiwand.generate_uuid(uppercase=True)

print(f"Test ID: {test_id}")
print(f"Session: {session_id}")
print(f"User: {user_id}")
print(f"Transaction: {transaction_id}")
``` 