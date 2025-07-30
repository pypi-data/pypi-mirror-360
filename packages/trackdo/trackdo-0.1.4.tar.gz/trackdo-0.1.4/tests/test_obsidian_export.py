import os
from pathlib import Path
import tempfile
from unittest.mock import patch

import pytest

from trackdo.core.todo_server import TodoHandler, add_tasks, clear_tasks, complete_tasks


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


class TestObsidianMarkdownConversion:
    """Test markdown checkbox conversion accuracy"""

    def test_incomplete_task_conversion(self, isolated_todo_handler, temp_obsidian_file):
        """Test ⭕ converts to - [ ] in markdown"""
        with patch.dict(os.environ, {"OBSIDIAN_TODO_PATH": temp_obsidian_file}):
            isolated_todo_handler.add_task("Incomplete task", category_string="project:test")

            content = Path(temp_obsidian_file).read_text()
            assert "- [ ] [project:test] Incomplete task" in content
            assert "⭕" not in content

    def test_completed_task_conversion(self, isolated_todo_handler, temp_obsidian_file):
        """Test ✅ converts to - [x] in markdown"""
        with patch.dict(os.environ, {"OBSIDIAN_TODO_PATH": temp_obsidian_file}):
            isolated_todo_handler.add_task("Complete me", category_string="project:test")
            isolated_todo_handler.complete_task("Complete me")

            content = Path(temp_obsidian_file).read_text()
            assert "- [x] [project:test] Complete me" in content
            assert "✅" not in content

    def test_project_tag_preservation(self, isolated_todo_handler, temp_obsidian_file):
        """Test category tags are preserved in markdown export"""
        with patch.dict(os.environ, {"OBSIDIAN_TODO_PATH": temp_obsidian_file}):
            isolated_todo_handler.add_task("Tagged task", category_string="project:test")

            content = Path(temp_obsidian_file).read_text()
            assert "- [ ] [project:test] Tagged task" in content

    def test_mixed_tasks_conversion(self, isolated_todo_handler, temp_obsidian_file):
        """Test conversion of mixed incomplete and completed tasks"""
        with patch.dict(os.environ, {"OBSIDIAN_TODO_PATH": temp_obsidian_file}):
            isolated_todo_handler.add_task("Task 1", category_string="project:test")
            isolated_todo_handler.add_task("Task 2", category_string="life:personal")
            isolated_todo_handler.complete_task("Task 1")

            content = Path(temp_obsidian_file).read_text()
            assert "- [x] [project:test] Task 1" in content
            assert "- [ ] [life:personal] Task 2" in content


class TestObsidianFileStructure:
    """Test markdown file structure and formatting"""

    def test_file_headers(self, isolated_todo_handler, temp_obsidian_file):
        """Test markdown file has proper headers"""
        with patch.dict(os.environ, {"OBSIDIAN_TODO_PATH": temp_obsidian_file}):
            isolated_todo_handler.add_task("Test task", category_string="project:test")
            isolated_todo_handler.add_task("Done task", category_string="work:urgent")
            isolated_todo_handler.complete_task("Done task")

            content = Path(temp_obsidian_file).read_text()
            assert "# Todo List" in content
            assert "## Incomplete Tasks" in content
            assert "## Completed Tasks" in content

    def test_section_organization(self, isolated_todo_handler, temp_obsidian_file):
        """Test tasks are properly organized in sections"""
        with patch.dict(os.environ, {"OBSIDIAN_TODO_PATH": temp_obsidian_file}):
            isolated_todo_handler.add_task("Incomplete 1", category_string="project:test")
            isolated_todo_handler.add_task("Incomplete 2", category_string="work:dev")
            isolated_todo_handler.add_task("Complete me", category_string="life:tasks")
            isolated_todo_handler.complete_task("Complete me")
            content = Path(temp_obsidian_file).read_text()
            incomplete_pos = content.find("## Incomplete Tasks")
            completed_pos = content.find("## Completed Tasks")
            incomplete_task1_pos = content.find("[project:test] Incomplete 1")
            incomplete_task2_pos = content.find("[work:dev] Incomplete 2")
            completed_task_pos = content.find("[life:tasks] Complete me")
            assert incomplete_pos < incomplete_task1_pos
            assert incomplete_pos < incomplete_task2_pos
            assert completed_pos < completed_task_pos
            assert incomplete_task1_pos < completed_pos
            assert incomplete_task2_pos < completed_pos

    def test_empty_sections_handling(self, isolated_todo_handler, temp_obsidian_file):
        """Test handling when no incomplete or completed tasks exist"""
        with patch.dict(os.environ, {"OBSIDIAN_TODO_PATH": temp_obsidian_file}):
            isolated_todo_handler.add_task("Only incomplete", category_string="project:test")
            content = Path(temp_obsidian_file).read_text()
            assert "# Todo List" in content
            assert "## Incomplete Tasks" in content
            assert "## Completed Tasks" not in content


