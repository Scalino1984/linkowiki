#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
import shutil
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[1]
WIKI_DIR = BASE_DIR / "wiki"
CHANGELOG = WIKI_DIR / ".changelog"

sys.path.insert(0, str(BASE_DIR))

# Load config early
from tools.config import get_config
CONFIG = get_config()

from tools.session.manager import (
    start_session,
    end_session,
    load_session,
    add_history,
    attach_file,
)

# ANSI Color Codes
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    
    # Foreground
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # Bright foreground
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    
    # Background
    BG_BLACK = "\033[40m"
    BG_BLUE = "\033[44m"
    BG_CYAN = "\033[46m"

    # Accent
    ACCENT = BRIGHT_MAGENTA


def get_terminal_size():
    """Get terminal width and height"""
    return shutil.get_terminal_size(fallback=(80, 24))


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def visible_len(text: str) -> int:
    return len(strip_ansi(text))


def pad_to(text: str, width: int) -> str:
    padding = max(width - visible_len(text), 0)
    return f"{text}{' ' * padding}"


def print_box(text, color=Colors.CYAN, prefix="", width=70):
    """Print text in a nice box"""
    lines = text.split('\n')
    print(f"\n{color}╭{'─' * (width - 2)}╮{Colors.RESET}")
    for line in lines:
        padding = width - len(line) - 4 - len(prefix)
        print(f"{color}│{Colors.RESET} {prefix}{line}{' ' * padding} {color}│{Colors.RESET}")
    print(f"{color}╰{'─' * (width - 2)}╯{Colors.RESET}\n")


def print_user_input(text):
    """Format user input"""
    print(f"\n{Colors.BRIGHT_BLUE}{Colors.BOLD}You{Colors.RESET}")
    print(f"{Colors.BRIGHT_BLACK}{'─' * 70}{Colors.RESET}")
    print(f"{text}")
    print()


def print_assistant_message(text):
    """Format assistant response"""
    print(f"{Colors.BRIGHT_MAGENTA}{Colors.BOLD}Assistant{Colors.RESET}")
    print(f"{Colors.BRIGHT_BLACK}{'─' * 70}{Colors.RESET}")
    
    # Wrap text nicely
    import textwrap
    for line in text.split('\n'):
        if line.strip():
            wrapped = textwrap.fill(line, width=70)
            print(wrapped)
        else:
            print()
    print()


def print_actions_box(actions):
    """Print actions in a styled box"""
    print(f"\n{Colors.YELLOW}{Colors.BOLD}📋 Vorgeschlagene Aktionen{Colors.RESET}")
    print(f"{Colors.BRIGHT_BLACK}{'─' * 70}{Colors.RESET}")
    
    for a in actions:
        action_color = Colors.GREEN if a.type == "create" else Colors.CYAN
        print(f"  {action_color}▸{Colors.RESET} {Colors.BOLD}{a.type.upper()}{Colors.RESET} {Colors.DIM}{a.path}{Colors.RESET}")
    
    print(f"\n{Colors.BRIGHT_BLACK}  → Tippe {Colors.RESET}{Colors.BRIGHT_WHITE}apply{Colors.RESET}{Colors.BRIGHT_BLACK} zum Ausführen oder diskutiere weiter{Colors.RESET}\n")


def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')


def print_separator(char="─", color=Colors.BRIGHT_BLACK):
    """Print a separator line"""
    print(f"{color}{char * 50}{Colors.RESET}")


def print_options(options):
    """Print interactive options"""
    if not options:
        return
    
    print(f"{Colors.CYAN}⚙ Options{Colors.RESET}")
    print_separator()
    
    for i, opt in enumerate(options, 1):
        label = opt.label if hasattr(opt, 'label') else opt
        desc = opt.description if hasattr(opt, 'description') else None
        
        print(f"  {i}. {label}")
        if desc:
            print(f"     {Colors.DIM}{desc}{Colors.RESET}")
    
    print()
    print(f"{Colors.DIM}  Type number or enter custom message{Colors.RESET}")
    print()


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


def build_claude_panel_lines(session, term_width):
    """Build Claude-style panel header lines."""
    from tools.ai.providers import get_provider_registry
    
    # Ensure session has provider
    if "active_provider_id" not in session or not session.get("active_provider_id"):
        from tools.config import get_config
        config = get_config()
        session["active_provider_id"] = config.default_provider
    
    registry = get_provider_registry()
    provider = registry.get_provider(session.get("active_provider_id"))
    
    # Shorten path
    cwd = os.getcwd()
    home = os.path.expanduser("~")
    if cwd.startswith(home):
        short_cwd = "~" + cwd[len(home):]
    else:
        short_cwd = cwd
    
    # Git branch
    git_branch = get_git_branch()
    
    model_short = provider.id.replace("openai-", "").replace("anthropic-", "")
    model_label = f"{Colors.DIM}{model_short} (1x){Colors.RESET}"
    branch_label = f"{short_cwd}{f' [{git_branch}]' if git_branch else ''}"

    inner_width = max(term_width - 2, 40)
    content_width = inner_width - 2
    lines = []
    lines.append(f"{Colors.ACCENT}╭{'─' * inner_width}╮{Colors.RESET}")

    title_left = f"{Colors.BRIGHT_WHITE}LinkoWiki Code{Colors.RESET} {Colors.DIM}Session{Colors.RESET}"
    title_spacing = content_width - visible_len(title_left) - visible_len(model_label)
    if title_spacing < 1:
        title_spacing = 1
    title_line = (
        f"{Colors.ACCENT}│{Colors.RESET} "
        f"{title_left}{' ' * title_spacing}{model_label}"
        f" {Colors.ACCENT}│{Colors.RESET}"
    )
    lines.append(title_line)

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


