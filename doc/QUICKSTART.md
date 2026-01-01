# PydanticAI v2 - Quick Start Guide

## Schnellstart

### 1. Installation

```bash
# Abhängigkeiten installieren
make install

# Oder manuell
pip install -r requirements.txt
```

### 2. API Keys konfigurieren

```bash
# In .bashrc oder .zshrc
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 3. Validierung

```bash
# Konfiguration validieren
make validate

# Conformance-Tests
make test

# Alles zusammen
make check
```

### 4. Session starten

```bash
# Interaktiv
./tools/linkowiki-admin.py

# Oder direkt
./tools/linkowiki-admin.py session start
./tools/linkowiki-admin.py session shell
```

## Model Management

### Im Session Shell

```bash
# Aktuelles Modell
:model

# Modelle auflisten
:model list

# Modell wechseln
:model set openai-gpt5-reasoning
:model set openai-gpt5-nano-text
:model set anthropic-claude-3-5-sonnet
```

### Verfügbare Modelle

| Model ID | Type | Use Case |
|----------|------|----------|
| `openai-gpt5-reasoning` | Reasoning | Tiefe Analysen, Strukturen |
| `openai-gpt5-text` | Text | Standard-Aufgaben |
| `openai-gpt5-mini-text` | Text | Bulk-Operationen |
| `openai-gpt5-nano-text` | Text | Tags, Metadaten |
| `anthropic-claude-3-5-sonnet` | Text | Vielseitig |
| `anthropic-claude-3-haiku` | Text | Schnell |

## Typische Workflows

### Wiki-Eintrag erstellen

```bash
# Session starten (write-mode)
./tools/linkowiki-admin.py session start -w

# Shell öffnen
./tools/linkowiki-admin.py session shell

# Im Shell
> Erstelle einen Wiki-Eintrag für Docker Grundlagen

# Aktionen anwenden
> apply
```

### Tags generieren (optimiert)

```bash
# Auto-routing nutzt nano-model für tags
> Generate tags for: Linux systemd tutorial
# → Verwendet automatisch openai-gpt5-nano-text

> apply
```

### Komplexe Analyse (optimiert)

```bash
# Auto-routing nutzt reasoning-model
> Analyze the structure of our wiki and suggest improvements
# → Verwendet automatisch openai-gpt5-reasoning

# Modell manuell wählen
:model set openai-gpt5-reasoning
> Create detailed outline for security documentation
```

### Bulk-Operation (optimiert)

```bash
# Auto-routing nutzt mini-model
> Rewrite all entries in category 'linux' to be more concise
# → Verwendet automatisch openai-gpt5-mini-text
```

## Python API

### Basic Usage

```python
from tools.ai.assistant import run_ai
from tools.session.manager import load_session, set_active_provider

# Session laden
session = load_session()

# Modell wechseln
set_active_provider("openai-gpt5-text")

# AI nutzen
result = run_ai(
    prompt="Erstelle Wiki-Eintrag für Python",
    files={},
    session=session
)

print(result.message)
for action in result.actions:
    print(f"Action: {action.type} {action.path}")
```

### Mit Auto-Routing

```python
from tools.ai.routing import ProviderRouter
from tools.ai.agent_factory import create_agent_for_task
from pydantic import BaseModel

class TagsOutput(BaseModel):
    tags: list[str]

# Automatisch nano-model für tags
agent = create_agent_for_task(
    task_type="tags",
    output_type=TagsOutput,
    system_prompt="Extract relevant tags"
)

result = agent.run_sync("Article about Python programming")
print(result.output.tags)
```

## Debugging

### Validierung fehlgeschlagen

```bash
# Details anzeigen
python tools/validate_providers.py

# Häufige Fehler:
# - Reasoning model hat temperature
# - Non-reasoning model hat reasoning_effort
# - Default provider existiert nicht
```

### Tests fehlgeschlagen

```bash
# Tests mit Details
python tests/test_pydantic_ai_conformance.py -v

# Einzelne Tests
python -c "from tests.test_pydantic_ai_conformance import *; test_routing()"
```

### Provider-Probleme

```python
# Python Console
from tools.ai.providers import get_provider_registry, reset_provider_registry

# Registry neu laden
reset_provider_registry()
registry = get_provider_registry()

# Alle Provider auflisten
for pid, provider in registry.list_providers().items():
    print(f"{pid}: reasoning={provider.reasoning}")
```

## Neue Provider hinzufügen

### 1. In `etc/providers.json`

```json
{
  "id": "my-new-provider",
  "provider": "openai",
  "model": "gpt-6",
  "api_base": "https://api.openai.com/v1",
  "reasoning": false,
  "env_key": "OPENAI_API_KEY",
  "default_settings": {
    "temperature": 0.25
  },
  "description": "GPT-6 - Next generation"
}
```

### 2. Validieren

```bash
make validate
```

### 3. Testen

```bash
# In Session
:model set my-new-provider
> Hello, test!
```

## Best Practices

### ✅ Empfohlen

1. Nutze Auto-Routing für optimale Performance
2. Validiere Config nach Änderungen
3. Verwende Session-basierte Agents
4. Teste mit `make check` vor Commit

### ❌ Vermeiden

1. Keine Magic Defaults außerhalb JSON
2. Keine direkten API-Calls ohne Factory
3. Keine inline Agent-Instanzen
4. Keine gemischten Settings

## Troubleshooting

### API Key Fehler

```bash
# Keys prüfen
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Keys setzen
export OPENAI_API_KEY="sk-..."
```

### Schema Validierung schlägt fehl

```bash
# Schema-Fehler zeigen
python tools/validate_providers.py

# JSON formatieren
cat etc/providers.json | python -m json.tool
```

### Session-Probleme

```bash
# Session zurücksetzen
rm .linkowiki-session.json

# Neue Session
./tools/linkowiki-admin.py session start
```

## Weitere Ressourcen

- [Vollständige Architektur-Dokumentation](doc/PYDANTICAI_V2_ARCHITECTURE.md)
- [Provider Schema](etc/providers.schema.json)
- [Conformance Tests](tests/test_pydantic_ai_conformance.py)

## Support

Bei Fragen oder Problemen:

1. Validierung prüfen: `make validate`
2. Tests ausführen: `make test`
3. Dokumentation lesen: `doc/PYDANTICAI_V2_ARCHITECTURE.md`
