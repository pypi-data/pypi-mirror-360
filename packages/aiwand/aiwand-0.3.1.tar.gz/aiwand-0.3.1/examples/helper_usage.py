#!/usr/bin/env python3
"""
Example: Using AIWand Helper Functions

This example demonstrates how to use AIWand's helper utilities,
specifically the Chrome browser detection functionality.
"""

from aiwand.helper import find_chrome_binary, get_chrome_version

def main():
    """Demonstrate helper function usage."""
    print("AIWand Helper Functions Example")
    print("=" * 35)
    
    # Find Chrome browser executable
    print("\n1. Finding Chrome browser executable...")
    try:
        chrome_path = find_chrome_binary()
        print(f"✓ Chrome found at: {chrome_path}")
        
        # Get Chrome version
        print("\n2. Getting Chrome version...")
        version = get_chrome_version(chrome_path)
        if version:
            print(f"✓ Chrome version: {version}")
        else:
            print("⚠ Could not determine Chrome version")
            
        # Alternative: Get version with auto-detection
        print("\n3. Auto-detecting Chrome and getting version...")
        auto_version = get_chrome_version()  # No path needed
        if auto_version:
            print(f"✓ Auto-detected Chrome version: {auto_version}")
        else:
            print("⚠ Could not auto-detect Chrome version")
            
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        print("\n💡 Tip: Make sure Google Chrome or Chromium is installed on your system")
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    print("\n4. Usage tips for different scenarios...")
    print(f"   For terminal copying: Use quoted format")
    print(f"   For shell scripts: Use --path-only flag")
    print(f"   Example: CHROME_PATH=$(aiwand helper chrome --path-only)")

    print("\n" + "=" * 35)
    print("Example completed!")

if __name__ == "__main__":
    main() 