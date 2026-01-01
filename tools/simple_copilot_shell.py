#!/usr/bin/env python3
"""
Simple Copilot-style session shell
Fixed layout with prompt at bottom
"""
import os
import sys
import shutil
import signal
import time
import re
from pathlib import Path

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import Completer, Completion
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.styles import Style
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False
    import readline
    import atexit

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from tools.session.manager import load_session


class Colors:
    """ANSI color codes"""
    RESET = "\033[0m"
    DIM = "\033[2m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BRIGHT_WHITE = "\033[97m"
    ACCENT = "\033[95m"


# Global for SIGINT handling
_last_sigint_time = 0
_sigint_count = 0


def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')


def get_terminal_size():
    """Get terminal width and height"""
    return shutil.get_terminal_size(fallback=(120, 40))


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def visible_len(text: str) -> int:
    return len(strip_ansi(text))


def pad_to(text: str, width: int) -> str:
    padding = max(width - visible_len(text), 0)
    return f"{text}{' ' * padding}"


def get_git_branch():
    """Get current git branch with dirty indicator"""
    try:
        import subprocess
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=BASE_DIR
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=BASE_DIR
            )
            is_dirty = bool(status.stdout.strip())
            return f"{branch}*" if is_dirty else branch
        return ""
    except:
        return ""


def build_claude_panel_lines(session, term_width):
    """Build Claude-style panel header lines."""
    from tools.ai.providers import get_provider_registry
    from tools.config import get_config

    if "active_provider_id" not in session or not session.get("active_provider_id"):
        config = get_config()
        session["active_provider_id"] = config.default_provider

    registry = get_provider_registry()
    provider = registry.get_provider(session.get("active_provider_id"))

    cwd = os.getcwd()
    home = os.path.expanduser("~")
    short_cwd = "~" + cwd[len(home):] if cwd.startswith(home) else cwd

    git_branch = get_git_branch()
    branch_label = f"{short_cwd}{f' [{git_branch}]' if git_branch else ''}"

    model_short = provider.id.replace("openai-", "").replace("anthropic-", "")
    model_label = f"{Colors.DIM}{model_short} (1x){Colors.RESET}"

    inner_width = max(term_width - 2, 60)
    content_width = inner_width - 2
    lines = []
    lines.append(f"{Colors.ACCENT}╭{'─' * inner_width}╮{Colors.RESET}")

    title_left = f"{Colors.BRIGHT_WHITE}LinkoWiki Code{Colors.RESET} {Colors.DIM}Session{Colors.RESET}"
    title_spacing = content_width - visible_len(title_left) - visible_len(model_label)
    if title_spacing < 1:
        title_spacing = 1
    lines.append(
        f"{Colors.ACCENT}│{Colors.RESET} "
        f"{title_left}{' ' * title_spacing}{model_label}"
        f" {Colors.ACCENT}│{Colors.RESET}"
    )

    left_lines = [
        f"{Colors.BRIGHT_WHITE}Welcome back!{Colors.RESET}",
        f"{Colors.DIM}Session ID: {session.get('id', 'unknown')}{Colors.RESET}",
        f"{Colors.DIM}Mode: {'Write' if session.get('write') else 'Read-only'}{Colors.RESET}",
        f"{Colors.DIM}Path: {branch_label}{Colors.RESET}",
    ]
    right_lines = [
        f"{Colors.BRIGHT_WHITE}Tips for getting started{Colors.RESET}",
        f"{Colors.DIM}Use /help to see commands{Colors.RESET}",
        f"{Colors.DIM}Use /attach <file> to add context{Colors.RESET}",
        f"{Colors.BRIGHT_WHITE}Recent activity{Colors.RESET}",
        f"{Colors.DIM}{len(session.get('history', []))} messages so far{Colors.RESET}",
    ]

    left_width = (content_width - 1) // 2
    right_width = content_width - 1 - left_width
    max_lines = max(len(left_lines), len(right_lines))

    for idx in range(max_lines):
        left_text = left_lines[idx] if idx < len(left_lines) else ""
        right_text = right_lines[idx] if idx < len(right_lines) else ""
        left_padded = pad_to(left_text, left_width)
        right_padded = pad_to(right_text, right_width)
        lines.append(
            f"{Colors.ACCENT}│{Colors.RESET} "
            f"{left_padded}{Colors.ACCENT}│{Colors.RESET} "
            f"{right_padded} {Colors.ACCENT}│{Colors.RESET}"
        )

    lines.append(f"{Colors.ACCENT}╰{'─' * inner_width}╯{Colors.RESET}")
    return lines


