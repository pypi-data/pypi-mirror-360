"""MCP Tools for managing tasks in the todo list from AI agents like Claire or Claude."""

from typing import Any, Literal

from bear_utils.extras.responses.function_response import FAILURE, SUCCESS, FunctionResponse

from trackdo.core._mcp_server import mcp
from trackdo.core.task_handler import Task, TodoHandler, get_todo_handler


@mcp.tool()
def add_tasks(tasks: list[str], category: str, sub_category: str) -> dict[str, Any]:
    """Add tasks to the todo list for the specified category and subcategory.

    Args:
        tasks (list[str]): List of task descriptions to add
        category (str): Category for the tasks
        sub_category (str): Subcategory for the tasks

    Returns:
        dict: Success status, content, and error info

    Example:
        add_tasks(["Fix bug", "Write tests"], "dev", "features")
    """
    if not tasks:
        return FunctionResponse().fail(error="tasks list cannot be empty").done(to_dict=True, suppress=FAILURE)

    if not category or not sub_category:
        return (
            FunctionResponse().fail(error="category and sub_category are required").done(to_dict=True, suppress=FAILURE)
        )

    return _add_tasks(tasks=tasks, category=category, sub_category=sub_category)


@mcp.tool()
def working_tasks(tasks: list[str]) -> dict:
    """These are the working tasks for Claire (or Claude) to be used while actively in agent mode and working on tasks.

    Ideally all tasks should be be resolved before concluding the agent mode.

    Args:
        tasks (list[str]): A list of task descriptions to add

    Returns:
        dict: A dictionary containing the success status, content, and error message if any.
    """
    return add_tasks(tasks=tasks, category="claire", sub_category="working_tasks")


@mcp.tool()
def get_working_tasks() -> dict:
    """Get the current working tasks for Claire (or Claude) to be used while in Agent mode.

    Returns:
        dict: A dictionary containing the success status and content of the current working tasks.
    """
    return get_tasks_by_category(category="claire", subcategory="working_tasks")


@mcp.tool()
def clear_completed_working_tasks() -> dict:
    """Clear all completed working tasks for Claire (or Claude) to be used while in Agent mode.

    Returns:
        dict: A dictionary containing the success status and content of the operation.
    """
    todo_handler: TodoHandler = get_todo_handler()
    response = FunctionResponse(name="Deleted Working Tasks")
    tasks: dict[int, Task] = todo_handler.get_tasks_by_category(category="claire", subcategory="working_tasks")
    for task_id, task in tasks.items():
        if task.completed:
            delete_response: str = todo_handler.delete_task(task_id=task_id)
            if "not found" in delete_response:
                response.sub_task(name=f"Task_{task_id}", content=delete_response, returncode=1)
            else:
                response.sub_task(name=f"Task_{task_id}", content=delete_response)
    return response.done(to_dict=True, suppress=SUCCESS)


@mcp.tool()
def add_subtask(tasks: list[str], parent_task_id: int) -> dict:
    """Add a subtask to an existing task

    Args:
        tasks (list[str]): A list of task descriptions to add as subtasks
        parent_task_id (int): The ID of the parent task

    Returns:
        dict: A dictionary containing the success status, content, and error message if any.
    """
    todo_handler: TodoHandler = get_todo_handler()
    parent_task: Task | None = todo_handler.get_task(parent_task_id)
    if parent_task is None:
        return (
            FunctionResponse()
            .fail(error=f"Parent task ID#{parent_task_id} not found.")
            .done(to_dict=True, suppress=["name"])
        )
    responses: FunctionResponse = FunctionResponse(name="Added Subtasks")
    for task_text in tasks:
        response: str = todo_handler.add_subtask(
            text=task_text,
            category=parent_task.category,
            subcategory=parent_task.subcategory,
            parent_task_id=parent_task_id,
        )
        responses.sub_task(name=f"Subtask_{task_text}", content=response)
    return responses.done(to_dict=True, suppress=SUCCESS)


