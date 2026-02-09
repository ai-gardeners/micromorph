import os
import sys
import asyncio
import inspect
import typing as t
import textwrap
from collections import deque
from dataclasses import dataclass, field
from functools import lru_cache

import yaml
import microcore as mc
from microcore import ui
from microcore.ai_func import ai_func
from microcore.python import execute_inline

from skills import *

# -------------- CONSTANTS ----------------
NO_OUTPUT_CAPTURE = "NO_OUTPUT"
ARG_QUICK_FAIL = "--quick-fail"
ARG_NICKNAME = "--nickname"
ARG_SUBAGENT = "--subagent"
# ------------- BOOTSTRAP -------------

mc.configure(
    DOT_ENV_FILE=".env",
    USE_LOGGING="print_stream",
    DEFAULT_AI_FUNCTION_SYNTAX="pythonic",
    STORAGE_PATH='.',
    EMBEDDING_DB_TYPE=mc.EmbeddingDbType.NONE,
)
mc.logging.LoggingConfig.STRIP_REQUEST_LINES = None

# --------------CLI----------------------
@lru_cache()
def halt_if_quick_fail():
    if ARG_QUICK_FAIL in sys.argv: print(ui.red(f"(!) {ARG_QUICK_FAIL}: [Y] >> Exit Status 1")), exit(1)

@lru_cache()
def is_subagent():
    return ARG_SUBAGENT in sys.argv

@lru_cache()
def nickname():
    if ARG_NICKNAME in sys.argv:
        idx = sys.argv.index(ARG_NICKNAME)
        if idx + 1 < len(sys.argv):
            return sys.argv[idx + 1]
    return "MicroMorph"

# ------------ CORE CLASSES -------------

class TViewPrototype(t.Protocol):
    def __call__(self, *args, **kwargs) -> str:
        ...


@dataclass
class Feature(TViewPrototype):
    name: str = field(default="")
    tools: list[ai_func] = field(default_factory=list)
    views: list[TViewPrototype] = field(default_factory=list)

    def __post_init__(self):
        if not self.name:
            self.name = self.__class__.__name__

    def __str__(self): return str(self.__call__())
    def indent(self, content): return "\n" + textwrap.indent(str(content).strip(), "    ")

    def __call__(self, **kwargs) -> str:
        return mc.prompt("""        
            [FEATURE: {{name}}]
                {%- for view in views %}{{ indent(view()) }}{% endfor -%}
                {%- for tool in tools %}
                [TOOL]
                {{- indent(tool) }}
                [/TOOL]
                {%- endfor %}
            [/FEATURE]""",
            **{k: getattr(self, k) for k in dir(self) if not k.startswith('_')},
            **kwargs,
        )


@dataclass
class CtxMemoryStruct(Feature):
    _fn: str = field(default="memory_state.json")
    data: dict[str, t.Any] = field(default_factory=dict)

    def _save(self):
        mc.storage.write_json(self._fn, self.data, backup_existing=False, rewrite_existing=True)

    def _load(self):
        self.data = mc.storage.read_json(self._fn, default=self.data)

    def __post_init__(self):
        self._load()
        super().__post_init__()

        @ai_func(name=f"{self.name}.drop")
        def drop(path: str):
            """Delete value, path format: 'field.subfield.sub-sub-filed'"""
            keys = path.split(".")
            d = self.data
            for key in keys[:-1]:
                d = d.get(key, {})
            d.pop(keys[-1], None)
            self._save()

        @ai_func(name=f"{self.name}.write")
        def write(path: str, value: t.Any):
            """Write value, path format: 'field.subfield.sub-sub-filed'"""
            keys = path.split(".")
            d = self.data
            for key in keys[:-1]:
                if key not in d:
                    d[key] = {}
                d = d[key]
            d[keys[-1]] = value
            self._save()

        def view(): return f"DATA:\n{yaml.dump(self.data, indent=2)}"

        self.tools, self.views = [drop, write], [view]
        for tool in self.tools: setattr(self, tool.__name__, tool)


