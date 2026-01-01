# tools/session/manager.py
import json
import getpass
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parents[2]
SESSION_FILE = BASE_DIR / ".linkowiki-session.json"


def load_session():
    if not SESSION_FILE.exists():
        return None
    return json.loads(SESSION_FILE.read_text())


def save_session(session: dict):
    SESSION_FILE.write_text(json.dumps(session, indent=2))


def start_session(write=False):
    if SESSION_FILE.exists():
        raise RuntimeError("Session läuft bereits")

    from tools.ai.providers import get_provider_registry
    registry = get_provider_registry()
    
    session = {
        "id": datetime.now().isoformat(timespec="seconds"),
        "write": write,
        "cwd": str(BASE_DIR),
        "started_by": getpass.getuser(),
        "history": [],
        "files": {},
        "changes": [],
        "pending_actions": [],
        "active_provider_id": registry.default_provider_id
    }

    save_session(session)
    return session


def end_session():
    if SESSION_FILE.exists():
        SESSION_FILE.unlink()


def add_history(entry: str):
    s = load_session()
    if not s:
        return
    s["history"].append(entry)
    save_session(s)


def attach_file(path: str):
    s = load_session()
    if not s:
        raise RuntimeError("Keine aktive Session")

    p = Path(path).expanduser().resolve()
    if not p.exists() or not p.is_file():
        raise FileNotFoundError(path)

    s["files"][str(p)] = p.read_text()
    save_session(s)


def set_active_provider(provider_id: str):
    """Set active AI provider for session"""
    s = load_session()
    if not s:
        raise RuntimeError("Keine aktive Session")
    
    # Validate provider exists
    from tools.ai.providers import get_provider_registry
    registry = get_provider_registry()
    provider = registry.get_provider(provider_id)  # Raises if not found
    
    s["active_provider_id"] = provider_id
    save_session(s)


def get_active_provider() -> str:
    """Get active provider ID from session"""
    s = load_session()
    if not s:
        return None
    return s.get("active_provider_id")


def record_change(entry: str):
    s = load_session()
    if not s:
        return
    s["changes"].append(entry)
    save_session(s)

