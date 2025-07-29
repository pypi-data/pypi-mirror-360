from pathlib import Path
from typing import Optional

from prompt_toolkit.history import FileHistory


def get_history_file_path():
    """Get the history file path based on current working directory"""
    # Get current working directory
    cwd = Path.cwd()

    # Get user's home directory
    home = Path.home()

    # Calculate relative path from home to current directory
    try:
        relative_path = cwd.relative_to(home)
    except ValueError:
        # If current directory is not under home, use absolute path components
        relative_path = Path(*cwd.parts[1:]) if cwd.is_absolute() else cwd

    # Create history directory structure
    history_dir = home / ".tinybird" / "projects" / relative_path
    history_dir.mkdir(parents=True, exist_ok=True)

    # Return history file path
    return history_dir / "history.txt"


def load_history() -> Optional[FileHistory]:
    try:
        history_file = get_history_file_path()
        return FileHistory(str(history_file))
    except Exception:
        return None


def clear_history():
    """Clear the history file"""
    history_file = get_history_file_path()
    history_file.unlink(missing_ok=True)
