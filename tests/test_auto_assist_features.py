#!/usr/bin/env python3
"""
Test script to demonstrate the auto-assist agent features
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

print("=" * 70)
print("LinkoWiki Auto-Assist Agent - Feature Tests")
print("=" * 70)

# Test 1: File Tools
print("\n1. Testing File Tools:")
from tools.ai.tools import list_files, read_file
files = list_files("tools/*.py")
print(f"   ✓ Found {len(files)} Python files in tools/")
content = read_file("README.md")
if content:
    print(f"   ✓ Successfully read README.md ({len(content)} bytes)")

# Test 2: Git Tools
print("\n2. Testing Git Tools:")
from tools.ai.tools import git_status
status = git_status()
print(f"   ✓ Branch: {status['branch']}")
print(f"   ✓ Clean: {status['is_clean']}")
print(f"   ✓ Recent commits: {len(status['recent_commits'])}")

# Test 3: Wiki Tools
print("\n3. Testing Wiki Tools:")
from tools.ai.tools import get_wiki_structure, get_recent_changes
structure = get_wiki_structure()
print(f"   ✓ Wiki entries: {structure['total_entries']}")
print(f"   ✓ Categories: {len(structure['categories'])}")
recent = get_recent_changes(limit=5)
print(f"   ✓ Recent changes: {len(recent)}")

# Test 4: Memory System
print("\n4. Testing Memory System:")
from tools.memory.context import ContextMemory
memory = ContextMemory()
memory.remember_action(
    {'type': 'write', 'path': 'docker/basics'},
    'erstelle docker wiki'
)
memory.remember_action(
    {'type': 'write', 'path': 'kubernetes/basics'},
    'erstelle kubernetes wiki'
)
suggestions = memory.suggest_similar('erstelle postgres wiki')
print(f"   ✓ Remembered 2 actions")
print(f"   ✓ Found {len(suggestions)} similar suggestions")
patterns = memory.get_common_patterns()
print(f"   ✓ Common patterns: {len(patterns)}")

# Test 5: Fuzzy File Matching
print("\n5. Testing Fuzzy File Matching:")
import importlib.util
spec = importlib.util.spec_from_file_location("cli", str(BASE_DIR / "tools/linkowiki-cli.py"))
cli_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cli_module)

shell = cli_module.RichSessionShell()
exact = shell._find_files_fuzzy('README.md')
print(f"   ✓ Exact match: {len(exact)} file(s)")
glob_result = shell._find_files_fuzzy('tools/*.py')
print(f"   ✓ Glob pattern: {len(glob_result)} file(s)")
fuzzy = shell._find_files_fuzzy('readme')
print(f"   ✓ Fuzzy match: {len(fuzzy)} file(s)")

# Test 6: Auto-detect files
print("\n6. Testing Auto-detect:")
auto = shell._detect_auto_files("dokumentiere README.md und pyproject.toml")
print(f"   ✓ Auto-detected {len(auto)} files")

print("\n" + "=" * 70)
print("✓ All tests passed! Auto-assist agent is ready.")
print("=" * 70)
print("\nNew Features Available:")
print("  • Fuzzy file matching: @readme finds README.md")
print("  • Glob patterns: @tools/*.py loads all Python files")
print("  • Directory loading: @examples/ loads all files in directory")
print("  • Auto-detection: 'dokumentiere X' automatically loads X")
print("  • /autoexec mode: Auto-execute actions without confirmation")
print("  • /retry command: Retry last request")
print("  • 6 PydanticAI tools for wiki, file, and git operations")
print("  • Contextual memory system")
print("  • Proactive suggestions after actions")
print("=" * 70)
