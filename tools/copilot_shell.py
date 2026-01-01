#!/usr/bin/env python3
"""
LinkoWiki Session Shell - Copilot Style Design
Based on design.md specifications
"""
import os
import sys
import shutil
from pathlib import Path
from typing import List, Dict, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))


class Colors:
    """ANSI color codes"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    # Foreground
    BLACK = "\033[30m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"


class CopilotShell:
    """Copilot-style interactive shell"""
    
    COMMANDS = {
        "/help": "Show help for interactive commands",
        "/model": "Show current AI model",
        "/model list": "List all available models",
        "/model set <id>": "Switch to a different model",
        "/attach <file>": "Attach a file to the context",
        "/files": "List attached files",
        "/tree": "Show wiki structure",
        "/clear": "Clear the conversation history",
        "/exit": "Exit the shell",
        "/quit": "Exit the shell",
        "/apply": "Apply pending actions",
        "/reject": "Reject pending actions",
    }
    
    def __init__(self):
        self.term_width, self.term_height = shutil.get_terminal_size(fallback=(80, 24))
        self.cwd = os.getcwd()
        self.git_branch = self._get_git_branch()
        self.model_name = "openai-gpt5-text"
        self.model_count = "1x"
        
    def _get_git_branch(self) -> str:
        """Get current git branch"""
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
    
    def _print_header(self):
        """Print header line with cwd and model info"""
        # Format: ~/path/to/dir[ branch*]                                      model-name (1x)
        
        # Shorten path
        home = os.path.expanduser("~")
        if self.cwd.startswith(home):
            short_cwd = "~" + self.cwd[len(home):]
        else:
            short_cwd = self.cwd
        
        # Build left side
        left = short_cwd
        if self.git_branch:
            left += f"[ {self.git_branch}]"
        
        # Build right side
        right = f"{self.model_name} ({self.model_count})"
        
        # Calculate spacing
        spacing = self.term_width - len(left) - len(right)
        if spacing < 1:
            spacing = 1
        
        print(f"{Colors.DIM}{left}{' ' * spacing}{right}{Colors.RESET}")
    
    def _print_separator(self):
        """Print horizontal separator line"""
        print(f"{Colors.DIM}{'─' * self.term_width}{Colors.RESET}")
    
    def _print_prompt(self, text: str = ""):
        """Print the input prompt"""
        cursor = "█"
        print(f"> {text}{cursor}", end="", flush=True)
    
    def _print_autocomplete(self, items: List[Tuple[str, str]], selected_idx: int = 0):
        """
        Print autocomplete dropdown
        
        Args:
            items: List of (command, description) tuples
            selected_idx: Index of selected item (shows ▌)
        """
        self._print_separator()
        
        for i, (cmd, desc) in enumerate(items):
            marker = "▌" if i == selected_idx else " "
            # Format: marker command                   description
            
            # Calculate spacing between command and description
            spacing = 30 - len(cmd)
            if spacing < 2:
                spacing = 2
            
            print(f"{marker} {Colors.BRIGHT_WHITE}{cmd}{Colors.RESET}{' ' * spacing}{Colors.DIM}{desc}{Colors.RESET}")
    
    def _filter_commands(self, prefix: str) -> List[Tuple[str, str]]:
        """Filter commands by prefix"""
        prefix = prefix.lower()
        matches = []
        for cmd, desc in self.COMMANDS.items():
            if cmd.lower().startswith(prefix):
                matches.append((cmd, desc))
        return matches
    
    def _get_files_for_autocomplete(self, prefix: str = "") -> List[Tuple[str, str]]:
        """Get files/directories for @ autocomplete"""
        results = []
        
        # Add directories first
        results.append((f"@[DIR]  {BASE_DIR}", "Project root"))
        results.append((f"@[DIR]  /tmp", "Temporary directory"))
        
        # Add files from current directory
        try:
            for item in sorted(BASE_DIR.iterdir()):
                if prefix and not str(item.name).startswith(prefix.lstrip("@")):
                    continue
                
                if item.is_dir() and not item.name.startswith("."):
                    results.append((f"@[DIR]  {item.name}", "Directory"))
                elif item.is_file():
                    results.append((f"@{item.name}", "File"))
                
                if len(results) >= 10:  # Limit to 10 items
                    break
        except:
            pass
        
        return results
    
    def show_idle(self):
        """Show idle state (empty prompt)"""
        self._print_header()
        self._print_separator()
        self._print_prompt()
        print()  # Newline for cursor
    
    def show_command_help(self, cmd: str):
        """Show command with description"""
        self._print_header()
        self._print_separator()
        self._print_prompt(cmd)
        print()
        self._print_separator()
        
        if cmd in self.COMMANDS:
            desc = self.COMMANDS[cmd]
            print(f"  {Colors.BRIGHT_WHITE}{cmd}{Colors.RESET}{'.' * 25}{Colors.DIM}{desc}{Colors.RESET}")
    
    def show_command_autocomplete(self, cmd: str):
        """Show command autocomplete list"""
        matches = self._filter_commands(cmd)
        
        self._print_header()
        self._print_separator()
        self._print_prompt(cmd)
        print()
        
        if matches:
            self._print_autocomplete(matches)
    
    def show_file_autocomplete(self, prefix: str = ""):
        """Show file/directory picker for @ symbol"""
        files = self._get_files_for_autocomplete(prefix)
        
        self._print_header()
        self._print_separator()
        self._print_prompt(prefix if prefix else "@")
        print()
        
        if files:
            # Don't show descriptions for files to match design
            simple_items = [(f, "") for f, _ in files]
            self._print_autocomplete(simple_items)
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')


def demo_views():
    """Demo all view states from design.md"""
    shell = CopilotShell()
    
    # View 1: Idle
    print("\n=== VIEW 1: IDLE ===\n")
    shell.clear_screen()
    shell.show_idle()
    input("\nPress Enter for next view...")
    
    # View 2: /help command
    print("\n=== VIEW 2: /help ===\n")
    shell.clear_screen()
    shell.show_command_help("/help")
    input("\nPress Enter for next view...")
    
    # View 3: /add-dir autocomplete
    print("\n=== VIEW 3: Command Autocomplete ===\n")
    shell.clear_screen()
    shell.show_command_autocomplete("/")
    input("\nPress Enter for next view...")
    
    # View 4: @ file picker
    print("\n=== VIEW 4: File Picker (@) ===\n")
    shell.clear_screen()
    shell.show_file_autocomplete()
    input("\nPress Enter for next view...")
    
    # View 5: @.git filtered
    print("\n=== VIEW 5: Filtered Files (@.git) ===\n")
    shell.clear_screen()
    shell.show_file_autocomplete("@.git")
    input("\nPress Enter to finish...")


if __name__ == "__main__":
    # Run demo
    demo_views()
