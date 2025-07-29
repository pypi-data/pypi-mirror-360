import asyncio
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

import pytest
from typer.testing import CliRunner

from mcp2cli.main import MCPCLI

runner = CliRunner()


@pytest.fixture(scope="module")
def http_server():
    """Fixture to start and stop the example HTTP server."""
    process = subprocess.Popen(
        [
            "uv",
            "run",
            "python",
            "examples/server.py",
            "--transport",
            "http",
            "--port",
            "8001",
        ]
    )
    # Give the server a moment to start
    time.sleep(2)
    yield
    process.terminate()
    process.wait()


def run_cli_for_test(config_path: str, args: list[str]):
    """Helper function to run the CLI for testing purposes."""
    cli = MCPCLI(config_path=config_path)
    asyncio.run(cli._prepare_cli())
    return runner.invoke(cli._app, args)


def test_stdio_transport(tmp_path: Path):
    """Test the CLI with stdio transport."""
    config_path = tmp_path / "mcp.json"
    shutil.copy("tests/mcp_stdio.json", config_path)

    # Test listing tools
    result = run_cli_for_test(str(config_path), [])
    assert result.exit_code == 0
    assert "stdio_server" in result.stdout
    assert "sum" in result.stdout
    assert "get_weather" in result.stdout

    # Test executing a tool
    result = run_cli_for_test(str(config_path), ["sum", "--a", "5", "--b", "10"])
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"result": 15}


def test_http_transport(http_server, tmp_path: Path):
    """Test the CLI with HTTP transport."""
    config_path = tmp_path / "mcp.json"
    shutil.copy("tests/mcp_http.json", config_path)

    # Test listing tools
    result = run_cli_for_test(str(config_path), [])
    assert result.exit_code == 0
    assert "http_server" in result.stdout
    assert "sum" in result.stdout
    assert "get_weather" in result.stdout

    # Test executing a tool
    result = run_cli_for_test(str(config_path), ["sum", "--a", "7", "--b", "8"])
    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"result": 15} 