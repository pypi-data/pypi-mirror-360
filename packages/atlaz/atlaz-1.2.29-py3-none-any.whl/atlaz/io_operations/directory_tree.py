# atlaz/io_operations/directory_tree.py
import logging
import os
from pathlib import Path
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def build_directory_tree_json(root_path: Path, ignore=None, max_depth=20, level=0):
    """
    Recursively build a nested JSON representation of the directory tree.
    """
    if ignore is None:
        ignore = set()
    if level > max_depth:
        return []
    items = []
    try:
        for entry in sorted(os.scandir(root_path), key=lambda e: e.name.lower()):
            if entry.name in ignore or entry.name.startswith('.'):
                continue
            entry_path = Path(entry.path)
            if entry.is_dir():
                items.append({
                    "name": entry.name,
                    "type": "directory",
                    "path": str(entry_path),
                    "children": build_directory_tree_json(
                        entry_path,
                        ignore=ignore,
                        max_depth=max_depth,
                        level=level + 1
                    )
                })
            else:
                items.append({
                    "name": entry.name,
                    "type": "file",
                    "path": str(entry_path)
                })
    except PermissionError:
        pass
    return items


def build_directory_tree_string(selected_files: List[str]) -> str:
    """
    Builds an ASCII directory tree string from a list of file paths.
    """
    tree = {}
    directories = set()
    files = set()
    for file_path in selected_files:
        path = Path(file_path)
        if file_path.endswith('/'):
            directories.add(path.as_posix().rstrip('/'))
        else:
            files.add(path.as_posix())
    for file_path in files:
        path = Path(file_path)
        for parent in path.parents:
            if parent == Path('/'):
                continue
            directories.add(parent.as_posix())
    conflicting_paths = directories.intersection(files)
    if conflicting_paths:
        conflict_path = conflicting_paths.pop()
        raise ValueError(f"Conflict at '{conflict_path}': path is both a file and a directory.")
    sorted_directories = sorted(directories, key=lambda x: x.count('/'))
    for dir_path in sorted_directories:
        path = Path(dir_path)
        parts = path.parts
        current_level = tree
        for part in parts:
            if part not in current_level:
                current_level[part] = {}
            current_level = current_level[part]
    for file_path in sorted(files):
        path = Path(file_path)
        parts = path.parts
        current_level = tree
        for part in parts[:-1]:
            current_level = current_level[part]
        file_name = parts[-1]
        current_level[file_name] = None
    lines = []
    def traverse(current_dict: Dict[str, Any], prefix: str = ""):
        dirs = sorted([k for k, v in current_dict.items() if isinstance(v, dict)], key=lambda x: x.lower())
        files_sorted = sorted([k for k, v in current_dict.items() if v is None], key=lambda x: x.lower())
        sorted_keys = dirs + files_sorted
        total_items = len(sorted_keys)
        for idx, key in enumerate(sorted_keys):
            is_last = (idx == total_items - 1)
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{key}")
            if isinstance(current_dict[key], dict):
                extension = "    " if is_last else "│   "
                traverse(current_dict[key], prefix + extension)
    traverse(tree)
    return "\n".join(lines)


def make_paths_relative(tree_list, root_path: Path):
    """
    Recursively convert each item's 'path' from absolute to relative
    relative to `root_path`.
    """
    new_list = []
    for item in tree_list:
        new_item = item.copy()
        abs_path = Path(new_item['path'])
        try:
            rel_path = abs_path.relative_to(root_path)
            new_item['path'] = str(rel_path)
        except ValueError:
            pass
        if 'children' in new_item:
            new_item['children'] = make_paths_relative(new_item['children'], root_path)
        new_list.append(new_item)
    return new_list
