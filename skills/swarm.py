import subprocess, os, fcntl, select, sys, signal
from typing import TYPE_CHECKING

import microcore as mc
from microcore.ai_func import ai_func

if TYPE_CHECKING:
    from micromorph import Conversation

class Worker:
    def __init__(
        self,
        master_thread: "Conversation",
        nickname: str,
        master_instruction: str
    ):
        from micromorph import ARG_QUICK_FAIL, ARG_SUBAGENT
        self.out = ""
        self.master_thread = master_thread
        self.nickname = nickname
        self.messages = ["@master: " + master_instruction]
        self.proc = subprocess.Popen(
            ["python", "micromorph.py", ARG_QUICK_FAIL, ARG_SUBAGENT]
            + (["--nickname", nickname] if nickname else [])
            + [master_instruction],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, bufsize=1,
        )
        fcntl.fcntl(self.proc.stdout, fcntl.F_SETFL, os.O_NONBLOCK)
        _workers[nickname] = self

    def kill(self):
        self.proc.send_signal(signal.SIGUSR1)  # calls managed cleanup
        #self.proc.kill()
        del _workers[self.nickname]

    def on_response(self, message: str):
        self.master_thread.add(mc.AssistantMsg(f"@worker [{self.nickname}]: {message}"))

    def capture_messages(self):
        blocks = mc.utils.extract_tags(self.out, True)
        for tag, attrs, content in blocks:
            if tag == "TO_MASTER":
                if content not in self.messages:
                    self.messages.append("@worker: " + content)
                    self.on_response(content)

    def listen(self):
        proc = self.proc
        while proc.poll() is None:
            if select.select([proc.stdout], [], [], 0.5)[0]:
                try:
                    chunk = proc.stdout.read(4096)
                    if chunk:
                        print(
                            str(chunk).replace("\n", f"\n@{self.nickname} | "),
                            file=sys.__stdout__,
                            end="",
                            flush=True
                        )
                        self.out += chunk
                        self.capture_messages()
                except BlockingIOError:
                    pass

            # if "[ANSWER IS=35]" in out:
            #     print("\n[calculation successful, exiting]")
            #     proc.kill()
            #     break

            if stdin_blocked(proc.pid):
                msg = f"@worker [{self.nickname}] is waiting..."
                print(msg, file=sys.__stdout__, flush=True)
                self.master_thread.add(mc.AssistantMsg(msg))
                return

    def send_input(self, input_str: str):
        self.messages.append(input_str)
        self.proc.stdin.write(input_str + "\n")
        self.proc.stdin.flush()

    def is_waiting_for_input(self) -> bool:
        return stdin_blocked(self.proc.pid)

    def is_finished(self) -> bool:
        return self.proc.poll() is not None


def stdin_blocked(pid) -> bool:
    try:
        for tid in os.listdir(f"/proc/{pid}/task"):
            p = open(f"/proc/{pid}/task/{tid}/syscall").read().split()
            if p[0] == "0" and p[1] == "0x0": return True
    except: pass
    return False


_workers: dict[str, Worker] = {}

@ai_func()
def spawn_worker(nickname: str, master_instruction: str):
    """
    Spawn a new worker.
    Important: do not duplicate master_instruction using 'request_worker'.
    """
    from micromorph import conv
    Worker(
        nickname=nickname,
        master_instruction=master_instruction,
        master_thread=conv,
    ).listen()

@ai_func()
def request_worker(nickname: str, message: str):
    _workers[nickname].send_input(message)
    _workers[nickname].listen()


@ai_func()
def kill_worker(nickname: str):
    _workers[nickname].kill()

swarm_tools = [spawn_worker, request_worker, kill_worker]

__all__ = ["swarm_tools", "spawn_worker", "request_worker", "kill_worker"]
