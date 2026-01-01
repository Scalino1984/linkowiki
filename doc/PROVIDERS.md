# Provider System - PydanticAI v2 Integration 🤖

## 🎯 Übersicht

LinkoWiki verwendet jetzt ein **flexibles Provider-System** für AI-Modelle, vollständig konform mit **PydanticAI v2**.

### Hauptfeatures:

✅ **Multi-Provider Support** - OpenAI, Anthropic Claude, mehr...  
✅ **Reasoning & Non-Reasoning** - Korrekte API-Nutzung je Typ  
✅ **Runtime Model Switch** - Modell in laufender Session wechseln  
✅ **JSON-Config** - Alle Provider zentral in `etc/providers.json`  
✅ **Validation** - Verhindert falsche Settings (temperature bei Reasoning)  
✅ **Session-Based** - Jede Session hat eigenes aktives Modell  

---

## 📁 Architektur

```
tools/ai/
├── providers.py        # Provider Registry & Validation
├── agent_factory.py    # Agent Creation Factory
└── assistant.py        # High-Level AI Interface

etc/
└── providers.json      # Provider Configuration
```

### Datenfluss:

```
Session → Provider ID → Agent Factory → Configured Agent → AI Response
```

---

## 🔧 Provider-Konfiguration

### `etc/providers.json`

```json
{
  "providers": [
    {
      "id": "openai-gpt4o",
      "provider": "openai",
      "model": "gpt-4o",
      "api_base": "https://api.openai.com/v1",
      "reasoning": false,
      "env_key": "OPENAI_API_KEY",
      "default_settings": {
        "temperature": 0.3
      },
      "description": "GPT-4o - Schnell und effizient"
    },
    {
      "id": "openai-o1",
      "provider": "openai",
      "model": "o1",
      "reasoning": true,
      "env_key": "OPENAI_API_KEY",
      "default_settings": {
        "reasoning_effort": "medium"
      },
      "description": "O1 - Reasoning für komplexe Probleme"
    }
  ],
  "default_provider": "openai-gpt4o"
}
```

### Provider-Felder:

| Feld | Beschreibung | Erforderlich |
|------|--------------|--------------|
| `id` | Eindeutige Provider-ID | ✓ |
| `provider` | Provider-Name (openai, anthropic) | ✓ |
| `model` | Modellname | ✓ |
| `api_base` | API-Basis-URL | ✗ |
| `reasoning` | Reasoning-Modell? (true/false) | ✓ |
| `env_key` | Environment-Variable für API-Key | ✓ |
| `default_settings` | Standard Model-Settings | ✓ |
| `description` | Beschreibung | ✗ |

---

## 🚨 Validierungsregeln

### Reasoning-Modelle (`reasoning: true`)

✅ **Erlaubt:**
- `reasoning_effort: low|medium|high`

❌ **NICHT erlaubt:**
- `temperature`
- `top_p`

### Non-Reasoning-Modelle (`reasoning: false`)

✅ **Erlaubt:**
- `temperature`
- `top_p`
- Andere Standard-Parameter

❌ **NICHT erlaubt:**
- `reasoning_effort`

**Fehler bei Verstoß:**
```
ValueError: Reasoning model 'openai-o1' does not support temperature/top_p.
Use reasoning_effort instead.
```

---

## 💻 Verwendung

### In der Session Shell

```bash
# Session starten
linkowiki-admin session start -w

# Session Shell öffnen
linkowiki-admin session shell

# Aktuelles Modell anzeigen
:model

# Verfügbare Modelle auflisten
:model list

# Modell wechseln
:model set openai-o1

# Jetzt mit neuem Modell arbeiten
erstelle ein wiki für docker
```

### Modell-Liste Beispiel:

```
🤖 Verfügbare Modelle
──────────────────────────────────────────────────────────────────
→ openai-gpt4o 
  GPT-4o - Schnell und effizient für allgemeine Aufgaben

  openai-gpt4o-mini 
  GPT-4o Mini - Kostengünstig für einfache Tasks

  openai-o1 [R]
  O1 - Reasoning-Modell für komplexe Problemlösung

  openai-o1-mini [R]
  O1 Mini - Schnelles Reasoning für mittlere Komplexität

  anthropic-claude-3-5-sonnet 
  Claude 3.5 Sonnet - Balanciert und vielseitig

Tippe ':model set <id>' zum Wechseln
```

