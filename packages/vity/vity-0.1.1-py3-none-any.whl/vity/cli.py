#!/usr/bin/env python3
"""
Vity CLI - AI-powered terminal assistant
"""
import sys
import os
import argparse
from pathlib import Path
from typing import Optional

from .config import config
from .llm import generate_command, generate_chat_response
from .schema import Command


def setup_config() -> bool:
    """Setup configuration on first run"""
    config_dir = Path.home() / ".config" / "vity"
    config_file = config_dir / ".env"
    
    if not config_file.exists():
        print("🤖 Welcome to Vity! Let's set up your OpenAI API key.")
        print("You can get one at: https://platform.openai.com/api-keys")
        print()
        
        api_key = input("Enter your OpenAI API key: ").strip()
        if not api_key:
            print("❌ API key is required")
            return False
        
        config_dir.mkdir(parents=True, exist_ok=True)
        config_file.write_text(f"OPENAI_API_KEY={api_key}\n")
        
        print("✅ Configuration saved!")
        print(f"Config file: {config_file}")
        print()
        
        # Set environment variable for this session
        os.environ["OPENAI_API_KEY"] = api_key
        
    return True


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Vity - AI-powered terminal assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  vity do "find all python files"
  vity chat "explain this error"
  vity -f session.log do "fix the deployment issue"
  
