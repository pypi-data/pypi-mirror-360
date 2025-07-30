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
    focus_directories: Optional[List[str]] = None,
    manual_ignore_files: Optional[List[str]] = None,
    project_root: Union[str, Path, None] = None,
) -> str:
    """
    Build an overview prompt (directory tree + code snippets).

    Args:
        focus_directories: paths to scan.  *None* or [] ⇒ scan the whole
            project_root.
        manual_ignore_files: extra filename or glob patterns to skip.
        project_root: root of the project you want to scan; defaults to the
            caller’s current working directory.

    Returns:
        A single, ready-to-prompt string.
    """
    # ------------------------------------------------------------------ #
    # 1. Decide where the project root is and what we want to walk
    # ------------------------------------------------------------------ #
    project_root = (
        Path(project_root).resolve()
        if project_root is not None
        else Path.cwd().resolve()
    )

    if not focus_directories:                    # catches None *and* []
        focus_directories = [str(project_root)]

    manual_ignore_files = manual_ignore_files or []

    # Fake script_path so that  .parent.parent.parent  ===  project_root
    fake_script_path = (
        project_root / "__atlaz_dummy__" / "__atlaz_dummy__" / "__dummy__.py"
    )

    directory_data, directory_structure = gather_repository(
        script_path=fake_script_path,
        focus_directories=focus_directories,
        manual_ignore_files=manual_ignore_files,
    )

    # ------------------------------------------------------------------ #
    # 2. Trim *common* leading whitespace so the root is flush-left
    # ------------------------------------------------------------------ #
    raw_lines = directory_structure.splitlines()

    # Leading-space length for every line that contains a tree marker
    indents = [
        len(line) - len(line.lstrip())
        for line in raw_lines
        if "──" in line
    ]
    left_margin = min(indents) if indents else 0

    aligned_tree = "\n".join(line[left_margin:] for line in raw_lines)

    # ------------------------------------------------------------------ #
    # 3. Convert absolute file names inside directory_data → relative
    # ------------------------------------------------------------------ #
    for fd in directory_data:
        abs_path = Path(fd["name"]).resolve()
        try:
            fd["name"] = abs_path.relative_to(project_root).as_posix()
        except ValueError:
            fd["name"] = abs_path.name  # fallback if the file is outside

    # ------------------------------------------------------------------ #
    # 4. Stitch everything into the final prompt
    # ------------------------------------------------------------------ #
    prompt = aligned_tree + "\n\n" + build_code_prompt(directory_data)
    prompt = f'```CodeOverview\n{prompt}\n```'
    return prompt

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