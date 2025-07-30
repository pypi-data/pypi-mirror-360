# Development Guide

Comprehensive guide for AIWand development workflow and advanced topics.

> 📋 **Quick Start**: See [CONTRIBUTING.md](../CONTRIBUTING.md) for essential guidelines and standards that both AI assistants and human contributors must follow.

## 🚀 Development Environment

### Automated Setup (Recommended)

```bash
# Linux/Mac
git clone https://github.com/onlyoneaman/aiwand.git
cd aiwand
chmod +x scripts/setup-dev.sh
./scripts/setup-dev.sh

# Windows
git clone https://github.com/onlyoneaman/aiwand.git
cd aiwand
scripts\setup-dev.bat
```

### Manual Setup

```bash
# 1. Clone and navigate
git clone https://github.com/onlyoneaman/aiwand.git
cd aiwand

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 3. Install in development mode
pip install -e .

# 4. Verify installation
python test_install.py
python examples/basic_usage.py
```

## 🏗️ Architecture Overview

### Package Structure (src/ layout)

```
src/aiwand/
├── __init__.py          # Package exports & VERSION (single source of truth)
├── config.py            # API configuration & smart provider selection  
├── core.py              # Core AI functionality (summarize, chat, generate_text)
├── cli.py               # Command line interface
└── helper.py            # Utility functions (random, uuid, etc.)
```

### Key Design Decisions

#### Single Source of Truth
- **Version**: Only in `src/aiwand/__init__.py`
- **Configuration**: Centralized in `config.py`
- **Public API**: Explicitly defined in `__all__`

#### Smart Provider Selection
- Automatic detection of available API keys
- Fallback logic: OpenAI → Gemini → Error
- User preferences with persistent storage
- Environment variable override support

#### Package-First Design
- Primary focus: Python package usability
- Secondary: CLI interface
- API consistency between Python and CLI

## 🔧 Development Workflows

### Version Management

#### Using Bump Script (Recommended)
```bash
# Patch version (default)
python scripts/bump-version.py        # 0.3.1 -> 0.3.2

# Specific version types
python scripts/bump-version.py patch  # 0.3.1 -> 0.3.2
python scripts/bump-version.py minor  # 0.3.1 -> 0.4.0
python scripts/bump-version.py major  # 0.3.1 -> 1.0.0
```

#### Manual Version Update
```python
# Only edit this file:
# src/aiwand/__init__.py
__version__ = "X.Y.Z"
```

### Publishing Workflow

#### Automated Publishing (Recommended)
```bash
python scripts/publish.py
```

The script performs:
1. ✅ Git status verification
2. 🧪 Installation tests
3. 📦 Package building
4. 🚀 PyPI upload
5. 🏷️ Git tag creation
6. 📤 GitHub push

#### Manual Publishing
```bash
# Build package
python -m build

# Upload to PyPI
python -m twine upload dist/*

# Create and push git tag
git tag vX.Y.Z
git push origin vX.Y.Z
```

## 🧪 Testing Strategy

### Installation Testing
```bash
python test_install.py
```

Verifies:
- Package imports correctly
- All exported functions available
- Configuration system works
- Error handling functions properly

### Functional Testing
```bash
# Test core functionality
python examples/basic_usage.py

# Test helper utilities
python examples/helper_usage.py

# Test CLI
aiwand --help
aiwand status
aiwand helper --help
```

### Integration Testing
```bash
# Test with different providers
export OPENAI_API_KEY="your-key"
python examples/basic_usage.py

export GEMINI_API_KEY="your-key"
python examples/basic_usage.py
```

## 🔧 Advanced Development Topics

### Adding New Core AI Functions

1. **Implementation Template**:
```python
# In src/aiwand/core.py
def new_ai_function(
    text: str,
    option: str = "default",
    model: Optional[str] = None
) -> str:
    """Brief description of the function.
    
    Args:
        text: Input text to process
        option: Processing option (default: "default")
        model: Specific model to use (auto-selected if not provided)
        
    Returns:
        Processed text result
        
    Raises:
        ValueError: If text is empty
        AIError: If API call fails
    """
    if not text.strip():
        raise ValueError("Text cannot be empty")
    
    try:
        client = get_ai_client()
        if model is None:
            model = get_model_name()
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": f"Process: {text}"}],
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    except AIError as e:
        raise AIError(str(e))
    except Exception as e:
        raise Exception(f"Failed to process text: {str(e)}")
```

2. **Export in `__init__.py`**:
```python
from .core import summarize, chat, generate_text, new_ai_function

__all__ = [
    # ... existing functions ...
    "new_ai_function",
]
```

3. **Add CLI Command**:
```python
# In src/aiwand/cli.py
new_parser = subparsers.add_parser('new-command', help='Description')
new_parser.add_argument('text', help='Text to process')
new_parser.add_argument('--option', default='default', help='Processing option')

# In command handling
elif args.command == 'new-command':
    result = new_ai_function(text=args.text, option=args.option)
    print(result)
```

