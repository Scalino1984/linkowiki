# LinkoWiki - Beispiele und Testaufrufe

Dieses Dokument enthält praktische Beispiele zum Testen aller Funktionen von LinkoWiki.

---

## 📋 Grundlegende Befehle

### Wiki-Struktur anzeigen
```bash
tools/linkowiki-admin.py tree
```

**Erwartete Ausgabe:**
```
📚 Wiki-Struktur (/home/user/linko-wiki/wiki):

📂 wiki
  📄 README
```

---

## 🧠 Session Management

### Session starten (Read-Only)
```bash
tools/linkowiki-admin.py session start
```

**Erwartete Ausgabe:**
```json
🟢 Session gestartet

{
  "id": "2026-01-01T13:30:00",
  "write": false,
  "cwd": "/home/user/linko-wiki",
  "started_by": "username",
  "history": [],
  "files": {},
  "changes": []
}
```

### Session starten (Write-Mode)
```bash
tools/linkowiki-admin.py session start --write
```

### Session-Status anzeigen
```bash
tools/linkowiki-admin.py session status
```

### Session beenden
```bash
tools/linkowiki-admin.py session end
```

**Erwartete Ausgabe:**
```
🔴 Session beendet
```

---

## 💬 Interaktive Session Shell

### Shell starten
```bash
tools/linkowiki-admin.py session start --write
tools/linkowiki-admin.py session shell
```

**Erwartete Ausgabe:**
```
🧠 Session-Shell gestartet (`exit` zum Beenden)

linkowiki(session)>
```

### Verfügbare Shell-Befehle

#### 1. Wiki-Struktur anzeigen
```
linkowiki(session)> :tree
```

#### 2. Datei an Session anhängen
```
linkowiki(session)> :attach README.md
```

**Erwartete Ausgabe:**
```
📎 Datei angehängt
```

#### 3. Angehängte Dateien auflisten
```
linkowiki(session)> :files
```

**Erwartete Ausgabe:**
```
📎 /home/user/linko-wiki/README.md
```

#### 4. Write-Modus aktivieren
```
linkowiki(session)> :write on
```

**Erwartete Ausgabe:**
```
✍️ Write-Modus aktiviert
```

#### 5. Write-Modus deaktivieren
```
linkowiki(session)> :write off
```

**Erwartete Ausgabe:**
```
🔒 Write-Modus deaktiviert
```

#### 6. AI-Befehl ausführen (erfordert API-Key)
```
linkowiki(session)> erstelle eine wiki-seite über git grundlagen
```

**Erwartete Ausgabe (ohne API-Key):**
```
❌ KI-Fehler: The api_key client option must be set...
```

**Erwartete Ausgabe (mit API-Key + Write-Mode):**
```
🧪 DRY RUN
========================================
CREATE  git/grundlagen
========================================
➡️ Änderungen durchführen? (ja/nein): ja
✅ Änderungen angewendet
```

#### 7. Shell beenden
```
linkowiki(session)> exit
```

---

## 🤖 Direkter AI-Befehl

### Einfacher AI-Befehl (Read-Only)
```bash
tools/linkowiki-admin.py ai -p "erstelle eine wiki seite über docker"
```

**Erwartete Ausgabe:**
```
🧪 DRY RUN
========================================
CREATE  docker/grundlagen
========================================
ℹ️ Read-only Modus
```

### AI-Befehl mit Write-Mode
```bash
tools/linkowiki-admin.py ai -p "erstelle eine wiki seite über kubernetes" -w
```

**Erwartete Ausgabe:**
```
🧪 DRY RUN
========================================
CREATE  kubernetes/einfuehrung
========================================
➡️ Änderungen durchführen? (ja/nein): ja
✅ Änderungen angewendet
```

### AI-Befehl mit angehängter Datei
```bash
tools/linkowiki-admin.py ai -f README.md -p "fasse diese datei zusammen" -w
```

