# Building MCP Servers with FastMCP

> **Version**: FastMCP â‰¥ 2.x  
> **Last updated**: 2025-07-04

——

## Table of Contents

1. [Introduction](#introduction)
1. [Installation & Project Setup](#installation—project-setup)
1. [Creating Your First Server](#creating-your-first-server)
1. [Defining Tools](#defining-tools)
1. [Serving Data with Resources & Templates](#serving-data-with-resources—templates)
1. [Reusable Interaction Patterns with Prompts](#reusable-interaction-patterns-with-prompts)
1. [Using the Context Object](#using-the-context-object)
1. [Testing & Debugging](#testing—debugging)
1. [Running & Deploying Servers](#running—deploying-servers)
1. [Advanced Patterns](#advanced-patterns)
1. [Error Handling & Security](#error-handling—security)
1. [Best Practices Checklist](#best-practices-checklist)
1. [CLI Reference](#cli-reference)
1. [Further Reading](#further-reading)

——

## Introduction

FastMCP is a high-level, Pythonic framework that removes the boilerplate of the **Model Context Protocol (MCP)**. It lets you expose **Tools**, **Resources**, and **Prompts** to Large Language Models (LLMs) with nothing more than decorators and type-hints [6].

```mermaid
graph TD; A[LLM Client] —MCP—> B(FastMCP Server); B —>|Tools| C[PostgreSQL]; B —>|Resources| D[Filesystem]; B —>|Prompts| A;
```

——

## Installation & Project Setup

### 1 â€” Create a project

```bash
mkdir my-mcp-server && cd my-mcp-server
uv init  # or python -m venv .venv && source .venv/bin/activate
```

### 2 â€” Install FastMCP

```bash
uv add fastmcp          # recommended
# or
pip install fastmcp
```

Verify:

```bash
fastmcp version         # prints FastMCP, MCP & Python versions [17]
```

### 3 â€” Folder layout

```
my-mcp-server/
â”œâ”€ server.py      # main entry point
â””â”€ ...            # optional modules, data, tests
```

——

## Creating Your First Server

```python
# server.py
from fastmcp import FastMCP

mcp = FastMCP(“Demo ðŸš€”)      # name shown to clients [6]

@mcp.tool
def add(a: int, b: int) -> int:
    “””Add two numbers”””
    return a + b

if __name__ == “__main__”:
    mcp.run()                # defaults to STDIO transport
```

Run locally:

```bash
python server.py            # STDIO (Claude Desktop, Cursor, etc.)
```

Or via the CLI:

```bash
fastmcp run server.py —transport streamable-http —port 8000  # web
```

——

## Defining Tools

Tools let the LLM **perform actions** (similar to POST endpoints).

### Minimal tool

```python
@mcp.tool
def greet(name: str) -> str:
    “””Return a friendly greeting”””
    return f”Hello, {name}!”  # auto-validated & schema-generated [39]
```

### Async tool with Pydantic model & progress

```python
from pydantic import BaseModel, Field
from fastmcp import Context

class Email(BaseModel):
    to: str = Field(pattern=r”^[^@]+@[^@]+\.[^@]+$”)
    subject: str
    body: str

@mcp.tool(tags={“email”})
async def send_email(msg: Email, ctx: Context) -> dict:
    await ctx.info(f”Sending email to {msg.to}”)
    # ... actual send ...
    await ctx.report_progress(1, 1)
    return {“status”: “sent”, “to”: msg.to}
```

Key points [5][39]:

- Decorator infers **name**, **description**, **schema**.
- Type-hints â†’ JSON schema for validation.
- `async def` prevents blocking I/O.
- `ctx` unlocks logging, resources, sampling, progress.

——

## Serving Data with Resources & Templates

Resources are **read-only** data (think GET).

### Static text resource

```python
@mcp.resource(“config://motd”)
def motd() -> str:
    return “Welcome to FastMCP!”
```

### Dynamic JSON resource

```python
@mcp.resource(“weather://{city}/current”, mime_type=“application/json”)
async def current_weather(city: str) -> dict:
    data = await fetch_city_weather(city)
    return data
```

The placeholder `{city}` creates a **resource template** that clients call as `weather://london/current` [21].

### File resource using built-ins

```python
from pathlib import Path
from fastmcp.resources import FileResource

mcp.add_resource(
    FileResource(uri=“file://readme”, path=Path(“README.md”), mime_type=“text/markdown”)
)
```

——

## Reusable Interaction Patterns with Prompts

Prompts are **parameterised message templates** reusable by clients.

```python
from fastmcp.prompts.prompt import Message

@mcp.prompt
def ask_explain(topic: str) -> Message:
    return Message(f”Explain the concept of {topic} in simple terms.”)
```

Prompts accept typed arguments (auto-converted from strings) and may be **async** if they fetch data [Prompts docs].

——

## Using the Context Object

Add `ctx: Context` to any tool/resource/prompt to access:

- `ctx.debug/info/warning/error()` â€” structured logging.
- `ctx.report_progress(cur, total)` â€” progress bars.
- `await ctx.read_resource(uri)` â€” consume other resources.
- `await ctx.sample(messagesâ€¦)` â€” **LLM sampling** (ask the client LLM to help) [29][33].

Example: summarise a file with help from the client LLM [33].

```python
@mcp.tool()
async def summarise(uri: str, ctx: Context) -> str:
    text = (await ctx.read_resource(uri))[0].content
    resp = await ctx.sample(f”Summarise in 3 bullets:\n{text[:500]}”)
    return resp.text
```

——

## Testing & Debugging

### In-memory tests (fastest) [27]

```python
import pytest
from fastmcp import FastMCP, Client

@pytest.fixture
def server():
    s = FastMCP(“Test”)
    @s.tool
    def echo(x: int) -> int: return x
    return s

@pytest.mark.asyncio
async def test_echo(server):
    async with Client(server) as c:
        res = await c.call_tool(“echo”, {“x”: 5})
        assert res.data == 5
```

### Inspect live traffic

```bash
fastmcp dev server.py        # opens MCP Inspector GUI
```

——

## Running & Deploying Servers

|Transport          |Use case                          |Command                                                        |
|-——————|-———————————|—————————————————————|
|**STDIO** (default)|Local IDE plugins, CLI tools      |`python server.py`                                             |
|**streamable-http**|Web / micro-services (recommended)|`fastmcp run server.py —transport streamable-http —port 8000`|
|**SSE**            |Legacy web clients                |`fastmcp run server.py —transport sse`                        |

FastMCP CLI ignores `if __main__` and looks for a variable called `mcp`, `server`, or `app` [31].

**Health check & ping** options are configurable when using HTTP transports [28].

——

## Advanced Patterns

### Composition

```python
parent = FastMCP(“Composite”)
parent.mount(“weather”, weather_mcp)   # prefixes tool names
parent.mount(“news”, news_mcp)
```

### Proxying another server

```python
from fastmcp import Client, FastMCP
from fastmcp.client.transports import PythonStdioTransport

backend = Client(PythonStdioTransport(“other_server.py”))
proxy   = await FastMCP.as_proxy(backend, name=“stdioâ†’http proxy”)
proxy.run(transport=“streamable-http”, port=9001)
```

### Auto-generate from OpenAPI

```python
from fastmcp.codegen import generate_from_openapi
mcp = await generate_from_openapi(“openapi.yaml”)
```

——

## Error Handling & Security

- Raise standard exceptions **or** `ToolError` / `ResourceError` to return structured MCP errors [39][42].
- Set `mask_error_details=True` on `FastMCP(...)` to hide traceback details [39].
- Use decorator flag `enabled=False` to temporarily disable operations.
- Configure `authenticate=` callback or OAuth settings (HTTP flavour) for request auth [32].

——

## Best Practices Checklist

- [ ] Pin `fastmcp` version in `pyproject.toml` for reproducible builds [17].
- [ ] Keep transport STDIO for local, HTTP for production.
- [ ] Prefer **async** for network / disk I/O.
- [ ] Validate inputs with Pydantic or `Annotated[...]`.
- [ ] Add unit tests with in-memory `Client`.
- [ ] Use `ctx.sample()` sparinglyâ€”respect client token budgets.
- [ ] Document every tool/resource with clear docstrings.
- [ ] Enable health-checks for container orchestration.

——

## CLI Reference

|Command                      |Description                            |
|——————————|—————————————|
|`fastmcp version`            |Show FastMCP, MCP & Python versions    |
|`fastmcp run <file.py> [...]`|Run server overriding code transport   |
|`fastmcp dev <file.py>`      |Launch with Inspector & auto-reload    |
|`fastmcp inspect <url>`      |Open Inspector UI against remote server|

——

## Further Reading

1. Welcome to FastMCP 2.0 [6]
1. Quick-start guide [7]
1. PyPI package docs [5]
1. Tools deep-dive [39]
1. Resources & Templates docs [21]
1. Prompts docs [Prompts page]
1. Context object reference [29]
1. Testing pattern [27]
1. Deployment transports [31]
1. Composing & proxying [30]
1. LLM sampling [33]
1. Installation page [17]

——

*Â© 2025 FastMCP community.  Licensed under the Apache 2.0 License.*