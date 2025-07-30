"""The TrackDo MCP server for managing todo lists and categories."""

from mcp.server.fastmcp import FastMCP

from ._schemas import Categories, TodoList
from ._tools import (
    add_categories,
    add_tasks,
    clear_completed_tasks,
    clear_tasks,
    complete_tasks,
    delete_tasks,
    get_current_tasks,
    get_tasks_by_category,
    list_categories,
)
from .task_handler import Task, TodoHandler, get_todo_handler


def get_mcp() -> FastMCP:
    """Get the FastMCP instance for the todo list server."""
    from ._mcp_server import mcp  # noqa: PLC0415

    return mcp


__all__: list[str] = [
    "Categories",
    "Task",
    "TodoHandler",
    "TodoList",
    "add_categories",
    "add_tasks",
    "clear_completed_tasks",
    "clear_tasks",
    "complete_tasks",
    "delete_tasks",
    "get_current_tasks",
    "get_mcp",
    "get_tasks_by_category",
    "get_todo_handler",
    "list_categories",
]