def print_copilot_header(session):
    """Print Claude-style header panel."""
    term_width, _ = get_terminal_size()
    for line in build_claude_panel_lines(session, term_width):
        print(line)


def print_user_input(text):
    """Format user input"""
    print(f"\n{Colors.BRIGHT_BLACK}▶{Colors.RESET} {text}")
    print()


def print_assistant_message(text):
    """Format assistant response"""
    print(f"{Colors.CYAN}◆{Colors.RESET} {Colors.BOLD}Assistant{Colors.RESET}")
    print("─" * 50)
    
    import textwrap
    for line in text.split('\n'):
        if line.strip():
            wrapped = textwrap.fill(line, width=60, initial_indent="  ", subsequent_indent="  ")
            print(wrapped)
        else:
            print()
    print()


def print_actions_box(actions):
    """Print actions in a styled box"""
    print(f"{Colors.YELLOW}⚡ Actions{Colors.RESET}")
    print("─" * 50)
    
    for a in actions:
        action_type = a.type.upper()
        print(f"  {action_type:8} {a.path}")
    
    print()
    print(f"{Colors.DIM}  → 'apply' to execute{Colors.RESET}")
    print()


def print_options(options):
    """Print interactive options in Copilot style"""
    if not options:
        return
    
    term_width, _ = get_terminal_size()
    
    print()
    print(f"{Colors.BRIGHT_WHITE}Options:{Colors.RESET}")
    print(f"{Colors.DIM}{'─' * term_width}{Colors.RESET}")
    
    for i, opt in enumerate(options, 1):
        label = opt.label if hasattr(opt, 'label') else opt
        desc = opt.description if hasattr(opt, 'description') else None
        
        print(f"  {Colors.BRIGHT_WHITE}{i}.{Colors.RESET} {label}")
        if desc:
            print(f"     {Colors.DIM}{desc}{Colors.RESET}")
    
    print()
    print(f"  {Colors.DIM}Type number to select or enter custom message{Colors.RESET}")
    print()


def print_tree():
    if not WIKI_DIR.exists():
        print("📭 Wiki ist leer\n")
        return

    print(f"📚 Wiki-Struktur ({WIKI_DIR}):\n")
    for root, dirs, files in os.walk(WIKI_DIR):
        level = Path(root).relative_to(WIKI_DIR).parts
        indent = "  " * len(level)
        print(f"{indent}📂 {Path(root).name}")
        for f in sorted(files):
            print(f"{indent}  📄 {f}")
    print()


def confirm():
    return input("➡️ Änderungen durchführen? (ja/nein): ").strip() == "ja"


def log_change(actions, source="ai"):
    ts = datetime.now().isoformat(timespec="seconds")
    with CHANGELOG.open("a") as f:
        f.write(f"\n[{ts}] source={source}\n")
        for a in actions:
            f.write(f"  {a.type} {a.path}\n")


def validate_action(action):
    if ".." in action.path or action.path.startswith("/"):
        raise RuntimeError(f"Ungültiger Pfad: {action.path}")

    target = WIKI_DIR / action.path
    if target.exists() and target.is_dir():
        raise RuntimeError("Ziel ist ein Verzeichnis")

    if action.content and len(action.content) > 50_000:
        raise RuntimeError("Inhalt zu groß (>50KB)")


def apply_actions(actions, write):
    for a in actions:
        validate_action(a)

    print(f"{Colors.YELLOW}{Colors.BOLD}🧪 DRY RUN{Colors.RESET}")
    print(f"{Colors.BRIGHT_BLACK}{'─' * 70}{Colors.RESET}")
    for a in actions:
        action_color = Colors.GREEN if a.type == "create" else Colors.CYAN
        print(f"  {action_color}▸{Colors.RESET} {Colors.BOLD}{a.type.upper()}{Colors.RESET} {Colors.DIM}{a.path}{Colors.RESET}")
    print(f"{Colors.BRIGHT_BLACK}{'─' * 70}{Colors.RESET}")

    if not write:
        print(f"\n{Colors.YELLOW}⚠ Read-only Modus - keine Änderungen möglich{Colors.RESET}\n")
        return

    if not confirm():
        print(f"\n{Colors.RED}✗ Abgebrochen{Colors.RESET}\n")
        return

    for a in actions:
        target = WIKI_DIR / a.path
        if a.type == "create":
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(a.content or "")
        elif a.type == "append":
            target.write_text(target.read_text() + "\n" + (a.content or ""))

    log_change(actions)
    print(f"\n{Colors.GREEN}✓ Änderungen erfolgreich angewendet{Colors.RESET}\n")


