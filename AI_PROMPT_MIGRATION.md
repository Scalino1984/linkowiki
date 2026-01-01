# AI System Prompt - Auslagerung

## Zusammenfassung der Änderung

Der AI System Prompt wurde aus dem Python-Code in eine dedizierte, externe Datei ausgelagert.

## Änderungen

### 1. Neue Datei: `AI_SYSTEM_PROMPT.md`
- Enthält den vollständigen System-Prompt für den AI-Assistenten
- Im Projektroot gespeichert
- Version-kontrolliert
- Mit Kommentaren dokumentiert
- Leicht editierbar ohne Code-Änderungen

### 2. Angepasste Datei: `tools/ai/agents/wiki_agent.py`
**Vorher:**
- System-Prompt als String-Konstante im Code (`WIKI_SYSTEM_PROMPT`)
- Schwer wartbar
- Änderungen erfordern Code-Editing

**Nachher:**
- `get_wiki_system_prompt()` liest aus `AI_SYSTEM_PROMPT.md`
- Automatisches Laden beim Start
- Fallback auf embedded Prompt bei Datei-Fehler
- Keine Logik-Änderungen

### 3. Dokumentation: `README.md`
Neuer Abschnitt "AI System Prompt Configuration" mit:
- Pfad zur Prompt-Datei
- Anpassungs-Anleitung
- Hinweis auf Versionskontrolle

## Vorteile

✅ **Wartbarkeit**: Prompt kann ohne Code-Kenntnisse angepasst werden
✅ **Versionskontrolle**: Änderungen am Prompt werden im Git-Log sichtbar
✅ **Team-Zusammenarbeit**: Mehrere Personen können Prompt reviewen/anpassen
✅ **Flexibilität**: Verschiedene Prompts für verschiedene Deployments
✅ **Dokumentation**: Kommentare in der Prompt-Datei erklären Verwendung

## Verwendung

### Prompt anpassen
```bash
# Editiere die Datei
vim AI_SYSTEM_PROMPT.md

# Teste die Änderung
python tools/linkowiki-cli.py
```

### Prompt anzeigen
```python
from tools.ai.agents.wiki_agent import get_wiki_system_prompt
print(get_wiki_system_prompt())
```

## Technische Details

**Pfad-Auflösung:**
```python
project_root = Path(__file__).resolve().parents[3]
prompt_file = project_root / "AI_SYSTEM_PROMPT.md"
```

**Error Handling:**
- FileNotFoundError → Fallback auf embedded Prompt
- Keine Unterbrechung des CLI-Betriebs

**Keine Logik-Änderungen:**
- API bleibt identisch: `get_wiki_system_prompt()`
- Rückgabewert unverändert: `str`
- Alle existierenden Aufrufe funktionieren weiter

## Testing

```bash
# Test 1: Prompt lädt korrekt
python3 -c "from tools.ai.agents.wiki_agent import get_wiki_system_prompt; print(len(get_wiki_system_prompt()))"

# Test 2: CLI startet
python tools/linkowiki-cli.py

# Test 3: Fallback funktioniert
mv AI_SYSTEM_PROMPT.md AI_SYSTEM_PROMPT.md.bak
python3 -c "from tools.ai.agents.wiki_agent import get_wiki_system_prompt; print('Fallback works')"
mv AI_SYSTEM_PROMPT.md.bak AI_SYSTEM_PROMPT.md
```

## Fazit

Die Auslagerung des System-Prompts macht das Projekt wartbarer und flexibler, ohne die bestehende Funktionalität zu beeinträchtigen. Die Änderung folgt Best Practices für Konfigurationsmanagement.
