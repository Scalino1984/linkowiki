# tools/ai/tools/file_tools.py
"""File system tools for PydanticAI agent"""
from pathlib import Path
from typing import List, Optional
import glob as glob_module

BASE_DIR = Path(__file__).resolve().parents[3]


def read_file(filepath: str) -> Optional[str]:
    """
    Read and return the content of a file from the project.
    
    Args:
        filepath: Relative path to the file from project root
        
    Returns:
        File content as string, or None if file doesn't exist or can't be read
    """
    try:
        file_path = BASE_DIR / filepath
        if file_path.exists() and file_path.is_file():
            # Don't read binary files or very large files
            if file_path.stat().st_size > 1_000_000:  # 1MB limit
                return f"[File too large: {file_path.stat().st_size} bytes]"
            
            # Try to read as text
            try:
                return file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                return "[Binary file - cannot display content]"
        else:
            return None
    except Exception as e:
        return f"[Error reading file: {str(e)}]"


def list_files(pattern: str = "*") -> List[str]:
    """
    List files in the project matching a glob pattern.
    
    Args:
        pattern: Glob pattern to match files (default: "*" for all files)
                Examples: "*.py", "src/**/*.js", "tools/*.py"
        
    Returns:
        List of matching file paths relative to project root
    """
    try:
        # Handle recursive patterns
        if "**" in pattern:
            matches = glob_module.glob(str(BASE_DIR / pattern), recursive=True)
        else:
            matches = glob_module.glob(str(BASE_DIR / pattern))
        
        # Convert to relative paths and filter out directories
        files = []
        for match in matches:
            path = Path(match)
            if path.is_file() and not path.name.startswith('.'):
                try:
                    relative = path.relative_to(BASE_DIR)
                    files.append(str(relative))
                except ValueError:
                    continue
        
        # Sort and limit results
        files.sort()
        return files[:50]  # Limit to 50 files
        
    except Exception as e:
        return [f"Error listing files: {str(e)}"]