def print_copilot_separator():
    """Print horizontal separator line (full width)"""
    term_width, _ = get_terminal_size()
    print(f"{Colors.DIM}{'─' * term_width}{Colors.RESET}")


def print_copilot_prompt(text=""):
    """Print the > prompt with optional text"""
    print(f"> {text}", end="", flush=True)


def session_shell():
    from tools.ai.assistant import run_ai
    
    s = load_session()
    if not s:
        print(f"\n{Colors.RED}error: no active session{Colors.RESET}")
        print(f"{Colors.DIM}run 'linkowiki-admin session start' first{Colors.RESET}\n")
        return

    clear_screen()
    last_options = []
    last_content = []

    while True:
        # Clear and render full screen
        clear_screen()
        
        # Print Copilot-style header
        print_copilot_header(s)
        print()
        
        # Print last content if any
        if last_content:
            for line in last_content:
                print(line)
            print()
        
        # Print footer/separator/prompt at bottom
        hint_lines = [
            f"{Colors.DIM}Try \"/help\" for commands{Colors.RESET}",
            f"{Colors.DIM}? for shortcuts{Colors.RESET}",
        ]
        for line in hint_lines:
            print(f"  {line}")
        print()
        print_copilot_separator()
        print_copilot_prompt()
        
        try:
            cmd = input().strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not cmd:
            clear_screen()
            continue

        # Handle commands
        if cmd in ("exit", "quit", "/exit", "/quit"):
            print()
            break
        
        if cmd in ("/clear", "/cls"):
            last_content = []
            continue

        if cmd in ("help", "/help"):
            last_content = []
            commands = [
                ("/help", "Show help for interactive commands"),
                ("/model", "Show current AI model"),
                ("/model list", "List all available models"),
                ("/model set <id>", "Switch to a different model"),
                ("/attach <file>", "Attach a file to the context"),
                ("/files", "List attached files"),
                ("/tree", "Show wiki structure"),
                ("/clear", "Clear the screen"),
                ("/exit, /quit", "Exit the shell"),
                ("", ""),
                ("apply", "Apply pending actions"),
                ("reject", "Reject pending actions"),
            ]
            
            for cmd_name, desc in commands:
                if cmd_name:
                    spacing = 30 - len(cmd_name)
                    if spacing < 2:
                        spacing = 2
                    last_content.append(f"  {Colors.BRIGHT_WHITE}{cmd_name}{Colors.RESET}{' ' * spacing}{Colors.DIM}{desc}{Colors.RESET}")
                else:
                    last_content.append("")
            continue
        
        if cmd == "/model":
            from tools.ai.providers import get_provider_registry
            registry = get_provider_registry()
            provider = registry.get_provider(s.get("active_provider_id"))
            
            last_content = [
                f"  {Colors.BRIGHT_WHITE}Model:{Colors.RESET} {provider.id}",
                f"  {Colors.DIM}Provider:{Colors.RESET} {provider.provider}",
                f"  {Colors.DIM}Type:{Colors.RESET} {'Reasoning' if provider.reasoning else 'Text'}",
            ]
            if provider.description:
                last_content.append(f"  {Colors.DIM}{provider.description}{Colors.RESET}")
            continue
        
        if cmd == "/model list":
            from tools.ai.providers import get_provider_registry
            registry = get_provider_registry()
            providers = registry.list_providers()
            
            last_content = []
            for provider_id, provider in providers.items():
                is_active = (provider_id == s.get("active_provider_id"))
                marker = f"{Colors.BRIGHT_WHITE}▌{Colors.RESET}" if is_active else " "
                reasoning_tag = f"{Colors.YELLOW}[R]{Colors.RESET}" if provider.reasoning else ""
                
                last_content.append(f"{marker} {Colors.BRIGHT_WHITE}{provider_id}{Colors.RESET} {reasoning_tag}")
                if provider.description and is_active:
                    last_content.append(f"  {Colors.DIM}{provider.description}{Colors.RESET}")
            
            last_content.append("")
            last_content.append(f"  {Colors.DIM}Use /model set <id> to switch{Colors.RESET}")
            continue
        
        if cmd.startswith("/model set "):
            parts = cmd.split(" ", 2)
            if len(parts) < 3:
                print(f"  {Colors.DIM}Usage: /model set <id>{Colors.RESET}")
                continue
            
            new_provider_id = parts[2]
            try:
                from tools.session.manager import set_active_provider, save_session
                set_active_provider(new_provider_id)
                s = load_session()
                
                from tools.ai.providers import get_provider_registry
                registry = get_provider_registry()
                provider = registry.get_provider(new_provider_id)
                
                print_copilot_separator()
                print(f"  {Colors.BRIGHT_WHITE}✓{Colors.RESET} Model switched to {provider.id}")
            except Exception as e:
                print_copilot_separator()
                print(f"  {Colors.RED}✗{Colors.RESET} Error: {e}")
            continue

        if cmd.startswith("/attach "):
            path = cmd.split(" ", 1)[1]
            try:
                attach_file(path)
                print_copilot_separator()
                print(f"  {Colors.BRIGHT_WHITE}✓{Colors.RESET} File attached: {Colors.DIM}{path}{Colors.RESET}")
            except Exception as e:
                print_copilot_separator()
                print(f"  {Colors.RED}✗{Colors.RESET} Error: {e}")
            continue

        if cmd == "/tree":
            print_copilot_separator()
            if not WIKI_DIR.exists():
                print(f"  {Colors.DIM}Wiki is empty{Colors.RESET}")
                continue
            
            for root, dirs, files in os.walk(WIKI_DIR):
                level = Path(root).relative_to(WIKI_DIR).parts
                indent = "  " * len(level)
                if level:
                    print(f"  {indent}📂 {Path(root).name}")
                for f in sorted(files):
                    if not f.startswith("."):
                        print(f"  {indent}  📄 {f}")
            continue

        if cmd == "/files":
            s = load_session()
            files = s.get("files", {})
            print_copilot_separator()
            if files:
                for f in files:
                    print(f"  {Colors.BRIGHT_WHITE}@{Colors.RESET} {Colors.DIM}{f}{Colors.RESET}")
            else:
                print(f"  {Colors.DIM}No files attached{Colors.RESET}")
            continue

        if cmd == "apply":
            s = load_session()
            actions = s.get("pending_actions", [])
            if not actions:
                print_copilot_separator()
                print(f"  {Colors.DIM}No pending actions{Colors.RESET}")
                continue

            from tools.ai.assistant import Action
            print_copilot_separator()
            apply_actions([Action(**a) for a in actions], s["write"])
            s["pending_actions"] = []
            from tools.session.manager import save_session
            save_session(s)
            last_options = []
            continue

        if cmd == "reject":
            s = load_session()
            s["pending_actions"] = []
            from tools.session.manager import save_session
            save_session(s)
            print_copilot_separator()
            print(f"  {Colors.RED}✗{Colors.RESET} Pending actions rejected")
            last_options = []
            continue

        # Regular AI interaction
        print_copilot_separator()
        add_history(cmd)
        s = load_session()
        
        try:
            result = run_ai(cmd, s["files"], session=s)
            
            # Print response
            print(f"\n{result.message}\n")

            if result.options:
                last_options = result.options
                print_options(result.options)

            if result.actions:
                print_actions_box(result.actions)
                s["pending_actions"] = [a.dict() for a in result.actions]
                from tools.session.manager import save_session
                save_session(s)
        except Exception as e:
            print(f"  {Colors.RED}✗{Colors.RESET} Error: {e}")
            if "--debug" in sys.argv:
                import traceback
                print(f"{Colors.DIM}{traceback.format_exc()}{Colors.RESET}")