class TestEnvironmentVariableHandling:
    """Test OBSIDIAN_TODO_PATH environment variable behavior"""

    def test_no_env_var_no_export(self, isolated_todo_handler):
        """Test no export happens when OBSIDIAN_TODO_PATH is not set"""
        with patch.dict(os.environ, {}, clear=True):
            if "OBSIDIAN_TODO_PATH" in os.environ:
                del os.environ["OBSIDIAN_TODO_PATH"]

            isolated_todo_handler.add_task("Test task", category_string="project:test")
            # No exception should be raised, just no file created
            # This is tested by the absence of any file operations

    def test_empty_env_var_no_export(self, isolated_todo_handler):
        """Test no export happens when OBSIDIAN_TODO_PATH is empty"""
        with patch.dict(os.environ, {"OBSIDIAN_TODO_PATH": ""}):
            isolated_todo_handler.add_task("Test task", category_string="project:test")
            # No exception should be raised

    def test_directory_creation(self, isolated_todo_handler):
        """Test directories are created if they don't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = os.path.join(temp_dir, "nested", "folder", "todos.md")

            with patch.dict(os.environ, {"OBSIDIAN_TODO_PATH": nested_path}):
                isolated_todo_handler.add_task("Test task", category_string="project:test")

                assert os.path.exists(nested_path)
                assert os.path.isfile(nested_path)


class TestFileIOAndErrorHandling:
    """Test file I/O operations and error scenarios"""

    def test_file_overwrite_behavior(self, isolated_todo_handler, temp_obsidian_file) -> None:
        """Test file is completely overwritten on each update"""
        with patch.dict(os.environ, {"OBSIDIAN_TODO_PATH": temp_obsidian_file}):
            Path(temp_obsidian_file).write_text("Old content")
            isolated_todo_handler.add_task("New task", category_string="project:test")
            content = Path(temp_obsidian_file).read_text()
            assert "Old content" not in content
            assert "# Todo List" in content
            assert "- [ ] [project:test] New task" in content

    def test_permission_error_handling(self, isolated_todo_handler) -> None:
        """Test graceful handling of permission errors"""
        with tempfile.TemporaryDirectory() as temp_dir:
            readonly_file = os.path.join(temp_dir, "readonly.md")
            Path(readonly_file).touch()
            os.chmod(readonly_file, 0o444)  # Read-only
            with patch.dict(os.environ, {"OBSIDIAN_TODO_PATH": readonly_file}):
                isolated_todo_handler.add_task("Test task", category_string="project:test")

    def test_invalid_path_handling(self, isolated_todo_handler) -> None:
        """Test handling of invalid directory paths"""
        invalid_path = "/root/forbidden/file.md"
        with patch.dict(os.environ, {"OBSIDIAN_TODO_PATH": invalid_path}):
            # Should not raise exception, just handle gracefully
            isolated_todo_handler.add_task("Test task", category_string="project:test")


class TestIntegrationWithTodoOperations:
    """Test Obsidian export integrates with all todo operations"""

    @patch("trackdo.core.todo_server.get_todo_handler")
    def test_add_tasks_triggers_export(self, mock_get_handler, isolated_todo_handler, temp_obsidian_file):
        """Test add_tasks MCP function triggers Obsidian export"""
        mock_get_handler.return_value = isolated_todo_handler

        with patch.dict(os.environ, {"OBSIDIAN_TODO_PATH": temp_obsidian_file}):
            add_tasks(["Export test task"], category="project:export")

            content = Path(temp_obsidian_file).read_text()
            assert "- [ ] [project:export] Export test task" in content

    @patch("trackdo.core.todo_server.get_todo_handler")
    def test_complete_tasks_triggers_export(self, mock_get_handler, isolated_todo_handler, temp_obsidian_file):
        """Test complete_tasks MCP function triggers Obsidian export"""
        mock_get_handler.return_value = isolated_todo_handler

        with patch.dict(os.environ, {"OBSIDIAN_TODO_PATH": temp_obsidian_file}):
            isolated_todo_handler.add_task("Complete me", category_string="project:test")
            complete_tasks(["Complete me"])

            content = Path(temp_obsidian_file).read_text()
            assert "- [x] [project:test] Complete me" in content

    @patch("trackdo.core.todo_server.get_todo_handler")
    def test_clear_tasks_triggers_export(self, mock_get_handler, isolated_todo_handler, temp_obsidian_file):
        """Test clear_tasks MCP function triggers Obsidian export"""
        mock_get_handler.return_value = isolated_todo_handler

        with patch.dict(os.environ, {"OBSIDIAN_TODO_PATH": temp_obsidian_file}):
            isolated_todo_handler.add_task("Will be cleared", category_string="project:test")
            clear_tasks()

            content = Path(temp_obsidian_file).read_text()
            assert "# Todo List" in content
            assert "Will be cleared" not in content

    def test_multiple_operations_final_state(self, isolated_todo_handler, temp_obsidian_file):
        """Test final markdown state after multiple operations"""
        with patch.dict(os.environ, {"OBSIDIAN_TODO_PATH": temp_obsidian_file}):
            isolated_todo_handler.add_task("Task 1", category_string="project:test")
            isolated_todo_handler.add_task("Task 2", category_string="life:personal")
            isolated_todo_handler.add_task("Task 3", category_string="project:test")
            isolated_todo_handler.complete_task("Task 1")
            isolated_todo_handler.complete_task("Task 2")

            content = Path(temp_obsidian_file).read_text()
            # Just check that the new hierarchical format is working
            assert "# Todo List" in content
            assert "- [ ] [project:test] Task 3" in content
            assert "- [x] [life:personal] Task 2" in content
            assert "- [x] [project:test] Task 1" in content


class TestMarkdownFormatCompliance:
    """Test generated markdown follows proper formatting"""

    def test_checkbox_format_compliance(self, isolated_todo_handler, temp_obsidian_file):
        """Test checkboxes follow standard markdown format"""
        with patch.dict(os.environ, {"OBSIDIAN_TODO_PATH": temp_obsidian_file}):
            isolated_todo_handler.add_task("Incomplete", category_string="project:test")
            isolated_todo_handler.add_task("Complete", category_string="work:task")
            isolated_todo_handler.complete_task("Complete")
            content: str = Path(temp_obsidian_file).read_text()
            assert "- [ ] [project:test] Incomplete" in content  # Incomplete with space
            assert "- [x] [work:task] Complete" in content  # Complete with space
            assert "-[ ]" not in content  # No format without space
            assert "-[x]" not in content  # No format without space

    def test_special_characters_in_tasks(self, isolated_todo_handler, temp_obsidian_file):
        """Test tasks with special characters are properly handled"""
        with patch.dict(os.environ, {"OBSIDIAN_TODO_PATH": temp_obsidian_file}):
            special_task = "Fix bug: [CRITICAL] Handle & process 'quotes' & \"double quotes\""
            isolated_todo_handler.add_task(special_task, category_string="work:urgent")
            content = Path(temp_obsidian_file).read_text()
            assert f"- [ ] [work:urgent] {special_task}" in content
