from pathlib import Path

from microcore import storage
from microcore.ai_func import ai_func


@ai_func()
def write_file(name: str, content: str | bytes, encoding: str = "utf-8"):
    """Write file"""
    return storage.write(name, content, encoding=encoding)

@ai_func()
def read_file(name: str, encoding: str = "utf-8") -> str:
    """Read file"""
    return storage.read(name, encoding=encoding)

@ai_func()
def delete_file(name: str) -> str:
    """Delete file or directory"""
    return storage.delete(name)

@ai_func()
def ls(path: str) -> list[str]:
    """List files"""
    gitignore = set(storage.read(".gitignore", default="").splitlines())
    return [str(p) for p in Path(path).iterdir() if p.name not in gitignore]

fs_tools = [ls, delete_file, write_file, read_file]

__all__ = ["fs_tools", "ls", "delete_file", "write_file", "read_file"]
