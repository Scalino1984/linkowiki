# LinkoWiki Configuration Guide 🔧

## 📁 Config-Datei: `etc/linkowiki.conf`

Die zentrale Konfigurationsdatei für alle LinkoWiki-Einstellungen.

### Format

Standard INI-Format mit Sektionen und Key-Value-Paaren:

```ini
[section]
key = value
```

---

## 🎯 Verfügbare Einstellungen

### [ai] - AI-Provider-Einstellungen

```ini
[ai]
# Default AI provider für neue Sessions
# Muss einem Provider in etc/providers.json entsprechen
default_provider = openai-gpt4o

# Standard-Temperatur für Non-Reasoning-Modelle (0.0 - 2.0)
default_temperature = 0.3

# Standard-Reasoning-Effort für Reasoning-Modelle (low, medium, high)
default_reasoning_effort = medium
```

**Werte:**
- `default_provider`: Jeder `id` aus `providers.json`
- `default_temperature`: 0.0 (deterministisch) bis 2.0 (kreativ)
- `default_reasoning_effort`: `low`, `medium`, `high`

---

### [session] - Session-Verwaltung

```ini
[session]
# Maximale Anzahl History-Einträge
max_history = 100

# Auto-Save nach jeder Interaktion
auto_save = true

# Standard-Modus für neue Sessions (read oder write)
default_mode = read
```

**Werte:**
- `max_history`: Positive Ganzzahl
- `auto_save`: `true` oder `false`
- `default_mode`: `read` oder `write`

---

### [wiki] - Wiki-Einstellungen

```ini
[wiki]
# Root-Verzeichnis für Wiki-Content
wiki_root = wiki

# Standard-Kategorie für unkategorisierte Einträge
default_category = general

# Maximale Dateigröße für Wiki-Einträge (in KB)
max_file_size = 500
```

**Werte:**
- `wiki_root`: Relativer oder absoluter Pfad
- `default_category`: String
- `max_file_size`: Positive Ganzzahl (KB)

---

### [ui] - Benutzeroberfläche

```ini
[ui]
# Terminal-Breite für Formatierung (0 = auto-detect)
terminal_width = 0

# Farbige Ausgabe aktivieren
colors = true

# Vollständige Error-Traces anzeigen
debug = false
```

**Werte:**
- `terminal_width`: 0 (auto) oder Ganzzahl (z.B. 80, 120)
- `colors`: `true` oder `false`
- `debug`: `true` oder `false`

---

### [export] - Export-Einstellungen

```ini
[export]
# Standard-Verzeichnis für Session-Exports
export_dir = session_exports

# Export-Format (markdown, json, html)
export_format = markdown
```

**Werte:**
- `export_dir`: Relativer oder absoluter Pfad
- `export_format`: `markdown`, `json`, `html`

---

## 🔧 Verwendung

### Config laden (Python):

```python
from tools.config import get_config

config = get_config()

# Properties verwenden
provider = config.default_provider
temperature = config.default_temperature
wiki_root = config.wiki_root

# Werte setzen
config.set('ai', 'default_provider', 'openai-o1')
config.save()
```

### Config ändern (manuell):

```bash
# Config-Datei editieren
vim etc/linkowiki.conf

# Änderungen werden beim nächsten Start geladen
linkowiki-admin session shell
```

---

## 💡 Best Practices

### 1. **Provider-Wechsel**

Statt Provider in Session zu wechseln, kannst du den Default ändern:

```ini
[ai]
default_provider = openai-o1  # Jetzt nutzen neue Sessions O1
```

### 2. **Debug-Modus**

Bei Problemen aktiviere Debug:

```ini
[ui]
debug = true
```

Jetzt siehst du vollständige Stack-Traces.

### 3. **Read-Only Default**

Für Sicherheit:

```ini
[session]
default_mode = read  # Sessions starten im Read-only-Modus
```

### 4. **Custom Wiki-Location**

Wenn Wiki woanders liegt:

```ini
[wiki]
wiki_root = /home/user/my-wiki
```

---

## 🔄 Config-Migration

### Von v2 zu v3:

Die Config-Datei wird automatisch erstellt beim ersten Start von v3.

**Alte Sessions:** Werden automatisch migriert und nutzen `default_provider` aus Config.

**Neue Sessions:** Nutzen alle Settings aus `linkowiki.conf`.

---

## 📊 Beispiel-Konfigurationen

### Entwickler-Setup (Debug + Write):

```ini
[ai]
default_provider = openai-gpt4o-mini  # Günstig für Tests

[session]
default_mode = write  # Direktes Schreiben

[ui]
debug = true  # Vollständige Errors
```

### Produktions-Setup (Safe):

```ini
[ai]
default_provider = anthropic-claude-3-5-sonnet  # Stabil

[session]
default_mode = read  # Sicherer Start

[ui]
debug = false  # Keine Tech-Details
```

### Reasoning-Setup (Complex Tasks):

```ini
[ai]
default_provider = openai-o1  # Reasoning-Power
default_reasoning_effort = high  # Maximum denken

[session]
max_history = 200  # Mehr Kontext
```

---

## 🚨 Fehlerbehebung

### Config wird nicht geladen:

```bash
# Prüfe Pfad
ls -la etc/linkowiki.conf

# Prüfe Syntax
cat etc/linkowiki.conf

# Neu erstellen
rm etc/linkowiki.conf
linkowiki-admin  # Erstellt neue Default-Config
```

### Falscher Provider:

```
ValueError: Unknown provider: wrong-provider
```

**Lösung:** Check `default_provider` gegen `etc/providers.json`:

```bash
# Zeige verfügbare Provider
linkowiki-admin session shell
:model list
```

### Permission-Fehler:

```bash
# Config-File muss lesbar sein
chmod 644 etc/linkowiki.conf
```

---

## 🔮 Geplante Features

- [ ] **Multi-Profile** - Verschiedene Configs (dev, prod)
- [ ] **Config CLI** - `linkowiki-admin config set ai.default_provider openai-o1`
- [ ] **Config Validation** - Automatische Prüfung beim Start
- [ ] **Config Export/Import** - Configs zwischen Systemen teilen
- [ ] **Environment-Overrides** - `LINKOWIKI_DEFAULT_PROVIDER=...`

---

## 📖 Siehe auch

- [PROVIDERS.md](PROVIDERS.md) - Provider-System
- [SESSION_AI.md](SESSION_AI.md) - Session-Shell
- [FEATURES.md](FEATURES.md) - Feature-Übersicht

---

**Version:** 3.0  
**Datum:** 2026-01-01
