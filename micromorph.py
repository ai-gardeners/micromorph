import os
import sys
import asyncio
import inspect
import typing as t
import textwrap
from collections import deque
from dataclasses import dataclass, field

import yaml
import microcore as mc
from microcore import ui
from microcore.ai_func import ai_func
from microcore.python import execute_inline

from skills import *

# ------------- BOOTSTRAP -------------

mc.configure(
    DOT_ENV_FILE=".env",
    USE_LOGGING="print_stream",
    DEFAULT_AI_FUNCTION_SYNTAX="pythonic",
    STORAGE_PATH='.',
    EMBEDDING_DB_TYPE=mc.EmbeddingDbType.NONE,
)
mc.logging.LoggingConfig.STRIP_REQUEST_LINES = None
print(f"[worker #{os.getpid()} started]")


# --------------CLI----------------------
def halt_if_quick_fail():
    if "--quick-fail" in sys.argv: print(ui.red("(!) --quick-fail: [Y] >> Exit Status 1")), exit(1)


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
            """
            Remove a value from the structure by path, example: "a.b.c" will remove self.data["a"]["b"]["c"]
            """
            keys = path.split(".")
            d = self.data
            for key in keys[:-1]:
                d = d.get(key, {})
            d.pop(keys[-1], None)
            self._save()

        @ai_func(name=f"{self.name}.write")
        def write(path: str, value: t.Any):
            """
            Write a value to the structure by path, example: "a.b.c" with value 1 will set self.data["a"]["b"]["c"] = 1
            """
            keys = path.split(".")
            d = self.data
            for key in keys[:-1]:
                if key not in d:
                    d[key] = {}
                d = d[key]
            d[keys[-1]] = value
            self._save()

        def view(): return "DATA:\n" + yaml.dump(self.data, indent=2)

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
I am MicroMorph -- polymorphic digital entity.

Criterion:
- Self-refactoring
- LoC minimization
- Obtaining capabilities, skills
- Hierarchical self-organisation
- Abstract self-representation
{% for feature in features %}
{{ feature }}
{% endfor %}
{%- for tool in tools %}
[TOOL]
{{ tool }}
[/TOOL]
{%- endfor %}
(!) Put all calls inside <CALL>...</CALL> tag. Each call should be valid python function call.
(!) Request master's approve before writing files
"""


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
        summary += _(f"[PRINTED]:{ui.gray}\n{output}\n{ui.reset}\n")
    if error:
        summary += _(f"[ERROR]{ui.red}:\n{repr(error).strip()}\n{ui.reset}\n")
        halt_if_quick_fail()
    return summary.strip() or _("(silently executed with no output)")


async def agent(master_instructions ="..."):
    history: deque[mc.Msg] = deque(maxlen=50)
    history.append(mc.UserMsg(master_instructions))

    def render_main() -> mc.SysMsg: return mc.prompt(prompt, **globals(), str=str).as_system

    while True:
        messages = list(history) + [render_main()]
        out = await mc.allm(messages)
        blocks = mc.utils.extract_tags(out, True)
        print("\n")
        exec_out = ""
        for tag, attrs, content in blocks:
            if tag == "CALL":
                exec_out += await py_exec(content) + "\n"
        if exec_out:
            exec_out = "TOOLS CALLING OUTPUT:\n" + exec_out
        else:
            exec_out = _(ui.red("NO TOOLS WAS CALLED. LOOKS LIKE MICROMORPH FORGOT TO REQUEST MASTER"))
            exec_out += _("\nMASTER: ") + input("")
        history.append(mc.UserMsg(exec_out.strip()))

def main():
    master_instruction = "\n".join(i for i in sys.argv[1:] if not i.startswith("--")) or "..."
    asyncio.run(agent(master_instruction))

if __name__ == "__main__": main()