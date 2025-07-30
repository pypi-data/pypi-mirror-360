import os
import tempfile
from unittest.mock import patch

from bear_epoch_time import EpochTimestamp
import pytest

from trackdo.core.todo_server import (
    Categories,
    Task,
    TodoHandler,
    TodoList,
    add_categories,
    add_tasks,
    complete_tasks,
    delete_tasks,
    get_tasks_by_category,
    list_categories,
)

GET_TODO_HANDLER = "trackdo.core.todo_server.get_todo_handler"


@pytest.fixture
def isolated_todo_handler():
    """Create a TodoHandler with isolated test database."""
    if TodoHandler.has_instance():
        TodoHandler.reset_instance()

    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
    temp_db.close()
    with patch("trackdo.core.task_handler.getenv") as mock_getenv:

        def getenv_side_effect(key, default=None) -> str | None:
            if key == "DATABASE_PATH":
                return os.path.dirname(temp_db.name)
            if key == "DATABASE_FILENAME":
                return os.path.basename(temp_db.name)
            return default

        mock_getenv.side_effect = getenv_side_effect
        handler = TodoHandler()
    handler.db.get_base().metadata.create_all(handler.db.engine)
    handler.todo_list.clear()
    yield handler
    os.unlink(temp_db.name)
    if TodoHandler.has_instance():
        TodoHandler.reset_instance()


def test_task_with_category():
    """Test Task dataclass with category parameter"""
    task = Task(
        task_id=1,
        text="Fix bug",
        category="project",
        subcategory="mcp",
        created_at=EpochTimestamp.now(),
    )
    assert task.text == "Fix bug"
    assert task.category == "project"
    assert task.subcategory == "mcp"
    assert not task.completed
    assert "[project:mcp] Fix bug" in str(task)


def test_add_task_with_category(isolated_todo_handler):
    """Test adding task with category:subcategory format"""
    result = isolated_todo_handler.add_task("Fix whitespace", category_string="project:mcp")
    assert "Task added" in result
    assert "[project:mcp] Fix whitespace" in result
    assert "Fix whitespace" in isolated_todo_handler.todo_list
    task = isolated_todo_handler.todo_list["Fix whitespace"]
    assert task.category == "project"
    assert task.subcategory == "mcp"


def test_add_task_invalid_category_format(isolated_todo_handler):
    """Test adding task with invalid category format"""
    result = isolated_todo_handler.add_task("Invalid task", category_string="invalid")
    assert "must be in format 'category:subcategory'" in result


def test_add_task_nonexistent_category(isolated_todo_handler):
    """Test adding task with nonexistent category"""
    result = isolated_todo_handler.add_task("Invalid category task", category_string="invalid:subcategory")
    assert "does not exist" in result
    assert "Available categories:" in result


def test_get_tasks_by_category(isolated_todo_handler):
    """Test filtering tasks by category"""
    isolated_todo_handler.add_task("MCP task 1", category_string="project:mcp")
    isolated_todo_handler.add_task("MCP task 2", category_string="project:mcp")
    isolated_todo_handler.add_task("Work task", category_string="work:development")
    isolated_todo_handler.add_task("Life task", category_string="life:health")

    # Test filtering by category only
    project_tasks = isolated_todo_handler.get_tasks_by_category("project")
    assert len(project_tasks) == 2
    assert "MCP task 1" in project_tasks
    assert "MCP task 2" in project_tasks

    # Test filtering by category and subcategory
    mcp_tasks = isolated_todo_handler.get_tasks_by_category("project", "mcp")
    assert len(mcp_tasks) == 2
    assert "MCP task 1" in mcp_tasks
    assert "MCP task 2" in mcp_tasks

    # Test filtering by different category
    work_tasks = isolated_todo_handler.get_tasks_by_category("work")
    assert len(work_tasks) == 1
    assert "Work task" in work_tasks


def test_get_tasks_by_category_string(isolated_todo_handler):
    """Test filtering tasks by category string"""
    isolated_todo_handler.add_task("Test task", category_string="project:mcp")

    tasks = isolated_todo_handler.get_tasks_by_category_string("project:mcp")
    assert len(tasks) == 1
    assert "Test task" in tasks

    # Test invalid format
    empty_tasks = isolated_todo_handler.get_tasks_by_category_string("invalid")
    assert len(empty_tasks) == 0


