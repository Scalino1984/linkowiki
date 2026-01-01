#!/usr/bin/env python3
"""
Simple Copilot-style session shell
Fixed layout with prompt at bottom
"""
import os
import sys
import shutil
from pathlib import Path

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


def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')


def get_terminal_size():
    """Get terminal width and height"""
    return shutil.get_terminal_size(fallback=(120, 40))


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


def render_copilot_screen(session, content_lines=None):
    """Render complete Copilot-style screen"""
    term_width, _ = get_terminal_size()
    
    # Get session info
    from tools.ai.providers import get_provider_registry
    from tools.config import get_config
    
    if "active_provider_id" not in session or not session.get("active_provider_id"):
        config = get_config()
        session["active_provider_id"] = config.default_provider
    
    registry = get_provider_registry()
    provider = registry.get_provider(session.get("active_provider_id"))
    
    # Shorten CWD
    cwd = os.getcwd()
    home = os.path.expanduser("~")
    if cwd.startswith(home):
        short_cwd = "~" + cwd[len(home):]
    else:
        short_cwd = cwd
    
    # Git branch
    git_branch = get_git_branch()
    
    # Build header
    left = short_cwd
    if git_branch:
        left += f"[ {git_branch}]"
    
    model_short = provider.id.replace("openai-", "").replace("anthropic-", "")
    right = f"{model_short} (1x)"
    
    spacing = term_width - len(left) - len(right)
    if spacing < 1:
        spacing = 1
    
    # Clear and render
    clear_screen()
    
    # Header
    print(f"{Colors.DIM}{left}{' ' * spacing}{right}{Colors.RESET}")
    print(f"{Colors.DIM}{'─' * term_width}{Colors.RESET}")
    print()
    
    # Content
    if content_lines:
        for line in content_lines:
            print(line)
        print()
    
    # Footer/Separator/Prompt at bottom
    print(f"{Colors.DIM}{'─' * term_width}{Colors.RESET}")
    print(f"> ", end="", flush=True)


def simple_shell():
    """Simple Copilot-style shell"""
    s = load_session()
    if not s:
        print(f"\n{Colors.RED}error: no active session{Colors.RESET}")
        print(f"{Colors.DIM}run 'linkowiki-admin session start' first{Colors.RESET}\n")
        return
    
    content = []
    
    while True:
        render_copilot_screen(s, content)
        
        try:
            cmd = input().strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        
        if not cmd:
            continue
        
        if cmd in ("exit", "quit", "/exit", "/quit"):
            break
        
        if cmd in ("/clear", "/cls"):
            content = []
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
