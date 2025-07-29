import typer
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="Example Server")
app = typer.Typer()

@mcp.tool()
def sum(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b


@mcp.tool()
def get_weather(city: str, unit: str = "celsius") -> str:
    """Get weather for a city."""
    # This would normally call a weather API
    return f"Weather in {city}: 22degrees{unit[0].upper()}"


@app.command()
def main(
    transport: str = typer.Option("stdio", "--transport", "-t", help="The transport to use (stdio or http)."),
    port: int = typer.Option(8000, "--port", "-p", help="The port to use for HTTP transport.")
):
    """
    Run the example MCP server.
    """
    if transport == "http":
        mcp.settings.port = port
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    app() 