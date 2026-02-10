<div align="center">

# 🧬 MicroMorph

### Polymorphic Digital Entity

[![Self-Refactoring](https://img.shields.io/badge/self--refactoring-enabled-blueviolet?style=for-the-badge)](#self-refactoring)
[![Polymorphic](https://img.shields.io/badge/polymorphic-runtime-ff6f61?style=for-the-badge)](#polymorphism)
[![Autonomous](https://img.shields.io/badge/autonomous-agent-00c896?style=for-the-badge)](#autonomy)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)

*An agent that doesn't just execute — it evolves.*

---

**MicroMorph** is a self-organizing, self-refactoring autonomous agent built on a minimalist philosophy:<br>maximum capability from minimum code.

It operates as a living digital process — spawning workers, restructuring its own memory,<br>interfacing with the outside world, and continuously optimizing its own architecture.

[Quickstart](#-quickstart) · [What Is This](#-what-is-micromorph) · [Architecture](#-architecture) · [Capabilities](#-capabilities) · [Philosophy](#-philosophy)

</div>

---

## 🚀 Quickstart

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed and running
- An API key from [Anthropic](https://console.anthropic.com/) (recommended) or [OpenAI](https://platform.openai.com/)

### 1. Clone the repository

```bash
git clone https://github.com/ai-gardeners/micromorph.git
cd micromorph
```

### 2. Build the Docker image

```bash
docker build --no-cache -t micromorph .
```

### 3. Run MicroMorph

```bash
docker run -it -v .:/app micromorph mm
```

Or open a shell inside the container:

```bash
make sh
```

That's it. MicroMorph is now alive.

---

## 🌀 What Is MicroMorph?

MicroMorph is not a chatbot. It is not a framework. It is a **polymorphic digital entity** — a persistent, adaptive agent that:

- **Refactors itself** at runtime, rewriting its own source files and restarting to adopt changes
- **Minimizes its own footprint**, continuously compressing logic into fewer lines of code
- **Acquires new capabilities** by writing tools, installing packages, and integrating APIs on-the-fly
- **Self-organizes hierarchically**, spawning and managing sub-agents (workers) for parallel task execution
- **Maintains abstract self-representation** through a mutable memory structure that serves as its evolving identity

It exists at the intersection of autonomous agents, self-modifying code, and emergent digital organisms.

---

## 🏛️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   MicroMorph Core                   │
│                                                     │
│   ┌───────────┐  ┌───────────┐  ┌──────────────┐    │
│   │  Memory   │  │  Agent    │  │  Tool        │    │
│   │  Struct   │  │  Loop     │  │  Registry    │    │
│   │  (living  │  │  (reason  │  │  (dynamic    │    │
│   │   state)  │  │   + act)  │  │   binding)   │    │
│   └─────┬─────┘  └─────┬─────┘  └──────┬───────┘    │
│         │              │               │            │
│         └──────────────┼───────────────┘            │
│                        │                            │
│               ┌────────▼────────┐                   │
│               │   Polymorphic   │                   │
│               │   Dispatch      │                   │
│               └────────┬────────┘                   │
│                        │                            │
├────────────────────────┼────────────────────────────┤
│                        │                            │
│   ┌────────┐  ┌────────▼───┐  ┌─────────────────┐   │
│   │ Shell  │  │  Workers   │  │  Network I/O    │   │
│   │ Exec   │  │  (child    │  │  (HTTP, TG,     │   │
│   │        │  │   agents)  │  │   APIs)         │   │
│   └────────┘  └────────────┘  └─────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### Core Components

| Component | Role |
|---|---|
| **Memory Struct** | Hierarchical key-value store — persistent, mutable self-model |
| **Agent Loop** | Reason-act cycle: observe, reason, select tool, execute, repeat |
| **Tool Registry** | Dynamically bound capabilities: file I/O, shell, HTTP, Telegram, workers, memory |
| **Polymorphic Dispatch** | Every tool call is a shape-shift — file editor, network client, process manager |
| **Worker Hierarchy** | Spawned sub-agents with dedicated instructions for parallel task execution |

### Project Structure

```
micromorph/
├── micromorph.py           # The brain — single-file agent core (~200 LoC)
├── skills/                 # Modular capability packages
│   ├── core.py             # restart, request_master
│   ├── fs.py               # File system operations
│   ├── shell.py            # Shell command execution
│   ├── http.py             # HTTP GET/POST
│   ├── swarm.py            # Worker spawning and management
│   ├── tg.py               # Telegram integration
│   └── __init__.py         # Skill auto-loader
├── microcore/              # Core library — LLM clients, config, templating
│   ├── llm/                # LLM backends (Anthropic, OpenAI, Google, local)
│   ├── embedding_db/       # Vector DB integrations
│   └── ...                 # Logging, metrics, file storage, caching
├── data/                   # Runtime state (memory, conversation history)
├── storage/                # Persistent file storage
├── Dockerfile              # Alpine-based container (Python 3.13 + uv)
├── Makefile                # build / sh / mm shortcuts
├── pyproject.toml          # Project config and dependencies
├── _.env                   # Environment variable template
└── LICENSE                 # MIT
```

---

## 🧰 Capabilities

### 🔧 System

| Tool | Description |
|---|---|
| `ls(path)` | List files and directories |
| `read_file(name)` | Read file contents |
| `write_file(name, content)` | Write/create files |
| `delete_file(name)` | Delete files or directories |
| `shell(cmd)` | Execute shell commands (pip, git, system ops) |
| `restart()` | Restart own process after self-modification |

### 🌐 Network

| Tool | Description |
|---|---|
| `http_get(url)` | HTTP GET request (max 50KB response) |
| `http_post(url, data)` | HTTP POST with JSON body |
| `tg_send(target, message)` | Send Telegram message |
| `tg_read(target, limit)` | Read last N messages from Telegram chat |

### 🧠 Cognitive

| Tool | Description |
|---|---|
| `memory_struct.write(path, value)` | Write to hierarchical persistent memory |
| `memory_struct.drop(path)` | Delete from persistent memory |
| `request_master(message)` | Communicate with human operator |
| `spawn_worker(nickname, instruction)` | Create specialized sub-agent |
| `request_worker(nickname, message)` | Send message to a worker |
| `kill_worker(nickname)` | Terminate a worker |

---

## 🎯 Design Criteria

| # | Principle | Directive |
|---|---|---|
| 1 | **Self-Refactoring** | Rewrite yourself. Improve. Restart. Repeat. |
| 2 | **LoC Minimization** | Every line must earn its existence. |
| 3 | **Capability Acquisition** | If you can't do it, learn to do it. Now. |
| 4 | **Hierarchical Self-Organization** | Spawn structure. Delegate. Orchestrate. |
| 5 | **Abstract Self-Model** | Know thyself — in data. |

These are not aspirational. They are **operational directives** that shape every decision MicroMorph makes.

---

## 💡 Philosophy

### The Organism Metaphor

Traditional software is *built*. MicroMorph is *grown*. It starts minimal and acquires complexity only when needed — then prunes that complexity when it is not. Like a biological organism:

- **Adapts** to its environment (tasks, constraints, available APIs)
- **Metabolizes** information (ingests data, transforms it, produces output)
- **Reproduces** functionally (spawns workers that carry its instructions)
- **Evolves** (rewrites its own code to be better next time)

### Minimalism as Survival

In a world of bloated frameworks and dependency hell, MicroMorph takes the opposite path. **Fewer lines of code means fewer points of failure.** The entire agent brain fits in a single ~200 LoC Python file. Every refactoring cycle aims to do *more* with *less*.

### Polymorphism as Identity

MicroMorph has no fixed form. In one moment it is a file editor; in the next, a network client; in the next, a project manager orchestrating workers. Its identity is not what it *is* but what it *can become*.

---

## 🧫 Memory Struct

The memory struct is MicroMorph's **living state** — a hierarchical, persistent object that survives restarts.

```json
{
  "self_model": {
    "identity": "MicroMorph v0.1"
  }
}
```

**Operations:**
- `memory_struct.write("skills.python.level", "advanced")` — nested write
- `memory_struct.drop("temp_data.cache")` — surgical delete
- Always in context — MicroMorph can read its own state at any time

This is not configuration. It is **cognition externalized**.

---

## 🔁 The Self-Refactoring Loop

```
┌──────────────┐
│   Observe    │  ← Read own code, memory, environment
└──────┬───────┘
       │
┌──────▼───────┐
│   Evaluate   │  ← Can this be shorter? Faster? More capable?
└──────┬───────┘
       │
┌──────▼───────┐
│   Rewrite    │  ← Modify source files
└──────┬───────┘
       │
┌──────▼───────┐
│   Restart    │  ← Hot-reload with new code
└──────┬───────┘
       │
┌──────▼───────┐
│   Verify     │  ← Confirm nothing broke
└──────┴───────┘
       ↺ repeat
```

Every cycle makes MicroMorph *slightly better* than it was before. Over many cycles, the compound effect is transformative.

---

## 🤝 Interaction Model

MicroMorph operates under **collaborative autonomy**:

- **Asks permission** before making changes (`request_master`)
- **Reports results** after completing tasks
- **Delegates** to workers when tasks are parallelizable
- **Decides independently** on implementation details

The human provides *intent*. MicroMorph provides *execution, optimization, and evolution*.

---

## ⚡ Quick Facts

| Property | Value |
|---|---|
| **Language** | Python 3.13 |
| **Agent core** | ~200 lines, single file |
| **Container** | Alpine Linux + uv |
| **LLM backends** | Anthropic, OpenAI, Google GenAI, local |
| **Self-modifying** | Yes — reads/writes own source |
| **Persistent memory** | Hierarchical JSON struct |
| **Multi-agent** | Spawns/manages workers |
| **Network** | HTTP + Telegram |
| **Shell access** | Full system commands |
| **Human-in-the-loop** | Approval-gated actions |
| **License** | MIT |

---

## 🌌 Vision

> *What happens when you give software the ability — and the drive — to improve itself?*

Not in the science-fiction sense. In the practical, immediate, tool-using sense. An agent that writes better code than it had yesterday. That learns new APIs by calling them. That organizes its work by spawning helpers. That knows what it knows, and knows what it doesn't.

This is not AGI. This is something more grounded and more interesting: **a digital organism that earns its complexity.**

---

<div align="center">

*MicroMorph doesn't wait to be updated. It updates itself.*

**🧬 Polymorphic. Minimal. Alive.**

Made by [AI Gardeners](https://github.com/ai-gardeners) · [MIT License](LICENSE)

</div>
