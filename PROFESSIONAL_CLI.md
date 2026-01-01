# 🚀 LinkoWiki Professional CLI

Enterprise-grade CLI tool mit Rich TUI, Live-Updates, und modernen Features auf dem Level von Claude Code, GitHub Copilot und Cursor.

---

## ✨ Features

### 🎨 **Professional User Interface**
- **Auto-Resizing Layout** - Passt sich automatisch an Terminal-Größe an (kein Zerreißen mehr!)
- **Rich TUI Components** - Professionelle Panels, Tables und Layouts
- **Live Progress Indicators** - Echtzeit-Feedback während AI-Processing
- **Syntax Highlighting** - Automatisches Highlighting für Code-Blöcke
- **Markdown Rendering** - Schöne Darstellung von AI-Antworten

### 🧠 **Intelligent Features**
- **Auto-Completion**
  - Slash-Commands mit `/`
  - File-Mentions mit `@`
  - Smart Suggestions basierend auf Kontext
- **File Browser** - Git-tracked Files mit Emoji-Icons
- **History Search** - Ctrl+R für History-Suche
- **Context-Aware** - Zeigt aktuelle Context-Usage und API-Limits

### 📊 **Status & Monitoring**
- **Live Task Status** - Sieht den AI-Processing-Status in Echtzeit
- **Context Usage Bar** - Zeigt % bis Truncation
- **Requests Remaining** - API-Limit Tracking
- **Git Integration** - Zeigt Branch und Dirty-Status

### ⌨️ **Keyboard Shortcuts**
- `Ctrl+C` - Exit
- `Ctrl+R` - History Search
- `Tab` - Auto-Complete
- `↑/↓` - Navigate History
- `/` - Show Slash Commands
- `@` - Show Files for Mention

---

## 📦 Installation

```bash
# Install all professional dependencies
pip install -r requirements.txt

# Or install manually:
pip install rich textual typer questionary pyfiglet prompt_toolkit
```

---

## 🚀 Usage

### **Start Professional Shell**

```bash
# New Rich-based shell (RECOMMENDED)
python tools/rich_session_shell.py

# Classic copilot CLI
python tools/copilot_cli_full.py

# Legacy session shell
linkowiki-admin session shell
```

### **Quick Start Guide**

1. **Start a conversation:**
   ```
   ❯ Hello! Can you help me refactor my code?
   ```

2. **Mention files:**
   ```
   ❯ @src/main.py explain this function
   ```
   - Type `@` and see all git-tracked files
   - Use Tab/↓ to navigate
   - Files show with emoji icons (🐍 Python, 💛 JS, etc.)

3. **Use slash commands:**
   ```
   ❯ /help              # Show all commands
   ❯ /model             # Show current model
   ❯ /attach file.py    # Attach file to context
   ❯ /clear             # Clear conversation
   ```

4. **Apply AI actions:**
   ```
   ❯ apply    # Execute pending file changes
   ❯ reject   # Cancel pending changes
   ```

---

## 🎯 Professional Features in Detail

### **1. Auto-Resizing Layout**

**Problem Solved:** Trennlinien werden beim Resize nicht mehr "zerrissen"

**How it works:**
- Rich TUI automatisch re-rendert bei SIGWINCH
- Layout passt sich dynamisch an aktuelle Terminal-Größe an
- Keine festen Breiten - alles ist responsive

**Before:**
```
────────────────────────────────────────  (80 chars)
# Terminal resize auf 40 chars
────────────────────────────────
──────────────  (zerrissen!)
```

**After:**
```
────────────────────────────────────────  (80 chars)
# Terminal resize auf 40 chars
────────────────────────────────────────  (40 chars - automatisch angepasst)
```

### **2. Live Progress Updates**

**Shows Real-Time AI Processing:**
```
⠋ Processing your request...
```

**With Task Info:**
```
● Implementing feature XYZ (Esc to cancel · 13.0 KiB)
```

### **3. Markdown & Syntax Highlighting**

**AI Responses mit Code:**
```python
# Automatically highlighted
def hello_world():
    print("Hello, World!")
```

**Tables and Lists:**
- ✅ Auto-formatted
- ✅ Proper spacing
- ✅ Professional look

### **4. File Mentions with @**

```
❯ @sr<TAB>

Suggestions:
🐍 src/main.py
🐍 src/utils.py
📝 src/README.md
```

**File Type Icons:**
- 🐍 Python (.py)
- 💛 JavaScript/TypeScript
- 📝 Markdown/Text
- ⚙️ Config (JSON/YAML)
- 📄 Other Files

### **5. Smart Slash Commands**

```
❯ /<TAB>

/help        📚 Show all commands
/model       🤖 Show/change AI model
/attach      📎 Attach file to context
/files       📁 List attached files
/clear       🧹 Clear conversation
/exit        🚪 Exit shell
```

