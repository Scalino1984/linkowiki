Hier ist eine **vollständige ASCII-Darstellung NUR für die Eingabe im Footer**, inklusive Autocomplete-Zuständen wie `/help`, `/add-dir` und `@`.

---

## 🧩 FOOTER – ASCII-DARSTELLUNG (COPILOT-STYLE)

### 1️⃣ Leerer Prompt (Idle)

```text
~/Projekte/linko-wiki[ master*]                                              claude-sonnet-4.5 (1x)
──────────────────────────────────────────────────────────────────────────────────────────────────
> █
──────────────────────────────────────────────────────────────────────────────────────────────────
```

---

### 2️⃣ Eingabe `/help` (Command erkannt + Beschreibung)

```text
~/Projekte/linko-wiki[ master*]                                              claude-sonnet-4.5 (1x)
──────────────────────────────────────────────────────────────────────────────────────────────────
> /help█
──────────────────────────────────────────────────────────────────────────────────────────────────
  /help                         Show help for interactive commands
```

---

### 3️⃣ Eingabe `/add-dir` (Autocomplete + Liste)

```text
~/Projekte/linko-wiki[ master*]                                              claude-sonnet-4.5 (1x)
──────────────────────────────────────────────────────────────────────────────────────────────────
> /add-dir█
──────────────────────────────────────────────────────────────────────────────────────────────────
▌ /add-dir <directory>        Add a directory to the allowed list for file access
  /clear                      Clear the conversation history
  /cwd [directory]            Change working directory or show current directory
  /exit, /quit                Exit the CLI
  /feedback                   Provide feedback about the CLI
  /help                       Show help for interactive commands
  /list-dirs                  Display all allowed directories for file access
  /login                      Log in to Copilot
  /logout                     Log out of Copilot
  /mcp [show|add|edit|...]    Manage MCP server configuration
```

**Legende:**

* `▌` = aktuell fokussierter Eintrag
* Linke Spalte = Befehl
* Rechte Spalte = Beschreibung
* Monospace, strikt linksbündig

---

### 4️⃣ Eingabe `@` (File/Directory-Picker)

```text
~/Projekte/linko-wiki[ master*]                                              claude-sonnet-4.5 (1x)
──────────────────────────────────────────────────────────────────────────────────────────────────
> @█
──────────────────────────────────────────────────────────────────────────────────────────────────
▌ @[DIR]  /home/astier/Projekte/linko-wiki
  @[DIR]  /tmp
  @.dockerignore
  @.env.example
  @.github/workflows/pydanticai-conformance.yml
  @.github/workflows/tests-macos.yml
  @.github/workflows/tests-ubuntu.yml
  @.gitignore
  @.linkowiki-session.json
  @.venv/include/site/python3.11/greenlet/greenlet.h
```

---

### 5️⃣ Eingabe `@<pfad>` (gefiltert)

```text
~/Projekte/linko-wiki[ master*]                                              claude-sonnet-4.5 (1x)
──────────────────────────────────────────────────────────────────────────────────────────────────
> @.git█
──────────────────────────────────────────────────────────────────────────────────────────────────
▌ @.gitignore
  @.github/workflows/pydanticai-conformance.yml
  @.github/workflows/tests-macos.yml
  @.github/workflows/tests-ubuntu.yml
```

---

## 📌 Semantik für Agenten (wichtig)

```text
PROMPT-ZEILE:
> <eingabe>

AUTOCOMPLETE:
- erscheint DIREKT unter der Eingabe
- über volle Terminalbreite
- scrollbar (implizit)
- Fokus durch ▌
- @ = Filesystem-Kontext
- / = Command-Kontext
```