---

## 🛡️ Guardrails testen

### Test 1: Path Traversal blockieren
```bash
# Python-Test
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
import importlib.util
spec = importlib.util.spec_from_file_location("admin", "tools/linkowiki-admin.py")
admin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(admin)

from tools.ai.assistant import Action

try:
    action = Action(type='create', path='../etc/passwd', content='test')
    admin.validate_action(action)
    print("❌ FEHLER: Path traversal nicht blockiert!")
except RuntimeError as e:
    print(f"✅ Path traversal blockiert: {e}")
EOF
```

**Erwartete Ausgabe:**
```
✅ Path traversal blockiert: Ungültiger Pfad: ../etc/passwd
```

### Test 2: Absolute Pfade blockieren
```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
import importlib.util
spec = importlib.util.spec_from_file_location("admin", "tools/linkowiki-admin.py")
admin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(admin)

from tools.ai.assistant import Action

try:
    action = Action(type='create', path='/etc/hosts', content='test')
    admin.validate_action(action)
    print("❌ FEHLER: Absolute Pfade nicht blockiert!")
except RuntimeError as e:
    print(f"✅ Absolute Pfade blockiert: {e}")
EOF
```

**Erwartete Ausgabe:**
```
✅ Absolute Pfade blockiert: Ungültiger Pfad: /etc/hosts
```

### Test 3: Größenlimit testen
```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
import importlib.util
spec = importlib.util.spec_from_file_location("admin", "tools/linkowiki-admin.py")
admin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(admin)

from tools.ai.assistant import Action

try:
    action = Action(type='create', path='test', content='x' * 60000)
    admin.validate_action(action)
    print("❌ FEHLER: Größenlimit nicht blockiert!")
except RuntimeError as e:
    print(f"✅ Größenlimit blockiert: {e}")
EOF
```

**Erwartete Ausgabe:**
```
✅ Größenlimit blockiert: Inhalt zu groß (>50KB)
```

---

## 📝 Changelog testen

### Changelog anzeigen
```bash
cat wiki/.changelog
```

**Erwartete Ausgabe (Beispiel):**
```
[2026-01-01T13:30:00] source=ai
  create linux/commands
  append git/workflow

[2026-01-01T13:35:15] source=ai
  create docker/basics
```

### Changelog-Schreiben testen
```bash
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
import importlib.util
spec = importlib.util.spec_from_file_location("admin", "tools/linkowiki-admin.py")
admin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(admin)

from tools.ai.assistant import Action

actions = [
    Action(type='create', path='test/page1', content='content1'),
    Action(type='append', path='test/page2', content='content2')
]

admin.log_change(actions, source="manual-test")
print("✅ Changelog-Eintrag erstellt")

with open('wiki/.changelog', 'r') as f:
    print("\n" + f.read())
EOF
```

---

## 📊 Session Changes testen

### Changes tracken
```bash
tools/linkowiki-admin.py session start

python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from tools.session.manager import record_change, load_session

record_change("Teständerung 1")
record_change("Teständerung 2")
record_change("Teständerung 3")

s = load_session()
print("Getrackte Changes:")
for i, change in enumerate(s['changes'], 1):
    print(f"  {i}. {change}")
EOF

tools/linkowiki-admin.py session end
```

**Erwartete Ausgabe:**
```
Getrackte Changes:
  1. Teständerung 1
  2. Teständerung 2
  3. Teständerung 3
```

---

## 🌐 Web-Integration testen

### Voraussetzung: API-Key setzen
```bash
export OPENAI_API_KEY=your-key-here
```

### 1. Session starten
```bash
tools/linkowiki-admin.py session start --write
```

### 2. Wiki-Server starten
```bash
./start-wiki
```

### 3. AI-Endpoint testen
```bash
curl -X POST http://localhost:8002/ai \
  -H "Content-Type: application/json" \
  -d '{"prompt": "erstelle eine wiki-seite über python basics"}'
```