For shell integration, run: vity install
        """
    )
    
    parser.add_argument(
        "-f", "--file", dest="history_file",
        help="Path to terminal session log file for context"
    )
    parser.add_argument(
        "-m", "--mode", dest="interaction_mode",
        choices=["do", "chat"],
        default="do",
        help="Interaction mode (default: do)"
    )
    parser.add_argument(
        "--version", action="version", version="%(prog)s 0.1.1"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Do command
    do_parser = subparsers.add_parser("do", help="Generate shell command")
    do_parser.add_argument("prompt", nargs="+", help="What you want to do")
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Chat with AI")
    chat_parser.add_argument("prompt", nargs="+", help="Your question")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install shell integration")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument("--reset", action="store_true", help="Reset configuration")
    
    args = parser.parse_args()
    
    # Handle special commands first
    if args.command == "install":
        install_shell_integration()
        return
    
    if args.command == "config":
        if args.reset:
            reset_config()
        else:
            show_config()
        return
    
    # Setup config if needed
    if not setup_config():
        sys.exit(1)
    
    # Handle main commands
    if not args.command:
        parser.print_help()
        return
    
    if args.command in ["do", "chat"]:
        user_input = " ".join(args.prompt)
        
        # Load terminal history if provided
        terminal_history = ""
        if args.history_file:
            try:
                with open(args.history_file, "r") as f:
                    terminal_history = f.read()
            except FileNotFoundError:
                print(f"⚠️  Warning: history file '{args.history_file}' not found")
        
        print("🤖 Vity is thinking...")
        
        try:
            if args.command == "do":
                command = generate_command(terminal_history, user_input)
                cmd_string = f"{command.command} # {command.comment}"
                print(f"Command: {cmd_string}")
                
                # Add to bash history
                history_file = Path.home() / ".bash_history"
                if history_file.exists():
                    with open(history_file, "a") as f:
                        f.write(f"{cmd_string} # Vity generated\n")
                
            elif args.command == "chat":
                response = generate_chat_response(terminal_history, user_input)
                print(response)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)


def install_shell_integration():
    """Install shell integration"""
    script_content = '''
# Vity shell integration
vity() {
    if [[ "$1" == "record" ]]; then
        shift
        log_dir="$HOME/.local/share/vity/logs"
        mkdir -p "$log_dir"
        logfile="$log_dir/$(date +%Y%m%d-%H%M%S)-$$.log"
        
        export VITY_ACTIVE_LOG="$logfile"
        export VITY_RECORDING="🔴"
        export VITY_OLD_PS1="$PS1"
        export PS1="$VITY_RECORDING $PS1"
        echo -ne "\\033]0;🔴 RECORDING - Vity Session\\007"
        
        echo "🔴 Starting recording session"
        echo "📝 Use 'vity do' or 'vity chat' for contextual help"
        echo "🛑 Type 'exit' to stop recording"
        
        script -f "$logfile"
        
        unset VITY_ACTIVE_LOG VITY_RECORDING VITY_OLD_PS1
        export PS1="$VITY_OLD_PS1"
        echo -ne "\\033]0;Terminal\\007"
        echo "🟢 Recording session ended"
        
    elif [[ "$1" == "do" ]]; then
        shift
        if [[ -n "$VITY_ACTIVE_LOG" && -f "$VITY_ACTIVE_LOG" ]]; then
            command vity -f "$VITY_ACTIVE_LOG" do "$@"
        else
            echo "⚠️  No active recording. Use 'vity record' for context."
            command vity do "$@"
        fi
        
    elif [[ "$1" == "chat" ]]; then
        shift
        if [[ -n "$VITY_ACTIVE_LOG" && -f "$VITY_ACTIVE_LOG" ]]; then
            command vity -f "$VITY_ACTIVE_LOG" chat "$@"
        else
            echo "⚠️  No active recording. Use 'vity record' for context."
            command vity chat "$@"
        fi
        
    elif [[ "$1" == "status" ]]; then
        if [[ -n "$VITY_ACTIVE_LOG" ]]; then
            echo "🔴 Recording active: $VITY_ACTIVE_LOG"
        else
            echo "⚫ No active recording"
        fi
        
    elif [[ "$1" == "help" || "$1" == "-h" || "$1" == "--help" ]]; then
        cat << 'EOF'
🤖 Vity - AI Terminal Assistant

USAGE:
    vity <command> [options] [prompt]

COMMANDS:
    do <prompt>      Generate a shell command (adds to history)
    chat <prompt>    Chat with AI about terminal/coding topics
    record           Start recording session for context
    status           Show current recording status
    help             Show this help message

EXAMPLES:
    vity do "find all python files"
    vity chat "explain this error message"
    vity record
    vity do "deploy the app"  # (with context from recording)
    vity status

CONTEXT:
    • Use 'vity record' to start capturing session context
    • Commands run during recording provide better AI responses
    • Recording indicator (🔴) shows in your prompt
    • Use 'exit' to stop recording
EOF
        
    else
        # Show help for unknown commands or no arguments
        if [[ -n "$1" ]]; then
            echo "❌ Unknown command: $1"
            echo ""
        fi
        echo "🤖 Vity - AI Terminal Assistant"
        echo ""
        echo "Usage: vity <command> [prompt]"
        echo ""
        echo "Commands:"
        echo "  do <prompt>      Generate shell command"
        echo "  chat <prompt>    Chat with AI"
        echo "  record           Start recording session"
        echo "  status           Show recording status"
        echo "  help             Show detailed help"
        echo ""
        echo "Run 'vity help' for more details and examples."
    fi
    
    history -n 2>/dev/null || true
}
'''
    
    bashrc = Path.home() / ".bashrc"
    if bashrc.exists():
        content = bashrc.read_text()
        if "# Vity shell integration" not in content:
            with open(bashrc, "a") as f:
                f.write(f"\n{script_content}")
            print("✅ Shell integration installed!")
            print("Run 'source ~/.bashrc' or start a new terminal session")
        else:
            print("✅ Shell integration already installed")
    else:
        print("❌ ~/.bashrc not found")


def reset_config():
    """Reset configuration"""
    config_dir = Path.home() / ".config" / "vity"
    config_file = config_dir / ".env"
    
    if config_file.exists():
        config_file.unlink()
        print("✅ Configuration reset")
    else:
        print("ℹ️  No configuration found")


def show_config():
    """Show current configuration"""
    config_dir = Path.home() / ".config" / "vity"
    config_file = config_dir / ".env"
    
    if config_file.exists():
        print(f"📁 Config file: {config_file}")
        print("🔑 API key configured")
    else:
        print("❌ No configuration found")
        print("Run 'vity config' to set up")


if __name__ == "__main__":
    main() 