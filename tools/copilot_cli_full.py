#!/usr/bin/env python3
"""
LinkoWiki Copilot CLI - Full Interactive Implementation
Professional Copilot-style CLI with complete feature set
"""
import os
import sys
import shutil
import time
import signal
from pathlib import Path
from typing import Optional, List, Tuple

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import Completer, Completion
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False

from tools.session.manager import load_session, start_session, add_history
from tools.ai.assistant import run_ai


class Colors:
    """ANSI color codes for Copilot CLI"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Foreground
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    BRIGHT_WHITE = "\033[97m"
    BRIGHT_MAGENTA = "\033[95m"


class CopilotCLI:
    """Full Copilot-style CLI implementation"""
    
    def __init__(self):
        self.term_width, self.term_height = shutil.get_terminal_size(fallback=(120, 40))
        self.cwd = os.getcwd()
        self.git_branch = self._get_git_branch()
        self.model_name = "claude-sonnet-4.5"
        self.model_count = "1x"
        self.context_usage = 0.13  # 13% to truncation
        self.requests_remaining = 98.2  # Remaining requests: 98.2%
        self.active_task: Optional[str] = None
        self.task_size: Optional[str] = None
        
    def _get_git_branch(self) -> str:
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
                # Check if dirty
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
    
    def _shorten_path(self) -> str:
        """Shorten CWD with ~ for home"""
        home = os.path.expanduser("~")
        if self.cwd.startswith(home):
            return "~" + self.cwd[len(home):]
        return self.cwd
    
    def _render_header(self) -> str:
        """Render upper status bar"""
        short_cwd = self._shorten_path()
        left = short_cwd
        if self.git_branch:
            left += f"[ {self.git_branch}]"
        
        right = f"{self.model_name} ({self.model_count})"
        
        spacing = self.term_width - len(left) - len(right)
        if spacing < 1:
            spacing = 1
        
        return f"{Colors.DIM}{left}{' ' * spacing}{right}{Colors.RESET}"
    
    def _render_separator(self) -> str:
        """Render horizontal separator line"""
        return f"{Colors.DIM}{'─' * self.term_width}{Colors.RESET}"
    
    def _render_footer_status(self) -> str:
        """Render lower status bar with context usage"""
        short_cwd = self._shorten_path()
        left = short_cwd
        if self.git_branch:
            left += f"[ {self.git_branch}]"
        
        middle = f"{self.model_name} ({self.model_count})"
        right = f"{int(self.context_usage * 100)}% to truncation"
        
        # Calculate spacing
        total_middle_right = len(middle) + len(right) + 3  # +3 for spacing
        spacing_left = self.term_width - len(left) - total_middle_right
        if spacing_left < 1:
            spacing_left = 1
        
        return f"{Colors.DIM}{left}{' ' * spacing_left}{middle}   {right}{Colors.RESET}"
    
    def _render_prompt(self, text: str = "", placeholder: bool = True) -> str:
        """Render input prompt"""
        if not text and placeholder:
            return f"> {Colors.DIM}Enter @ to mention files or / for commands{Colors.RESET}"
        elif text:
            return f"> {text}█"
        else:
            return f"> █"
    
    def _render_help_bar(self) -> str:
        """Render global help bar (bottom line)"""
        left = "Ctrl+C Exit · Ctrl+R Expand recent"
        right = f"Remaining requests: {self.requests_remaining}%"
        
        spacing = self.term_width - len(left) - len(right)
        if spacing < 1:
            spacing = 1
        
        return f"{Colors.DIM}{left}{' ' * spacing}{right}{Colors.RESET}"
    
    def _render_active_task(self) -> Optional[str]:
        """Render live status message for running task"""
        if not self.active_task:
            return None
        
        task_info = f"(Esc to cancel"
        if self.task_size:
            task_info += f" · {self.task_size}"
        task_info += ")"
        
        return f"{Colors.BRIGHT_MAGENTA}● {self.active_task} {Colors.DIM}{task_info}{Colors.RESET}"
    
    def render_diff_block(self, lines: List[Tuple[str, str, str]]):
        """
        Render code diff block
        
        Args:
            lines: List of (line_type, line_num, content) tuples
                   line_type: 'removed', 'added', 'context'
        """
        for line_type, line_num, content in lines:
            if line_type == 'removed':
                print(f"{Colors.RED}-{line_num:3} {content}{Colors.RESET}")
            elif line_type == 'added':
                print(f"{Colors.GREEN}+{line_num:3} {content}{Colors.RESET}")
            else:  # context
                print(f"{Colors.DIM} {line_num:3} {content}{Colors.RESET}")
    
    def render_full_screen(self, content_lines: List[str] = None, input_text: str = ""):
        """Render full Copilot CLI screen"""
        # Clear screen
        pass  # Don't clear terminal - preserve history
        
        # Upper header
        print(self._render_header())
        print(self._render_separator())
        print()
        
        # Content area
        if content_lines:
            for line in content_lines:
                print(line)
            print()
        
        # Active task status (if any)
        task_line = self._render_active_task()
        if task_line:
            print(task_line)
            print()
        
        # Lower status bar
        print(self._render_footer_status())
        print(self._render_separator())
        
        # Prompt
        print(self._render_prompt(input_text, placeholder=(not input_text)))
        
        # Global help bar
        print(self._render_help_bar())
    
    def start_task(self, task_description: str, size: Optional[str] = None):
        """Start a live task"""
        self.active_task = task_description
        self.task_size = size
    
    def stop_task(self):
        """Stop active task"""
        self.active_task = None
        self.task_size = None
    
    def update_context_usage(self, usage: float):
        """Update context window usage (0.0 - 1.0)"""
        self.context_usage = usage
    
    def update_requests_remaining(self, remaining: float):
        """Update remaining requests percentage"""
        self.requests_remaining = remaining


class CopilotCompleter(Completer):
    """Auto-completion for Copilot CLI"""

    COMMANDS = [
        ("/help", "Show all commands"),
        ("/model", "Change AI model"),
        ("/model list", "List available models"),
        ("/attach", "Attach file to context"),
        ("/files", "List attached files"),
        ("/clear", "Clear screen"),
        ("/exit", "Exit shell"),
        ("apply", "Apply pending actions"),
        ("reject", "Reject pending actions"),
    ]

    def __init__(self):
        self.files_cache = []
        self._update_files_cache()

    def _update_files_cache(self):
        """Update list of available files for @ mentions"""
        try:
            import subprocess
            result = subprocess.run(
                ["git", "ls-files"],
                capture_output=True,
                text=True,
                cwd=BASE_DIR
            )
            if result.returncode == 0:
                self.files_cache = result.stdout.strip().split('\n')
        except:
            self.files_cache = []

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor

        # File mentions with @
        if '@' in text:
            at_pos = text.rfind('@')
            file_prefix = text[at_pos + 1:]
            for file_path in self.files_cache:
                if file_path.startswith(file_prefix):
                    yield Completion(
                        file_path,
                        start_position=-len(file_prefix),
                        display=file_path,
                        display_meta="📄 File"
                    )
        # Slash commands
        elif text.startswith('/') or not text:
            for cmd, desc in self.COMMANDS:
                if cmd.startswith(text if text else '/'):
                    yield Completion(
                        cmd,
                        start_position=-len(text) if text else 0,
                        display=cmd,
                        display_meta=desc
                    )


def interactive_copilot_shell():
    """Run interactive Copilot-style shell"""
    # Load or create session
    s = load_session()
    if not s:
        print(f"{Colors.YELLOW}No active session. Starting new session...{Colors.RESET}")
        s = start_session(write=True)

    cli = CopilotCLI()

    # Setup prompt_toolkit if available
    session_prompt = None
    if PROMPT_TOOLKIT_AVAILABLE:
        try:
            history_file = BASE_DIR / ".copilot_cli_history"
            session_prompt = PromptSession(
                history=FileHistory(str(history_file)),
                completer=CopilotCompleter(),
                complete_while_typing=True,
                auto_suggest=AutoSuggestFromHistory(),
            )
        except:
            pass

    last_content = []

    while True:
        # Update terminal size (dynamic)
        cli.term_width, cli.term_height = shutil.get_terminal_size(fallback=(120, 40))

        # Render screen
        print()  # Spacing
        cli.render_full_screen(last_content)

        # Get input
        try:
            if session_prompt:
                user_input = session_prompt.prompt("")
            else:
                user_input = input("")

            user_input = user_input.strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{Colors.DIM}Exiting...{Colors.RESET}\n")
            break

        if not user_input:
            continue

        # Handle commands
        if user_input in ("/exit", "/quit", "exit", "quit"):
            break

        if user_input == "/clear":
            last_content = []
            continue

        if user_input in ("/help", "help"):
            last_content = [
                f"{Colors.BRIGHT_WHITE}Available Commands:{Colors.RESET}",
                "",
                f"  {Colors.CYAN}/help{Colors.RESET}              Show this help",
                f"  {Colors.CYAN}/model{Colors.RESET}             Show current model",
                f"  {Colors.CYAN}/model list{Colors.RESET}        List available models",
                f"  {Colors.CYAN}/attach <file>{Colors.RESET}     Attach file to context",
                f"  {Colors.CYAN}/files{Colors.RESET}             List attached files",
                f"  {Colors.CYAN}/clear{Colors.RESET}             Clear screen",
                f"  {Colors.CYAN}/exit{Colors.RESET}              Exit shell",
                "",
                f"  {Colors.CYAN}@<file>{Colors.RESET}            Mention a file (e.g., @src/main.py)",
                f"  {Colors.CYAN}apply{Colors.RESET}              Apply pending AI actions",
                f"  {Colors.CYAN}reject{Colors.RESET}             Reject pending AI actions",
                "",
                f"{Colors.DIM}Keyboard Shortcuts:{Colors.RESET}",
                f"  Ctrl+C              Exit",
                f"  Ctrl+R              Search history",
                f"  Tab                 Auto-complete",
                f"  ↑/↓                 Navigate history",
            ]
            continue

        # AI interaction
        cli.start_task("Processing your request", "")
        add_history(user_input)

        try:
            result = run_ai(user_input, s.get("files", {}), session=s)
            cli.stop_task()

            # Display response
            last_content = []
            last_content.append(f"{Colors.BRIGHT_MAGENTA}Assistant:{Colors.RESET}")
            last_content.append("")
            last_content.extend(result.message.split('\n'))

            # Show actions if any
            if result.actions:
                last_content.append("")
                last_content.append(f"{Colors.YELLOW}Pending Actions:{Colors.RESET}")
                for action in result.actions:
                    last_content.append(f"  {Colors.GREEN}►{Colors.RESET} {action.type.upper()} {action.path}")
                last_content.append("")
                last_content.append(f"{Colors.DIM}Type 'apply' to execute or 'reject' to cancel{Colors.RESET}")

                # Store in session
                s["pending_actions"] = [a.dict() for a in result.actions]
                from tools.session.manager import save_session
                save_session(s)

        except Exception as e:
            cli.stop_task()
            last_content = [
                f"{Colors.RED}Error:{Colors.RESET} {str(e)}"
            ]


def demo_copilot_cli():
    """Demonstrate full Copilot CLI"""
    cli = CopilotCLI()

    # Demo 1: Empty state
    print("\n=== DEMO 1: Empty State ===\n")
    cli.render_full_screen()
    input("\nPress Enter for next demo...")

    # Demo 2: Code diff display
    print("\n=== DEMO 2: Code Diff ===\n")
    diff_lines = [
        ('context', '192', '    pending = len(session.get(\'pending_actions\', []))'),
        ('context', '193', ''),
        ('removed', '161', '    print(f"\\n{Colors.CYAN}linkowiki session{Colors.RESET}")'),
        ('removed', '162', '    print("-" * 50)'),
        ('removed', '163', '    print(f"  model     {provider.id}")'),
        ('removed', '164', '    print(f"  mode      {mode}")'),
        ('removed', '165', '    print(f"  files     {files}")'),
        ('removed', '166', '    print(f"  pending   {pending}")'),
        ('removed', '167', '    print()'),
        ('context', '193', ''),
        ('added', '194', '    # Git branch'),
        ('added', '195', '    git_branch = get_git_branch()'),
        ('added', '196', ''),
        ('added', '197', '    # Build left side: ~/path[ branch*]'),
        ('added', '198', '    left = short_cwd'),
        ('added', '199', '    if git_branch:'),
        ('added', '200', '        left += f"[ {git_branch}]"'),
        ('added', '201', ''),
        ('added', '202', '    # Build right side: model-name (1x)'),
        ('added', '203', '    model_short = provider.id.replace("openai-", "").replace("anthropic-", "")'),
        ('added', '204', '    right = f"{model_short} (1x)"'),
    ]

    content = []
    for line_type, line_num, text in diff_lines:
        if line_type == 'removed':
            content.append(f"{Colors.RED}-{line_num:3} {text}{Colors.RESET}")
        elif line_type == 'added':
            content.append(f"{Colors.GREEN}+{line_num:3} {text}{Colors.RESET}")
        else:
            content.append(f"{Colors.DIM} {line_num:3} {text}{Colors.RESET}")

    cli.render_full_screen(content)
    input("\nPress Enter for next demo...")

    # Demo 3: Active task
    print("\n=== DEMO 3: Active Task ===\n")
    cli.start_task("Implementing Copilot-style CLI design", "13.0 KiB")
    cli.update_context_usage(0.13)
    cli.render_full_screen(content)
    input("\nPress Enter for next demo...")

    # Demo 4: With input
    print("\n=== DEMO 4: User Input ===\n")
    cli.stop_task()
    cli.render_full_screen(content, input_text="/help")
    input("\nPress Enter for next demo...")

    # Demo 5: High context usage
    print("\n=== DEMO 5: High Context Usage ===\n")
    cli.update_context_usage(0.87)
    cli.update_requests_remaining(23.5)
    cli.render_full_screen(content)
    input("\nPress Enter to finish...")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="LinkoWiki Copilot CLI")
    parser.add_argument("--demo", action="store_true", help="Run demo mode")
    args = parser.parse_args()

    if args.demo:
        demo_copilot_cli()
    else:
        interactive_copilot_shell()
