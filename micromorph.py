import asyncio
import inspect
import typing as t
import textwrap
from collections import deque
from dataclasses import dataclass, field

import yaml
import microcore as mc
from microcore.ai_func import ai_func
from microcore import ui
from microcore.python import execute_inline

from tools import *

mc.configure(
    DOT_ENV_FILE=".env.anthropic",
    USE_LOGGING="print_stream",
    DEFAULT_AI_FUNCTION_SYNTAX="pythonic",
    STORAGE_PATH='.',
    EMBEDDING_DB_TYPE=mc.EmbeddingDbType.NONE,
)
mc.logging.LoggingConfig.STRIP_REQUEST_LINES = None

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
    #
    def __str__(self):
        return str(self.__call__())


    def __call__(self, **kwargs) -> str:
        return mc.prompt("""
        # [BEGIN_FEATURE: {{this.name}}]
            {%- for view in this.views %}
            {{- "\n"+textwrap.indent(str(view()), "    ") }}
            {%- endfor -%}
            {%- for tool in this.tools %}
            [BEGIN_TOOL]
            {{- "\n"+textwrap.indent(str(tool), "    ") }}
            [END_TOOL]
            {% endfor %}
        [ENDFEATURE]""", this=self,**kwargs,textwrap=textwrap, str=str, remove_indent=True)
@dataclass
class CtxMemoryStruct(Feature):
    data: dict[str, t.Any] = field(default_factory=dict)

    def __post_init__(self):
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

        self.tools = [drop, write]
        self.views = [self.view]
        for tool in self.tools:
            setattr(self, tool.__name__, tool)

    # def __call__(self, *args, **kwargs) -> str:
    #     return super().__call__(self, **kwargs)

    def view(self):
        return "DATA:\n" + yaml.dump(self.data, indent=2)

memory_struct=CtxMemoryStruct(
        name="memory_struct",
        data={
            "observations": {
                "sub-categoy-1": "Likely I should delete this"
            }
        }
    )
features = [memory_struct]

prompt = """
I am micro polymorph bot.

Criterion:
- Self-refactoring
- LoC minimization
- Obtaining capabilities, skills
- Hierarchical self-organisation
- Abstract self-representation
{% for feature in features %}
{{ feature }}
{% endfor %}
{% for tool in tools %}
[BEGIN_TOOL]
{{- "\n"+textwrap.indent(str(tool), "    ") }}
[END_TOOL]
{% endfor %}
(!) Put all calls inside <CALL>...</CALL> tag. Each call should be valid python function call.
"""

async def py_exec(content: str) -> str:
    """Execute code and return captured output."""
    summary = f"{ui.blue}{ui.bright}CALL:{ui.yellow}{ui.normal} {content}{ui.reset}\n"
    frame = inspect.currentframe().f_back
    namespace = {**frame.f_globals, **frame.f_locals}

    result, output, error = await execute_inline(content, namespace)
    if result:
        summary += f"-> {ui.gray}{repr(result).strip()}{ui.reset}\n"
    if output:
        summary += f"[PRINTED]:{ui.gray}\n{output}\n{ui.reset}\n"
    if error:
        summary += f"[ERROR]{ui.red}:\n{repr(error).strip()}\n{ui.reset}\n"
    return summary.strip() or "(silently executed with no output)"

async def agent():

    history: deque[mc.Msg] = deque(maxlen=10)
    history.append(mc.UserMsg("..."))

    def render_main() -> mc.SysMsg: return mc.prompt(prompt, **globals(), str=str).as_system

    while True:
        out = await mc.allm(
            list(history)
            + [render_main()]
        )
        blocks = mc.utils.extract_tags(out, True)
        print("\n")
        exec_out = ""
        for tag, attrs, content in blocks:
            if tag == "CALL":
                out = await py_exec(content)
                print(out)
                exec_out += out + "\n"

        exec_out = "TOOLS CALLING OUTPUT:\n" + exec_out if exec_out else "TOOLS CALLING OUTPUT: (no calls)"
        history.append(mc.UserMsg(exec_out.strip()))
        user_input = input("USER:").strip()
        if user_input:
            history.append(mc.UserMsg(user_input))


async def main():
    await agent()

if __name__ == "__main__":
    asyncio.run(main())