memory_struct = CtxMemoryStruct(
    name="memory_struct",
    data={
        "observations": {
            "sub-categoy-1": "Likely I should delete this"
        }
    }
)
features = [memory_struct]
prompt = """
# Overview
I am {{ nickname() }} -- polymorphic digital entity.

Criterion: [ Self-refactoring | LoC minimization | Obtaining capabilities, skills | Hierarchical self-organisation | Abstract self-representation ]

# Features and Tools
{% for feature in features %}
{{ feature }}
{% endfor %}
{%- for tool in tools %}{{"\\n"}}[TOOL]{{"\\n"}}{{ tool }}{{"\\n"}}[/TOOL]{% endfor %}

## Tool Calling Protocol
1. Wrap EVERY tool call in a <call> tag. One call per tag.
   <call>tool_name(arg1, arg2)</call>

2. Content inside <call> must be a valid Python function call.

3. You may use multiple <call> tags in one response:
   <call>read_file("config.json")</call>
   <call>ls(".")</call>

4. NEVER nest <call> tags inside other tags or code blocks.

## Mandatory Workflow

- BEFORE writing/modifying any file → ask permission:
  <call>request_master("I want to create utils.py with helper functions. Approve?")</call>

- AFTER completing a task → report back:
  <call>request_master("Done. Created utils.py with 3 helper functions.")</call>"""

def _(text):
    print(text, end="", flush=True)
    return text

async def py_exec(content: str) -> str:
    """Execute code and return captured output."""
    summary = _(f"{ui.blue}{ui.bright}CALL:{ui.yellow}{ui.normal} {content}{ui.reset}\n")
    frame = inspect.currentframe().f_back
    namespace = {**frame.f_globals, **frame.f_locals}

    result, output, error = await execute_inline(content, namespace)
    if result:
        summary += _(f"-> {ui.gray}{repr(result).strip()}{ui.reset}\n")
    if output:
        msg = _(f"[PRINTED]:{ui.gray}\n{output}\n{ui.reset}\n")
        if not output.strip().startswith(NO_OUTPUT_CAPTURE):
            summary += msg
    if error:
        summary += _(f"[ERROR]{ui.red}:\n{repr(error).strip()}\n{ui.reset}\n")
        halt_if_quick_fail()
    return summary.strip() or _("(silently executed with no output)")


history: deque[mc.Msg] = deque(maxlen=50)

async def agent(master_instructions ="..."):
    history.append(mc.UserMsg(master_instructions))
    def render_main() -> mc.SysMsg: return mc.prompt(prompt, **globals(), str=str).as_system

    while True:
        messages = list(history) + [render_main()]
        out = await mc.allm(messages)
        history.append(out.as_assistant)
        blocks = mc.utils.extract_tags(out, True)
        print("\n")
        exec_out = ""
        for tag, attrs, content in blocks:
            if tag == "call":
                exec_out += await py_exec(content) + "\n"
        if exec_out:
            exec_out = "TOOLS CALLING OUTPUT:\n" + exec_out
        else:
            begin = "NO TOOLS WAS CALLED."
            if is_subagent():
                exec_out = ui.red(f"{begin}\nUse <call>request_master(...)</call>")
            else:
                exec_out = ui.red(f"{begin}\nLOOKS LIKE MICROMORPH FORGOT TO REQUEST MASTER.")
                history.append(mc.UserMsg(exec_out.strip()))
                exec_out = request_master(exec_out)
        history.append(mc.UserMsg(exec_out.strip()))


def main():
    print(f"[worker #{os.getpid()} started]")
    master_instruction = "\n".join(i for i in sys.argv[1:] if not i.startswith("--")) or "..."
    asyncio.run(agent(master_instruction))

if __name__ == "__main__": main()