def test_default_categories_initialization(isolated_todo_handler):
    """Test that default categories are initialized"""
    categories = isolated_todo_handler.get_categories()
    assert "project" in categories
    assert "life" in categories
    assert "work" in categories


def test_add_category(isolated_todo_handler):
    """Test adding a new category"""
    result = isolated_todo_handler.add_category("personal")
    assert "added successfully" in result

    categories = isolated_todo_handler.get_categories()
    assert "personal" in categories


def test_add_duplicate_category(isolated_todo_handler):
    """Test adding a duplicate category"""
    isolated_todo_handler.add_category("personal")
    result = isolated_todo_handler.add_category("personal")
    assert "already exists" in result


@patch(GET_TODO_HANDLER)
def test_add_tasks_mcp_tool(mock_get_handler, isolated_todo_handler):
    """Test the MCP tool function for adding tasks with categories"""
    mock_get_handler.return_value = isolated_todo_handler
    result = add_tasks(["Unique test task 1", "Unique test task 2"], category="project:unittest")
    assert result["success"] is True
    assert "[project:unittest] Unique test task 1" in result["content"]
    assert "[project:unittest] Unique test task 2" in result["content"]


@patch(GET_TODO_HANDLER)
def test_add_tasks_mcp_tool_invalid_format(mock_get_handler, isolated_todo_handler):
    """Test the MCP tool function with invalid category format"""
    mock_get_handler.return_value = isolated_todo_handler
    result = add_tasks(["Invalid task"], category="invalid")
    assert result["success"] is False
    assert "must be in format" in result["error"]


@patch(GET_TODO_HANDLER)
def test_get_tasks_by_category_mcp_tool(mock_get_handler, isolated_todo_handler):
    """Test the MCP tool function for filtering by category"""
    mock_get_handler.return_value = isolated_todo_handler
    add_tasks(["Unique filter test task"], category="project:filtertest")
    add_tasks(["Unique work filter task"], category="work:development")

    result = get_tasks_by_category("project:filtertest")
    assert result["success"] is True
    assert "[project:filtertest] Unique filter test task" in result["content"]

    result = get_tasks_by_category("nonexistent:category")
    assert result["success"] is False
    assert "No tasks found for category" in result["error"]


@patch(GET_TODO_HANDLER)
def test_list_categories_mcp_tool(mock_get_handler, isolated_todo_handler):
    """Test the MCP tool function for listing categories"""
    mock_get_handler.return_value = isolated_todo_handler
    result = list_categories()
    assert result["success"] is True
    assert "project" in result["content"]
    assert "work" in result["content"]
    assert "life" in result["content"]


@patch(GET_TODO_HANDLER)
def test_add_category_mcp_tool(mock_get_handler, isolated_todo_handler):
    """Test the MCP tool function for adding categories"""
    mock_get_handler.return_value = isolated_todo_handler
    result = add_categories(["personal"])
    assert result["success"] is True
    assert "added successfully" in result["content"]
    result = add_categories(["personal"])
    assert result["success"] is False
    assert "already exists" in result["error"]


@patch(GET_TODO_HANDLER)
def test_complete_tasks_with_categories(mock_get_handler, isolated_todo_handler):
    """Test completing tasks that have category tags"""
    mock_get_handler.return_value = isolated_todo_handler

    add_tasks(["Unique completable task"], category="project:completetest")
    result = complete_tasks(["Unique completable task"])
    assert result["success"] is True
    assert "Task completed" in result["content"]


def test_todo_list_model_with_category():
    """Test the SQLAlchemy model with category fields"""
    todo_entry = TodoList(task_text="Model test", completed=False, category="project", subcategory="test")
    assert str(todo_entry.task_text) == "Model test"
    assert str(todo_entry.category) == "project"
    assert str(todo_entry.subcategory) == "test"
    assert not bool(todo_entry.completed)
    assert "[project:test] Model test" in str(todo_entry)


def test_categories_model():
    """Test the Categories SQLAlchemy model"""
    category = Categories(name="test")
    assert str(category.name) == "test"
    assert "Category: test" in str(category)


def test_empty_task_text(isolated_todo_handler):
    """Test handling empty task text"""
    result = isolated_todo_handler.add_task("", category_string="project:test")
    assert "cannot be empty" in result