**Erwartete Ausgabe (JSON):**
```json
{
  "actions": [
    {
      "type": "create",
      "path": "python/basics",
      "content": "# Python Basics\n\n..."
    }
  ],
  "recommendation": "..."
}
```

### 4. Ohne Session (Fehlerfall)
```bash
# Session beenden
tools/linkowiki-admin.py session end

# Endpoint testen
curl -X POST http://localhost:8002/ai \
  -H "Content-Type: application/json" \
  -d '{"prompt": "test"}'
```

**Erwartete Ausgabe:**
```json
{
  "error": "no session"
}
```

---

## 🧪 Vollständiger Integrationstest

### Kompletter Workflow
```bash
#!/bin/bash

echo "=== LinkoWiki Integrationstest ==="
echo

echo "1. Session starten"
tools/linkowiki-admin.py session start --write
echo

echo "2. Status prüfen"
tools/linkowiki-admin.py session status
echo

echo "3. Datei anhängen"
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from tools.session.manager import attach_file
attach_file('README.md')
print("✅ README.md angehängt")
EOF
echo

echo "4. History hinzufügen"
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from tools.session.manager import add_history
add_history('Befehl 1')
add_history('Befehl 2')
print("✅ 2 History-Einträge hinzugefügt")
EOF
echo

echo "5. Changes tracken"
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from tools.session.manager import record_change
record_change('Änderung 1')
record_change('Änderung 2')
print("✅ 2 Changes getrackt")
EOF
echo

echo "6. Session-Status final"
tools/linkowiki-admin.py session status
echo

echo "7. Session beenden"
tools/linkowiki-admin.py session end
echo

echo "8. Changelog prüfen"
if [ -f wiki/.changelog ]; then
    echo "✅ Changelog existiert:"
    cat wiki/.changelog
else
    echo "⚠️  Kein Changelog vorhanden"
fi
echo

echo "=== Test abgeschlossen ==="
```

---

## 🔧 Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'pydantic_ai'"
```bash
pip install pydantic-ai
```

### Problem: "OpenAIError: The api_key client option must be set"
```bash
export OPENAI_API_KEY=your-actual-key-here
# Oder in .env Datei:
echo "OPENAI_API_KEY=your-key" > .env
```

### Problem: Session läuft bereits
```bash
# Session forciert beenden
rm .linkowiki-session.json
# Oder sauber beenden:
tools/linkowiki-admin.py session end
```

### Problem: Changelog wird nicht erstellt
```bash
# wiki-Verzeichnis existiert?
ls -la wiki/
# Berechtigung prüfen
ls -la wiki/.changelog
```

---

## 📚 Weitere Ressourcen

- **Vollständige Dokumentation:** `doc/SESSION_AI.md`
- **API-Key Beispiel:** `.env.example`
- **Quellcode:** `tools/linkowiki-admin.py`, `tools/session/manager.py`, `tools/ai/assistant.py`

---

## ✅ Checkliste: Alle Features testen

- [ ] `tree` - Wiki-Struktur anzeigen
- [ ] `session start` - Session starten
- [ ] `session status` - Session-Status
- [ ] `session end` - Session beenden
- [ ] `session shell` - Interaktive Shell
- [ ] `:tree` - Struktur in Shell
- [ ] `:attach` - Datei anhängen
- [ ] `:files` - Dateien auflisten
- [ ] `:write on/off` - Write-Modus toggle
- [ ] `ai -p` - Direkter AI-Befehl
- [ ] Guardrails (Path traversal, absolute paths, size)
- [ ] Changelog (Schreiben & Lesen)
- [ ] Session Changes (Tracking)
- [ ] Web-Integration (AI-Endpoint)
- [ ] Vollständiger Workflow

---

**Stand:** 2026-01-01  
**Version:** LinkoWiki mit Session & AI Integration
