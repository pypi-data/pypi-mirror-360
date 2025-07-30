# Development Guide

This guide covers the development workflow for AIWand, including version management, testing, and publishing.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/onlyoneaman/aiwand.git
   cd aiwand
   ```

2. **Set up development environment:**
   ```bash
   # Linux/Mac
   ./scripts/setup-dev.sh
   
   # Windows
   scripts\setup-dev.bat
   ```

3. **Install development dependencies:**
   ```bash
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate     # Windows
   
   pip install -e .
   pip install build twine pytest
   ```

## Version Management

AIWand uses centralized version management with the version defined in `src/aiwand/__init__.py`.

### Bumping Versions

Use the automated version bumping script:

```bash
# Patch version (0.1.0 -> 0.1.1)
python scripts/bump-version.py patch

# Minor version (0.1.0 -> 0.2.0)
python scripts/bump-version.py minor

# Major version (0.1.0 -> 1.0.0)
python scripts/bump-version.py major
```

### Manual Version Updates

If you need to manually update the version:
1. Edit the `__version__` variable in `src/aiwand/__init__.py`
2. Update `CHANGELOG.md` with the new version and changes
3. Follow the publishing process below

## Testing

### Run Installation Tests
```bash
python test_install.py
```

### Run Basic Functionality Tests
```bash
python examples/basic_usage.py
```

### CLI Testing
```bash
aiwand --help
aiwand summarize "Your text here"
aiwand chat "Hello, how are you?"
```

## Publishing Process

### Automated Publishing (Recommended)

Use the automated publishing script:

```bash
python scripts/publish.py
```

This script will:
1. Check git working directory is clean
2. Run installation tests
3. Clean previous builds
4. Build the package
5. Upload to PyPI
6. Create and push git tags
7. Push to GitHub

### Manual Publishing

If you need to publish manually:

1. **Update version and changelog:**
   ```bash
   # Update version in src/aiwand/__init__.py
   # Update CHANGELOG.md
   ```

2. **Clean previous builds:**
   ```bash
   rm -rf dist/ build/ src/*.egg-info/
   ```

3. **Build the package:**
   ```bash
   python -m build
   ```

4. **Upload to PyPI:**
   ```bash
   python -m twine upload dist/*
   ```

5. **Create and push git tag:**
   ```bash
   git tag v$(python -c "import sys; sys.path.append('src'); from aiwand import __version__; print(__version__)")
   git push origin main --tags
   ```

## Changelog Management

Follow [Keep a Changelog](https://keepachangelog.com/) format:

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** in case of vulnerabilities

## Git Workflow

1. **Create feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes and commit:**
   ```bash
   git add .
   git commit -m "Descriptive commit message"
   ```

3. **Push and create PR:**
   ```bash
   git push origin feature/your-feature-name
   ```

4. **After PR approval, merge to main:**
   ```bash
   git checkout main
   git pull origin main
   ```

5. **Update version and publish:**
   ```bash
   python scripts/bump-version.py patch  # or minor/major
   # Update CHANGELOG.md
   git add . && git commit -m "Bump version to X.Y.Z"
   python scripts/publish.py
   ```

## Code Style

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write descriptive docstrings for all public functions and classes
- Keep functions focused and modular
- Use meaningful variable and function names

## Documentation

- Update relevant documentation in `docs/` directory when making changes
- Keep README.md concise and up-to-date
- Ensure API reference in `docs/api-reference.md` reflects current functionality
- Update CLI documentation in `docs/cli.md` for command-line changes

## Environment Variables

For development and testing:
```bash
# Copy example environment file
cp .env.example .env

# Add your API keys
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
AI_DEFAULT_PROVIDER=gemini  # or openai
```

## Best Practices

1. **Test thoroughly** before publishing
2. **Update documentation** with any API changes
3. **Follow semantic versioning** (MAJOR.MINOR.PATCH)
4. **Keep changelog updated** with each release
5. **Use automated scripts** for consistency
6. **Check git status** before publishing
7. **Tag releases** for version tracking 