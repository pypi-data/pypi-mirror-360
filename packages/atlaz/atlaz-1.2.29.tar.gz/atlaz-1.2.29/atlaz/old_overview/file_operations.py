import io
import os
from pathlib import Path

from atlaz.old_overview.file_utils import filter_dirs, filter_files, skip_depth

def gather_directory_tree(
    focus_dirs: list,
    ignore_spec,
    manual_ignore_files: list,
    max_depth: int,
    base_path: Path
) -> str:
    """
    Recursively walks the given focus items (files or directories),
    building a textual tree (e.g. lines with '├── ...'), and returns
    the entire tree as a single string. Skips ignored items,
    as well as directories beyond max_depth.
    """
    base_path = (base_path or Path.cwd()).resolve()
    buffer = io.StringIO()
    for focus_dir in focus_dirs:
        focus_path = Path(focus_dir)

        # If the path is a file, just add a simple line to the "tree"
        if focus_path.is_file():
            # Simple check if it’s ignored
            if ignore_spec and ignore_spec.match_file(
                focus_path.relative_to(focus_path.anchor).as_posix()
            ):
                continue
            if focus_path.name in manual_ignore_files:
                continue
            # Indent depth might be base_path.parts - 1, but you can keep it simple:
            try:
                rel_name = focus_path.relative_to(base_path).as_posix()
            except ValueError:
                # Fallback: keep the absolute path if the file sits outside
                rel_name = focus_path.as_posix()

            buffer.write(f"├── {rel_name}\n")
            continue

        # Otherwise, if it’s a directory, walk it
        if focus_path.is_dir():
            for root, dirs, files in os.walk(focus_path):
                root_path = Path(root)
                if skip_depth(root_path, focus_path, max_depth):
                    continue
                dirs[:] = filter_dirs(root_path, dirs, ignore_spec, manual_ignore_files)
                files = filter_files(root_path, files, ignore_spec, manual_ignore_files)
                write_tree_structure(buffer, root_path, files)
    return buffer.getvalue()

def read_file_data(
    file_path: Path,
    max_size_bytes: int,
    max_lines: int,
    current_line_count: int
) -> tuple[int, str]:
    """
    Reads the file up to max_lines or until total read content
    would exceed max_size_bytes. Returns:
      - new_line_count after reading
      - the actual file text (which may be truncated if we hit a limit)
    """
    file_content_lines = []
    total_bytes = 0

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                current_line_count += 1
                total_bytes += len(line.encode('utf-8'))

                if (total_bytes > max_size_bytes) or (current_line_count >= max_lines):
                    break
                file_content_lines.append(line)

    except Exception as e:
        file_content_lines.append(f"Could not read file: {e}\n")
        current_line_count += 1

    file_text = "".join(file_content_lines)
    return current_line_count, file_text

def write_tree_structure(out_stream, root_path: Path, files: list):
    """
    Writes a simple tree structure (lines with '├── ...') for the given
    directory (root_path) and file list to out_stream (a StringIO).
    """
    depth = len(root_path.parts) - 1
    indent = '    ' * depth
    out_stream.write(f"{indent}├── {root_path.name}\n")
    for file_name in files:
        file_indent = '    ' * (depth + 1) + '└── '
        out_stream.write(f"{file_indent}{file_name}\n")