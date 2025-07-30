from pathlib import Path
from fnmatch import fnmatch

def skip_depth(root_path: Path, base_path: Path, max_depth: int) -> bool:
    """
    Returns True if root_path is deeper than max_depth relative to base_path.
    """
    return len(root_path.relative_to(base_path).parts) > max_depth

def filter_dirs(root_path: Path, dirs: list, ignore_spec, manual_ignore_files: list) -> list:
    """
    Removes directories from 'dirs' if they match ignore patterns or
    are in manual_ignore_files.
    """
    return [d for d in dirs if not is_ignored_file(root_path / d, ignore_spec, manual_ignore_files)]

def filter_files(root_path: Path, files: list, ignore_spec, manual_ignore_files: list) -> list:
    """
    Removes files from 'files' if they match ignore patterns or
    are in manual_ignore_files.
    """
    return [f for f in files if not is_ignored_file(root_path / f, ignore_spec, manual_ignore_files)]

def is_ignored_file(
    file_path: Path,
    ignore_spec,
    manual_ignore_files: list
) -> bool:
    """
    True  → skip this path
    False → keep it
    """

    # 1) .gitignore + extra wild-card patterns ---------------------------
    if ignore_spec and ignore_spec.match_file(
        file_path.relative_to(file_path.anchor).as_posix()
    ):
        return True

    # 2) literal file-names that must *always* be skipped ----------------
    if manual_ignore_files:
        # normalise the list once per call
        base_names = {Path(p).name for p in manual_ignore_files}

        #   • exact base-name match  (postcss.config.cjs)
        #   • caller accidentally supplied a path (frontend/postcss.config.cjs)
        #   • caller gave a simple glob (postcss.*)
        name = file_path.name
        if (
            name in base_names
            or file_path.as_posix() in manual_ignore_files
            or any(fnmatch(name, pattern) for pattern in manual_ignore_files)
        ):
            return True
    return False
