#!/usr/bin/env python3
"""
LinkoWiki Professional Session Shell
Rich-based TUI with auto-resize, live-updates, and professional styling
"""
import os
import sys
import signal
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

# Add project root to path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

# Rich imports for professional TUI
from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.layout import Layout
from rich.text import Text
from rich.style import Style
from rich import box
from rich.columns import Columns

# Prompt toolkit for advanced input
try:
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import Completer, Completion
    from prompt_toolkit.history import FileHistory
    from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
    from prompt_toolkit.formatted_text import HTML
    PROMPT_TOOLKIT_AVAILABLE = True
except ImportError:
    PROMPT_TOOLKIT_AVAILABLE = False

# Project imports
from tools.session.manager import load_session, start_session, add_history, save_session
from tools.ai.assistant import run_ai, Action


class ProfessionalCompleter(Completer):
    """Professional auto-completer for files and commands"""

    COMMANDS = [
        ("/help", "📚 Show all commands"),
        ("/model", "🤖 Show/change AI model"),
        ("/model list", "📋 List available models"),
        ("/attach", "📎 Attach file to context"),
        ("/files", "📁 List attached files"),
        ("/clear", "🧹 Clear conversation"),
        ("/exit", "🚪 Exit shell"),
        ("apply", "✅ Apply pending actions"),
        ("reject", "❌ Reject pending actions"),
    ]

    def __init__(self):
        self.files_cache: List[str] = []
        self._update_files_cache()

    def _update_files_cache(self):
        """Update git-tracked files cache"""
        try:
            result = subprocess.run(
                ["git", "ls-files"],
                capture_output=True,
                text=True,
                cwd=BASE_DIR,
                timeout=2
            )
            if result.returncode == 0:
                self.files_cache = [
                    f for f in result.stdout.strip().split('\n')
                    if f and not f.startswith('.')
                ]
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
                    # Determine file type emoji
                    if file_path.endswith('.py'):
                        emoji = '🐍'
                    elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
                        emoji = '💛'
                    elif file_path.endswith(('.md', '.txt')):
                        emoji = '📝'
                    elif file_path.endswith(('.json', '.yaml', '.yml')):
                        emoji = '⚙️'
                    else:
                        emoji = '📄'

                    yield Completion(
                        file_path,
                        start_position=-len(file_prefix),
                        display=file_path,
                        display_meta=f"{emoji} File"
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


class RichSessionShell:
    """Professional session shell with Rich TUI"""

    def __init__(self):
        self.console = Console()
        self.session = None
        self.conversation_history: List[Dict[str, Any]] = []
        self.is_processing = False
        self.current_task = None

        # Terminal info
        self.update_terminal_size()

        # Setup signal handlers
        signal.signal(signal.SIGWINCH, self._handle_resize)

    def _handle_resize(self, signum, frame):
        """Handle terminal resize - Rich handles this automatically"""
        self.update_terminal_size()

    def update_terminal_size(self):
        """Update terminal dimensions"""
        size = self.console.size
        self.term_width = size.width
        self.term_height = size.height

    def _get_git_info(self) -> Dict[str, str]:
        """Get git branch and status"""
        try:
            # Get branch
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                cwd=BASE_DIR
            )
            branch = result.stdout.strip() if result.returncode == 0 else ""

            # Check if dirty
            if branch:
                status = subprocess.run(
                    ["git", "status", "--porcelain"],
                    capture_output=True,
                    text=True,
                    cwd=BASE_DIR
                )
                is_dirty = bool(status.stdout.strip())
                branch = f"{branch}*" if is_dirty else branch

            return {"branch": branch}
        except:
            return {"branch": ""}

    def _create_header_panel(self) -> Panel:
        """Create professional header panel"""
        git_info = self._get_git_info()

        # Get session info
        provider_id = "unknown"
        mode = "Unknown"
        if self.session:
            from tools.ai.providers import get_provider_registry
            registry = get_provider_registry()
            provider = registry.get_provider(self.session.get("active_provider_id"))
            provider_id = provider.id.replace("openai-", "").replace("anthropic-", "")
            mode = "Write" if self.session.get("write") else "Read-only"

        # Create header table
        table = Table.grid(padding=(0, 2))
        table.add_column(style="bold cyan", justify="left")
        table.add_column(style="dim", justify="right")

        # Path and git
        cwd = os.getcwd()
        home = os.path.expanduser("~")
        short_cwd = "~" + cwd[len(home):] if cwd.startswith(home) else cwd

        left = f"[bold]LinkoWiki Code[/bold] [dim]Session[/dim]"
        right = f"[dim]{provider_id} (1x)[/dim]"
        table.add_row(left, right)

        if git_info["branch"]:
            path_text = f"{short_cwd} [{git_info['branch']}]"
        else:
            path_text = short_cwd

        table.add_row(
            f"[dim]Path:[/dim] {path_text}",
            f"[dim]Mode:[/dim] {mode}"
        )

        return Panel(
            table,
            border_style="cyan",
            box=box.ROUNDED,
            title="[bold]🧠 LinkoWiki[/bold]",
            title_align="left"
        )

    def _create_status_footer(self) -> Panel:
        """Create status footer panel"""
        # Calculate context usage (placeholder for now)
        context_usage = 0.13
        requests_remaining = 98.2

        # Create status table
        table = Table.grid(padding=(0, 2))
        table.add_column(style="dim", justify="left")
        table.add_column(style="dim", justify="center")
        table.add_column(style="dim", justify="right")

        # Left: Shortcuts
        left = "[dim]Ctrl+C[/dim] Exit · [dim]Ctrl+R[/dim] History · [dim]/help[/dim] Commands"

        # Middle: Context usage
        middle = f"Context: [yellow]{int(context_usage * 100)}%[/yellow] to truncation"

        # Right: Requests remaining
        right = f"Remaining: [green]{requests_remaining}%[/green]"

        table.add_row(left, middle, right)

        return Panel(
            table,
            border_style="dim",
            box=box.SIMPLE,
            padding=(0, 1)
        )

    def _create_conversation_panel(self) -> Optional[Panel]:
        """Create conversation history panel"""
        if not self.conversation_history:
            return None

        # Create conversation display
        conversation_parts = []

        for turn in self.conversation_history[-5:]:  # Last 5 turns
            role = turn.get("role", "user")
            content = turn.get("content", "")

            if role == "user":
                text = Text()
                text.append("→ ", style="bold cyan")
                text.append(content, style="white")
                conversation_parts.append(text)
            else:  # assistant
                # Render as markdown if it looks like markdown
                if "```" in content or "#" in content:
                    conversation_parts.append(Markdown(content))
                else:
                    text = Text()
                    text.append("← ", style="bold magenta")
                    text.append(content, style="white")
                    conversation_parts.append(text)

            # Add spacing
            conversation_parts.append(Text(""))

        group = Group(*conversation_parts)

        return Panel(
            group,
            border_style="dim",
            box=box.SIMPLE,
            padding=(1, 2)
        )

    def _create_help_text(self) -> Table:
        """Create help commands table"""
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column(style="cyan", width=20)
        table.add_column(style="dim")

        commands = [
            ("/help", "Show all commands"),
            ("/model", "Show/change AI model"),
            ("/attach <file>", "Attach file to context"),
            ("/files", "List attached files"),
            ("/clear", "Clear conversation"),
            ("/exit", "Exit shell"),
            ("@<file>", "Mention a file in your question"),
        ]

        for cmd, desc in commands:
            table.add_row(cmd, desc)

        return table

    def _create_input_prompt(self):
        """Create input prompt text for prompt_toolkit"""
        # Use prompt_toolkit's HTML for colored prompt
        if PROMPT_TOOLKIT_AVAILABLE:
            return HTML('<ansi-cyan><b>❯</b></ansi-cyan> ')
        else:
            return "❯ "

    def show_help(self):
        """Display help in conversation"""
        help_panel = Panel(
            self._create_help_text(),
            title="[bold]Available Commands[/bold]",
            border_style="cyan",
            box=box.ROUNDED
        )

        self.console.print(help_panel)
        self.console.print()

    def show_model_info(self):
        """Display model information"""
        if not self.session:
            self.console.print("[red]No active session[/red]")
            return

        from tools.ai.providers import get_provider_registry
        registry = get_provider_registry()
        provider = registry.get_provider(self.session.get("active_provider_id"))

        table = Table(show_header=False, box=box.SIMPLE)
        table.add_column(style="dim", width=15)
        table.add_column(style="white")

        table.add_row("Model:", provider.id)
        table.add_row("Provider:", provider.provider)
        table.add_row("Type:", "Reasoning" if provider.reasoning else "Text")
        if provider.description:
            table.add_row("Description:", provider.description)

        panel = Panel(
            table,
            title="[bold]Current Model[/bold]",
            border_style="cyan",
            box=box.ROUNDED
        )

        self.console.print(panel)
        self.console.print()

    def process_ai_request(self, user_input: str):
        """Process AI request with live updates"""
        self.is_processing = True

        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })

        # Show processing indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold magenta]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task("Processing your request...", total=None)

            try:
                # Add to session history
                add_history(user_input)

                # Call AI
                result = run_ai(user_input, self.session.get("files", {}), session=self.session)

                # Add assistant response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": result.message
                })

                # Display response
                self.console.print()
                if "```" in result.message or "#" in result.message:
                    # Render as markdown
                    self.console.print(Panel(
                        Markdown(result.message),
                        border_style="magenta",
                        box=box.ROUNDED,
                        title="[bold]Assistant[/bold]",
                        title_align="left"
                    ))
                else:
                    self.console.print(f"[bold magenta]←[/bold magenta] {result.message}")

                self.console.print()

                # Show actions if any
                if result.actions:
                    self._display_actions(result.actions)
                    self.session["pending_actions"] = [a.dict() for a in result.actions]
                    save_session(self.session)

            except Exception as e:
                self.console.print(f"[red]Error:[/red] {str(e)}")
                import traceback
                self.console.print(f"[dim]{traceback.format_exc()}[/dim]")

            finally:
                self.is_processing = False

    def _display_actions(self, actions: List[Action]):
        """Display pending actions beautifully"""
        table = Table(show_header=True, box=box.SIMPLE_HEAD)
        table.add_column("Type", style="yellow")
        table.add_column("Path", style="cyan")
        table.add_column("Description", style="dim")

        for action in actions:
            table.add_row(
                action.type.upper(),
                str(action.path),
                action.description or ""
            )

        panel = Panel(
            table,
            title="[bold yellow]Pending Actions[/bold yellow]",
            border_style="yellow",
            box=box.ROUNDED,
            subtitle="[dim]Type 'apply' to execute or 'reject' to cancel[/dim]"
        )

        self.console.print(panel)
        self.console.print()

    def run(self):
        """Run the interactive shell"""
        # Load or create session
        self.session = load_session()
        if not self.session:
            self.console.print("[yellow]No active session. Starting new session...[/yellow]")
            self.session = start_session(write=True)

        # Setup prompt_toolkit if available
        session_prompt = None
        if PROMPT_TOOLKIT_AVAILABLE:
            history_file = BASE_DIR / ".rich_session_history"
            session_prompt = PromptSession(
                history=FileHistory(str(history_file)),
                completer=ProfessionalCompleter(),
                complete_while_typing=True,
                auto_suggest=AutoSuggestFromHistory(),
            )

        # Show welcome
        self.console.print(self._create_header_panel())
        self.console.print()
        self.console.print("[dim]Type /help for commands, @file to mention files, / for slash commands[/dim]")
        self.console.print()

        # Main loop
        while True:
            try:
                # Show conversation if any
                conv_panel = self._create_conversation_panel()
                if conv_panel:
                    self.console.print(conv_panel)

                # Show footer
                self.console.print(self._create_status_footer())

                # Get input
                self.console.print()
                if session_prompt:
                    user_input = session_prompt.prompt(
                        self._create_input_prompt(),
                        enable_suspend=True
                    ).strip()
                else:
                    self.console.print(self._create_input_prompt(), end="")
                    user_input = input().strip()

                if not user_input:
                    continue

                # Handle commands
                if user_input in ("/exit", "/quit", "exit", "quit"):
                    self.console.print("[dim]Goodbye! 👋[/dim]")
                    break

                if user_input in ("/clear", "/cls"):
                    self.conversation_history = []
                    self.console.clear()
                    self.console.print(self._create_header_panel())
                    self.console.print()
                    continue

                if user_input in ("/help", "help"):
                    self.show_help()
                    continue

                if user_input == "/model":
                    self.show_model_info()
                    continue

                # AI request
                self.process_ai_request(user_input)

            except (EOFError, KeyboardInterrupt):
                self.console.print("\n[dim]Goodbye! 👋[/dim]")
                break
            except Exception as e:
                self.console.print(f"[red]Error:[/red] {str(e)}")


def main():
    """Main entry point"""
    shell = RichSessionShell()
    shell.run()


if __name__ == "__main__":
    main()
