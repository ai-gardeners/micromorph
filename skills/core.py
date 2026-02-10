import os, sys

from microcore.ai_func import ai_func

@ai_func()
def request_master(message: str) -> str:
    """Send a message to the master user or process and wait for response."""
    from micromorph import is_subagent
    message = f"<TO_MASTER>\n{message}\n</TO_MASTER>\n>> " if is_subagent() else f"{message}\n>> "
    print(message, file=sys.__stdout__, end='', flush=True)
    return f"<FROM_MASTER>{input()}</FROM_MASTER>"

@ai_func()
def restart():
    """Restart the current process (run it after .py files editing)."""
    os.execv(sys.executable, [sys.executable] + sys.argv)

core_tools = [request_master, restart]

__all__ = ["core_tools", "request_master", "restart"]