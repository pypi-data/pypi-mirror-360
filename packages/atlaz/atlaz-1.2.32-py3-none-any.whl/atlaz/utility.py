import json
import os
from pathlib import Path
import tiktoken
from typing import Optional, List, Union
from atlaz.old_overview.main_overview import gather_repository

def count_tokens(string_inp):
    encc = tiktoken.encoding_for_model("gpt-4")
    encoded_str = encc.encode(string_inp)
    return len(encoded_str)

def build_code_prompt(file_contents: list[dict]):
    output_text = '\n'
    for file in file_contents:
        output_text += f'```{file["name"]}\n{file["content"]}\n```\n\n\n'
    return output_text[:-2]

def manual_overview(
    *,
    focus_directories: Optional[List[str]] = None,
    manual_ignore_files: Optional[List[str]] = None,
    project_root: Union[str, Path, None] = None,
    use_gitignore: bool = False,  # ← NEW
) -> str:
    """
    Build a combined directory-tree + code-snippet prompt.

    Parameters
    ----------
    focus_directories
        List of paths to scan. ``None`` ⇒ the entire *project_root*.
    manual_ignore_files
        Extra filename/glob patterns to skip **in addition** to defaults.
    project_root
        Root of the project; defaults to the caller's CWD.
    use_gitignore
        If ``False``, ignore rules from the repository's `.gitignore`
        are *not* loaded.
    """
    # -- 1. Resolve root & targets ------------------------------------ #
    project_root = Path(project_root).resolve() if project_root else Path.cwd().resolve()
    focus_directories = focus_directories or [str(project_root)]
    manual_ignore_files = manual_ignore_files or []

    # Fake script_path so that .parent.parent.parent == project_root
    fake_script_path = project_root / "__atlaz_dummy__" / "__atlaz_dummy__" / "__dummy__.py"

    directory_data, directory_structure = gather_repository(
        script_path=fake_script_path,
        focus_directories=focus_directories,
        manual_ignore_files=manual_ignore_files,
        use_gitignore=use_gitignore,  # ← pass through
    )

    # -- 2. Align tree flush-left ------------------------------------- #
    raw_lines = directory_structure.splitlines()
    indents = [len(l) - len(l.lstrip()) for l in raw_lines if "──" in l]
    left_margin = min(indents) if indents else 0
    aligned_tree = "\n".join(l[left_margin:] for l in raw_lines)

    # -- 3. Convert absolute paths → repo-relative -------------------- #
    for fd in directory_data:
        abs_path = Path(fd["name"]).resolve()
        try:
            fd["name"] = abs_path.relative_to(project_root).as_posix()
        except ValueError:
            fd["name"] = abs_path.name

    # -- 4. Stitch final prompt --------------------------------------- #
    prompt = aligned_tree + "\n\n" + build_code_prompt(directory_data)
    return f"```CodeOverview\n{prompt}\n```"

def get_directory_data(focus_directories: list[str], manual_ignore_files: list[str]) -> list[dict]:
    """
    Uses gather_repository to scan the repository and return the file data.
    
    Returns a list of dictionaries, each with 'name' and 'content' keys.
    """
    directory_data, _ = gather_repository(
        script_path=Path(__file__).resolve().parent,
        focus_directories=focus_directories,
        manual_ignore_files=manual_ignore_files
    )
    return directory_data

def analyze_long_files(directory_data: list[dict], min_lines: int = 150) -> list[str]:
    """
    Returns a list of strings for files that are longer than min_lines.
    
    Each string includes the file name and its line count.
    """
    long_files = []
    for file in directory_data:
        line_count = len(file["content"].splitlines())
        if line_count > min_lines:
            long_files.append(f"{file['name']}: {line_count} lines")
    return long_files

def analyze_folders(focus_directories: list[str], ignore_set: set = None, threshold: int = 6) -> list[str]:
    """
    Walks through each focus directory and returns a list of folder summaries.
    
    Only folders with more than `threshold` items (files or subdirectories)
    are included, while ignoring any items in the provided ignore_set.
    """
    if ignore_set is None:
        ignore_set = {"__init__.py", "__pycache__"}
    
    folders_info = []
    
    for focus_dir in focus_directories:
        focus_path = Path(focus_dir)
        # Skip if the focus item is a file.
        if focus_path.is_file():
            continue
        
        # Walk through the directory tree.
        for root, dirs, files in os.walk(focus_path):
            # Filter out ignored directories for traversal.
            dirs[:] = [d for d in dirs if d not in ignore_set]
            if Path(root).name in ignore_set:
                continue
            
            # Combine subdirectories and files, filtering out ignored items.
            items = dirs + files
            filtered_items = [item for item in items if item not in ignore_set]
            if len(filtered_items) > threshold:
                try:
                    rel_path = Path(root).relative_to(focus_path)
                except ValueError:
                    rel_path = Path(root)
                folder_name = str(rel_path) if str(rel_path) != "." else focus_dir
                folders_info.append(f"Folder '{folder_name}': {len(filtered_items)} items")
    
    return folders_info

def build_report(long_files: list[str], folders_info: list[str]) -> str:
    """
    Combines the results from file and folder analyses into a final report.
    """
    report_lines = []
    
    if long_files:
        report_lines.append("Files longer than 150 lines:")
        report_lines.extend(long_files)
    else:
        report_lines.append("No files longer than 150 lines found.")
    
    if folders_info:
        report_lines.append("\nFolders with more than 6 items:")
        report_lines.extend(folders_info)
    else:
        report_lines.append("\nNo folders with more than 6 items found.")
    
    return "\n".join(report_lines)

def analyse_codebase(focus_directories: list[str], manual_ignore_files: list[str]) -> str:
    """
    Scans the repository using the given focus directories and ignore files.
    
    Returns a string report containing:
      1. A list of scripts (files) that are longer than 150 lines with their line counts.
      2. A list of folders that contain more than 6 items (files or subdirectories),
         excluding standard ignored items (e.g. '__init__.py' and '__pycache__').
    """
    directory_data = get_directory_data(focus_directories, manual_ignore_files)
    long_files = analyze_long_files(directory_data, min_lines=150)
    folders_info = analyze_folders(focus_directories, ignore_set={"__init__.py", "__pycache__"}, threshold=6)
    return build_report(long_files, folders_info)