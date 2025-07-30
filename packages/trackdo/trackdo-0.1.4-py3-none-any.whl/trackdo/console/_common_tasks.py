from typing import LiteralString, cast

from trackdo.core._schemas import Task
from trackdo.core.task_handler import TodoHandler


def get_incomplete_tasks() -> dict[int, Task]:
    """Retrieve all incomplete tasks from the todo list."""
    todo_handler = TodoHandler()
    tasks: dict[int, Task] = todo_handler.get_tasks()
    incomplete_tasks: dict[int, Task] = {tid: task for tid, task in tasks.items() if not task.completed}
    return incomplete_tasks


def get_completed_tasks() -> dict[int, Task]:
    """Retrieve all completed tasks from the todo list."""
    todo_handler = TodoHandler()
    tasks: dict[int, Task] = todo_handler.get_tasks()
    completed_tasks: dict[int, Task] = {tid: task for tid, task in tasks.items() if task.completed}
    return completed_tasks


def get_invalid_ids(task_ids_input: str, tasks: dict[int, Task]) -> tuple[list[int], list[int]]:
    """Get a list of invalid task IDs that do not exist in the provided tasks."""
    invalid_ids: list[int] = []
    task_ids: list[int] = [int(tid.strip()) for tid in task_ids_input.split(",")]
    for task_id_str in task_ids:
        try:
            task_id: int = int(task_id_str)
            if task_id not in tasks:
                invalid_ids.append(task_id)
        except ValueError as err:
            raise ValueError(f"Invalid task ID: {task_id_str}") from err
    return task_ids, invalid_ids


def get_indent(sep: str, depth: int) -> LiteralString:
    """Get indentation string based on depth"""
    return cast("LiteralString", sep * depth)
