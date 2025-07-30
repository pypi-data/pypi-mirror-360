# atlaz/io_operations/file_mediator.py
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List
from flask import jsonify
from pydantic import ValidationError

from atlaz.codeGen.schema import Files
from atlaz.io_operations.file_utils import file_exists, is_large_or_binary, read_txt, unlink_file
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_files(selected_files: List[str]) -> List[Dict[str, Any]]:
    """
    Load a list of file paths, skipping large or binary files, returning 
    a list of dicts conforming to Pydantic schema `Files`.
    """
    loaded_files = []
    for file_path_str in selected_files:
        file_path = Path(file_path_str)
        if not file_exists(file_path):
            logger.warning(f"File does not exist: {file_path}")
            continue
        if is_large_or_binary(file_path):
            logger.warning(f"Skipping binary or large file: {file_path}")
            continue
        try:
            content = read_txt(file_path)
        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            continue
        try:
            file_record = Files(name=file_path_str, content=content)
            loaded_files.append(file_record.dict())
            logger.info(f"Loaded file: {file_path.name}")
        except ValidationError as ve:
            logger.error(f"Validation error for file {file_path}: {ve}")
            continue
    return loaded_files

def obtain_write_paths():
    """
    Creates or clears out the standard 3 directories we use:
    original/, replacing/, created/.
    Also unlinks the 'files.json' if it exists.
    Returns a tuple of (replacing_dir, created_dir, original_dir, files_json_path).
    """
    atlaz_helper_dir = Path(__file__).parent.parent.parent.parent / ".atlaz_helper"
    original_dir = atlaz_helper_dir / "original"
    replacing_dir = atlaz_helper_dir / "replacing"
    created_dir = atlaz_helper_dir / "created"
    original_dir.mkdir(parents=True, exist_ok=True)
    replacing_dir.mkdir(parents=True, exist_ok=True)
    created_dir.mkdir(parents=True, exist_ok=True)
    frontend_dir = Path(__file__).parent.parent / 'frontend'
    files_json_path = frontend_dir / 'files.json'
    unlink_file(files_json_path)
    return replacing_dir, created_dir, original_dir, files_json_path, frontend_dir

def remove_json_files():
    """
    Delete atlaz/frontend/files.json if it exists.
    """
    frontend_dir = Path(__file__).parent.parent / 'frontend'
    files_json_path = frontend_dir / 'files.json'
    unlink_file(files_json_path)

def remove_explanation_file():
    """
    Delete atlaz/frontend/explanation.txt if it exists.
    """
    frontend_dir = Path(__file__).parent.parent / 'frontend'
    explanation_file_path = frontend_dir / 'explanation.txt'
    unlink_file(explanation_file_path)

def handle_apply_changes():
    project_root = Path(__file__).resolve().parents[2]  
    cmd_root = Path.cwd()
    frontend_dir = project_root / 'atlaz' / 'frontend'
    files_json_path = frontend_dir / 'files.json'
    if not files_json_path.exists():
        return jsonify({"status": "error", "message": "No files.json found."}), 404
    with files_json_path.open("r", encoding="utf-8") as f:
        generated_files = json.load(f)
    for file_info in generated_files:
        file_type = file_info.get('type')
        full_name = file_info.get('full_name')
        content = file_info.get('content', '')
        if not full_name:
            continue
        if file_type == 'replacing':
            real_relative = full_name.replace('replacing-', '', 1)
        elif file_type == 'created':
            real_relative = full_name.replace('created-', '', 1)
        else:
            continue
        real_path = cmd_root / real_relative
        real_path.parent.mkdir(parents=True, exist_ok=True)
        real_path.write_text(content, encoding='utf-8')
    return jsonify({"status": "success", "message": "Applied changes successfully."})