def print_main_menu():
    """Print interactive main menu"""
    print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}╔{'═' * 68}╗{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.RESET}  {Colors.BOLD}🧠 LinkoWiki Admin - Hauptmenü{Colors.RESET}                               {Colors.BRIGHT_CYAN}{Colors.BOLD}║{Colors.RESET}")
    print(f"{Colors.BRIGHT_CYAN}{Colors.BOLD}╚{'═' * 68}╝{Colors.RESET}\n")
    
    menu_items = [
        ("Session Management", [
            ("1", "Session starten (read-only)"),
            ("2", "Session starten (write-mode)"),
            ("3", "Session Shell öffnen"),
            ("4", "Session Status anzeigen"),
            ("5", "Session beenden"),
            ("6", "Session exportieren"),
        ]),
        ("Wiki Browsing", [
            ("7", "Wiki-Struktur anzeigen"),
            ("8", "Wiki durchsuchen"),
            ("9", "Letzte Änderungen anzeigen"),
            ("10", "Kategorien & Statistiken"),
        ]),
        ("AI Tools", [
            ("11", "KI-Abfrage (einmalig)"),
            ("12", "Wiki-Eintrag erstellen (geführt)"),
        ]),
        ("Weitere Optionen", [
            ("h", "Hilfe anzeigen"),
            ("q", "Beenden"),
        ])
    ]
    
    for section, items in menu_items:
        print(f"  {Colors.BRIGHT_CYAN}{section}{Colors.RESET}")
        for num, desc in items:
            print(f"    {Colors.CYAN}{num:3}{Colors.RESET}  {desc}")
        print()
    
    print()