def _add_tasks(tasks: list[str], category: str, sub_category: str, parent_task_id: int | None = None) -> dict:
    """Add tasks to the todo list with optional parent task

    Args:
        tasks (list[str]): A list of task descriptions to add
        category (str): Category to add the tasks to
        sub_category (str): Subcategory to add the tasks to
        parent_task_id (int | None): Optional parent task ID to make these subtasks

    Returns:
        dict: A dictionary containing the success status, content, and error message if any.
    """
    todo_handler: TodoHandler = get_todo_handler()
    func_response = FunctionResponse(name="Added Tasks")
    for task_text in tasks:
        if parent_task_id is not None:
            response: str = todo_handler.add_subtask(task_text, category, sub_category, parent_task_id)
        else:
            response: str = todo_handler.add_task(task_text, category=category, sub_category=sub_category)
        func_response.sub_task(name=f"Task_{task_text[:10]}", content=response) if not (
            "cannot be empty" in response
            or "does not exist" in response
            or "must be in format" in response
            or "not found" in response
            or "Failed" in response
        ) else func_response.sub_task(name=f"Task_{task_text[:10]}", error=response, returncode=1)
    return func_response.done(to_dict=True, suppress=SUCCESS)


@mcp.tool()
def delete_tasks(task_ids: list[int]) -> dict:
    """Delete tasks from the todo list using their IDs

    Args:
        task_ids (list[int]): A list of task IDs to delete. Can be a single task: [1] or multiple: [1, 2, 3]

    Returns:
        dict: A dictionary containing the success status, content, and error message if any.
    """
    todo_handler: TodoHandler = get_todo_handler()
    responses: FunctionResponse = FunctionResponse(name="Deleted Tasks")
    for task_id in task_ids:
        res = FunctionResponse(name=f"Task_{task_id}")
        if task_id not in todo_handler.todo_list:
            res.fail(error=f"Task ID#{task_id} not found.")
        else:
            response: str = todo_handler.delete_task(task_id)
            res.successful(content=response) if "Deleted" in response else res.fail(error=response)
        responses.add(content=str(res))
    return responses.done(to_dict=True, suppress=SUCCESS)


@mcp.tool()
def complete_tasks(task_ids: list[int]) -> dict:
    """Mark tasks as completed using their IDs

    Args:
        task_ids (list[int]): A list of task IDs to mark as completed. Can be a single task: [1] or multiple: [1, 2, 3]

    Returns:
        dict: A dictionary containing the success status, content, and error message if any.
    """
    todo_handler: TodoHandler = get_todo_handler()
    responses: FunctionResponse = FunctionResponse(name="Completed Tasks")
    for task_id in task_ids:
        res = FunctionResponse(name=f"Task_{task_id}")
        response: str = todo_handler.complete_task(task_id)
        res.successful(content=response) if "not found" not in response else res.fail(error=response)
        responses.add(content=str(res))
    return responses.done(to_dict=True, suppress=SUCCESS)


@mcp.tool()
def edit_task(task_id: int, new_text: str) -> dict:
    """Edit an existing task's text via its ID and new text.

    Args:
        task_id (int): The ID of the task to edit
        new_text (str): The new text for the task

    Returns:
        dict: A dictionary containing the success status and content of the operation.
    """
    todo_handler: TodoHandler = get_todo_handler()
    response: str = todo_handler.edit_task(task_id=task_id, new_text=new_text)
    func_response = FunctionResponse(name="Edited Task")
    if "not found" in response or "Failed" in response:
        return func_response.fail(error=response).done(to_dict=True, suppress=FAILURE)
    return func_response.successful(content=response).done(to_dict=True, suppress=SUCCESS)


@mcp.tool()
def undo_complete_tasks(task_ids: list[int]) -> dict:
    """Mark tasks as not completed using their IDs

    Args:
        task_ids (list[int]): A list of task IDs to mark as not completed. Can be a single task: [1] or multiple: [1, 2, 3]

    Returns:
        dict: A dictionary containing the success status, content, and error message if any.
    """
    todo_handler: TodoHandler = get_todo_handler()
    responses: FunctionResponse = FunctionResponse(name="Undone Tasks")
    for task_id in task_ids:
        response: str = todo_handler.undo_complete_task(task_id)
        if "not found" in response:
            return responses.fail(error=response).done(to_dict=True, suppress=FAILURE)
        responses.add(content=response)
    return responses.done(to_dict=True, suppress=SUCCESS)