### Adding Helper Utilities

1. **Implementation in `helper.py`**:
```python
def new_helper_function(param: str) -> str:
    """Description of helper function.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param is invalid
    """
    if not param:
        raise ValueError("Parameter cannot be empty")
    
    # Implementation
    return result
```

2. **CLI Integration**:
```python
# Add subcommand
helper_parser = helper_subparsers.add_parser('new-helper', help='Description')
helper_parser.add_argument('param', help='Parameter description')

# Add handling
elif args.helper_command == 'new-helper':
    result = new_helper_function(args.param)
    print(result)
```

### Configuration System Deep Dive

#### Provider Selection Logic
```python
def get_preferred_provider_and_model() -> Tuple[Optional[str], Optional[str]]:
    # 1. User preferences (from ~/.aiwand/config.json)
    # 2. Environment variable (AI_DEFAULT_PROVIDER)
    # 3. First available provider
    # 4. None if no providers available
```

#### Adding New Providers
```python
# In config.py
def get_supported_models() -> Dict[str, list]:
    return {
        "openai": [...],
        "gemini": [...],
        "new_provider": ["model1", "model2"],  # Add here
    }

def get_ai_client() -> OpenAI:
    # Add new provider handling
    if provider == "new_provider":
        return NewProviderClient(api_key=api_key)
```

### Error Handling Strategy

#### Error Hierarchy
```python
# Base exception
class AIError(Exception):
    """Custom exception for AI-related errors."""
    pass

# Usage in functions
try:
    result = api_call()
except ProviderSpecificError as e:
    raise AIError(f"Provider error: {e}")
except NetworkError as e:
    raise AIError(f"Network error: {e}")
except Exception as e:
    raise AIError(f"Unexpected error: {e}")
```

#### CLI Error Handling
```python
try:
    result = function_call()
    print(result)
except AIError as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
except ValueError as e:
    print(f"Input error: {e}", file=sys.stderr)
    sys.exit(1)
```

## 📝 Documentation Workflow

### Documentation Files Structure
```
docs/
├── api-reference.md     # Complete API documentation
├── cli.md               # CLI command reference
├── installation.md      # Installation instructions
├── development.md       # This file
└── venv-guide.md        # Virtual environment guide
```

### Keeping Documentation in Sync

#### When Adding Functions
1. Update `docs/api-reference.md`
2. Update `docs/cli.md` (if CLI command added)
3. Update README.md examples
4. Update relevant examples in `examples/`

#### Documentation Templates
See [CONTRIBUTING.md](../CONTRIBUTING.md) for documentation standards and templates.

## 🔍 Debugging and Troubleshooting

### Common Development Issues

#### Import Errors
```bash
# Ensure package is installed in development mode
pip install -e .

# Check installation
python -c "import aiwand; print(aiwand.__version__)"
```

#### API Configuration Issues
```bash
# Check configuration
python -c "import aiwand; aiwand.show_current_config()"

# Test API connectivity
python -c "
import aiwand
try:
    result = aiwand.chat('test')
    print('API working:', result[:50] + '...')
except Exception as e:
    print('API error:', e)
"
```

#### CLI Issues
```bash
# Verify CLI installation
which aiwand

# Test CLI help
aiwand --help

# Check CLI version
python -c "import aiwand; print(aiwand.__version__)"
```

### Development Environment Issues

#### Virtual Environment
```bash
# Recreate if corrupted
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

#### Package Building
```bash
# Clean build artifacts
rm -rf dist/ build/ *.egg-info

# Rebuild
python -m build
```

## 🚀 Performance Considerations

### API Efficiency
- **Smart caching**: Consider caching for repeated requests
- **Batch operations**: Support multiple items when applicable
- **Timeout handling**: Reasonable timeouts for API calls
- **Rate limiting**: Respect API rate limits

### Package Size
- **Minimal dependencies**: Only essential packages
- **Optional dependencies**: Use extras for optional features
- **Import optimization**: Lazy imports where appropriate

## 🔒 Security Best Practices

### API Key Handling
- **Never hardcode**: API keys in source code
- **Environment variables**: Preferred method
- **User prompts**: For interactive setup only
- **Secure storage**: Use system keyring when available

### Input Validation
- **Sanitize inputs**: Before API calls
- **Length limits**: Prevent excessive API usage
- **Type checking**: Validate parameter types
- **Error boundaries**: Prevent information leakage

## 📊 Monitoring and Analytics

### Usage Tracking (Optional)
- **Anonymous metrics**: For improvement insights
- **Opt-in only**: User consent required
- **Privacy first**: No sensitive data collection
- **Transparent**: Clear documentation of what's tracked

### Error Reporting
- **Structured logging**: For debugging
- **Error aggregation**: For pattern identification
- **User feedback**: For improvement suggestions

---

For contribution guidelines, coding standards, and AI assistant instructions, see [CONTRIBUTING.md](../CONTRIBUTING.md). 