def interactive_menu():
    """Run interactive menu loop"""
    while True:
        print_main_menu()
        
        try:
            choice = input(f"{Colors.BRIGHT_BLACK}Wähle eine Option{Colors.RESET} {Colors.BRIGHT_BLACK}❯{Colors.RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{Colors.DIM}👋 Auf Wiedersehen{Colors.RESET}\n")
            break
        
        if not choice:
            continue
            
        if choice == "q":
            print(f"\n{Colors.DIM}👋 Auf Wiedersehen{Colors.RESET}\n")
            break
        
        elif choice == "h":
            show_detailed_help()
            input(f"\n{Colors.DIM}Drücke Enter zum Fortfahren...{Colors.RESET}")
            
        elif choice == "1":
            try:
                # Use default mode from config
                write_mode = (CONFIG.default_session_mode == "write")
                s = start_session(write=write_mode)
                mode_str = "write-mode" if write_mode else "read-only"
                print(f"\n{Colors.GREEN}✓ Session gestartet ({mode_str}){Colors.RESET}")
                print(f"{Colors.DIM}  ID: {s['id']}{Colors.RESET}\n")
                input(f"{Colors.DIM}Drücke Enter zum Fortfahren...{Colors.RESET}")
            except RuntimeError as e:
                print(f"\n{Colors.RED}✗ {e}{Colors.RESET}\n")
                input(f"{Colors.DIM}Drücke Enter zum Fortfahren...{Colors.RESET}")
        
        elif choice == "2":
            try:
                s = start_session(write=True)
                print(f"\n{Colors.GREEN}✓ Session gestartet (write-mode){Colors.RESET}")
                print(f"{Colors.DIM}  ID: {s['id']}{Colors.RESET}\n")
                input(f"{Colors.DIM}Drücke Enter zum Fortfahren...{Colors.RESET}")
            except RuntimeError as e:
                print(f"\n{Colors.RED}✗ {e}{Colors.RESET}\n")
                input(f"{Colors.DIM}Drücke Enter zum Fortfahren...{Colors.RESET}")
        
        elif choice == "3":
            session_shell()
        
        elif choice == "4":
            s = load_session()
            if s:
                print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}📊 Session Status{Colors.RESET}")
                print(f"{Colors.BRIGHT_BLACK}{'─' * 70}{Colors.RESET}")
                print(f"  {Colors.CYAN}ID:{Colors.RESET} {s['id']}")
                print(f"  {Colors.CYAN}Modus:{Colors.RESET} {Colors.GREEN if s['write'] else Colors.RED}{'Write' if s['write'] else 'Read-only'}{Colors.RESET}")
                print(f"  {Colors.CYAN}Gestartet von:{Colors.RESET} {s['started_by']}")
                print(f"  {Colors.CYAN}Verlauf:{Colors.RESET} {len(s.get('history', []))} Einträge")
                print(f"  {Colors.CYAN}Dateien:{Colors.RESET} {len(s.get('files', {}))} angehängt")
                print(f"  {Colors.CYAN}Ausstehende Aktionen:{Colors.RESET} {len(s.get('pending_actions', []))}")
                print()
            else:
                print(f"\n{Colors.DIM}ℹ️  Keine aktive Session{Colors.RESET}\n")
            input(f"{Colors.DIM}Drücke Enter zum Fortfahren...{Colors.RESET}")
        
        elif choice == "5":
            s = load_session()
            if s:
                confirm = input(f"\n{Colors.YELLOW}⚠  Session wirklich beenden? (j/n):{Colors.RESET} ").strip().lower()
                if confirm == "j":
                    end_session()
                    print(f"\n{Colors.GREEN}✓ Session beendet{Colors.RESET}\n")
                else:
                    print(f"\n{Colors.DIM}Abgebrochen{Colors.RESET}\n")
            else:
                print(f"\n{Colors.DIM}ℹ️  Keine aktive Session{Colors.RESET}\n")
            input(f"{Colors.DIM}Drücke Enter zum Fortfahren...{Colors.RESET}")
        
        elif choice == "6":
            s = load_session()
            if s:
                from tools.session.export import export_session_history
                try:
                    output_file = export_session_history(s)
                    print(f"\n{Colors.GREEN}✓ Session exportiert:{Colors.RESET} {Colors.DIM}{output_file}{Colors.RESET}\n")
                except Exception as e:
                    print(f"\n{Colors.RED}✗ Export fehlgeschlagen:{Colors.RESET} {e}\n")
            else:
                print(f"\n{Colors.DIM}ℹ️  Keine aktive Session{Colors.RESET}\n")
            input(f"{Colors.DIM}Drücke Enter zum Fortfahren...{Colors.RESET}")
        
        elif choice == "7":
            print()
            print_tree()
            input(f"{Colors.DIM}Drücke Enter zum Fortfahren...{Colors.RESET}")
        
        elif choice == "8":
            search_wiki_interactive()
        
        elif choice == "9":
            show_recent_changes()
        
        elif choice == "10":
            show_wiki_statistics()
        
        elif choice == "11":
            run_single_ai_query()
        
        elif choice == "12":
            guided_wiki_creation()
        
        else:
            print(f"\n{Colors.RED}✗ Ungültige Auswahl{Colors.RESET}\n")
            input(f"{Colors.DIM}Drücke Enter zum Fortfahren...{Colors.RESET}")


