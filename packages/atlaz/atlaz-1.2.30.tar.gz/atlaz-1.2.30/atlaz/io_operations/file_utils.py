# atlaz/io_operations/file_mediator.py
import json
import logging
from pathlib import Path
from pydantic import BaseModel
from typing import Any, Union

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def file_exists(path: Path) -> bool:
    """
    Check if a file/directory at `path` exists.
    """
    return path.exists()

def unlink_file(path: Path) -> None:
    """
    Delete a file at `path` if it exists.
    """
    if path.exists():
        path.unlink()

def read_txt(path: Union[Path, str]) -> str:
    """
    Read and return text from a .txt file at `path`.
    """
    if isinstance(path, str):
        path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return f.read()

def write_txt(content: str, path: Union[Path, str]) -> None:
    """
    Write `content` to a .txt file at `path`, ensuring parent dirs exist.
    """
    if isinstance(path, str):
        path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write(content)

def read_json(path: Union[Path, str]) -> Any:
    """
    Read JSON data from `path` and return the parsed object.
    """
    if isinstance(path, str):
        path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def _pydantic_default(obj: Any) -> Any:
    """
    Fallback encoder for json.dump(): converts Pydantic models to dicts.

    • Pydantic v2 → model_dump(mode="json", exclude_none=True)
    • Pydantic v1 → dict(exclude_none=True)
    • Anything else → str(obj)  (last-ditch fallback to keep json.dump happy)
    """
    if BaseModel is not None and isinstance(obj, BaseModel):
        if hasattr(obj, "model_dump"):                # Pydantic v2
            return obj.model_dump(mode="json", exclude_none=True)
        return obj.dict(exclude_none=True)            # Pydantic v1
    return str(obj)


def write_json(data: Any, path: Union[Path, str]) -> None:
    """
    Serialize *any* Python object to pretty-printed UTF-8 JSON and write it to
    `path`, creating parent directories as needed.

    Pydantic models are handled transparently via `_pydantic_default`.
    """
    path = Path(path) if isinstance(path, str) else path
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4, default=_pydantic_default)

def is_binary(file_path: Path) -> bool:
    """
    A simple check for binary content by scanning the first 1024 bytes for null bytes.
    """
    try:
        with file_path.open('rb') as f:
            chunk = f.read(1024)
            return b'\0' in chunk
    except Exception:
        return True

def is_large_or_binary(file_path: Path) -> bool:
    """
    Returns True if the file is likely binary or if it's larger than 1 MB.
    """
    one_mb_in_bytes = 1024 * 1024
    if file_path.exists():
        if file_path.stat().st_size > one_mb_in_bytes:
            return True
        if is_binary(file_path):
            return True
    return False