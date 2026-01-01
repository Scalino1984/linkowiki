# tools/session/export.py
"""Session export and history management"""
import json
from pathlib import Path
from datetime import datetime


def export_session_history(session: dict, output_dir: Path = None):
    """Export session history to markdown file"""
    if not output_dir:
        from tools.config import get_config
        config = get_config()
        output_dir = config.export_dir
    
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"session_{timestamp}.md"
    output_file = output_dir / filename
    
    content = []
    content.append(f"# LinkoWiki Session Export\n")
    content.append(f"**Session ID:** {session['id']}")
    content.append(f"**Started by:** {session['started_by']}")
    content.append(f"**Mode:** {'Write' if session['write'] else 'Read-only'}")
    content.append(f"**Exported:** {timestamp}\n")
    
    if session.get('history'):
        content.append("## 📝 Conversation History\n")
        for i, entry in enumerate(session['history'], 1):
            content.append(f"### Query {i}")
            content.append(f"```\n{entry}\n```\n")
    
    if session.get('files'):
        content.append("## 📎 Attached Files\n")
        for filepath in session['files'].keys():
            content.append(f"- `{filepath}`")
        content.append("")
    
    if session.get('changes'):
        content.append("## ✏️  Changes Made\n")
        for change in session['changes']:
            content.append(f"- {change}")
        content.append("")
    
    if session.get('pending_actions'):
        content.append("## ⏳ Pending Actions\n")
        for action in session['pending_actions']:
            content.append(f"- **{action['type'].upper()}** `{action['path']}`")
        content.append("")
    
    output_file.write_text('\n'.join(content))
    return output_file


def get_session_statistics(session: dict):
    """Calculate session statistics"""
    return {
        "total_queries": len(session.get('history', [])),
        "files_attached": len(session.get('files', {})),
        "changes_made": len(session.get('changes', [])),
        "pending_actions": len(session.get('pending_actions', [])),
        "write_mode": session.get('write', False),
        "duration": "active"  # Could calculate duration if we store start time
    }
