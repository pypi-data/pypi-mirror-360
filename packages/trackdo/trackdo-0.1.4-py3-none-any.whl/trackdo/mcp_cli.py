"""The TrackDo MCP CLI launch script."""

from pathlib import Path

from dotenv import load_dotenv
from mcp.server.fastmcp.server import FastMCP

from trackdo.core.todo_server import get_mcp

load_dotenv(str(Path(__file__).parent.parent.parent / ".env"))
mcp: FastMCP = get_mcp()
