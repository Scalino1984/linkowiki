# tools/wiki_search.py
"""Search and browse wiki content"""
import re
from pathlib import Path
from typing import List, Tuple


def search_wiki(query: str, wiki_dir: Path) -> List[Tuple[Path, List[str]]]:
    """Search wiki files for query string"""
    results = []
    
    if not wiki_dir.exists():
        return results
    
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    
    for file_path in wiki_dir.rglob("*"):
        if file_path.is_file() and not file_path.name.startswith('.'):
            try:
                content = file_path.read_text()
                lines = content.split('\n')
                matches = []
                
                for i, line in enumerate(lines, 1):
                    if pattern.search(line):
                        matches.append(f"Line {i}: {line.strip()}")
                
                if matches:
                    results.append((file_path, matches))
            except Exception:
                continue
    
    return results


def list_recent_files(wiki_dir: Path, limit: int = 10) -> List[Tuple[Path, float]]:
    """List recently modified wiki files"""
    if not wiki_dir.exists():
        return []
    
    files = []
    for file_path in wiki_dir.rglob("*"):
        if file_path.is_file() and not file_path.name.startswith('.'):
            mtime = file_path.stat().st_mtime
            files.append((file_path, mtime))
    
    files.sort(key=lambda x: x[1], reverse=True)
    return files[:limit]


def get_wiki_categories(wiki_dir: Path) -> List[str]:
    """Get list of wiki categories (directories)"""
    if not wiki_dir.exists():
        return []
    
    categories = set()
    for item in wiki_dir.rglob("*"):
        if item.is_file() and not item.name.startswith('.'):
            relative = item.relative_to(wiki_dir)
            if len(relative.parts) > 1:
                categories.add(relative.parts[0])
    
    return sorted(categories)


def get_category_stats(wiki_dir: Path) -> dict:
    """Get statistics about wiki categories"""
    if not wiki_dir.exists():
        return {}
    
    stats = {}
    for file_path in wiki_dir.rglob("*"):
        if file_path.is_file() and not file_path.name.startswith('.'):
            relative = file_path.relative_to(wiki_dir)
            category = relative.parts[0] if len(relative.parts) > 1 else "root"
            
            if category not in stats:
                stats[category] = {"files": 0, "total_size": 0}
            
            stats[category]["files"] += 1
            stats[category]["total_size"] += file_path.stat().st_size
    
    return stats
