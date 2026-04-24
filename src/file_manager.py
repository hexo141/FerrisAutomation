import os
import pathlib
import logging
from pathlib import Path
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


class FileManager:
    def __init__(self, allowed_base_paths: Optional[List[str]] = None):
        if allowed_base_paths is None:
            self._allowed_base_paths = None
        else:
            self._allowed_base_paths = [Path(p).resolve() for p in allowed_base_paths]

    def _validate_path(self, path: str) -> Path:
        resolved = Path(path).resolve()
        if self._allowed_base_paths is not None:
            if not any(resolved == base or resolved.is_relative_to(base) for base in self._allowed_base_paths):
                raise ValueError(f"Path '{resolved}' is not within allowed base paths")
        return resolved

    def read_file(self, path: str, encoding: str = "utf-8") -> str:
        resolved = self._validate_path(path)
        logger.info(f"Reading file: {resolved}")
        with open(resolved, "r", encoding=encoding) as f:
            return f.read()

    def write_file(self, path: str, content: str, encoding: str = "utf-8", mode: str = "w") -> None:
        resolved = self._validate_path(path)
        logger.info(f"Writing file: {resolved}")
        with open(resolved, mode, encoding=encoding) as f:
            f.write(content)

    def append_file(self, path: str, content: str, encoding: str = "utf-8") -> None:
        resolved = self._validate_path(path)
        logger.info(f"Appending to file: {resolved}")
        with open(resolved, "a", encoding=encoding) as f:
            f.write(content)

    def list_directory(self, path: str) -> List[Dict]:
        resolved = self._validate_path(path)
        logger.info(f"Listing directory: {resolved}")
        items = []
        for item in resolved.iterdir():
            item_info = {
                "name": item.name,
                "type": "file" if item.is_file() else "directory",
                "size": item.stat().st_size if item.is_file() else 0
            }
            items.append(item_info)
        return items

    def get_file_info(self, path: str) -> Dict:
        resolved = self._validate_path(path)
        logger.info(f"Getting file info: {resolved}")
        stat = resolved.stat()
        return {
            "name": resolved.name,
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "is_file": resolved.is_file(),
            "is_dir": resolved.is_dir()
        }

    def delete_file(self, path: str) -> None:
        resolved = self._validate_path(path)
        logger.info(f"Deleting file: {resolved}")
        if resolved.is_file():
            resolved.unlink()
        else:
            raise ValueError(f"Path '{resolved}' is not a file")

    def create_directory(self, path: str, exist_ok: bool = True) -> None:
        resolved = self._validate_path(path)
        logger.info(f"Creating directory: {resolved}")
        resolved.mkdir(parents=True, exist_ok=exist_ok)

    def search_files(self, path: str, pattern: str) -> List[Path]:
        resolved = self._validate_path(path)
        logger.info(f"Searching files in {resolved} with pattern: {pattern}")
        matches = list(resolved.glob(pattern))
        return matches