---

## 🎨 Visual Design

### **Header Panel**
```
╭─────────────────────────────────────────────────╮
│ LinkoWiki Code Session          claude (1x)     │
│ Path: ~/projekt [main*]         Mode: Write     │
╰─────────────────────────────────────────────────╯
```

### **Conversation Display**
```
→ User question here

← Assistant response with markdown support

→ Follow-up question

← Answer with code:
  ```python
  def example():
      return "highlighted!"
  ```
```

### **Status Footer**
```
╭─────────────────────────────────────────────────╮
│ Ctrl+C Exit · Ctrl+R History    Context: 13%   │
│ /help Commands                   Remaining: 98% │
╰─────────────────────────────────────────────────╯
```

### **Pending Actions**
```
╭─ Pending Actions ─────────────────────────────╮
│ Type        Path              Description      │
│ ─────────────────────────────────────────────  │
│ WRITE       src/main.py       Add new function │
│ EDIT        src/utils.py      Refactor code    │
╰───────────────────────────────────────────────╯
Type 'apply' to execute or 'reject' to cancel
```

---

## 🔧 Technical Architecture

### **Libraries Used**

| Library | Purpose |
|---------|---------|
| `rich` | Professional TUI, auto-resize, panels |
| `prompt_toolkit` | Advanced input, completion, history |
| `textual` | Future: Full TUI framework |
| `typer` | CLI argument parsing |
| `questionary` | Interactive prompts |
| `pyfiglet` | ASCII art headers |
| `pygments` | Syntax highlighting |

### **Key Components**

```
rich_session_shell.py
├── ProfessionalCompleter     # Auto-completion engine
├── RichSessionShell          # Main shell class
│   ├── _create_header_panel()      # Dynamic header
│   ├── _create_status_footer()     # Status bar
│   ├── _create_conversation_panel()  # Chat history
│   ├── process_ai_request()        # AI interaction
│   └── run()                       # Main loop
└── main()                    # Entry point
```

### **Auto-Resize Mechanism**

```python
# Signal handler
signal.signal(signal.SIGWINCH, self._handle_resize)

# Rich automatically handles re-rendering
# No manual clearing or redrawing needed!
```

---

## 🆚 Comparison mit Competitors

| Feature | LinkoWiki Pro | Claude Code | GitHub Copilot |
|---------|--------------|-------------|----------------|
| Auto-Resize | ✅ | ✅ | ✅ |
| Syntax Highlighting | ✅ | ✅ | ✅ |
| Markdown Rendering | ✅ | ✅ | ✅ |
| File Mentions (@) | ✅ | ✅ | ✅ |
| Live Progress | ✅ | ✅ | ✅ |
| Context Usage Bar | ✅ | ✅ | ✅ |
| Git Integration | ✅ | ✅ | ✅ |
| Custom AI Models | ✅ | ❌ | ❌ |
| Local Deployment | ✅ | ❌ | ❌ |

---

## 🎓 Advanced Usage

### **Custom Model Configuration**

```bash
# Set model
❯ /model set claude-opus-4

# List available models
❯ /model list
```

### **Attach Multiple Files**

```bash
❯ /attach src/main.py src/utils.py config.json
```

### **Context Management**

```bash
# View attached files
❯ /files

# Clear context but keep conversation
❯ /clear
```

---

## 🐛 Troubleshooting

### **Auto-Completion not working**

```bash
# Install prompt_toolkit
pip install prompt_toolkit>=3.0.0
```

### **Layout issues**

```bash
# Clear and restart
❯ /clear

# Or restart shell
Ctrl+C
python tools/rich_session_shell.py
```

### **Slow performance**

```bash
# Reduce file cache size
# Edit rich_session_shell.py
# Change git ls-files to specific paths
```

---

## 📈 Roadmap

### **Coming Soon**
- [ ] Textual-based Full-Screen TUI
- [ ] Multi-pane layout (code + chat)
- [ ] Integrated Diff Viewer
- [ ] Real-time Collaboration
- [ ] Plugin System
- [ ] Themes & Customization

---

## 🤝 Contributing

Contributions welcome! Die CLI ist jetzt auf dem Level der großen Tools.

### **Development Setup**

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run tests
pytest

# Format code
black tools/

# Lint
pylint tools/
```

---

## 📄 License

MIT License - See LICENSE file

---

## 🌟 Credits

Built with:
- [Rich](https://github.com/Textualize/rich) by Textualize
- [Prompt Toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit)
- [Pydantic AI](https://github.com/pydantic/pydantic-ai)

Inspired by:
- Claude Code (Anthropic)
- GitHub Copilot
- Cursor AI

---

**Made with ❤️ for professional developers**
