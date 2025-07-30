# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.1] - 2025-01-27

### Fixed
- **Documentation Accuracy**: Removed non-existent `configure_api_key()` function from all documentation
- **API Reference**: Corrected configuration approach to use environment variables and `setup_user_preferences()`
- **Model Names**: Updated supported model lists to match actual implementation
- **Installation Guide**: Fixed programmatic setup examples to show correct methods
- **Package Focus**: Prioritized Python package usage over CLI in documentation

### Changed
- **API Exports**: Removed unrelated Chrome helper functions (`find_chrome_binary`, `get_chrome_version`) from public API
- **Documentation Structure**: Reorganized README to emphasize package-first usage
- **Error Handling**: Enhanced documentation with proper `AIError` exception examples

### Technical Improvements
- Cleaned up package exports to focus on core AI functionality
- Improved documentation consistency across all files
- Better error handling examples and best practices

## [0.3.0] - 2025-06-23

### Added
- **Direct Prompt Support**: New simplified CLI usage - `aiwand "Your prompt here"` for instant AI chat
- **Enhanced CLI Experience**: Direct prompts bypass subcommands for faster interaction
- **Updated Documentation**: Added quick start examples and direct prompt usage guide
- **Backward Compatibility**: All existing subcommands (chat, summarize, generate) continue to work

### Changed
- **CLI Help Text**: Updated to showcase direct prompt feature as primary usage method
- **README Examples**: Prioritized direct prompt usage in documentation
- **CLI Reference**: Added comprehensive direct prompt examples and use cases

### Technical Improvements
- Smart command detection that differentiates between subcommands and direct prompts
- Maintained full backward compatibility with existing CLI structure
- Enhanced argument parsing with better help formatting

## [0.2.0] - 2025-06-23

### Added
- **Interactive Setup System**: New `aiwand setup` command for guided configuration
- **User Preferences**: Persistent configuration storage in `~/.aiwand/config.json`
- **Enhanced Model Support**: Added GPT-4o, GPT-4o-mini, Gemini 2.0 Flash Experimental models
- **Configuration Status Command**: New `aiwand status` to display current settings
- **Smart Provider Selection**: Hierarchical preference system (user config → env vars → auto-detection)
- **Per-Provider Model Selection**: Configure different models for each AI provider
- **AIError Exception Class**: Better error handling with specific error types

### Changed
- **Completely Rewritten Configuration System**: More robust and user-friendly
- **Updated CLI Interface**: Removed old config command, added setup/status commands
- **Enhanced Examples**: Updated to showcase new setup system and preferences
- **Improved Test Suite**: Tests now cover new API functions and error handling
- **Better Error Messages**: More helpful guidance for setup and configuration

### Technical Improvements
- Centralized configuration management with fallback logic
- Support for multiple model options per provider
- Persistent user preference storage
- Enhanced type hints and error handling
- Improved CLI argument parsing and help messages

## [0.1.0] - 2025-06-23

### Added
- Centralized version management (single source of truth in `__init__.py`)
- Comprehensive documentation structure in `docs/` directory
- Professional README with badges and social links  
- X (Twitter) profile integration (@onlyoneaman)
- Detailed installation guide with troubleshooting
- Complete API reference documentation
- CLI reference with examples
- Virtual environment best practices guide

### Changed
- Updated contact email to 2000.aman.sinha@gmail.com
- Streamlined README from 308 to 106 lines (65% reduction)
- Reorganized documentation into modular structure
- Improved package metadata and descriptions

### Fixed
- Improved error handling and validation
- Enhanced setup scripts for development environment

## [0.0.1] - 2025-06-23

### Added
- Initial release of AIWand
- Smart AI provider selection (OpenAI & Gemini APIs)
- Text summarization with multiple styles (concise, detailed, bullet-points)
- AI chat functionality with conversation history support
- Text generation with customizable parameters
- Command line interface (CLI) with auto-model selection
- Virtual environment support with automated setup scripts
- Environment-based configuration with `.env` file support
- Smart model selection based on available API keys
- Support for both OpenAI and Google Gemini models
- Comprehensive error handling and input validation
- MIT License
- PyPI package distribution
- GitHub repository with complete documentation

### Technical Features
- Python 3.8+ compatibility
- Type hints throughout codebase
- Modular architecture with separate config, core, and CLI modules
- Automated development environment setup (Linux/Mac/Windows)
- Professional package structure with src/ layout
- Comprehensive test suite and installation verification 