def render_copilot_screen(session, content_lines=None):
    """Render complete Claude-style screen"""
    term_width, _ = get_terminal_size()

    # Don't clear screen - preserve terminal history
    print()
    for line in build_claude_panel_lines(session, term_width):
        print(line)
    print()

    # Content area (if any)
    if content_lines:
        print()
        for line in content_lines:
            print(line)
        print()

    hints = [
        f"{Colors.DIM}Try \"/help\" for commands{Colors.RESET}",
        f"{Colors.DIM}? for shortcuts{Colors.RESET}",
    ]
    for line in hints:
        print(f"  {line}")
    print()

    print(f"{Colors.DIM}{'─' * term_width}{Colors.RESET}")
    print(f"> ", end="", flush=True)


def sigint_handler(signum, frame):
    """Handle Ctrl+C with double-press detection"""
    global _last_sigint_time, _sigint_count

    current_time = time.time()

    # Reset count if more than 2 seconds since last SIGINT
    if current_time - _last_sigint_time > 2.0:
        _sigint_count = 0

    _sigint_count += 1
    _last_sigint_time = current_time

    if _sigint_count >= 2:
        # Second Ctrl+C within 2 seconds - exit
        print(f"\n\n{Colors.DIM}Exiting...{Colors.RESET}\n")
        sys.exit(0)
    else:
        # First Ctrl+C - show message and raise to interrupt input()
        print(f"\n{Colors.YELLOW}⚠  Press Ctrl+C again within 2 seconds to exit{Colors.RESET}")
        raise KeyboardInterrupt


# Available commands for completion
COMMANDS = [
    "/help", "/model", "/model list", "/model set",
    "/clear", "/cls", "/exit", "/quit", "/attach",
    "exit", "quit", "help"
]

COMMAND_DESCRIPTIONS = {
    "/help": "Show help",
    "/model": "Show current model",
    "/model list": "List all models",
    "/model set": "Switch model",
    "/clear": "Clear screen",
    "/cls": "Clear screen",
    "/exit": "Exit shell",
    "/quit": "Exit shell",
    "/attach": "Attach file for context",
    "exit": "Exit shell",
    "quit": "Exit shell",
    "help": "Show help",
}


if PROMPT_TOOLKIT_AVAILABLE:
    class PromptToolkitCompleter(Completer):
        """Auto-completion with arrow key selection for prompt_toolkit"""

        def get_completions(self, document, complete_event):
            """Yield completions for the current input"""
            text = document.text_before_cursor

            # Show all commands if we're at the beginning or after typing /
            for cmd in COMMANDS:
                if cmd.startswith(text):
                    description = COMMAND_DESCRIPTIONS.get(cmd, "")
                    yield Completion(
                        cmd,
                        start_position=-len(text),
                        display=cmd,
                        display_meta=description
                    )


class ReadlineCompleter:
    """Tab completion for readline (fallback)"""

    def __init__(self, options):
        self.options = sorted(options)

    def complete(self, text, state):
        """Return the next possible completion for 'text'"""
        if state == 0:
            # First call: generate matches
            if text:
                self.matches = [cmd for cmd in self.options if cmd.startswith(text)]
            else:
                self.matches = self.options[:]

        # Return match indexed by state
        try:
            return self.matches[state]
        except IndexError:
            return None


def setup_readline():
    """Configure readline for history and completion (fallback)"""
    if PROMPT_TOOLKIT_AVAILABLE:
        return  # prompt_toolkit handles this

    # History file
    history_file = BASE_DIR / ".copilot_history"

    # Load history if it exists
    if history_file.exists():
        try:
            readline.read_history_file(str(history_file))
        except:
            pass

    # Set history length
    readline.set_history_length(1000)

    # Save history on exit
    atexit.register(lambda: readline.write_history_file(str(history_file)))

    # Setup tab completion
    completer = ReadlineCompleter(COMMANDS)
    readline.set_completer(completer.complete)
    readline.parse_and_bind("tab: complete")

    # Enable vi or emacs mode (emacs is default)
    readline.parse_and_bind("set editing-mode emacs")