**Legende:**
- `→` = Aktives Modell
- `[R]` = Reasoning-Modell

---

## 🔌 API-Integration

### Environment Variables

Setze API-Keys in deiner Shell:

```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

Oder in `.env` Datei:

```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

---

## 🛠️ Programmatische Verwendung

### Agent Factory verwenden:

```python
from tools.ai.agent_factory import AgentFactory
from tools.ai.assistant import AIResult

# Agent für spezifischen Provider erstellen
agent = AgentFactory.create_agent(
    provider_id="openai-o1",
    output_type=AIResult,
    system_prompt="Du bist ein Assistent...",
    custom_settings={"reasoning_effort": "high"}  # Optional override
)

# Agent verwenden
result = agent.run_sync("Was ist Docker?")
print(result.output.message)
```

### Session-basierte Agent-Erstellung:

```python
from tools.ai.agent_factory import create_agent_for_session
from tools.session.manager import load_session

# Lädt Provider-ID aus Session
session = load_session()

agent = create_agent_for_session(
    session=session,
    output_type=AIResult,
    system_prompt="..."
)
```

---

## 🔄 Provider wechseln

### In laufender Session:

```python
from tools.session.manager import set_active_provider

# Modell wechseln
set_active_provider("openai-o1")

# Neue Requests nutzen jetzt O1
```

### Validierung:

Das System validiert automatisch:
- Provider existiert
- API-Key verfügbar
- Settings passen zum Modell-Typ

---

## 📊 Session State

Neue Session-Felder:

```json
{
  "id": "2026-01-01T12:00:00",
  "active_provider_id": "openai-gpt4o",
  "write": true,
  ...
}
```

`active_provider_id` wird:
- Beim Session-Start auf `default_provider` gesetzt
- Bei `:model set` aktualisiert
- Für jeden AI-Request verwendet

---

## 🧪 Beispiele

### Reasoning-Modell für komplexe Aufgabe:

```bash
:model set openai-o1

erstelle einen kompletten security-guide für kubernetes mit best practices
```

O1 nutzt `reasoning_effort: medium` und denkt strukturiert durch das Problem.

### Non-Reasoning für schnelle Antwort:

```bash
:model set openai-gpt4o-mini

was ist der unterschied zwischen docker und podman?
```

GPT-4o Mini antwortet schnell mit `temperature: 0.3`.

---

## 🚀 Neue Provider hinzufügen

1. **`etc/providers.json` editieren:**

```json
{
  "id": "anthropic-claude-opus",
  "provider": "anthropic",
  "model": "claude-3-opus-20240229",
  "reasoning": false,
  "env_key": "ANTHROPIC_API_KEY",
  "default_settings": {
    "temperature": 0.3
  },
  "description": "Claude Opus - Höchste Qualität"
}
```

2. **API-Key setzen:**

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

3. **Sofort verfügbar:**

```bash
:model list
:model set anthropic-claude-opus
```

---

## ⚠️ Fehlerbehandlung

### Häufige Fehler:

**1. API-Key fehlt:**
```
ValueError: API key not found. Set environment variable: OPENAI_API_KEY
```

**Lösung:**
```bash
export OPENAI_API_KEY="sk-..."
```

**2. Falscher Provider:**
```
ValueError: Unknown provider: wrong-id
```

**Lösung:**
```bash
:model list  # Zeigt verfügbare Provider
```

**3. Falsche Settings:**
```
ValueError: Reasoning model 'openai-o1' does not support temperature/top_p
```

**Lösung:** Settings in `providers.json` korrigieren (nur `reasoning_effort` bei Reasoning-Modellen).

---

## 🔮 Roadmap

- [ ] **Custom Provider** - Eigene OpenAI-kompatible Endpoints
- [ ] **Model Presets** - Gespeicherte Setting-Profile
- [ ] **Cost Tracking** - Token-Usage pro Provider
- [ ] **Fallback Chain** - Automatischer Fallback bei Errors
- [ ] **Local Models** - Ollama-Integration
- [ ] **Multi-Model Responses** - Vergleich mehrerer Modelle

---

## 📖 Weitere Docs

- [PydanticAI Documentation](https://ai.pydantic.dev/)
- [OpenAI Models](https://platform.openai.com/docs/models)
- [Anthropic Claude](https://docs.anthropic.com/en/docs/models-overview)

---

**Version:** 3.0  
**PydanticAI:** v2.x  
**Datum:** 2026-01-01
