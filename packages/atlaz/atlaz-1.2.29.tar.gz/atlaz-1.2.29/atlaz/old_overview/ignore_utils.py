from pathlib import Path

import pathspec

def append_default_ignores(manual_ignore_files: list) -> list:
    """
    Add common ignore directories and patterns if they're not already present.
    """
    common_ignores = [
        '.git', 'node_modules', 'dist', '__pycache__',
        'venv', '*.log', 'node_modules/', '*.tmp', '.env', 'dist/','atlaz.egg-info', 'LICENSE', 'MANIFEST.in'
    ]
    if not manual_ignore_files:
        manual_ignore_files = []
    for pattern in common_ignores:
        if pattern not in manual_ignore_files:
            manual_ignore_files.append(pattern)
    return manual_ignore_files

def compile_ignore_patterns(base_path: Path, manual_patterns: list):
    """
    Load .gitignore patterns plus any manual_patterns, compile into a PathSpec.
    """
    gitignore_patterns = load_gitignore_patterns(base_path)
    all_patterns = gitignore_patterns + (manual_patterns or [])
    if all_patterns:
        return pathspec.PathSpec.from_lines('gitwildmatch', all_patterns)
    return None

def load_gitignore_patterns(base_path: Path) -> list:
    """
    Reads the .gitignore (if present) and returns the patterns.
    """
    gitignore_path = base_path / '.gitignore'
    if gitignore_path.exists():
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            return f.readlines()
    return []