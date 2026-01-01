#!/usr/bin/env python3
"""
LinkoWiki Professional Session Shell
Rich-based TUI with auto-resize, live-updates, and professional styling
"""
import os
import sys
import signal
import subprocess
import re
import glob as glob_module
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from difflib import get_close_matches

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
from rich.rule import Rule

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
from tools.ai.assistant import run_ai, run_ai_streaming, Action
from tools.memory.context import ContextMemory


class ProfessionalCompleter(Completer):
    """Professional auto-completer for files and commands"""

    COMMANDS = [
        ("/help", "📚 Show all commands"),
        ("/model", "🤖 Show/change AI model"),
        ("/model list", "📋 List available models"),
        ("/attach", "📎 Attach file to context"),
        ("/files", "📁 List attached files"),
        ("/clear", "🧹 Clear conversation"),
        ("/search", "🔍 Search conversation history"),
        ("/autoexec", "⚡ Toggle auto-execute mode"),
        ("/retry", "🔄 Retry last request"),
        ("/exit", "🚪 Exit shell"),
        ("/stream on", "🌊 Enable streaming output"),
        ("/stream off", "⏸️  Disable streaming output"),
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

    def get_file_icon(self, file_path: str) -> str:
        """Get emoji icon for file type"""
        if file_path.endswith('.py'):
            return '🐍'
        elif file_path.endswith(('.js', '.ts', '.jsx', '.tsx')):
            return '💛'
        elif file_path.endswith(('.md', '.txt')):
            return '📝'
        elif file_path.endswith(('.json', '.yaml', '.yml')):
            return '⚙️'
        else:
            return '📄'

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor

        # File mentions with @
        if '@' in text:
            at_pos = text.rfind('@')
            file_prefix = text[at_pos + 1:]

            for file_path in self.files_cache:
                if file_path.startswith(file_prefix):
                    emoji = self.get_file_icon(file_path)
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
        self.attached_files: Dict[str, str] = {}  # filename -> content
        self.streaming_enabled = False  # Disable streaming by default due to structured output requirements
        self.last_displayed_turn = -1  # Track which turn was last displayed to avoid duplicates
        self.autoexec_enabled = False  # Auto-execute actions without confirmation
        self.memory = ContextMemory()  # Contextual memory system

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

    def _read_file(self, filepath: str) -> Optional[str]:
        """Read file content from disk"""
        try:
            file_path = BASE_DIR / filepath
            if file_path.exists() and file_path.is_file():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception as e:
            self.console.print(f"[red]Error reading file {filepath}: {str(e)}[/red]")
        return None

    def _find_files_fuzzy(self, pattern: str) -> List[str]:
        """Find files using fuzzy matching, glob patterns, or directory listing"""
        # Check if it's a glob pattern
        if '*' in pattern or '?' in pattern:
            matches = glob_module.glob(str(BASE_DIR / pattern), recursive=True)
            return [str(Path(m).relative_to(BASE_DIR)) for m in matches if Path(m).is_file()]
        
        # Check if it's a directory
        dir_path = BASE_DIR / pattern
        if dir_path.exists() and dir_path.is_dir():
            files = []
            for file_path in dir_path.rglob('*'):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    files.append(str(file_path.relative_to(BASE_DIR)))
            return files
        
        # Try exact match first
        file_path = BASE_DIR / pattern
        if file_path.exists() and file_path.is_file():
            return [pattern]
        
        # Fuzzy matching - search for files with similar names
        try:
            result = subprocess.run(
                ["git", "ls-files"],
                capture_output=True,
                text=True,
                cwd=BASE_DIR,
                timeout=2
            )
            if result.returncode == 0:
                all_files = result.stdout.strip().split('\n')
                # Find files that contain the pattern or are close matches
                matches = []
                pattern_lower = pattern.lower()
                for f in all_files:
                    if pattern_lower in f.lower():
                        matches.append(f)
                
                # If we found matches, return them
                if matches:
                    return matches[:5]  # Limit to 5 fuzzy matches
                
                # Try get_close_matches as fallback
                close = get_close_matches(pattern, all_files, n=3, cutoff=0.6)
                return close
        except:
            pass
        
        return []

    def _detect_auto_files(self, text: str) -> List[str]:
        """Automatically detect files mentioned in text without @ prefix"""
        files = []
        
        # Common file patterns
        file_patterns = [
            r'\b([\w\-/]+\.(?:py|js|ts|jsx|tsx|md|txt|json|yaml|yml|toml|ini|cfg|sh))\b',
            r'\b(README\.md|pyproject\.toml|package\.json|Dockerfile|Makefile)\b',
        ]
        
        for pattern in file_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Check if file exists
                if (BASE_DIR / match).exists():
                    files.append(match)
        
        return files

    def _extract_and_load_files(self, text: str) -> Tuple[str, Dict[str, str]]:
        """Extract @file mentions and load their content automatically with fuzzy matching"""
        # Find all @file mentions
        file_pattern = r'@([^\s]+)'
        matches = re.findall(file_pattern, text)
        
        loaded_files = {}
        
        # Process @mentions
        for filepath in matches:
            if filepath not in self.attached_files:
                # Try fuzzy/glob/directory matching
                found_files = self._find_files_fuzzy(filepath)
                
                if not found_files:
                    self.console.print(f"[yellow]⚠ Could not find: {filepath}[/yellow]")
                    continue
                
                # If multiple files found, show them
                if len(found_files) > 1:
                    self.console.print(f"[dim]📎 Found {len(found_files)} matches for '{filepath}':[/dim]")
                    for f in found_files[:10]:  # Show max 10
                        self.console.print(f"[dim]   - {f}[/dim]")
                
                # Load all found files
                for f in found_files:
                    if f not in self.attached_files:
                        content = self._read_file(f)
                        if content:
                            loaded_files[f] = content
                            self.attached_files[f] = content
                            self.console.print(f"[dim]📎 Loaded: {f}[/dim]")
        
        # Auto-detect files mentioned without @
        if "dokumentiere" in text.lower() or "erstelle wiki" in text.lower():
            auto_files = self._detect_auto_files(text)
            for f in auto_files:
                if f not in self.attached_files:
                    content = self._read_file(f)
                    if content:
                        loaded_files[f] = content
                        self.attached_files[f] = content
                        self.console.print(f"[dim]📎 Auto-loaded: {f}[/dim]")
        
        # Context-aware loading for project documentation requests
        if any(keyword in text.lower() for keyword in ["projekt", "project", "wiki für dieses", "dokumentiere das"]):
            context_files = ["README.md", "pyproject.toml", "package.json", "requirements.txt"]
            for f in context_files:
                if (BASE_DIR / f).exists() and f not in self.attached_files:
                    content = self._read_file(f)
                    if content:
                        loaded_files[f] = content
                        self.attached_files[f] = content
                        self.console.print(f"[dim]📎 Context-loaded: {f}[/dim]")
        
        return text, loaded_files

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

        # Add autoexec badge if enabled
        badges = []
        if self.autoexec_enabled:
            badges.append("[bold yellow]⚡AUTOEXEC[/bold yellow]")
        
        left = f"[bold]LinkoWiki Code[/bold] [dim]Session[/dim]"
        right_parts = [f"[dim]{provider_id} (1x)[/dim]"]
        if badges:
            right_parts.extend(badges)
        right = " ".join(right_parts)
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

    def _create_status_footer(self) -> Group:
        """Create status footer with proper separator line"""
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

        # Use Rule for proper separator line (not text-based)
        return Group(
            Rule(style="dim"),
            table
        )

    def _create_conversation_panel(self) -> Optional[Panel]:
        """Create conversation history panel"""
        if not self.conversation_history:
            return None

        # Create conversation display
        conversation_parts = []

        # Show last 5 turns, but exclude the last one if it was just displayed
        history_to_show = self.conversation_history[-5:]
        
        # If the last turn was just displayed (tracked by last_displayed_turn),
        # don't show it again in the panel
        if self.last_displayed_turn == len(self.conversation_history) - 1:
            history_to_show = self.conversation_history[-6:-1] if len(self.conversation_history) > 5 else self.conversation_history[:-1]

        for turn in history_to_show:
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

        if not conversation_parts:
            return None

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
            ("/attach <file>", "Manually attach file to context"),
            ("/files", "List attached files"),
            ("/clear", "Clear conversation"),
            ("/search <text>", "Search conversation history"),
            ("/autoexec [on|off]", "Toggle auto-execute mode (no confirmation needed)"),
            ("/retry", "Retry last AI request"),
            ("/stream on/off", "Enable/disable streaming output"),
            ("/exit", "Exit shell"),
            ("@<file>", "Auto-load file (e.g., @src/main.py)"),
            ("@*.py", "Load files with glob pattern (e.g., @src/*.py)"),
            ("@examples/", "Load all files in directory"),
            ("apply", "Apply pending actions"),
            ("reject", "Reject pending actions"),
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

    def process_ai_request(self, user_input: str, is_retry: bool = False):
        """Process AI request with live updates and automatic file loading"""
        self.is_processing = True

        # Store for retry capability
        if not is_retry:
            self.last_user_input = user_input
            self.last_files = self.attached_files.copy()

        # Check for repeated patterns in memory
        pattern_hint = self.memory.detect_repeated_pattern(user_input)
        if pattern_hint:
            self.console.print(f"[dim]💡 {pattern_hint}[/dim]")

        # Extract and load files automatically
        processed_input, loaded_files = self._extract_and_load_files(user_input)

        # Add user message to history
        if not is_retry:
            self.conversation_history.append({
                "role": "user",
                "content": user_input
            })

        try:
            # Add to session history
            if not is_retry:
                add_history(user_input)

            # Merge loaded files with session files
            all_files = {**self.session.get("files", {}), **self.attached_files}

            if self.streaming_enabled:
                # Streaming mode
                self._process_ai_streaming(processed_input, all_files)
            else:
                # Non-streaming mode
                self._process_ai_standard(processed_input, all_files)

        except FileNotFoundError as e:
            self._handle_file_not_found_error(str(e))
        except PermissionError as e:
            self.console.print(f"[red]❌ Permission denied:[/red] {str(e)}")
            self.console.print("[dim]Check file permissions and try again[/dim]")
        except ConnectionError as e:
            self._handle_connection_error(str(e))
        except Exception as e:
            error_msg = str(e)
            if "api" in error_msg.lower() and "key" in error_msg.lower():
                self._handle_api_key_error()
            elif "rate" in error_msg.lower() and "limit" in error_msg.lower():
                self._handle_rate_limit_error()
            else:
                self.console.print(f"[red]❌ Error:[/red] {error_msg}")
                self.console.print("[dim]Use /retry to try again[/dim]")

        finally:
            self.is_processing = False

    def _handle_file_not_found_error(self, error_msg: str):
        """Handle file not found errors with suggestions"""
        self.console.print(f"[red]❌ File not found[/red]")
        
        # Try to extract filename from error
        import re
        match = re.search(r"['\"](.*?)['\"]", error_msg)
        if match:
            filename = match.group(1)
            # Find similar files
            try:
                result = subprocess.run(
                    ["git", "ls-files"],
                    capture_output=True,
                    text=True,
                    cwd=BASE_DIR,
                    timeout=2
                )
                if result.returncode == 0:
                    all_files = result.stdout.strip().split('\n')
                    similar = get_close_matches(filename, all_files, n=5, cutoff=0.5)
                    if similar:
                        self.console.print("\n[yellow]💡 Did you mean one of these?[/yellow]")
                        for f in similar:
                            self.console.print(f"   [cyan]@{f}[/cyan]")
            except:
                pass

    def _handle_connection_error(self, error_msg: str):
        """Handle connection errors with retry option"""
        self.console.print(f"[red]❌ Connection error:[/red] Network unavailable")
        self.console.print("[yellow]💡 Options:[/yellow]")
        self.console.print("   1. Check your internet connection")
        self.console.print("   2. Use [cyan]/retry[/cyan] to try again")
        self.console.print("   3. Wait a moment and try again")

    def _handle_api_key_error(self):
        """Handle missing or invalid API key errors"""
        self.console.print(f"[red]❌ API Key Error[/red]")
        self.console.print("\n[yellow]💡 How to fix:[/yellow]")
        self.console.print("   1. Set your API key in environment variables:")
        self.console.print("      [cyan]export OPENAI_API_KEY='your-key'[/cyan]")
        self.console.print("      [cyan]export ANTHROPIC_API_KEY='your-key'[/cyan]")
        self.console.print("   2. Or create a .env file with your keys")
        self.console.print("   3. Restart the CLI after setting keys")

    def _handle_rate_limit_error(self):
        """Handle rate limit errors"""
        self.console.print(f"[red]❌ Rate Limit Exceeded[/red]")
        self.console.print("\n[yellow]💡 What to do:[/yellow]")
        self.console.print("   1. Wait a few minutes before trying again")
        self.console.print("   2. Use [cyan]/retry[/cyan] after waiting")
        self.console.print("   3. Consider upgrading your API plan")
        self.console.print("\n[dim]Typical wait time: 1-5 minutes[/dim]")

    def _process_ai_standard(self, user_input: str, all_files: Dict[str, str]):
        """Process AI request without streaming"""
        # Show processing indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold magenta]{task.description}"),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task("Processing your request...", total=None)

            # Call AI
            result = run_ai(user_input, all_files, session=self.session)

            # Add assistant response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": result.message
            })
            
            # Track that this turn was just displayed
            self.last_displayed_turn = len(self.conversation_history) - 1

            # Display response with proper formatting
            self.console.print()
            self._display_ai_response(result.message)
            self.console.print()
            
            # Display options if any
            if result.options:
                self._display_options(result.options)

            # Show actions if any
            if result.actions:
                self._display_actions(result.actions)
                
                # Remember actions in memory
                for action in result.actions:
                    self.memory.remember_action(action.dict(), user_input)
                
                self.session["pending_actions"] = [a.dict() for a in result.actions]
                save_session(self.session)
                
                # Auto-execute if enabled (but skip DELETE actions)
                if self.autoexec_enabled:
                    # Check if any actions are DELETE
                    has_delete = any(a.type.upper() == "DELETE" for a in result.actions)
                    
                    if has_delete:
                        self.console.print("\n[yellow]⚠ DELETE action detected - confirmation required even in autoexec mode[/yellow]")
                    else:
                        self.console.print("\n[bold yellow]⚡ AUTOEXEC:[/bold yellow] Executing actions automatically...")
                        self._execute_pending_actions()
                        
                        # Show proactive suggestions after auto-execution
                        self._show_proactive_suggestions(result.actions, user_input)
            else:
                # Show suggestions even without actions
                self._show_proactive_suggestions([], user_input)

    def _process_ai_streaming(self, user_input: str, all_files: Dict[str, str]):
        """Process AI request with streaming output
        
        Note: Streaming with structured output (AIResult with options) is complex.
        This attempts streaming but falls back to standard mode on any issues.
        """
        # Due to complexity of streaming structured output, 
        # use standard mode which properly handles AIResult with options
        self.console.print("[dim]Note: Using standard mode for structured output support[/dim]")
        self._process_ai_standard(user_input, all_files)

    def _display_ai_response(self, message: str):
        """Display AI response with proper markdown and syntax highlighting"""
        if "```" in message or "#" in message:
            # Render as markdown with syntax highlighting
            self.console.print(Panel(
                Markdown(message),
                border_style="magenta",
                box=box.ROUNDED,
                title="[bold]Assistant[/bold]",
                title_align="left"
            ))
        else:
            # Simple text response
            self.console.print(f"[bold magenta]←[/bold magenta] {message}")

    def _display_options(self, options: List):
        """Display interactive options from AIResult"""
        if not options:
            return
        
        table = Table(show_header=True, box=box.SIMPLE_HEAD)
        table.add_column("#", style="cyan", width=4)
        table.add_column("Option", style="white", width=40)
        table.add_column("Description", style="dim")
        
        for idx, option in enumerate(options, 1):
            # Access Pydantic model fields directly
            label = option.label
            description = option.description if option.description else ""
            table.add_row(str(idx), label, description)
        
        panel = Panel(
            table,
            title="[bold cyan]Available Options[/bold cyan]",
            border_style="cyan",
            box=box.ROUNDED,
            subtitle="[dim]Choose an option or continue with your own question[/dim]"
        )
        
        self.console.print(panel)
        self.console.print()

    def _display_actions(self, actions: List[Action]):
        """Display pending actions with better diff visualization"""
        table = Table(show_header=True, box=box.SIMPLE_HEAD)
        table.add_column("Type", style="yellow", width=8)
        table.add_column("Path", style="cyan", width=40)
        table.add_column("Preview", style="dim")

        for action in actions:
            action_type = action.type.upper()
            # Color-code action types
            if action_type == "WRITE":
                type_styled = f"[green]{action_type}[/green]"
            elif action_type == "EDIT":
                type_styled = f"[yellow]{action_type}[/yellow]"
            elif action_type == "DELETE":
                type_styled = f"[red]{action_type}[/red]"
            else:
                type_styled = action_type
            
            # Show content preview if available
            preview = ""
            if action.content:
                # First 50 chars of content as preview
                preview = action.content[:50].replace("\n", " ")
                if len(action.content) > 50:
                    preview += "..."
            
            table.add_row(
                type_styled,
                str(action.path),
                preview
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
        
        # Show preview of content for edits/writes
        for action in actions[:3]:  # Show max 3 previews
            if action.content and action.type in ("write", "edit"):
                self._show_action_preview(action)

    def _show_action_preview(self, action: Action):
        """Show preview of action content"""
        content = action.content
        if len(content) > 500:
            content = content[:500] + "\n... (truncated)"
        
        # Detect language for syntax highlighting
        lang = "text"
        if action.path.endswith('.py'):
            lang = "python"
        elif action.path.endswith(('.js', '.ts')):
            lang = "javascript"
        elif action.path.endswith('.json'):
            lang = "json"
        elif action.path.endswith(('.yaml', '.yml')):
            lang = "yaml"
        
        syntax = Syntax(content, lang, theme="monokai", line_numbers=True)
        
        panel = Panel(
            syntax,
            title=f"[dim]Preview: {action.path}[/dim]",
            border_style="dim",
            box=box.MINIMAL
        )
        self.console.print(panel)

    def _execute_pending_actions(self):
        """Execute pending actions from session"""
        if not self.session.get("pending_actions"):
            self.console.print("[dim]No pending actions to execute[/dim]")
            return
        
        actions = self.session["pending_actions"]
        self.console.print(f"\n[bold green]Executing {len(actions)} action(s)...[/bold green]")
        
        for action_dict in actions:
            action_type = action_dict.get("type", "").upper()
            path = action_dict.get("path", "")
            content = action_dict.get("content", "")
            
            file_path = WIKI_ROOT / path if not path.startswith('/') else Path(path)
            
            try:
                if action_type == "WRITE":
                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    file_path.write_text(content, encoding='utf-8')
                    self.console.print(f"[green]✓[/green] Written: {path}")
                    
                elif action_type == "EDIT":
                    if file_path.exists():
                        file_path.write_text(content, encoding='utf-8')
                        self.console.print(f"[green]✓[/green] Edited: {path}")
                    else:
                        self.console.print(f"[yellow]⚠[/yellow] File not found, creating: {path}")
                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        file_path.write_text(content, encoding='utf-8')
                        
                elif action_type == "DELETE":
                    if file_path.exists():
                        file_path.unlink()
                        self.console.print(f"[green]✓[/green] Deleted: {path}")
                    else:
                        self.console.print(f"[dim]File already deleted: {path}[/dim]")
                        
            except Exception as e:
                self.console.print(f"[red]✗[/red] Failed to {action_type.lower()} {path}: {str(e)}")
        
        # Clear pending actions
        self.session["pending_actions"] = []
        save_session(self.session)
        self.console.print("\n[bold green]✓ All actions completed[/bold green]")

    def _show_proactive_suggestions(self, actions: List[Action], prompt: str):
        """Generate and display proactive suggestions based on context"""
        suggestions = []
        
        # Check wiki structure for suggestions
        try:
            from tools.ai.tools.wiki_tools import get_wiki_structure, WIKI_ROOT
            
            # After wiki creation - suggest related topics
            if actions and any(a.type.upper() == "WRITE" for a in actions):
                created_paths = [a.path for a in actions if a.type.upper() == "WRITE"]
                
                # Extract topics and categories
                for path in created_paths:
                    parts = path.split('/')
                    if len(parts) > 1:
                        category = parts[0]
                        
                        # Suggest related topics based on category
                        related_topics = {
                            'docker': ['kubernetes', 'docker-compose', 'containerization'],
                            'kubernetes': ['helm', 'kubectl', 'k8s-networking'],
                            'python': ['pip', 'virtualenv', 'pytest'],
                            'linux': ['bash', 'systemd', 'networking'],
                            'git': ['github', 'gitlab', 'git-workflow']
                        }
                        
                        if category in related_topics:
                            for topic in related_topics[category]:
                                topic_path = f"{category}/{topic}"
                                if not (WIKI_ROOT / topic_path).exists():
                                    suggestions.append({
                                        'label': f"Erstelle '{topic}' Wiki-Eintrag",
                                        'description': f"Verwandtes Thema zu {category}",
                                        'type': 'related_topic'
                                    })
                                    if len(suggestions) >= 2:
                                        break
            
            # Check if wiki is empty
            wiki_structure = get_wiki_structure()
            if wiki_structure['total_entries'] == 0:
                suggestions.append({
                    'label': 'Wiki-Struktur vorschlagen',
                    'description': 'Ich kann eine Grundstruktur mit häufigen Kategorien erstellen',
                    'type': 'structure'
                })
            
            # Check for missing cross-references
            if actions:
                for action in actions:
                    if action.content and action.type.upper() in ["WRITE", "EDIT"]:
                        # Find mentions of other topics
                        content_lower = action.content.lower()
                        potential_topics = ['docker', 'kubernetes', 'python', 'linux', 'git', 'aws', 'azure']
                        
                        for topic in potential_topics:
                            if topic in content_lower and topic not in action.path:
                                topic_exists = (WIKI_ROOT / topic).exists() or any(
                                    topic in str(p) for p in WIKI_ROOT.rglob('*') if p.is_file()
                                )
                                if not topic_exists:
                                    suggestions.append({
                                        'label': f"Erstelle '{topic}' Eintrag",
                                        'description': f"Wird in {action.path} erwähnt",
                                        'type': 'cross_reference'
                                    })
                                    break  # Only suggest one cross-reference
        
        except Exception:
            pass  # Fail silently - suggestions are optional
        
        # Display suggestions if any
        if suggestions:
            self.console.print("\n[bold cyan]💡 Vorschläge:[/bold cyan]")
            
            table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
            table.add_column(style="yellow", width=6)
            table.add_column(style="white")
            table.add_column(style="dim")
            
            for idx, suggestion in enumerate(suggestions[:3], 1):  # Max 3 suggestions
                table.add_row(
                    f"[{idx}]",
                    suggestion['label'],
                    suggestion.get('description', '')
                )
            
            table.add_row("[0]", "Überspringen", "")
            
            self.console.print(table)
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
                multiline=False,  # Single line input
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

                # Show footer with proper separator
                self.console.print(self._create_status_footer())
                
                # Input section with separators
                self.console.print()
                
                # Top separator before input
                self.console.print(Rule(style="dim cyan"))
                
                # Get input
                if session_prompt:
                    user_input = session_prompt.prompt(
                        HTML('<ansi-cyan><b>❯</b></ansi-cyan> '),
                        enable_suspend=True
                    ).strip()
                else:
                    self.console.print("[cyan]❯[/cyan] ", end="")
                    user_input = input().strip()
                
                # Bottom separator after input
                self.console.print(Rule(style="dim cyan"))
                self.console.print()

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
                
                if user_input == "/files":
                    self.show_attached_files()
                    continue
                
                if user_input.startswith("/attach "):
                    filepath = user_input[8:].strip()
                    self.attach_file(filepath)
                    continue
                
                if user_input.startswith("/stream "):
                    arg = user_input[8:].strip().lower()
                    if arg == "on":
                        self.streaming_enabled = True
                        self.console.print("[green]✓[/green] Streaming enabled")
                    elif arg == "off":
                        self.streaming_enabled = False
                        self.console.print("[green]✓[/green] Streaming disabled")
                    else:
                        self.console.print("[red]Usage: /stream on|off[/red]")
                    continue
                
                if user_input.startswith("/search "):
                    query = user_input[8:].strip()
                    self.search_conversation(query)
                    continue
                
                # /autoexec command
                if user_input.startswith("/autoexec"):
                    arg = user_input[9:].strip().lower()
                    if arg == "on":
                        self.autoexec_enabled = True
                        self.console.print("[green]✓[/green] [bold yellow]⚡ AUTOEXEC enabled[/bold yellow] - Actions will execute automatically")
                        self.console.print("[dim]Note: DELETE actions will still require confirmation[/dim]")
                    elif arg == "off":
                        self.autoexec_enabled = False
                        self.console.print("[green]✓[/green] AUTOEXEC disabled - Manual confirmation required")
                    elif arg == "":
                        status = "[bold yellow]ON[/bold yellow]" if self.autoexec_enabled else "[dim]OFF[/dim]"
                        self.console.print(f"[cyan]AUTOEXEC status:[/cyan] {status}")
                    else:
                        self.console.print("[red]Usage: /autoexec [on|off][/red]")
                    continue
                
                # /retry command
                if user_input == "/retry":
                    if hasattr(self, 'last_user_input') and self.last_user_input:
                        self.console.print("[cyan]🔄 Retrying last request...[/cyan]")
                        # Restore previous file state
                        if hasattr(self, 'last_files'):
                            self.attached_files = self.last_files.copy()
                        self.process_ai_request(self.last_user_input, is_retry=True)
                    else:
                        self.console.print("[dim]No previous request to retry[/dim]")
                    continue
                
                # apply/reject commands
                if user_input == "apply":
                    self._execute_pending_actions()
                    continue
                
                if user_input == "reject":
                    if self.session.get("pending_actions"):
                        self.session["pending_actions"] = []
                        save_session(self.session)
                        self.console.print("[yellow]✓[/yellow] Pending actions rejected")
                    else:
                        self.console.print("[dim]No pending actions to reject[/dim]")
                    continue

                # AI request
                self.process_ai_request(user_input)

            except (EOFError, KeyboardInterrupt):
                self.console.print("\n[dim]Goodbye! 👋[/dim]")
                break
            except Exception as e:
                self.console.print(f"[red]Error:[/red] {str(e)}")

    def attach_file(self, filepath: str):
        """Manually attach a file to context"""
        content = self._read_file(filepath)
        if content:
            self.attached_files[filepath] = content
            self.console.print(f"[green]✓[/green] Attached: {filepath}")
        else:
            self.console.print(f"[red]✗[/red] Could not attach: {filepath}")

    def show_attached_files(self):
        """Show currently attached files"""
        if not self.attached_files:
            self.console.print("[dim]No files attached[/dim]")
            return
        
        table = Table(show_header=True, box=box.SIMPLE)
        table.add_column("File", style="cyan")
        table.add_column("Size", style="dim", justify="right")
        
        for filepath, content in self.attached_files.items():
            size = len(content)
            size_str = f"{size:,} bytes"
            if size > 1024:
                size_str = f"{size/1024:.1f} KB"
            table.add_row(filepath, size_str)
        
        panel = Panel(
            table,
            title="[bold]Attached Files[/bold]",
            border_style="cyan",
            box=box.ROUNDED
        )
        self.console.print(panel)
        self.console.print()

    def search_conversation(self, query: str):
        """Search through conversation history"""
        if not self.conversation_history:
            self.console.print("[dim]No conversation history to search[/dim]")
            return
        
        results = []
        for i, turn in enumerate(self.conversation_history):
            role = turn.get("role", "user")
            content = turn.get("content", "")
            
            if query.lower() in content.lower():
                results.append((i, role, content))
        
        if not results:
            self.console.print(f"[dim]No results found for: {query}[/dim]")
            return
        
        # Display results
        table = Table(show_header=True, box=box.SIMPLE)
        table.add_column("#", style="dim", width=4)
        table.add_column("Role", style="cyan", width=10)
        table.add_column("Content", style="white")
        
        for idx, role, content in results[:10]:  # Show max 10 results
            # Truncate content
            preview = content[:100] + "..." if len(content) > 100 else content
            # Highlight query in preview (case-insensitive)
            preview = re.sub(f'({re.escape(query)})', r'[yellow]\1[/yellow]', preview, flags=re.IGNORECASE)
            
            role_styled = "[cyan]User[/cyan]" if role == "user" else "[magenta]Assistant[/magenta]"
            table.add_row(str(idx), role_styled, preview)
        
        panel = Panel(
            table,
            title=f"[bold]Search Results for '{query}'[/bold]",
            border_style="cyan",
            box=box.ROUNDED,
            subtitle=f"[dim]Found {len(results)} result(s)[/dim]"
        )
        self.console.print(panel)
        self.console.print()


def main():
    """Main entry point"""
    shell = RichSessionShell()
    shell.run()


if __name__ == "__main__":
    main()
