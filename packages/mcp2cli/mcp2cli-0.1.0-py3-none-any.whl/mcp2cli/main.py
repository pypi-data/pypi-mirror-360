import asyncio
import inspect
import json
import os
import typer
from rich.console import Console
from rich.table import Table
from typing import Optional, List, Dict, Any, Tuple

from mcp.types import Tool, LoggingMessageNotification, SamplingMessage
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.stdio import stdio_client, StdioServerParameters


console = Console()


class MCPCLI:
    """
    A CLI for MCP servers, dynamically generating commands from tool definitions.
    """

    def __init__(self, config_path: str = "mcp.json"):
        """
        Initializes the MCPCLI, loading server configurations and setting up the Typer app.
        """
        self.config_path = config_path
        self.servers: Dict[str, Dict[str, Any]] = {}
        self.tools: Dict[str, List[str]] = {}  # server_name -> list of tool_names
        self.tool_to_servers: Dict[str, List[str]] = {}  # tool_name -> list of server_names
        self._app = typer.Typer(rich_markup_mode="rich", add_help_option=True, pretty_exceptions_show_locals=False)
        self._app.callback(invoke_without_command=True)(self.main)

    def _show_help(self):
        """
        Displays all available tools from all servers in a table, grouped by server.
        """
        table = Table(title="[bold]Available MCP Tools[/bold]")
        table.add_column("Server", style="cyan", no_wrap=True)
        table.add_column("Tool Name", style="magenta")
        table.add_column("Description", style="green")

        for server_name, tools in sorted(self.tools.items()):
            if tools:
                server_config = self.servers.get(server_name, {})
                for i, tool_name in enumerate(sorted(tools)):
                    tool_def = next((t for t in server_config.get("tools", []) if t.name == tool_name), None)
                    description = tool_def.description if tool_def else ""
                    if i == 0:
                        table.add_row(f"[bold]{server_name}[/bold]", tool_name, description, end_section=True if len(tools) == 1 else False)
                    else:
                        table.add_row("", tool_name, description, end_section=True if i == len(tools) - 1 else False)
        
        console.print(table)

    def main(self, ctx: typer.Context):
        """
        A CLI for MCP servers.
        """
        if ctx.invoked_subcommand is None:
            self._show_help()

    async def _get_client_session(self, server_name: str):
        server_config = self.servers[server_name]
        
        if "url" in server_config:
            return streamablehttp_client(server_config["url"])
        elif "command" in server_config:
            command_parts = server_config["command"].split()
            command = command_parts[0]
            args = command_parts[1:] + server_config.get("args", [])
            env = server_config.get("env", {})
            params = StdioServerParameters(command=command, args=args, env=env)
            return stdio_client(params)
        else:
            raise ValueError(f"Unknown or invalid transport configuration for server {server_name}")

    async def _load_server_tools(self, server_name: str, server_config: Dict[str, Any]):
        session_context = None
        try:
            session_context = await self._get_client_session(server_name)
            tools = []
            if 'command' in server_config:
                async with session_context as client_streams:
                    read, write = client_streams
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        tool_list = await session.list_tools()
                        tools = tool_list.tools
            else:
                async with session_context as (read, write, _):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        tool_list = await session.list_tools()
                        tools = tool_list.tools

            self.servers[server_name]["tools"] = tools
            tool_names = [tool.name for tool in tools]
            self.tools[server_name] = tool_names
            
            for tool in tools:
                if tool.name not in self.tool_to_servers:
                    self.tool_to_servers[tool.name] = []
                self.tool_to_servers[tool.name].append(server_name)
        except Exception as e:
            console.print(f"Error connecting to server '{server_name}': {e}", style="bold red")
            import traceback
            traceback.print_exc()

    def _add_tool_commands(self):
        for tool_name, server_names in self.tool_to_servers.items():
            first_server_name = server_names[0]
            server_config = self.servers[first_server_name]
            tool_def = next((t for t in server_config.get("tools", []) if t.name == tool_name), None)
            
            if tool_def:
                command_callback = self._create_command_callback(tool_name, tool_def, len(server_names) > 1)
                self._app.command(name=tool_name, help=tool_def.description)(command_callback)

    async def _load_all_servers(self):
        if not os.path.exists(self.config_path):
            console.print(f"Error: Configuration file not found at {self.config_path}", style="bold red")
            raise typer.Exit(code=1)
            
        with open(self.config_path, "r") as f:
            config = json.load(f)

        self.servers = config.get("mcpServers", {})
        for name, conf in self.servers.items():
            try:
                await self._load_server_tools(name, conf)
            except Exception as e:
                console.print(f"Failed to load server '{name}': {e}", style="bold red")

    def _create_command_callback(self, tool_name: str, tool_def: Tool, needs_server_option: bool):
        
        def callback(
            ctx: typer.Context,
            server_name: Optional[str] = typer.Option(None, "--server-name", help="Specify the server for the command."),
            **kwargs
        ):
            async def async_main():
                chosen_server = server_name
                if not chosen_server:
                    server_options = self.tool_to_servers.get(tool_name, [])
                    if len(server_options) == 1:
                        chosen_server = server_options[0]
                    else:
                        console.print(f"Tool '{tool_name}' is available on multiple servers: {server_options}. Please specify one with --server-name.", style="bold red")
                        raise typer.Exit(code=1)

                params = {k: v for k, v in kwargs.items() if k not in ['server_name'] and v is not None}
                
                try:
                    server_config = self.servers[chosen_server]
                    session_context = await self._get_client_session(chosen_server)

                    async def process_result(session):
                        await session.initialize()
                        call_result = await session.call_tool(tool_name, params)

                        # If the result is async iterable (streaming)
                        if hasattr(call_result, "__aiter__"):
                            final_result = None
                            async for item in call_result:
                                if isinstance(item, LoggingMessageNotification):
                                    if item.params and hasattr(item.params, 'data') and isinstance(item.params.data, str):
                                        console.print(item.params.data, end="")
                                elif isinstance(item, SamplingMessage) and item.role == "assistant":
                                    if hasattr(item.content, 'text'):
                                        final_result = item.content.text

                            if final_result is not None:
                                # Try to coerce to int/float if possible
                                try:
                                    result_val = int(final_result)
                                except (ValueError, TypeError):
                                    try:
                                        result_val = float(final_result)
                                    except (ValueError, TypeError):
                                        result_val = final_result
                                console.print(json.dumps({"result": result_val}))
                        else:
                            # Non-streaming result (e.g., CallToolResult)
                            result_val = None
                            # Prefer structuredContent if available
                            if hasattr(call_result, "structuredContent") and call_result.structuredContent is not None:
                                sc = call_result.structuredContent
                                if isinstance(sc, dict) and "result" in sc:
                                    result_val = sc["result"]
                                else:
                                    result_val = sc
                            elif hasattr(call_result, "content") and call_result.content:
                                # content may be list of TextContent objects
                                first = call_result.content[0] if isinstance(call_result.content, list) else call_result.content
                                if hasattr(first, "text"):
                                    try:
                                        result_val = int(first.text)
                                    except (ValueError, TypeError):
                                        try:
                                            result_val = float(first.text)
                                        except (ValueError, TypeError):
                                            result_val = first.text
                            else:
                                # Fallback: the object itself might be JSON serialisable
                                result_val = call_result

                            console.print(json.dumps({"result": result_val}))

                    if 'command' in server_config:
                        async with session_context as client_streams:
                            read, write = client_streams
                            async with ClientSession(read, write) as session:
                                await process_result(session)
                    else:
                        async with session_context as (read, write, _):
                            async with ClientSession(read, write) as session:
                                await process_result(session)

                except Exception as e:
                    console.print(f"Error calling tool {tool_name} on server {chosen_server}: {e}", style="bold red")

            asyncio.run(async_main())

        # Dynamically create the signature for Typer
        sig_params = [
             inspect.Parameter('ctx', inspect.Parameter.POSITIONAL_OR_KEYWORD)
        ]

        if needs_server_option:
             sig_params.append(inspect.Parameter('server_name', inspect.Parameter.KEYWORD_ONLY, annotation=Optional[str], default=typer.Option(None, "--server-name", help="Specify the server for the command.")))
        else:
             sig_params.append(inspect.Parameter('server_name', inspect.Parameter.KEYWORD_ONLY, annotation=Optional[str], default=typer.Option(None, "--server-name", help="Specify the server for the command.", hidden=True)))


        for p_name, p_schema in tool_def.inputSchema.get("properties", {}).items():
            schema_type = p_schema.get("type", "string")
            if schema_type == "integer":
                param_type = int
            elif schema_type == "number":
                param_type = float
            elif schema_type == "boolean":
                param_type = bool
            else:
                param_type = str

            sig_params.append(
                inspect.Parameter(
                    p_name,
                    inspect.Parameter.KEYWORD_ONLY,
                    annotation=param_type,
                    default=typer.Option(None, f"--{p_name}", help=p_schema.get("description"))
                )
            )

        callback.__signature__ = inspect.Signature(parameters=sig_params)
        return callback

    async def _prepare_cli(self):
        await self._load_all_servers()
        self._add_tool_commands()

    def run(self):
        """
        Loads all servers and runs the Typer application.
        """
        self._app()


def run_cli():
    """Initializes and runs the MCP-CLI application."""
    cli = MCPCLI()
    try:
        asyncio.run(cli._prepare_cli())
        cli.run()
    except Exception as e:
        console.print(f"Failed to prepare CLI: {e}", style="bold red")

if __name__ == "__main__":
    run_cli()
