import sys
from pathlib import Path

import microcore as mc
from microcore import ui
from microcore.ai_func import ai_func

@ai_func()
def write_file(name: str, content: str | bytes, encoding: str = "utf-8"):
    """Write file"""
    return mc.storage.write(name, content, encoding=encoding)

@ai_func()
def read_file(name: str, encoding: str = "utf-8") -> str:
    """Read file"""
    return mc.storage.read(name, encoding=encoding)

@ai_func()
def ls(path: str) -> list[str]:
    """List files"""
    return [str(p) for p in Path(path).iterdir()]

@ai_func()
def request_master(message: str) -> str:
    """Send a message to the master user or process and wait for response."""
    print(f"{ui.magenta(message)}\n>> ", file=sys.__stdout__, flush=True)
    return input()

tools = [write_file, read_file, ls, request_master]
__all__ = [t.__name__ for t in tools] + ["tools"]
