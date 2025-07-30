# Installation Guide

Complete installation instructions for AIWand.

## Quick Install

```bash
pip install aiwand
```

## Recommended: Virtual Environment

We strongly recommend using a virtual environment to avoid conflicts:

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install AIWand
pip install aiwand
```

## Development Installation

### Quick Setup (Recommended)

Use our automated setup scripts:

```bash
# Clone repository
git clone https://github.com/onlyoneaman/aiwand.git
cd aiwand

# Linux/Mac
chmod +x scripts/setup-dev.sh
./scripts/setup-dev.sh

# Windows
scripts\setup-dev.bat
```

### Manual Setup

```bash
# Clone repository
git clone https://github.com/onlyoneaman/aiwand.git
cd aiwand

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Verify installation
python test_install.py
```

## API Key Setup

Choose your AI provider and set up the corresponding API key:

### Option 1: OpenAI Only
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

### Option 2: Google Gemini Only
```bash
export GEMINI_API_KEY="your-gemini-api-key-here"
```

### Option 3: Both (with preference)
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
export GEMINI_API_KEY="your-gemini-api-key-here"
export AI_DEFAULT_PROVIDER="gemini"  # or "openai"
```

### Using .env File
Create a `.env` file in your project:
```
OPENAI_API_KEY=your-openai-key-here
GEMINI_API_KEY=your-gemini-key-here
AI_DEFAULT_PROVIDER=openai
```

### Interactive Setup
```python
import aiwand

# Interactive setup for preferences
aiwand.setup_user_preferences()

# Check current configuration
aiwand.show_current_config()
```

## Verification

Test your installation:

```python
import aiwand

# Check version
print(aiwand.__version__)

# Show current configuration
aiwand.show_current_config()

# Test basic functionality (requires API key)
try:
    response = aiwand.chat("Hello!")
    print("✅ Installation successful!")
except aiwand.AIError as e:
    print(f"❌ AI Error: {e}")
    print("💡 Run 'aiwand setup' or set environment variables")
except Exception as e:
    print(f"❌ Error: {e}")
```

## Requirements

- Python 3.8+
- At least one API key (OpenAI or Gemini)
- Internet connection

## Getting API Keys

### OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Go to API Keys section
4. Create a new API key

### Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/)
2. Sign up or log in
3. Get your API key from the interface

## Troubleshooting

### Installation Issues
```bash
# Upgrade pip
pip install --upgrade pip

# Clear pip cache
pip cache purge

# Install with verbose output
pip install -v aiwand
```

### Import Errors
```bash
# Check if package is installed
pip list | grep aiwand

# Reinstall if needed
pip uninstall aiwand
pip install aiwand
```

### API Key Issues
```bash
# Check environment variables
echo $OPENAI_API_KEY
echo $GEMINI_API_KEY

# Test configuration
python -c "import aiwand; aiwand.show_current_config()"

# Interactive setup
python -c "import aiwand; aiwand.setup_user_preferences()"
``` 