def test_special_characters_in_category(isolated_todo_handler):
    """Test category names with special characters"""
    isolated_todo_handler.add_category("test-123_special")
    result = isolated_todo_handler.add_task("Special char test", category_string="test-123_special:subcategory")
    assert "Task added" in result
    assert "[test-123_special:subcategory]" in result


class TestTaskDeletion:
    """Test task deletion functionality"""

    def test_delete_single_task(self, isolated_todo_handler):
        """Test deleting a single task"""
        isolated_todo_handler.add_task("Task to delete", category_string="project:test")
        result = isolated_todo_handler.delete_task("Task to delete")

        assert "Task deleted" in result
        assert "Task to delete" not in isolated_todo_handler.todo_list

    def test_delete_nonexistent_task(self, isolated_todo_handler):
        """Test deleting a task that doesn't exist"""
        result = isolated_todo_handler.delete_task("Nonexistent task")
        assert "not found" in result

    def test_delete_task_removes_from_database(self, isolated_todo_handler):
        """Test that deletion removes task from database"""
        isolated_todo_handler.add_task("DB delete test", category_string="project:test")
        session = isolated_todo_handler.db.session()
        db_task = session.query(TodoList).filter_by(task_text="DB delete test").first()
        assert db_task is not None
        isolated_todo_handler.delete_task("DB delete test")
        db_task = session.query(TodoList).filter_by(task_text="DB delete test").first()
        assert db_task is None

    def test_delete_completed_task(self, isolated_todo_handler):
        """Test deleting a completed task"""
        isolated_todo_handler.add_task("Complete then delete", category_string="project:test")
        isolated_todo_handler.complete_task("Complete then delete")

        result = isolated_todo_handler.delete_task("Complete then delete")
        assert "Task deleted" in result
        assert "Complete then delete" not in isolated_todo_handler.todo_list

    def test_delete_task_with_category(self, isolated_todo_handler):
        """Test deleting a task with category tag"""
        isolated_todo_handler.add_task("Category task delete", category_string="project:testproj")
        result = isolated_todo_handler.delete_task("Category task delete")

        assert "Task deleted" in result
        assert "[project:testproj]" in result
        assert "Category task delete" not in isolated_todo_handler.todo_list


@patch(GET_TODO_HANDLER)
def test_delete_tasks_mcp_tool_single(mock_get_handler, isolated_todo_handler):
    """Test the MCP tool function for deleting a single task"""
    mock_get_handler.return_value = isolated_todo_handler

    add_tasks(["Delete me please"], category="project:test")
    result = delete_tasks(["Delete me please"])

    assert result["success"] is True
    assert "Task deleted" in result["content"]
    assert "Delete me please" not in isolated_todo_handler.todo_list


@patch(GET_TODO_HANDLER)
def test_delete_tasks_mcp_tool_multiple(mock_get_handler, isolated_todo_handler):
    """Test the MCP tool function for deleting multiple tasks"""
    mock_get_handler.return_value = isolated_todo_handler

    add_tasks(["Delete task 1", "Delete task 2", "Keep this task"], category="project:test")
    result = delete_tasks(["Delete task 1", "Delete task 2"])

    assert result["success"] is True
    assert "Delete task 1" in result["content"]
    assert "Delete task 2" in result["content"]
    assert "Delete task 1" not in isolated_todo_handler.todo_list
    assert "Delete task 2" not in isolated_todo_handler.todo_list
    assert "Keep this task" in isolated_todo_handler.todo_list


@patch(GET_TODO_HANDLER)
def test_delete_tasks_mcp_tool_not_found(mock_get_handler, isolated_todo_handler):
    """Test the MCP tool function with nonexistent task"""
    mock_get_handler.return_value = isolated_todo_handler
    result = delete_tasks(["This task does not exist"])
    assert result["success"] is False
    assert "not found" in result["error"]


@patch(GET_TODO_HANDLER)
def test_delete_tasks_mixed_results(mock_get_handler, isolated_todo_handler):
    """Test deleting mix of existing and nonexistent tasks"""
    mock_get_handler.return_value = isolated_todo_handler
    add_tasks(["Exists"], category="project:test")
    result = delete_tasks(["Exists", "Does not exist"])
    assert result["success"] is False
    assert "not found" in result["error"]
    assert "Exists" in isolated_todo_handler.todo_list