def show_detailed_help():
    """Show detailed help information"""
    print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}📖 LinkoWiki Admin - Detaillierte Hilfe{Colors.RESET}")
    print(f"{Colors.BRIGHT_BLACK}{'═' * 70}{Colors.RESET}\n")
    
    sections = [
        ("🎯 Übersicht", [
            "LinkoWiki Admin ist ein KI-gestütztes Wiki-Management-Tool.",
            "Du kannst interaktiv mit einem KI-Assistenten arbeiten,",
            "der dir beim Erstellen und Organisieren von Wiki-Einträgen hilft."
        ]),
        ("🔐 Session-Modi", [
            "Read-only: KI schlägt Änderungen vor, führt sie aber nicht aus",
            "Write-mode: Änderungen können nach Bestätigung geschrieben werden"
        ]),
        ("💬 Session Shell", [
            "Interaktiver Dialog mit dem KI-Assistenten",
            "Der Assistent stellt Rückfragen und macht Vorschläge",
            "Actions werden erst nach 'apply' ausgeführt",
            "Kommandos: help, apply, reject, why, options, :tree, :files"
        ]),
        ("📁 Wiki-Struktur", [
            "Eine Datei = ein Thema",
            "Pfad = Kategorie/Thema (z.B. linux/systemctl)",
            "Keine Dateiendungen erforderlich",
            "Inhalte sollten kurz und strukturiert sein"
        ]),
        ("🤖 KI-Abfrage", [
            "Einmalige Abfrage ohne Session",
            "Nützlich für schnelle Wiki-Erstellung",
            "Dateien können als Kontext angehängt werden"
        ])
    ]
    
    for title, items in sections:
        print(f"{Colors.BRIGHT_CYAN}{title}{Colors.RESET}")
        print(f"{Colors.BRIGHT_BLACK}{'─' * 70}{Colors.RESET}")
        for item in items:
            print(f"  • {item}")
        print()


def run_single_ai_query():
    """Run a single AI query without session"""
    print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}🤖 Einmalige KI-Abfrage{Colors.RESET}")
    print(f"{Colors.BRIGHT_BLACK}{'─' * 70}{Colors.RESET}\n")
    
    prompt = input(f"{Colors.CYAN}Prompt:{Colors.RESET} ").strip()
    if not prompt:
        print(f"\n{Colors.RED}✗ Prompt erforderlich{Colors.RESET}\n")
        return
    
    file_path = input(f"{Colors.CYAN}Datei anhängen (optional, Enter überspringen):{Colors.RESET} ").strip()
    
    write = input(f"{Colors.CYAN}Write-Modus aktivieren? (j/n):{Colors.RESET} ").strip().lower() == "j"
    
    print()
    
    from tools.ai.assistant import run_ai
    
    files = {}
    if file_path:
        try:
            p = Path(file_path).expanduser().resolve()
            files[p.name] = p.read_text()
            print(f"{Colors.GREEN}✓ Datei geladen:{Colors.RESET} {Colors.DIM}{p.name}{Colors.RESET}\n")
        except Exception as e:
            print(f"{Colors.RED}✗ Fehler beim Laden:{Colors.RESET} {e}\n")
            return
    
    try:
        print_user_input(prompt)
        result = run_ai(prompt, files)
        print_assistant_message(result.message)
        
        if result.options:
            print_options(result.options)
        
        if result.actions:
            from tools.ai.assistant import Action
            apply_actions(result.actions, write)
        else:
            print(f"{Colors.DIM}Keine Aktionen vorgeschlagen{Colors.RESET}\n")
    except Exception as e:
        print(f"\n{Colors.RED}✗ KI-Fehler:{Colors.RESET} {e}\n")
    
    input(f"\n{Colors.DIM}Drücke Enter zum Fortfahren...{Colors.RESET}")


def search_wiki_interactive():
    """Interactive wiki search"""
    print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}🔍 Wiki durchsuchen{Colors.RESET}")
    print(f"{Colors.BRIGHT_BLACK}{'─' * 70}{Colors.RESET}\n")
    
    query = input(f"{Colors.CYAN}Suchbegriff:{Colors.RESET} ").strip()
    if not query:
        return
    
    from tools.wiki_search import search_wiki
    
    results = search_wiki(query, WIKI_DIR)
    
    if results:
        print(f"\n{Colors.GREEN}✓ {len(results)} Treffer gefunden:{Colors.RESET}\n")
        for file_path, matches in results:
            rel_path = file_path.relative_to(WIKI_DIR)
            print(f"{Colors.CYAN}▸{Colors.RESET} {Colors.BOLD}{rel_path}{Colors.RESET}")
            for match in matches[:3]:  # Show max 3 matches per file
                print(f"  {Colors.DIM}{match}{Colors.RESET}")
            if len(matches) > 3:
                print(f"  {Colors.DIM}... und {len(matches) - 3} weitere{Colors.RESET}")
            print()
    else:
        print(f"\n{Colors.YELLOW}⚠ Keine Treffer gefunden{Colors.RESET}\n")
    
    input(f"{Colors.DIM}Drücke Enter zum Fortfahren...{Colors.RESET}")


