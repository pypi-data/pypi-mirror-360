"""
Command Line Interface for AIWand
"""

import argparse
import sys
from typing import Optional
from .core import summarize, chat, generate_text
from .config import setup_user_preferences, show_current_config, AIError
from .helper import find_chrome_binary, get_chrome_version


def main():
    """Main CLI entry point."""
    # Check if this is a direct prompt (only works with quoted text containing spaces/punctuation)
    known_commands = {'summarize', 'chat', 'generate', 'setup', 'status', 'helper'}
    
    # Handle non-command arguments
    if len(sys.argv) > 1 and sys.argv[1] not in known_commands and not sys.argv[1].startswith('-'):
        
        if len(sys.argv) == 2:
            # Single argument case: aiwand "something" or aiwand something
            single_arg = sys.argv[1]
            
            # Only treat as direct prompt if it contains spaces (indicating it was quoted)
            # Single words without spaces are rejected to avoid command confusion
            if ' ' in single_arg:
                # Multi-word content - must have been quoted
                try:
                    result = chat(message=single_arg)
                    print(result)
                    return
                except AIError as e:
                    print(f"Error: {e}", file=sys.stderr)
                    sys.exit(1)
                except Exception as e:
                    print(f"Error: {e}", file=sys.stderr)
                    sys.exit(1)
            else:
                # Single word - show error
                print(f"Error: '{single_arg}' is not a recognized command.", file=sys.stderr)
                print("For single-word prompts, use the chat command:", file=sys.stderr)
                print(f"  aiwand chat \"{single_arg}\"", file=sys.stderr)
                print("For available commands, use: aiwand --help", file=sys.stderr)
                sys.exit(1)
                
        else:
            # Multiple unquoted words - show error
            attempted_prompt = ' '.join(sys.argv[1:])
            print(f"Error: Unquoted multi-word input detected.", file=sys.stderr)
            print(f"Did you mean: aiwand \"{attempted_prompt}\"", file=sys.stderr)
            print("Direct prompts must be quoted to avoid confusion with commands.", file=sys.stderr)
            sys.exit(1)
    
    # Original subcommand-based CLI logic
    parser = argparse.ArgumentParser(
        description="AIWand - AI toolkit for text processing\n\nQuick usage: aiwand \"Your multi-word prompt here\" for direct chat\n(Single words require: aiwand chat \"word\")",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Summarize command
    summarize_parser = subparsers.add_parser('summarize', help='Summarize text')
    summarize_parser.add_argument('text', help='Text to summarize')
    summarize_parser.add_argument('--style', choices=['concise', 'detailed', 'bullet-points'], 
                                 default='concise', help='Summary style')
    summarize_parser.add_argument('--max-length', type=int, help='Maximum length in words')
    summarize_parser.add_argument('--model', help='AI model to use (auto-selected if not provided)')
    
    # Chat command
    chat_parser = subparsers.add_parser('chat', help='Chat with AI')
    chat_parser.add_argument('message', help='Message to send')
    chat_parser.add_argument('--model', help='AI model to use (auto-selected if not provided)')
    chat_parser.add_argument('--temperature', type=float, default=0.7, help='Response creativity')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate text from prompt')
    generate_parser.add_argument('prompt', help='Prompt for text generation')
    generate_parser.add_argument('--max-tokens', type=int, default=500, help='Maximum tokens to generate')
    generate_parser.add_argument('--temperature', type=float, default=0.7, help='Response creativity')
    generate_parser.add_argument('--model', help='AI model to use (auto-selected if not provided)')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Interactive setup for preferences')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show current configuration')
    
    # Helper command
    helper_parser = subparsers.add_parser('helper', help='System helper utilities')
    helper_subparsers = helper_parser.add_subparsers(dest='helper_command', help='Helper utilities')
    
    # Chrome binary finder
    chrome_parser = helper_subparsers.add_parser('chrome', help='Find Chrome browser executable')
    chrome_parser.add_argument('--version', action='store_true', help='Also show Chrome version')
    chrome_parser.add_argument('--path-only', action='store_true', help='Output only the path (no quotes, for scripting)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'summarize':
            result = summarize(
                text=args.text,
                max_length=args.max_length,
                style=args.style,
                model=args.model
            )
            print(result)
            
        elif args.command == 'chat':
            result = chat(
                message=args.message,
                model=args.model,
                temperature=args.temperature
            )
            print(result)
            
        elif args.command == 'generate':
            result = generate_text(
                prompt=args.prompt,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
                model=args.model
            )
            print(result)
            
        elif args.command == 'setup':
            setup_user_preferences()
            
        elif args.command == 'status':
            show_current_config()
            
        elif args.command == 'helper':
            if not args.helper_command:
                print("Error: Please specify a helper command. Use 'aiwand helper --help' for options.", file=sys.stderr)
                sys.exit(1)
                
            if args.helper_command == 'chrome':
                try:
                    chrome_path = find_chrome_binary()
                    
                    if args.path_only:
                        # Just output the raw path for scripting
                        print(chrome_path)
                    else:
                        # Output quoted path for easy copying
                        print(f'"{chrome_path}"')
                    
                    if args.version:
                        version = get_chrome_version(chrome_path)
                        if version:
                            print(f"Version: {version}")
                        else:
                            print("Version: Unable to determine")
                            
                except FileNotFoundError as e:
                    print(f"Error: {e}", file=sys.stderr)
                    sys.exit(1)
            
    except AIError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 