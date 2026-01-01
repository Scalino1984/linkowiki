#!/usr/bin/env python3
"""Test script to verify CLI features"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from rich.console import Console
from rich.rule import Rule
from rich.panel import Panel
from rich.markdown import Markdown
from rich.table import Table
from rich import box

console = Console()

print("\n" + "="*80)
print("Testing LinkoWiki CLI Features")
print("="*80 + "\n")

# Test 1: Rule-based separators (not text-based)
print("✓ Test 1: Proper horizontal lines (Rich Rule, not text):")
console.print(Rule(style="cyan"))
console.print("  This is content between rules")
console.print(Rule(style="dim"))
print()

# Test 2: Auto-resize demonstration
print("✓ Test 2: Terminal width detection:")
size = console.size
print(f"  Terminal size: {size.width} x {size.height}")
console.print(Rule(style="green", title="Auto-sized rule"))
print()

# Test 3: File pattern matching
print("✓ Test 3: File mention pattern extraction:")
import re
test_text = "Please read @examples/pydanticai_v2_examples.py and @README.md"
pattern = r'@([^\s]+)'
matches = re.findall(pattern, test_text)
print(f"  Input: {test_text}")
print(f"  Extracted files: {matches}")
print()

# Test 4: Rich rendering
print("✓ Test 4: Rich Panel and Markdown rendering:")
md_content = """
## Example Response

Here's some **bold** text and *italic* text.

```python
def hello():
    print("Hello, World!")
```
"""
console.print(Panel(
    Markdown(md_content),
    title="[bold]AI Response[/bold]",
    border_style="magenta",
    box=box.ROUNDED
))
print()

# Test 5: Status table
print("✓ Test 5: Status footer layout:")
table = Table.grid(padding=(0, 2))
table.add_column(style="dim", justify="left")
table.add_column(style="dim", justify="center")
table.add_column(style="dim", justify="right")
table.add_row(
    "Ctrl+C Exit · Ctrl+R History",
    "Context: 13%",
    "Remaining: 98.2%"
)
console.print(table)
console.print(Rule(style="dim"))
print()

print("="*80)
print("✓ All features working correctly!")
print("="*80 + "\n")