def show_recent_changes():
    """Show recently modified wiki files"""
    print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}📅 Letzte Änderungen{Colors.RESET}")
    print(f"{Colors.BRIGHT_BLACK}{'─' * 70}{Colors.RESET}\n")
    
    from tools.wiki_search import list_recent_files
    from datetime import datetime
    
    recent = list_recent_files(WIKI_DIR, limit=15)
    
    if recent:
        for file_path, mtime in recent:
            rel_path = file_path.relative_to(WIKI_DIR)
            dt = datetime.fromtimestamp(mtime)
            time_str = dt.strftime("%Y-%m-%d %H:%M")
            print(f"{Colors.CYAN}▸{Colors.RESET} {rel_path} {Colors.DIM}({time_str}){Colors.RESET}")
        print()
    else:
        print(f"{Colors.DIM}ℹ️  Keine Dateien gefunden{Colors.RESET}\n")
    
    input(f"{Colors.DIM}Drücke Enter zum Fortfahren...{Colors.RESET}")


def show_wiki_statistics():
    """Show wiki statistics"""
    print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}📊 Wiki Statistiken{Colors.RESET}")
    print(f"{Colors.BRIGHT_BLACK}{'─' * 70}{Colors.RESET}\n")
    
    from tools.wiki_search import get_category_stats, get_wiki_categories
    
    categories = get_wiki_categories(WIKI_DIR)
    stats = get_category_stats(WIKI_DIR)
    
    if stats:
        total_files = sum(s["files"] for s in stats.values())
        total_size = sum(s["total_size"] for s in stats.values())
        
        print(f"{Colors.CYAN}Gesamt:{Colors.RESET}")
        print(f"  Dateien: {total_files}")
        print(f"  Größe: {total_size / 1024:.1f} KB")
        print(f"  Kategorien: {len(categories)}\n")
        
        print(f"{Colors.CYAN}Nach Kategorie:{Colors.RESET}")
        for category, data in sorted(stats.items(), key=lambda x: x[1]["files"], reverse=True):
            size_kb = data["total_size"] / 1024
            print(f"  {Colors.BOLD}{category:20}{Colors.RESET} {data['files']:3} Dateien  {size_kb:6.1f} KB")
        print()
    else:
        print(f"{Colors.DIM}ℹ️  Keine Statistiken verfügbar{Colors.RESET}\n")
    
    input(f"{Colors.DIM}Drücke Enter zum Fortfahren...{Colors.RESET}")


def guided_wiki_creation():
    """Guided wiki entry creation"""
    print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}📝 Wiki-Eintrag erstellen (Geführt){Colors.RESET}")
    print(f"{Colors.BRIGHT_BLACK}{'─' * 70}{Colors.RESET}\n")
    
    # Step 1: Category
    from tools.wiki_search import get_wiki_categories
    categories = get_wiki_categories(WIKI_DIR)
    
    print(f"{Colors.CYAN}Schritt 1: Kategorie{Colors.RESET}")
    if categories:
        print(f"{Colors.DIM}Existierende Kategorien: {', '.join(categories)}{Colors.RESET}")
    category = input("Kategorie (z.B. linux, security, dev): ").strip()
    
    if not category:
        print(f"\n{Colors.RED}✗ Kategorie erforderlich{Colors.RESET}\n")
        input(f"{Colors.DIM}Drücke Enter zum Fortfahren...{Colors.RESET}")
        return
    
    # Step 2: Topic
    print(f"\n{Colors.CYAN}Schritt 2: Thema{Colors.RESET}")
    topic = input("Thema (z.B. systemctl, firewall, git): ").strip()
    
    if not topic:
        print(f"\n{Colors.RED}✗ Thema erforderlich{Colors.RESET}\n")
        input(f"{Colors.DIM}Drücke Enter zum Fortfahren...{Colors.RESET}")
        return
    
    # Step 3: Content guidance
    print(f"\n{Colors.CYAN}Schritt 3: Inhalt{Colors.RESET}")
    print(f"{Colors.DIM}Was soll der Eintrag enthalten?{Colors.RESET}")
    content_desc = input("Beschreibung: ").strip()
    
    # Step 4: Context files
    print(f"\n{Colors.CYAN}Schritt 4: Kontext (optional){Colors.RESET}")
    file_path = input("Datei als Kontext anhängen (Enter überspringen): ").strip()
    
    # Build prompt
    prompt = f"Erstelle einen Wiki-Eintrag für '{category}/{topic}'."
    if content_desc:
        prompt += f" Inhalt: {content_desc}"
    prompt += " Strukturiere den Eintrag übersichtlich mit Markdown."
    
    # Step 5: Execute
    from tools.ai.assistant import run_ai
    
    files = {}
    if file_path:
        try:
            p = Path(file_path).expanduser().resolve()
            files[p.name] = p.read_text()
            print(f"\n{Colors.GREEN}✓ Datei geladen:{Colors.RESET} {Colors.DIM}{p.name}{Colors.RESET}")
        except Exception as e:
            print(f"\n{Colors.YELLOW}⚠ Warnung:{Colors.RESET} {e}")
    
    write = input(f"\n{Colors.CYAN}Änderungen direkt schreiben? (j/n):{Colors.RESET} ").strip().lower() == "j"
    
    print()
    print_user_input(prompt)
    
    try:
        result = run_ai(prompt, files)
        print_assistant_message(result.message)
        
        if result.options:
            print_options(result.options)
        
        if result.actions:
            from tools.ai.assistant import Action
            apply_actions(result.actions, write)
        else:
            print(f"{Colors.DIM}Keine Aktionen vorgeschlagen{Colors.RESET}\n")
    except Exception as e:
        print(f"\n{Colors.RED}✗ KI-Fehler:{Colors.RESET} {e}\n")
    
    input(f"\n{Colors.DIM}Drücke Enter zum Fortfahren...{Colors.RESET}")


