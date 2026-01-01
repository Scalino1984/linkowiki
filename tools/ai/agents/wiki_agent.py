# tools/ai/agents/wiki_agent.py
"""Central wiki agent with system prompt loaded from file - PydanticAI v2 compliant"""

from pathlib import Path


def _find_project_root() -> Path:
    """
    Find the project root directory by looking for marker files.
    
    Returns:
        Path: The project root directory
    """
    # Start from this file's directory
    current = Path(__file__).resolve().parent
    
    # Search upwards for marker files
    markers = ['.git', 'pyproject.toml', 'requirements.txt', 'AI_SYSTEM_PROMPT.md']
    
    for parent in [current] + list(current.parents):
        for marker in markers:
            if (parent / marker).exists():
                return parent
    
    # Fallback: three levels up from this file
    return Path(__file__).resolve().parents[3]


def get_wiki_system_prompt() -> str:
    """
    Get the wiki agent system prompt from external file.
    
    The system prompt is stored in AI_SYSTEM_PROMPT.md in the project root
    for easy maintenance and version control.
    
    Returns:
        str: The system prompt content
    """
    # Find project root using marker files
    project_root = _find_project_root()
    prompt_file = project_root / "AI_SYSTEM_PROMPT.md"
    
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Fallback to embedded prompt if file not found
        return """Du bist ein sachlicher Wiki-Assistent.

GRUNDREGELN:
- Sachlich und strukturiert
- Markdown-konform
- Keine Halluzinationen
- Keine Fülltexte
- Präzise und kurz

WIKI-STRUKTUR:
- Eine Datei = ein Thema
- Pfad = Kategorie/Thema (z.B. linux/systemctl)
- Keine Dateiendungen
- Inhalte kurz und strukturiert

INTERAKTION:
- Biete IMMER konkrete, nummerierte Optionen an (im 'options' Feld)
- Jede Option hat: label (kurz) und description (optional)
- Bei unklarer Anfrage: mehrere Wege anbieten
- Bei klarer Anfrage: nächste Schritte vorschlagen

BEISPIELE für gute Optionen:
Bei "hallo":
- Option: "Neuen Wiki-Eintrag erstellen"
- Option: "Existierenden Eintrag bearbeiten"
- Option: "Wiki durchsuchen"

Bei "erstelle docker wiki":
- Option: "Grundlagen-Eintrag (Installation, erste Schritte)"
- Option: "Docker Compose Tutorial"
- Option: "Best Practices & Security"

WORKFLOW:
1. Verstehe die Anfrage
2. Antworte freundlich im 'message' Feld
3. Biete konkrete Optionen im 'options' Feld an
4. Erzeuge Actions NUR nach expliziter Bestätigung

MARKDOWN-STIL:
- Überschriften mit #, ##, ###
- Code-Blöcke mit ```
- Listen mit - oder 1.
- Inline-Code mit `code`
- Keine übermäßige Formatierung
"""
