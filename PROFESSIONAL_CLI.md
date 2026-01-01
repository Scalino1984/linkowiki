# 🚀 LinkoWiki Professional CLI

Enterprise-grade CLI tool mit Rich TUI, Live-Updates, und modernen Features auf dem Level von Claude Code, GitHub Copilot und Cursor.

---

## ✨ Features

### 🎨 **Professional User Interface**
- **Auto-Resizing Layout** - Passt sich automatisch an Terminal-Größe an (kein Zerreißen mehr!)
- **Rich TUI Components** - Professionelle Panels, Tables und Layouts mit echten Line-Drawing Characters
- **Proper Separator Lines** - Verwendet Rich Rule für echte horizontale Linien (nicht text-basiert!)
- **Live Progress Indicators** - Echtzeit-Feedback während AI-Processing
- **Syntax Highlighting** - Automatisches Highlighting für Code-Blöcke
- **Markdown Rendering** - Schöne Darstellung von AI-Antworten
- **Streaming Output** - Live AI-Antworten wie bei Copilot/Claude

### 🧠 **Intelligent Features**
- **Auto-Completion**
  - Slash-Commands mit `/`
  - File-Mentions mit `@`
  - Smart Suggestions basierend auf Kontext
- **Automatic File Reading** - Files werden automatisch gelesen bei `@file` Mentions!
- **File Browser** - Git-tracked Files mit Emoji-Icons
- **History Search** - Ctrl+R für History-Suche + `/search` Command
- **Context-Aware** - Zeigt aktuelle Context-Usage und API-Limits
- **Conversation Search** - Suche in der Conversation-History mit `/search`

### 📊 **Status & Monitoring**
- **Live Task Status** - Sieht den AI-Processing-Status in Echtzeit
- **Context Usage Bar** - Zeigt % bis Truncation
- **Requests Remaining** - API-Limit Tracking
- **Git Integration** - Zeigt Branch und Dirty-Status
- **File Attachments** - Zeigt angehängte Dateien mit `/files`

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
python tools/linkowiki-cli.py

# Or use the alias
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

2. **Mention files - they are automatically read!:**
   ```
   ❯ @src/main.py explain this function
   ```
   - Type `@` and see all git-tracked files
   - Use Tab/↓ to navigate
   - Files show with emoji icons (🐍 Python, 💛 JS, etc.)
   - **Files are automatically loaded - kein manuelles Lesen nötig!**

3. **Use slash commands:**
   ```
   ❯ /help              # Show all commands
   ❯ /model             # Show current model
   ❯ /attach file.py    # Manually attach file to context
   ❯ /files             # Show attached files
   ❯ /search query      # Search conversation history
   ❯ /stream on         # Enable streaming output
   ❯ /clear             # Clear conversation
   ```

4. **Apply AI actions:**
   ```
   ❯ apply    # Execute pending file changes
   ❯ reject   # Cancel pending changes
   ```

---

## 🎯 Professional Features in Detail

### **1. Auto-Resizing Layout mit echten Linien**

**Problem Solved:** Trennlinien werden beim Resize nicht mehr "zerrissen" UND sind echte terminal lines!

**How it works:**
- Rich TUI automatisch re-rendert bei SIGWINCH
- Layout passt sich dynamisch an aktuelle Terminal-Größe an
- **Rich Rule** für echte horizontale Linien (keine Text-Characters wie "────")
- Keine festen Breiten - alles ist responsive

**Before:**
```
────────────────────────────────────────  (text-based, 80 chars)
# Terminal resize auf 40 chars
────────────────────────────────
──────────────  (zerrissen!)
```

**After:**
```
────────────────────────────────────────  (Rich Rule, auto-sized)
# Terminal resize auf 40 chars
────────────────────────────────────────  (automatically adjusted!)
```

### **2. Automatic File Reading**

**Problem Solved:** Files müssen nicht manuell gelesen werden!

**How it works:**
- Beim Tippen von `@filename` wird die Datei automatisch erkannt
- Datei wird vom Filesystem gelesen
- Content wird automatisch an den AI-Kontext angehängt
- User sieht: `📎 Loaded: filename`

**Example:**
```
❯ @examples/pydanticai_v2_examples.py erstelle ein wiki
📎 Loaded: examples/pydanticai_v2_examples.py

← Assistant kann jetzt den Dateiinhalt lesen und verarbeiten!
```

### **3. Streaming Output**

**Shows Real-Time AI Processing like Copilot/Claude:**
```
❯ Your question here

← Response appears word-by-word in real-time...
```

**Toggle streaming:**
```
❯ /stream off   # Disable for complete responses
❯ /stream on    # Enable for live output
```

### **4. Live Progress Updates**

**Shows Real-Time AI Processing:**
```
⠋ Processing your request...
```

**With Task Info:**
```
● Implementing feature XYZ (Esc to cancel · 13.0 KiB)
```

### **5. Markdown & Syntax Highlighting**

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

### **6. File Mentions with @ - Now with Auto-Loading!**

```
❯ @sr<TAB>

Suggestions:
🐍 src/main.py
🐍 src/utils.py
📝 src/README.md

# Select one and it's AUTOMATICALLY LOADED!
📎 Loaded: src/main.py
```

**File Type Icons:**
- 🐍 Python (.py)
- 💛 JavaScript/TypeScript
- 📝 Markdown/Text
- ⚙️ Config (JSON/YAML)
- 📄 Other Files

### **7. Smart Slash Commands**

```
❯ /<TAB>

/help        📚 Show all commands
/model       🤖 Show/change AI model
/attach      📎 Attach file to context
/files       📁 List attached files
/search      🔍 Search conversation history
/stream      🌊 Toggle streaming output
/clear       🧹 Clear conversation
/exit        🚪 Exit shell
```

### **8. Conversation Search**

```
❯ /search error handling

Search Results for 'error handling'
┌───┬───────────┬──────────────────────────────────────┐
│ # │ Role      │ Content                              │
├───┼───────────┼──────────────────────────────────────┤
│ 2 │ User      │ How to add error handling to...      │
│ 3 │ Assistant │ For error handling, use try-catch... │
└───┴───────────┴──────────────────────────────────────┘
```

### **9. Better Action Previews**

**With Syntax Highlighting:**
```python
╭─ Preview: src/main.py ─────────────────╮
│  1  def new_function():                 │
│  2      """Added by AI"""               │
│  3      return "Hello"                  │
╰─────────────────────────────────────────╯
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
| Real Terminal Lines | ✅ (Rich Rule) | ✅ | ✅ |
| Syntax Highlighting | ✅ | ✅ | ✅ |
| Markdown Rendering | ✅ | ✅ | ✅ |
| File Mentions (@) | ✅ | ✅ | ✅ |
| **Auto File Reading** | ✅ **NEW!** | ✅ | ✅ |
| Live Streaming Output | ✅ **NEW!** | ✅ | ✅ |
| Conversation Search | ✅ **NEW!** | ✅ | ❌ |
| Live Progress | ✅ | ✅ | ✅ |
| Context Usage Bar | ✅ | ✅ | ✅ |
| Git Integration | ✅ | ✅ | ✅ |
| Action Previews | ✅ **NEW!** | ✅ | ✅ |
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
