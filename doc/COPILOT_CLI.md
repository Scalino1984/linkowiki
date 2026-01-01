# Copilot-Style CLI Implementation

## Overview

LinkoWiki's session shell now uses a **full Copilot-style CLI** design based on GitHub Copilot CLI specifications.

## Visual Structure

```text
┌───────────────────────────────────────────────────────────────────────────┐
│ ~/path[ branch*]                             model-name (1x)             │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│   CODE / DIFF / TEXT                                                      │
│                                                                           │
│ ● Running task description (Esc to cancel · X KiB)                        │
│                                                                           │
├───────────────────────────────────────────────────────────────────────────┤
│ ~/path[ branch*]                   model-name (1x)   XX% to truncation   │
├───────────────────────────────────────────────────────────────────────────┤
│ > █                                                                        │
│ Ctrl+C Exit · Ctrl+R Expand recent        Remaining requests: XX.X%        │
└───────────────────────────────────────────────────────────────────────────┘
```

## Components

### 1. Upper Status Bar (Header)
```text
~/Projekte/linko-wiki[ master*]                      claude-sonnet-4.5 (1x)
```

- **Left**: Shortened CWD + Git branch with dirty indicator (*)
- **Right**: Active model name + parallelism factor
- **Color**: DIM/gray
- **Width**: Full terminal width, dynamic spacing

### 2. Separator Lines
```text
──────────────────────────────────────────────────────────────────────────────
```

- **Character**: Unicode U+2500 (─)
- **Width**: Full terminal width
- **Purpose**: Visual structure separation

### 3. Content Area

**Code Diff Display**:
```text
 192     pending = len(session.get('pending_actions', []))
-161     print(f"\n{Colors.CYAN}linkowiki session{Colors.RESET}")
+194     # Git branch
+195     git_branch = get_git_branch()
```

- `-` prefix: Removed lines (RED)
- `+` prefix: Added lines (GREEN)
- ` ` prefix: Context lines (DIM)
- Line numbers on left

### 4. Live Task Status
```text
● Implementing Copilot-style CLI design (Esc to cancel · 13.0 KiB)
```

- **Indicator**: ● (colored MAGENTA)
- **Text**: Dynamic task description
- **Actions**: "Esc to cancel"
- **Info**: Size or progress indicator

### 5. Lower Status Bar (Footer)
```text
~/path[ branch*]                   model-name (1x)   13% to truncation
```

- **Left**: Same as header (CWD + branch)
- **Middle**: Model info
- **Right**: Context window usage percentage

### 6. Input Prompt
```text
> Enter @ to mention files or / for commands
```

When typing:
```text
> /help█
```

- **Prompt**: `>` character
- **Cursor**: Block █
- **Placeholder**: Only when empty (DIM)

### 7. Global Help Bar
```text
Ctrl+C Exit · Ctrl+R Expand recent        Remaining requests: 98.2%
```

- **Left**: Keyboard shortcuts
- **Right**: API quota remaining
- **Always visible**: Bottom line
- **Color**: DIM

## Implementation Files

### Core CLI
- `tools/copilot_cli_full.py` - Full Copilot CLI implementation with demos
- `tools/copilot_shell.py` - Original prototype
- `tools/copilot_context.py` - Context usage tracking

### Integration
- `tools/linkowiki-admin.py` - Main CLI tool with Copilot-style session shell
- Uses Copilot components for rendering

## Features

### Dynamic Sizing
- All components adapt to terminal width
- Headers/footers stay visually aligned
- Content area scrolls independently

### Context Tracking
```python
from tools.copilot_context import get_context_tracker

tracker = get_context_tracker()
tracker.update(1500)  # Used 1500 tokens
print(tracker.get_display_string())  # "87% to truncation"
```

### Live Status
```python
cli.start_task("Processing wiki entries", "42.3 KiB")
# Shows: ● Processing wiki entries (Esc to cancel · 42.3 KiB)

cli.stop_task()
# Removes status line
```

### Color Scheme
- **BRIGHT_WHITE**: Active items, important text
- **DIM**: Secondary info, placeholders
- **RED**: Removed lines, errors
- **GREEN**: Added lines, success
- **MAGENTA**: Active tasks
- **YELLOW**: Warnings

## Usage

### Start Session
```bash
python tools/linkowiki-admin.py session start -w
python tools/linkowiki-admin.py session shell
```

### Run Demo
```bash
python tools/copilot_cli_full.py
```

Shows 5 demo views:
1. Empty state
2. Code diff display
3. Active task
4. User input
5. High context usage

## Technical Details

### No curses Required
- Pure `print()` statements
- ANSI escape codes for colors
- Works in any terminal
- No special dependencies

### Header Rendering
```python
def _render_header(self) -> str:
    left = f"{cwd}[ {branch}]"
    right = f"{model} (1x)"
    spacing = term_width - len(left) - len(right)
    return f"{left}{' ' * spacing}{right}"
```

### Footer with Context
```python
def _render_footer_status(self) -> str:
    left = f"{cwd}[ {branch}]"
    middle = f"{model} (1x)"
    right = f"{usage}% to truncation"
    # Calculate dynamic spacing
    return formatted_line
```

## Configuration

### Model Display
Default extracts short name:
- `openai-gpt5-text` → `gpt5-text`
- `anthropic-claude-3-5-sonnet` → `claude-3-5-sonnet`

Customize in session:
```python
cli.model_name = "custom-model-name"
cli.model_count = "2x"  # Parallelism factor
```

### Context Limits
```python
from tools.copilot_context import ContextTracker

tracker = ContextTracker(max_tokens=200000)  # 200k context window
```

### Quota Tracking
```python
from tools.copilot_context import RequestQuotaTracker

quota = RequestQuotaTracker(max_requests=1000)
quota.increment()  # Track each request
```

## Benefits

1. **Professional**: Matches GitHub Copilot CLI exactly
2. **Informative**: Shows context usage, git status, quotas
3. **Clean**: Minimal, focused design
4. **Dynamic**: Adapts to terminal size
5. **No Dependencies**: Pure Python + ANSI codes

## Future Enhancements

### Interactive Autocomplete
Add `prompt_toolkit` for:
- @ file picker with fuzzy search
- / command completion
- Arrow key navigation

### Streaming Output
Real-time updates during AI responses:
- Progressive diff display
- Live token counting
- Animated task indicator

### Split View
Top: Code diff
Bottom: Input + AI response in real-time

## References

- Design specification: `design.md`
- Original implementation: PydanticAI v2 architecture
- Inspired by: GitHub Copilot CLI
