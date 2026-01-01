# tools/ai/tools/git_tools.py
"""Git integration tools for PydanticAI agent"""
from pathlib import Path
from typing import Dict, List, Any
import subprocess

BASE_DIR = Path(__file__).resolve().parents[3]


def git_status() -> Dict[str, Any]:
    """
    Get current git status including branch, uncommitted changes, and recent commits.
    
    Returns:
        Dictionary with git status information
    """
    result = {
        "branch": "",
        "is_clean": True,
        "uncommitted_files": [],
        "recent_commits": [],
        "error": None
    }
    
    try:
        # Get current branch
        branch_result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=BASE_DIR,
            timeout=5
        )
        if branch_result.returncode == 0:
            result["branch"] = branch_result.stdout.strip()
        
        # Get uncommitted changes
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=BASE_DIR,
            timeout=5
        )
        if status_result.returncode == 0:
            status_lines = status_result.stdout.strip().split('\n')
            if status_lines and status_lines[0]:
                result["is_clean"] = False
                result["uncommitted_files"] = [
                    line.strip() for line in status_lines if line.strip()
                ][:10]  # Limit to 10 files
        
        # Get recent commits
        log_result = subprocess.run(
            ["git", "log", "--oneline", "-5"],
            capture_output=True,
            text=True,
            cwd=BASE_DIR,
            timeout=5
        )
        if log_result.returncode == 0:
            commits = log_result.stdout.strip().split('\n')
            result["recent_commits"] = [
                commit.strip() for commit in commits if commit.strip()
            ]
        
    except subprocess.TimeoutExpired:
        result["error"] = "Git command timed out"
    except FileNotFoundError:
        result["error"] = "Git not found - is it installed?"
    except Exception as e:
        result["error"] = f"Git error: {str(e)}"
    
    return result
