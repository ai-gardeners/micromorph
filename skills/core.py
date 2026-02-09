import os, sys
from microcore import ui
from microcore.ai_func import ai_func

@ai_func()
def request_master(message: str) -> str:
    """Send a message to the master user or process and wait for response."""
    print(f"{ui.magenta(message)}\n>> ", file=sys.__stdout__, flush=True)
    return input()

@ai_func()
def restart():
    """Restart the current process (run it after .py files editing)."""
    os.execv(sys.executable, [sys.executable] + sys.argv)

core_tools = [request_master, restart]

__all__ = ["core_tools", "request_master", "restart"]