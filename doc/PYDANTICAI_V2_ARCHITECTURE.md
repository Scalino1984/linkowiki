# PydanticAI v2 Architecture

## Übersicht

LinkoWiki verwendet eine **strikt PydanticAI v2 konforme** Architektur für KI-Integration. Die Implementierung trennt sauber zwischen Reasoning- und Non-Reasoning-Modellen und verhindert Fehlkonfigurationen auf Architekturebene.

## Kernprinzipien

### 1. Reasoning vs. Non-Reasoning Models

**REASONING-MODELLE** (z.B. OpenAI o1, o3):
- Verwenden **NUR** `reasoning_effort` Parameter
- **KEIN** `temperature` oder `top_p`
- Werte: `low`, `medium`, `high`

**NON-REASONING-MODELLE** (z.B. GPT-4, Claude):
- Verwenden **NUR** `temperature` und/oder `top_p`
- **KEIN** `reasoning_effort`
- Temperatur: 0.0 - 2.0

### 2. Single Source of Truth

**JSON ist die einzige Wahrheitsquelle:**
- `etc/providers.json` - Provider-Definitionen
- `etc/providers.schema.json` - JSON Schema zur Validierung
- Keine impliziten Defaults außerhalb der JSON

### 3. No Magic, No Fallbacks

- Keine automatischen Fallbacks
- Keine impliziten Defaults
- Keine Annahmen zur Laufzeit
- Fehlkonfigurationen werden **technisch verhindert**

## Dateistruktur

```
tools/ai/
├── providers.py           # Provider Registry mit Validierung
├── agent_factory.py       # Agent-Erstellung (PydanticAI v2)
├── routing.py            # Automatisches Task-Routing
├── assistant.py          # Haupt-Schnittstelle
└── agents/
    ├── __init__.py
    └── wiki_agent.py     # Zentraler Wiki-Agent mit System-Prompt

etc/
├── providers.json        # Provider-Definitionen
├── providers.schema.json # JSON Schema
└── linkowiki.conf       # App-Konfiguration

tools/
├── validate_providers.py # Schema-Validierung (CI/CD)
└── session/
    └── manager.py        # Session-Management mit Provider-Tracking
```

## Provider Configuration

### Beispiel Reasoning Model

```json
{
  "id": "openai-gpt5-reasoning",
  "provider": "openai",
  "model": "gpt-5",
  "reasoning": true,
  "env_key": "OPENAI_API_KEY",
  "default_settings": {
    "reasoning_effort": "medium"
  }
}
```

### Beispiel Non-Reasoning Model

```json
{
  "id": "openai-gpt5-text",
  "provider": "openai",
  "model": "gpt-5",
  "reasoning": false,
  "env_key": "OPENAI_API_KEY",
  "default_settings": {
    "temperature": 0.25
  }
}
```

## Automatisches Routing

Das System routet Tasks automatisch zum passenden Provider:

| Task Type | Provider | Verwendung |
|-----------|----------|------------|
| `tags` | gpt-5-nano | Tag-Generierung, schnelle Metadaten |
| `abstract` | gpt-5-nano | Kurzzusammenfassungen |
| `metadata` | gpt-5-nano | Eigenschaften extrahieren |
| `bulk` | gpt-5-mini | Massenverarbeitung |
| `rewrite` | gpt-5-mini | Texte umschreiben |
| `summary` | gpt-5-mini | Längere Summaries |
| `structure` | gpt-5-reasoning | Strukturanalyse |
| `outline` | gpt-5-reasoning | Gliederungen erstellen |
| `analysis` | gpt-5-reasoning | Tiefe Analysen |
| `default` | gpt-5-text | Standardaufgaben |

### Routing-Beispiele

```python
from tools.ai.routing import ProviderRouter

# Manuelles Routing
provider_id = ProviderRouter.route("tags")  
# → "openai-gpt5-nano-text"

# Auto-Detection
provider_id = ProviderRouter.route_auto("Generate tags for this article")
# → "openai-gpt5-nano-text"
```

## Agent Creation

### Über Session (Standard)

```python
from tools.ai.agent_factory import create_agent_for_session
from tools.session.manager import load_session

session = load_session()
agent = create_agent_for_session(
    session=session,
    output_type=MyOutputModel,
    system_prompt="You are a helpful assistant"
)

result = agent.run_sync("Hello!")
```

### Über Task-Routing

```python
from tools.ai.agent_factory import create_agent_for_task

agent = create_agent_for_task(
    task_type="tags",  # Auto-routes to nano model
    output_type=TagsOutput,
    system_prompt="Extract tags"
)
```

### Direkt mit Provider-ID