@mcp.tool()
def task_already_done(task_text: str, category: str, sub_category: str) -> dict:
    """Create and complete a task that is already done before adding it to the todo list.

    Args:
        task_text (str): The text of the task to mark as already done.
        category (str): The category of the task.
        sub_category (str): The subcategory of the task.

    Returns:
        dict: A dictionary containing the success status and content of the operation.
    """
    todo_handler: TodoHandler = get_todo_handler()
    response: str = todo_handler.add_task(task_text, category=category, sub_category=sub_category)
    func_response = FunctionResponse(name="Task Already Done")
    if "cannot be empty" in response or "does not exist" in response or "must be in format" in response:
        return func_response.fail(error=response).done(to_dict=True, suppress=FAILURE)
    if "not found" in response or "Failed" in response:
        return func_response.fail(error=response).done(to_dict=True, suppress=FAILURE)
    task_id: int = int(response.split(":")[1].split(":")[0].strip())
    complete_response: str = todo_handler.complete_task(task_id)
    if "not found" in complete_response or "Failed" in complete_response:
        return func_response.fail(error=complete_response).done(to_dict=True, suppress=FAILURE)
    return func_response.successful(content=f"Task already done: {task_id}").done(to_dict=True, suppress=SUCCESS)


@mcp.tool()
def clear_tasks(are_you_sure: bool = False) -> dict:
    """Clear all tasks from the todo list.

    THIS WILL DELETE ALL TASKS FROM THE DATABASE BY DEFAULT! BE VERY CAREFUL!

    Args:
        database_clear: If True, also clears tasks from the database. Defaults to True.

    Returns:
        dict: A dictionary containing the success status and content of the operation.
    """
    if not are_you_sure:
        return (
            FunctionResponse()
            .fail(
                error="Are you sure you want to clear all tasks from the database? Set 'are_you_sure' to True to confirm."
            )
            .done(to_dict=True, suppress=FAILURE)
        )
    todo_handler: TodoHandler = get_todo_handler()
    response: Literal["All tasks cleared."] = todo_handler.clear_tasks()
    return FunctionResponse().successful(content=response).done(to_dict=True, suppress=SUCCESS)


@mcp.tool()
def clear_completed_tasks() -> dict:
    """Clear all completed tasks from the todo list.

    Returns:
        dict: A dictionary containing the success status and content of the operation.
    """
    todo_handler: TodoHandler = get_todo_handler()
    response: Literal["All completed tasks cleared."] = todo_handler.clear_completed_tasks()
    return FunctionResponse().successful(content=response).done(to_dict=True, suppress=SUCCESS)


@mcp.tool()
def get_tasks_by_category(category: str, subcategory: str | None = None) -> dict:
    """Get tasks filtered by category and optionally subcategory

    Args:
        category (str): Category to filter by
        subcategory (str | None): Subcategory to filter by. If None, returns all tasks in category.

    Returns:
        dict: A dictionary containing the success status and filtered tasks.
    """
    todo_handler: TodoHandler = get_todo_handler()
    tasks: dict[int, Task] = todo_handler.get_tasks_by_category(category=category, subcategory=subcategory)
    response = FunctionResponse()
    if not tasks:
        if subcategory:
            return response.fail(
                error=f"No tasks found for category '{category}' and subcategory '{subcategory}'"
            ).done(to_dict=True, suppress=FAILURE)
        return response.fail(error=f"No tasks found for category '{category}'").done(to_dict=True, suppress=FAILURE)
    return response.successful(content=[str(task) for task in tasks.values()]).done(to_dict=True, suppress=SUCCESS)


