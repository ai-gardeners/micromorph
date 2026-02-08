import os
import sys
from pathlib import Path

from microcore import ui, storage
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
    gitignore = set(Path(".gitignore").read_text().splitlines()) if Path(".gitignore").exists() else set()
    return [str(p) for p in Path(path).iterdir() if p.name not in gitignore]

@ai_func()
def request_master(message: str) -> str:
    """Send a message to the master user or process and wait for response."""
    print(f"{ui.magenta(message)}\n>> ", file=sys.__stdout__, flush=True)
    return input()

@ai_func()
def restart():
    """Restart the current process (run it after .py files editing)."""
    os.execv(sys.executable, [sys.executable] + sys.argv)

tools = [write_file, read_file, delete_file, ls, request_master, restart]
__all__ = [t.__name__ for t in tools] + ["tools"]
