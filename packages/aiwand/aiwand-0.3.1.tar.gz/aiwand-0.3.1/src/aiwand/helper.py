"""
Helper utilities for AIWand
"""

import sys
import os
from pathlib import Path
from typing import Optional


def find_chrome_binary() -> str:
    """Find the Chrome browser executable on the current system.
    
    Searches for Chrome/Chromium executables in platform-specific locations:
    - macOS: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
    - Windows: Program Files, Program Files (x86), and Local AppData
    - Linux: Uses 'which' command to find google-chrome, chromium-browser, or chrome
    
    Returns:
        str: Path to the Chrome executable
        
    Raises:
        FileNotFoundError: When Chrome executable cannot be found on the system
        
    Examples:
        >>> chrome_path = find_chrome_binary()
        >>> print(f"Chrome found at: {chrome_path}")
    """
    plat = sys.platform
    
    if plat == "darwin":
        # macOS
        path = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        if path.exists():
            return str(path)
            
    elif plat.startswith("win"):
        # Windows
        paths = [
            os.environ.get("PROGRAMFILES(X86)"),
            os.environ.get("PROGRAMFILES"),
            os.environ.get("LOCALAPPDATA"),
        ]
        for base in filter(None, paths):
            candidate = Path(base) / "Google\\Chrome\\Application\\chrome.exe"
            if candidate.exists():
                return str(candidate)
                
    else:
        # Linux and other Unix-like systems
        for name in ("google-chrome", "chromium-browser", "chrome"):
            try:
                bin_path = os.popen(f"which {name}").read().strip()
                if bin_path and Path(bin_path).exists():
                    return bin_path
            except Exception:
                # Continue searching if 'which' command fails
                continue
    
    raise FileNotFoundError(
        f"Chrome executable not found on {plat} system. "
        "Please ensure Google Chrome or Chromium is installed."
    )


def get_chrome_version(chrome_path: Optional[str] = None) -> Optional[str]:
    """Get the version of Chrome browser.
    
    Args:
        chrome_path: Optional path to Chrome executable. If not provided,
                    will attempt to find it automatically.
                    
    Returns:
        str: Chrome version string, or None if version cannot be determined
        
    Examples:
        >>> version = get_chrome_version()
        >>> print(f"Chrome version: {version}")
    """
    if chrome_path is None:
        try:
            chrome_path = find_chrome_binary()
        except FileNotFoundError:
            return None
    
    try:
        import subprocess
        result = subprocess.run(
            [chrome_path, "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            # Extract version from output like "Google Chrome 120.0.6099.109"
            version_text = result.stdout.strip()
            if "Chrome" in version_text:
                parts = version_text.split()
                for part in parts:
                    if part.replace(".", "").replace("-", "").isdigit():
                        return part
        return None
    except Exception:
        return None 