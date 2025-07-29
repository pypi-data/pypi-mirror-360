# mcp2cli

A command-line interface (CLI) for interacting with Model Context Protocol (MCP) servers. It dynamically generates CLI commands from the tools exposed by an MCP server.

## Configuration

`mcp2cli` requires a `mcp.json` file in the current directory to define available MCP servers.

**`mcp.json` format:**

```json
{
  "mcpServers": {
    "local_server": {
      "command": "uv",
      "args": ["run", "python", "examples/server.py", "--transport", "stdio"]
    },
    "remote_server": {
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

- `command` and `args`: For servers managed by `mcp2cli` (e.g., via `stdio`).
- `url`: For remotely accessible servers (e.g., via `http`).

## Usage

**List all available tools:**
```bash
uvx mcp2cli
```

**Execute a tool:**
```bash
# Format: uvx mcp2cli <tool_name> [tool_arguments]
uvx mcp2cli sum --a 5 --b 3
```

**Get help for a tool:**
```bash
uvx mcp2cli <tool_name> --help
```

**Target a specific server** (if a tool is on multiple servers):
```bash
uvx mcp2cli <tool_name> --server-name <server_name>
```

## Example Server

The project includes an example server in `examples/server.py`.

1.  **Run the HTTP server:**
    ```bash
    uv run python examples/server.py --transport http
    ```
2.  **Configure `mcp.json`** to connect to it:
    ```json
    {
      "mcpServers": {
        "http_server": { "url": "http://127.0.0.1:8000/mcp" }
      }
    }
    ```
3.  **Use the CLI:**
    ```bash
    uvx mcp2cli sum --a 10 --b 20
    ```