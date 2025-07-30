# Virtual Environment Guide for AIWand

## Why Use Virtual Environments?

Virtual environments help you:
- **Isolate dependencies** - Avoid conflicts between different projects
- **Maintain clean system** - Keep your global Python installation clean
- **Reproduce environments** - Ensure consistent setups across different machines
- **Manage versions** - Use different package versions for different projects

## Quick Start

### Create and Activate

```bash
# Create virtual environment
python -m venv .venv

# Activate (Linux/Mac)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate

# Verify activation (you should see (.venv) in your prompt)
which python  # Should point to .venv/bin/python
```

### Install AIWand

```bash
# Install from PyPI
pip install aiwand

# Or install in development mode
pip install -e ".[dev]"
```

### Deactivate

```bash
# When you're done working
deactivate
```

## Automated Setup

Use our setup scripts for one-command setup:

```bash
# Linux/Mac
./scripts/setup-dev.sh

# Windows
scripts\setup-dev.bat
```

## Common Commands

```bash
# Check what's installed
pip list

# Create requirements file
pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt

# Update pip
pip install --upgrade pip

# Remove virtual environment
rm -rf .venv  # Linux/Mac
rmdir /s .venv  # Windows
```

## IDE Integration

### VS Code
1. Open the project folder
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Type "Python: Select Interpreter"
4. Choose the Python interpreter from `.venv/bin/python`

### PyCharm
1. Go to File → Settings → Project → Python Interpreter
2. Click the gear icon → Add
3. Select "Existing environment"
4. Choose `.venv/bin/python`

## Troubleshooting

### Virtual environment not activating
```bash
# Make sure you're in the project directory
pwd

# Check if .venv exists
ls -la .venv

# Recreate if needed
rm -rf .venv
python -m venv .venv
```

### Permission issues (Linux/Mac)
```bash
# Make sure scripts are executable
chmod +x scripts/setup-dev.sh
chmod +x .venv/bin/activate
```

### Python not found
```bash
# Try python3 instead of python
python3 -m venv .venv

# Or use full path
/usr/bin/python3 -m venv .venv
```

## Best Practices

1. **Always activate** your virtual environment before working
2. **Use .venv** as the standard directory name
3. **Don't commit** `.venv/` to version control (it's in .gitignore)
4. **Update pip** regularly: `pip install --upgrade pip`
5. **Use requirements.txt** to share dependencies
6. **Deactivate** when switching projects

## Environment Variables

Set your API keys after activation:

```bash
# Linux/Mac
export OPENAI_API_KEY="your-key-here"
export GEMINI_API_KEY="your-key-here"

# Windows
set OPENAI_API_KEY=your-key-here
set GEMINI_API_KEY=your-key-here

# Or use .env file
echo "OPENAI_API_KEY=your-key-here" >> .env
echo "GEMINI_API_KEY=your-key-here" >> .env
``` 