@mcp.tool()
def get_current_tasks() -> dict:
    """Get the current todo list as a dictionary:

    Tasks that are not completed are: ⭕
    Completed tasks are: ✅
    Format: [category:subcategory] Task text

    Returns:
        dict: A dictionary containing the success status and content of the current tasks.
    """
    todo_handler: TodoHandler = get_todo_handler()
    tasks: list[str] = todo_handler.get_task_strings()
    response = FunctionResponse(name="Current Tasks")
    if not tasks:
        return response.fail(error="No tasks found.").done(to_dict=True, suppress=FAILURE)
    return response.successful(content=tasks).done(to_dict=True, suppress=SUCCESS)


@mcp.tool()
def list_categories() -> dict:
    """Get list of available categories

    Returns:
        dict: A dictionary containing the success status and list of available categories.
    """
    todo_handler: TodoHandler = get_todo_handler()
    categories: list[str] = todo_handler.get_categories()
    response = FunctionResponse(name="List Categories")
    if not categories:
        return response.fail(error="No categories found.").done(to_dict=True, suppress=FAILURE)
    return response.successful(content=categories).done(to_dict=True, suppress=SUCCESS)


@mcp.tool()
def add_categories(category_names: list[str]) -> dict:
    """Add a new top level category to the todo list

    Args:
        category_names (list[str]): A list of category names to add. Each name should be a single string without subcategories.

    Returns:
        dict: A dictionary containing the success status, content, and error message if any.
    """
    todo_handler: TodoHandler = get_todo_handler()
    responses: FunctionResponse = FunctionResponse(name="Added Categories")
    for category_name in category_names:
        res = FunctionResponse(name=f"Category_{category_name}")
        if not category_name.strip() or ":" in category_name:
            res.fail(error="Category name cannot be empty or contain ':' character.")
        else:
            res.successful(content=todo_handler.add_category(category_name=category_name))
        responses.add(content=str(res))
    return responses.done(to_dict=True, suppress=SUCCESS)


@mcp.tool()
def delete_categories(category_names: list[str]) -> dict:
    """Delete categories from the todo list

    Args:
        category_names (list[str]): A list of category names to delete. Each name should be a single string without subcategories.

    Returns:
        dict: A dictionary containing the success status, content, and error message if any.
    """
    todo_handler: TodoHandler = get_todo_handler()
    responses: FunctionResponse = FunctionResponse(name="Deleted Categories")
    for category_name in category_names:
        res = FunctionResponse(name=f"Category_{category_name}")
        if not category_name.strip():
            res.fail(error="Category name cannot be empty.")
        else:
            res.successful(content=todo_handler.delete_category(category_name=category_name))
        responses.add(content=str(res))
    return responses.done(to_dict=True, suppress=SUCCESS)


@mcp.tool()
def get_task_hierarchy(task_id: int) -> dict:
    """Get a task and all its subtasks in a hierarchical structure

    Args:
        task_id (int): The ID of the root task to display hierarchy for

    Returns:
        dict: A dictionary containing the hierarchical task structure
    """
    todo_handler: TodoHandler = get_todo_handler()
    response: str = todo_handler.get_task_hierarchy(task_id=task_id)
    func_response = FunctionResponse(name="Task Hierarchy")
    if "not found" in response or "Failed" in response:
        return func_response.fail(error=response).done(to_dict=True, suppress=FAILURE)
    return func_response.successful(content=response).done(to_dict=True, suppress=SUCCESS)


@mcp.tool()
def get_subtasks(parent_task_id: int) -> dict:
    """Get all direct subtasks of a parent task

    Args:
        parent_task_id (int): The ID of the parent task

    Returns:
        dict: A dictionary containing the subtasks
    """
    todo_handler: TodoHandler = get_todo_handler()
    tasks: dict[int, Task] = todo_handler.get_subtasks(parent_task_id=parent_task_id)
    response = FunctionResponse(name="Subtasks")
    if not tasks:
        return response.fail(error=f"No subtasks found for task ID {parent_task_id}").done(
            to_dict=True, suppress=FAILURE
        )
    return response.successful(content=[task.to_string(get_id=True) for task in tasks.values()]).done(
        to_dict=True, suppress=SUCCESS
    )


if __name__ == "__main__":
    tasks = get_current_tasks()
