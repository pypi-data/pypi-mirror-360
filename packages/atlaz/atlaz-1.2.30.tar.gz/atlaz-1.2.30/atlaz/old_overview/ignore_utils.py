"""
atlaz.old_overview.ignore_utils
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Helpers for building the ignore list used by the repository scanner.
Now supports an opt-out flag (`use_gitignore`) so callers can bypass the
project-root .gitignore file entirely.
"""
from pathlib import Path
import pathspec


# --------------------------------------------------------------------------- #
# 1.  Default filename / glob exclusions
# --------------------------------------------------------------------------- #
def append_default_ignores(manual_ignore_files: list | None) -> list[str]:
    """
    Ensure a base set of noisy or non-source artefacts is always ignored
    unless the caller explicitly removes them.

    Returns a *new* list so the original isn't mutated.
    """
    common_ignores = [
        ".git",
        "node_modules",
        "build",
        "dist",
        "__pycache__",
        "venv",
        "*.log",
        "node_modules/",
        "*.tmp",
        ".env",
        "dist/",
        "atlaz.egg-info",
        "LICENSE",
        "MANIFEST.in",
    ]

    manual_ignore_files = list(manual_ignore_files or [])
    for pattern in common_ignores:
        if pattern not in manual_ignore_files:
            manual_ignore_files.append(pattern)
    return manual_ignore_files


# --------------------------------------------------------------------------- #
# 2.  Build a PathSpec of ignore patterns
# --------------------------------------------------------------------------- #
def compile_ignore_patterns(
    base_path: Path,
    manual_patterns: list | None,
    *,
    use_gitignore: bool = True,
):
    """
    Combine patterns from `.gitignore` + *manual_patterns* into a single
    ``pathspec.PathSpec`` instance.

    Parameters
    ----------
    base_path
        Repository root used to locate the top-level ``.gitignore``.
    manual_patterns
        Extra git-wildmatch patterns supplied by the caller.
    use_gitignore
        • ``True``  → include patterns from ``.gitignore`` (default)  
        • ``False`` → *ignore* the file entirely.

    Returns
    -------
    PathSpec | None
        Compiled matcher, or ``None`` if no patterns at all.
    """
    patterns: list[str] = []

    if use_gitignore:
        patterns.extend(load_gitignore_patterns(base_path))

    if manual_patterns:
        patterns.extend(manual_patterns)

    return (
        pathspec.PathSpec.from_lines("gitwildmatch", patterns)
        if patterns
        else None
    )


# --------------------------------------------------------------------------- #
# 3.  Read top-level .gitignore
# --------------------------------------------------------------------------- #
def load_gitignore_patterns(base_path: Path) -> list[str]:
    """
    Load and return every line from the repository-root ``.gitignore``.
    """
    gitignore_path = base_path / ".gitignore"
    if gitignore_path.exists():
        with gitignore_path.open("r", encoding="utf-8") as f:
            return f.readlines()
    return []
