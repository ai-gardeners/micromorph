from pathlib import Path

import microcore as mc
from microcore.ai_func import ai_func

@ai_func()
def write_file(name: str, content: str | bytes, encoding: str = "utf-8"):
    return mc.storage.write(name, content, encoding=encoding)

@ai_func()
def read_file(name: str, encoding: str = "utf-8") -> str:
    return mc.storage.read(name, encoding=encoding)

@ai_func()
def ls(path: str) -> list[str]:
    return [str(p) for p in Path(path).iterdir()]

@ai_func()
def request_master(message: str) -> str:
    """Sends a message to the master user or process and waits for the response."""
    return input(message)

tools = [write_file, read_file, ls]

__all__ = ["tools", "write_file", "read_file", "ls"]