def main():
    parser = argparse.ArgumentParser(description="LinkoWiki Admin - KI-gestütztes Wiki-Management")
    sub = parser.add_subparsers(dest="cmd")

    # Menu command
    sub.add_parser("menu", help="Interaktives Hauptmenü")

    # Tree command
    sub.add_parser("tree", help="Wiki-Struktur anzeigen")

    # Session commands
    sess = sub.add_parser("session", help="Session-Verwaltung")
    sess_sub = sess.add_subparsers(dest="action")

    s_start = sess_sub.add_parser("start", help="Session starten")
    s_start.add_argument("-w", "--write", action="store_true", help="Write-Modus aktivieren")

    sess_sub.add_parser("end", help="Session beenden")
    sess_sub.add_parser("status", help="Session-Status anzeigen")
    sess_sub.add_parser("shell", help="Session Shell öffnen")

    # AI command
    ai = sub.add_parser("ai", help="Einmalige KI-Abfrage")
    ai.add_argument("-p", "--prompt", required=True, help="KI-Prompt")
    ai.add_argument("-f", "--file", help="Datei als Kontext anhängen")
    ai.add_argument("-w", "--write", action="store_true", help="Write-Modus aktivieren")

    args = parser.parse_args()

    # If no command, show interactive menu
    if not args.cmd:
        interactive_menu()
        return

    if args.cmd == "menu":
        interactive_menu()
        return

    if args.cmd == "tree":
        print_tree()
        return

    if args.cmd == "session":
        if args.action == "start":
            try:
                s = start_session(write=args.write)
                mode = "write-mode" if args.write else "read-only"
                print(f"\n{Colors.GREEN}✓ Session gestartet ({mode}){Colors.RESET}")
                print(f"{Colors.DIM}  ID: {s['id']}{Colors.RESET}\n")
            except RuntimeError as e:
                print(f"\n{Colors.RED}✗ {e}{Colors.RESET}\n")
            return
        if args.action == "end":
            end_session()
            print(f"\n{Colors.GREEN}✓ Session beendet{Colors.RESET}\n")
            return
        if args.action == "status":
            s = load_session()
            if s:
                print(f"\n{Colors.BRIGHT_CYAN}{Colors.BOLD}📊 Session Status{Colors.RESET}")
                print(f"{Colors.BRIGHT_BLACK}{'─' * 70}{Colors.RESET}")
                print(json.dumps(s, indent=2))
                print()
            else:
                print(f"\n{Colors.DIM}ℹ️  Keine aktive Session{Colors.RESET}\n")
            return
        if args.action == "shell":
            session_shell()
            return

    if args.cmd == "ai":
        from tools.ai.assistant import run_ai
        
        files = {}
        if args.file:
            try:
                p = Path(args.file).expanduser().resolve()
                files[p.name] = p.read_text()
            except Exception as e:
                print(f"\n{Colors.RED}✗ Fehler beim Laden:{Colors.RESET} {e}\n")
                return
        
        try:
            result = run_ai(args.prompt, files)
            print_assistant_message(result.message)
            
            if result.options:
                print_options(result.options)
            
            if result.actions:
                from tools.ai.assistant import Action
                apply_actions(result.actions, args.write)
        except Exception as e:
            print(f"\n{Colors.RED}✗ KI-Fehler:{Colors.RESET} {e}\n")
        return

    parser.print_help()
    print()


if __name__ == "__main__":
    main()
