import os
from pathlib import Path
import tempfile
from unittest.mock import patch

import pytest

from trackdo.core.todo_server import TodoHandler, delete_tasks

GET_TODO_HANDLER = "trackdo.core.todo_server.get_todo_handler"


@pytest.fixture
def isolated_todo_handler():
    """Create a TodoHandler with isolated test database"""
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


@pytest.fixture
def temp_obsidian_file():
    """Create a temporary file path for Obsidian export testing"""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".md")
    temp_file.close()
    yield temp_file.name
    if os.path.exists(temp_file.name):
        os.unlink(temp_file.name)


class TestTaskDeletionObsidianIntegration:
    """Test Obsidian export integration with task deletion"""

    def test_delete_task_updates_obsidian_export(self, isolated_todo_handler, temp_obsidian_file):
        """Test task deletion triggers Obsidian export update"""
        with patch.dict(os.environ, {"OBSIDIAN_TODO_PATH": temp_obsidian_file}):
            isolated_todo_handler.add_task("Keep this task", category_string="life:important")
            isolated_todo_handler.add_task("Delete this task", category_string="project:test")
            content = Path(temp_obsidian_file).read_text()
            assert "- [ ] [life:important] Keep this task" in content
            assert "- [ ] [project:test] Delete this task" in content
            isolated_todo_handler.delete_task("Delete this task")
            content = Path(temp_obsidian_file).read_text()
            assert "- [ ] [life:important] Keep this task" in content
            assert "Delete this task" not in content

    @patch(GET_TODO_HANDLER)
    def test_delete_tasks_mcp_updates_obsidian(self, mock_get_handler, isolated_todo_handler, temp_obsidian_file):
        """Test delete_tasks MCP function updates Obsidian export"""
        mock_get_handler.return_value = isolated_todo_handler

        with patch.dict(os.environ, {"OBSIDIAN_TODO_PATH": temp_obsidian_file}):
            isolated_todo_handler.add_task("Task 1", category_string="project:test")
            isolated_todo_handler.add_task("Task 2", category_string="project:test")
            isolated_todo_handler.add_task("Task 3", category_string="project:test")
            result = delete_tasks(["Task 1", "Task 3"])
            assert result["success"] is True
            content = Path(temp_obsidian_file).read_text()
            assert "- [ ] [project:test] Task 2" in content
            assert "Task 1" not in content
            assert "Task 3" not in content

    def test_delete_completed_task_obsidian_update(self, isolated_todo_handler, temp_obsidian_file):
        """Test deleting completed task updates Obsidian sections properly"""
        with patch.dict(os.environ, {"OBSIDIAN_TODO_PATH": temp_obsidian_file}):
            isolated_todo_handler.add_task("Complete and delete", category_string="work:cleanup")
            isolated_todo_handler.complete_task("Complete and delete")
            content = Path(temp_obsidian_file).read_text()
            assert "## Completed Tasks" in content
            assert "- [x] [work:cleanup] Complete and delete" in content
            isolated_todo_handler.delete_task("Complete and delete")
            content = Path(temp_obsidian_file).read_text()
            assert "Complete and delete" not in content
