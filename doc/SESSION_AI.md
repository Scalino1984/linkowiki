# LinkoWiki Session & AI Integration

## ✅ Implementierte Features

### 1. Session Management (`tools/session/manager.py`)
- ✅ Session starten/beenden
- ✅ Session-Status abfragen
- ✅ History-Tracking
- ✅ Dateien an Session anhängen
- ✅ Write-Mode Toggle
- ✅ **NEU: Changes-Tracking** (`record_change()`)

### 2. AI Integration (`tools/ai/assistant.py`)
- ✅ pydanticai v2 Agent
- ✅ Strukturierte Actions (create, append)
- ✅ Lazy initialization (API-Key wird nur bei Bedarf geprüft)
- ✅ Kontextbasierte Prompts

### 3. CLI (`tools/linkowiki-admin.py`)
- ✅ `tree` - Wiki-Struktur anzeigen
- ✅ `session start [-w]` - Session starten (optional mit Write-Mode)
- ✅ `session end` - Session beenden
- ✅ `session status` - Session-Status
- ✅ `session shell` - Interaktive Shell
- ✅ `ai -p PROMPT [-f FILE] [-w]` - Direkte AI-Befehle
- ✅ **NEU: Changelog** - Automatisches Logging aller Änderungen
- ✅ **NEU: Guardrails** - Sicherheitsvalidierung für alle Actions

### 4. Web-Integration (`bin/ai_endpoint.py`)
- ✅ Flask-Endpoint `/ai` für AI-Anfragen
- ✅ Session-basierte Authentifizierung
- ✅ JSON-API für strukturierte Rückgaben

## 📋 Verwendung

### Session starten
```bash
tools/linkowiki-admin.py session start --write
```

### Session Shell (interaktiv)
```bash
tools/linkowiki-admin.py session shell
```

In der Shell:
- `:tree` - Struktur anzeigen
- `:attach <datei>` - Datei anhängen
- `:files` - **NEU:** Angehängte Dateien auflisten
- `:write on` - **NEU:** Write-Modus aktivieren
- `:write off` - **NEU:** Write-Modus deaktivieren
- Beliebiger Text - An AI senden
- `exit` - Shell beenden

### Direkter AI-Befehl
```bash
tools/linkowiki-admin.py ai -p "erstelle wiki eintrag" -f README.md -w
```

## 🔒 Sicherheit

### Guardrails (automatisch)
- ✅ **Path Traversal Protection** - Keine `..` in Pfaden
- ✅ **Absolute Path Protection** - Keine `/` am Anfang
- ✅ **Directory Protection** - Keine Verzeichnisse überschreiben
- ✅ **Size Limits** - Maximale Inhaltsgröße: 50 KB

### Bestätigungsflow
- **Dry-Run**: Alle Änderungen werden zunächst angezeigt
- **Bestätigung**: Bei Write-Mode wird Bestätigung verlangt
- **Read-Only Default**: Session startet im Read-Only Mode

### Changelog
Alle Änderungen werden automatisch in `wiki/.changelog` protokolliert:
```
[2026-01-01T13:25:43] source=ai
  create linux/commands
  append prompts/git
```

## 🧪 Getestet

- ✅ Session-Lifecycle
- ✅ History-Tracking
- ✅ File-Attachment
- ✅ CLI-Befehle
- ✅ Error-Handling
- ✅ AI-Module Import
- ✅ **NEU: Guardrails** (Path traversal, absolute paths, size limits)
- ✅ **NEU: Changelog** (Format, Schreiben)
- ✅ **NEU: Session Changes** (Tracking)
- ✅ **NEU: Session Commands** (`:write on/off`, `:files`)

## 🌐 Web-Integration

### AI-Endpoint verwenden
```bash
# Session starten
tools/linkowiki-admin.py session start --write

# Server starten
./start-wiki

# AI-Anfrage senden
curl -X POST http://localhost:8002/ai \
  -H "Content-Type: application/json" \
  -d '{"prompt": "erstelle wiki eintrag für git"}'
```

## ⚠️ Voraussetzungen

Für AI-Features:
```bash
# .env oder Environment Variable
export OPENAI_API_KEY=your-key-here
```

Oder andere pydanticai-kompatible Provider konfigurieren.

## 📁 Neue Dateien

- `wiki/.changelog` - Automatisches Änderungsprotokoll
- `bin/ai_endpoint.py` - Flask AI-Endpoint
- `.env.example` - Beispiel-Konfiguration
- `doc/SESSION_AI.md` - Diese Dokumentation

## 🎯 Nächste mögliche Erweiterungen

1. **Undo-Funktionalität** - Änderungen rückgängig machen
2. **Strikte Kategorien** - Whitelist für erlaubte Pfade
3. **Session-Review** - Zusammenfassung aller Änderungen
4. **Packaging** - Installation als CLI-Tool via pip
