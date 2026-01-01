#!/usr/bin/env python3
"""
LinkoWiki Copilot CLI - Full Implementation
Based on detailed text specification
"""
import os
import sys
import shutil
import time
from pathlib import Path
from typing import Optional, List, Tuple

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))


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
        os.system('clear' if os.name != 'nt' else 'cls')
        
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
    demo_copilot_cli()
