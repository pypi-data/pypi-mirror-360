"""
AIWand - A simple AI toolkit for text processing using OpenAI and Gemini
"""

__version__ = "0.3.1"
__author__ = "Aman Kumar"

from .core import summarize, chat, generate_text
from .config import setup_user_preferences, show_current_config, AIError

__all__ = [
    "summarize",
    "chat", 
    "generate_text",
    "setup_user_preferences",
    "show_current_config",
    "AIError",
] 