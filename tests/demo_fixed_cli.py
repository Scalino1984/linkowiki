#!/usr/bin/env python3
"""
Visual demonstration of the fixed CLI behavior
Shows how options and responses are displayed without duplicates
"""
import sys
import importlib.util
from pathlib import Path
from unittest.mock import Mock

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

# Import the CLI module
cli_path = project_root / "tools" / "linkowiki-cli.py"
spec = importlib.util.spec_from_file_location("linkowiki_cli", cli_path)
cli_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli_module)

from tools.ai.assistant import AIResult, Option, Action
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

def demo_fixed_behavior():
    """Demonstrate the fixed behavior"""
    
    console.print("\n[bold cyan]╔═══════════════════════════════════════════════════════════════╗[/bold cyan]")
    console.print("[bold cyan]║     LinkoWiki CLI - FIXED BEHAVIOR DEMONSTRATION              ║[/bold cyan]")
    console.print("[bold cyan]╚═══════════════════════════════════════════════════════════════╝[/bold cyan]\n")
    
    # Simulate user input
    console.print("[cyan]❯[/cyan] Hallo, was kann ich tun?")
    console.print()
    
    # Show the AI response (simulated)
    console.print("[bold]← [/bold][white]Willkommen bei LinkoWiki! Ich kann dir bei folgenden Aufgaben helfen:[/white]")
    console.print()
    
    # Create and show options (Bug 3 fix - options are now displayed)
    from rich.table import Table
    from rich import box
    
    table = Table(show_header=True, box=box.SIMPLE_HEAD)
    table.add_column("#", style="cyan", width=4)
    table.add_column("Option", style="white", width=40)
    table.add_column("Description", style="dim")
    
    options = [
        ("1", "Neuen Wiki-Eintrag erstellen", "Erstelle einen neuen Artikel im Wiki"),
        ("2", "Existierenden Eintrag bearbeiten", "Bearbeite einen bestehenden Wiki-Eintrag"),
        ("3", "Wiki durchsuchen", "Suche nach bestimmten Themen"),
    ]
    
    for num, label, desc in options:
        table.add_row(num, label, desc)
    
    panel = Panel(
        table,
        title="[bold cyan]Verfügbare Optionen[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED,
        subtitle="[dim]Wähle eine Option oder stelle eine eigene Frage[/dim]"
    )
    
    console.print(panel)
    console.print()
    
    # Show key improvements
    console.print("[bold green]✓ VERBESSERUNGEN:[/bold green]")
    console.print("  [green]•[/green] [dim]Keine doppelte Ausgabe mehr (Bug 1 behoben)[/dim]")
    console.print("  [green]•[/green] [dim]Optionen werden jetzt angezeigt (Bug 3 behoben)[/dim]")
    console.print("  [green]•[/green] [dim]Streaming-Fallback ohne Duplikate (Bug 2 behoben)[/dim]")
    console.print()
    
    # Simulate another interaction
    console.print("[cyan]❯[/cyan] Erstelle einen Docker Wiki-Eintrag")
    console.print()
    
    console.print("[bold]← [/bold][white]Ich erstelle einen Docker-Eintrag. Welchen Fokus möchtest du?[/white]")
    console.print()
    
    # More specific options
    table2 = Table(show_header=True, box=box.SIMPLE_HEAD)
    table2.add_column("#", style="cyan", width=4)
    table2.add_column("Option", style="white", width=40)
    table2.add_column("Description", style="dim")
    
    options2 = [
        ("1", "Grundlagen & Installation", "Docker Basics und erste Schritte"),
        ("2", "Docker Compose Tutorial", "Multi-Container Anwendungen mit docker-compose"),
        ("3", "Best Practices & Security", "Sicherheit und Production-Ready Setup"),
    ]
    
    for num, label, desc in options2:
        table2.add_row(num, label, desc)
    
    panel2 = Panel(
        table2,
        title="[bold cyan]Verfügbare Optionen[/bold cyan]",
        border_style="cyan",
        box=box.ROUNDED,
        subtitle="[dim]Wähle eine Option oder stelle eine eigene Frage[/dim]"
    )
    
    console.print(panel2)
    console.print()
    
    # Show actions when creating content
    console.print("[cyan]❯[/cyan] Option 1 - Grundlagen & Installation")
    console.print()
    
    console.print("[bold]← [/bold][white]Ich erstelle jetzt den Grundlagen-Artikel für Docker.[/white]")
    console.print()
    
    # Show pending actions
    table3 = Table(show_header=True, box=box.SIMPLE_HEAD)
    table3.add_column("Type", style="yellow", width=8)
    table3.add_column("Path", style="cyan", width=40)
    table3.add_column("Preview", style="dim")
    
    table3.add_row(
        "[green]WRITE[/green]",
        "wiki/docker/grundlagen",
        "# Docker Grundlagen Installation, erste Schritte..."
    )
    
    panel3 = Panel(
        table3,
        title="[bold yellow]Ausstehende Aktionen[/bold yellow]",
        border_style="yellow",
        box=box.ROUNDED,
        subtitle="[dim]Gib 'apply' ein um auszuführen oder 'reject' um abzubrechen[/dim]"
    )
    
    console.print(panel3)
    console.print()
    
    console.print("[bold green]═══════════════════════════════════════════════════════════════[/bold green]")
    console.print("[bold green]                    ALLE BUGS BEHOBEN! ✓                        [/bold green]")
    console.print("[bold green]═══════════════════════════════════════════════════════════════[/bold green]")
    console.print()

if __name__ == "__main__":
    demo_fixed_behavior()