def simple_shell():
    """Simple Copilot-style shell"""
    # Setup SIGINT handler
    signal.signal(signal.SIGINT, sigint_handler)

    s = load_session()
    if not s:
        print(f"\n{Colors.RED}error: no active session{Colors.RESET}")
        print(f"{Colors.DIM}run 'linkowiki-admin session start' first{Colors.RESET}\n")
        return

    # Setup input method
    if PROMPT_TOOLKIT_AVAILABLE:
        history_file = BASE_DIR / ".copilot_history"
        session = PromptSession(
            history=FileHistory(str(history_file)),
            completer=PromptToolkitCompleter(),
            complete_while_typing=True,
            enable_history_search=True,
        )
    else:
        setup_readline()
        session = None

    content = []
    while True:
        render_copilot_screen(s, content)

        try:
            # Get input
            if session:  # prompt_toolkit
                cmd = session.prompt().strip()
            else:  # readline fallback
                cmd = input().strip()

            # Print double separator AFTER input for visual separation
            term_width, _ = get_terminal_size()
            print(f"{Colors.DIM}{'─' * term_width}{Colors.RESET}")
            print()  # Empty line for spacing

            # Reset SIGINT counter on successful input
            global _sigint_count
            _sigint_count = 0
        except EOFError:
            print()
            break
        except KeyboardInterrupt:
            # Print separator after Ctrl+C
            term_width, _ = get_terminal_size()
            print(f"\n{Colors.DIM}{'─' * term_width}{Colors.RESET}")
            print()  # Empty line for spacing
            content = [f"  {Colors.YELLOW}Press Ctrl+C again to exit{Colors.RESET}"]
            continue
        
        if not cmd:
            continue
        
        if cmd in ("exit", "quit", "/exit", "/quit"):
            break
        
        if cmd in ("/clear", "/cls"):
            content = []
            clear_screen()  # Only clear on explicit user request
            continue
        
        if cmd in ("help", "/help"):
            content = [
                f"  {Colors.BRIGHT_WHITE}/help{Colors.RESET}                         Show help",
                f"  {Colors.BRIGHT_WHITE}/model{Colors.RESET}                        Show current model",
                f"  {Colors.BRIGHT_WHITE}/model list{Colors.RESET}                   List all models",
                f"  {Colors.BRIGHT_WHITE}/clear{Colors.RESET}                        Clear screen",
                f"  {Colors.BRIGHT_WHITE}/exit{Colors.RESET}                         Exit shell",
            ]
            continue
        
        if cmd == "/model":
            from tools.ai.providers import get_provider_registry
            registry = get_provider_registry()
            provider = registry.get_provider(s.get("active_provider_id"))
            
            content = [
                f"  {Colors.BRIGHT_WHITE}Active Model{Colors.RESET}",
                f"  {Colors.DIM}{'─' * 60}{Colors.RESET}",
                f"  ID: {provider.id}",
                f"  Provider: {provider.provider}",
                f"  Type: {'Reasoning' if provider.reasoning else 'Text'}",
            ]
            if provider.description:
                content.append(f"  {Colors.DIM}{provider.description}{Colors.RESET}")
            continue
        
        if cmd == "/model list":
            from tools.ai.providers import get_provider_registry
            registry = get_provider_registry()
            providers = registry.list_providers()
            
            content = [f"  {Colors.BRIGHT_WHITE}Available Models{Colors.RESET}", ""]
            for provider_id, provider in providers.items():
                is_active = (provider_id == s.get("active_provider_id"))
                marker = "▌" if is_active else " "
                reasoning_tag = "[R]" if provider.reasoning else ""
                
                line = f"{marker} {provider_id} {reasoning_tag}"
                content.append(line)
            
            content.append("")
            content.append(f"  {Colors.DIM}Use /model set <id> to switch{Colors.RESET}")
            continue
        
        # Default: show unknown command
        content = [f"  {Colors.DIM}Unknown command: {cmd}{Colors.RESET}"]


if __name__ == "__main__":
    simple_shell()