```python
from tools.ai.agent_factory import AgentFactory

agent = AgentFactory.create_agent(
    provider_id="openai-gpt5-reasoning",
    output_type=MyOutput,
    system_prompt="Think deeply"
)
```

## CLI-Funktionen

### Model Management

```bash
# Aktives Modell anzeigen
linkowiki-admin session shell
:model

# Modelle auflisten
:model list

# Modell wechseln
:model set openai-gpt5-reasoning
```

### Session-basiertes Switching

```python
from tools.session.manager import set_active_provider

# In einer Session
set_active_provider("openai-gpt5-reasoning")

# Nächster AI-Call nutzt automatisch reasoning model
```

## Validierung und CI/CD

### Manuelle Validierung

```bash
# Schema-Validierung
python tools/validate_providers.py

# Conformance-Tests
python tests/test_pydantic_ai_conformance.py
```

### CI/CD Integration

```yaml
# .github/workflows/validate.yml
name: Validate Configuration
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: pip install jsonschema pydantic pydantic-ai
      - name: Validate providers.json
        run: python tools/validate_providers.py
      - name: Run conformance tests
        run: python tests/test_pydantic_ai_conformance.py
```

**WICHTIG:** Build schlägt fehl wenn:
- `providers.json` gegen Schema verstößt
- Reasoning-Model `temperature` hat
- Non-Reasoning-Model `reasoning_effort` hat
- Default-Provider nicht existiert

## Wiki Agent

Der zentrale Wiki-Agent hat einen festen System-Prompt:

```python
from tools.ai.agents.wiki_agent import get_wiki_system_prompt

# System-Prompt enthält:
# - Sachliche Regeln
# - Markdown-Konventionen
# - Keine Halluzinationen
# - Strukturierte Ausgabe
```

### Verwendung

```python
from tools.ai.assistant import run_ai

result = run_ai(
    prompt="Erstelle Wiki-Eintrag für Docker",
    files={},
    session=current_session
)

print(result.message)    # AI-Antwort
print(result.options)    # Interaktive Optionen
print(result.actions)    # Vorgeschlagene Aktionen
```

## Best Practices

### ✅ DO

- Verwende Session-basierte Agent-Erstellung
- Nutze Auto-Routing für optimale Performance
- Validiere Provider-Config vor Deployment
- Teste mit Conformance-Suite

### ❌ DON'T

- Keine inline Agent-Instanzen im CLI-Code
- Keine Magic-Defaults außerhalb JSON
- Keine gemischten Settings (reasoning_effort + temperature)
- Keine direkten API-Calls ohne Factory

## Troubleshooting

### "API key not found"

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

### "Unknown provider: xyz"

Provider in `etc/providers.json` definieren und validieren:

```bash
python tools/validate_providers.py
```

### "Reasoning model cannot have temperature"

Settings in `etc/providers.json` korrigieren:

```json
// ❌ FALSCH
{
  "reasoning": true,
  "default_settings": {
    "temperature": 0.5  // <- FEHLER
  }
}

// ✅ RICHTIG
{
  "reasoning": true,
  "default_settings": {
    "reasoning_effort": "medium"
  }
}
```

## Migration Guide

Falls alte Sessions mit anderen Providern existieren:

```python
from tools.session.manager import load_session, set_active_provider

session = load_session()

# Falls kein active_provider_id gesetzt ist
if "active_provider_id" not in session:
    set_active_provider("openai-gpt5-text")
```

## Testing

```bash
# Alle Tests
python tests/test_pydantic_ai_conformance.py

# Nur Validierung
python tools/validate_providers.py

# Mit Debug-Output
python tests/test_pydantic_ai_conformance.py -v
```

## Erweiterung

### Neuen Provider hinzufügen

1. In `etc/providers.json` eintragen
2. Schema-Validierung durchführen
3. Tests ausführen
4. Ggf. Routing-Regeln anpassen

```json
{
  "id": "my-new-model",
  "provider": "openai",
  "model": "gpt-5-turbo",
  "reasoning": false,
  "env_key": "OPENAI_API_KEY",
  "default_settings": {
    "temperature": 0.3
  },
  "description": "Beschreibung"
}
```

### Neuen Task-Type hinzufügen

In `tools/ai/routing.py`:

```python
ROUTING_MAP = {
    ...
    "my_new_task": "my-preferred-provider",
}
```

## Zusammenfassung

Diese Architektur stellt sicher dass:

✅ Reasoning/Non-Reasoning sauber getrennt sind  
✅ JSON als Single Source of Truth dient  
✅ Fehlkonfigurationen technisch verhindert werden  
✅ Modellwechsel zur Laufzeit möglich sind  
✅ Auto-Routing optimal performt  
✅ CI/CD Validierung Build-Fehler erzwingt  
✅ PydanticAI v2 strikt eingehalten wird
