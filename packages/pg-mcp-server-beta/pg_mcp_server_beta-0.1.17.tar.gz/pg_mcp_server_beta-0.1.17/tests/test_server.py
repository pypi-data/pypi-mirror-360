from unittest.mock import patch

from fastmcp import FastMCP
from fastmcp.tools import FunctionTool


def test_server_creation_and_tool_registration():
    server = FastMCP("test-server")
    assert server is not None
    def test_tool() -> str:
        return "test"
    tool = FunctionTool.from_function(test_tool, name="test_tool", description="테스트")
    server.add_tool(tool)
    assert hasattr(server, "add_tool")

@patch("fastmcp.FastMCP.run")
def test_server_run_method(mock_run):
    server = FastMCP("test-server")
    server.run("stdio")
    mock_run.assert_called_once_with("stdio")

def test_main_function_importable():
    from pg_mcp_server_beta.server import main
    assert callable(main)

def test_imports_work():
    import importlib.util
    for mod in [
        "fastmcp",
        "fastmcp.tools",
        "pg_mcp_server_beta.tools.list_docs",
        "pg_mcp_server_beta.tools.get_docs",
        "pg_mcp_server_beta.tools.search_docs",
        "pg_mcp_server_beta.server",
    ]:
        assert importlib.util.find_spec(mod) is not None
