from typing import Literal

from bear_epoch_time import EpochTimestamp
import pytest

from trackdo.core._schemas import Task
from trackdo.core.markdown_export import update_obsidian_export


@pytest.fixture
def sample_tasks():
    """Fixture to create a sample todo list with various tasks and subtasks."""
    main_task_1 = Task(
        task_id=1,
        text="Implement authentication system",
        category="work",
        subcategory="backend",
        created_at=EpochTimestamp.now(),
        completed=False,
        parent_task_id=None,
        subtasks=[],
        depth=0,
    )

    main_task_2 = Task(
        task_id=2,
        text="Design user interface",
        category="work",
        subcategory="frontend",
        created_at=EpochTimestamp.now(),
        completed=True,
        parent_task_id=None,
        subtasks=[],
        depth=0,
    )

    main_task_3 = Task(
        task_id=3,
        text="Plan vacation",
        category="personal",
        subcategory="travel",
        created_at=EpochTimestamp.now(),
        completed=False,
        parent_task_id=None,
        subtasks=[],
        depth=0,
    )

    main_task_4 = Task(
        task_id=9,
        text="Go to gym",
        category="personal",
        subcategory="life",
        created_at=EpochTimestamp.now(),
        completed=False,
        parent_task_id=None,
        subtasks=[],
        depth=0,
    )

    main_task_5 = Task(
        task_id=10,
        text="Buy groceries",
        category="personal",
        subcategory="life",
        created_at=EpochTimestamp.now(),
        completed=True,
        parent_task_id=None,
        subtasks=[],
        depth=0,
    )

    subtask_1_1 = Task(
        task_id=4,
        text="Set up JWT tokens",
        category="work",
        subcategory="backend",
        created_at=EpochTimestamp.now(),
        completed=False,
        parent_task_id=1,
        subtasks=[],
        depth=1,
    )

    subtask_1_2 = Task(
        task_id=5,
        text="Create login endpoint",
        category="work",
        subcategory="backend",
        created_at=EpochTimestamp.now(),
        completed=True,
        parent_task_id=1,
        subtasks=[],
        depth=1,
    )

    sub_subtask_1_1_1 = Task(
        task_id=6,
        text="Research JWT libraries",
        category="work",
        subcategory="backend",
        created_at=EpochTimestamp.now(),
        completed=False,
        parent_task_id=4,
        subtasks=[],
        depth=2,
    )

    subtask_3_1 = Task(
        task_id=7,
        text="Book flights",
        category="personal",
        subcategory="travel",
        created_at=EpochTimestamp.now(),
        completed=True,
        parent_task_id=3,
        subtasks=[],
        depth=1,
    )

    subtask_3_2 = Task(
        task_id=8,
        text="Book hotel",
        category="personal",
        subcategory="travel",
        created_at=EpochTimestamp.now(),
        completed=False,
        parent_task_id=3,
        subtasks=[],
        depth=1,
    )

    subtask_1_1.subtasks = [sub_subtask_1_1_1]
    main_task_1.subtasks = [subtask_1_1, subtask_1_2]
    main_task_3.subtasks = [subtask_3_1, subtask_3_2]

    return {
        1: main_task_1,
        2: main_task_2,
        3: main_task_3,
        4: subtask_1_1,
        5: subtask_1_2,
        6: sub_subtask_1_1_1,
        7: subtask_3_1,
        8: subtask_3_2,
        9: main_task_4,
        10: main_task_5,
    }


@pytest.fixture
def temp_markdown_file(tmp_path):
    """Create a temporary markdown file for testing."""
    return tmp_path / "test_todos.md"


class TestMarkdownExport:
    """Test class for markdown export functionality."""

    def test_update_obsidian_export_success(self, sample_tasks, temp_markdown_file, monkeypatch):
        """Test successful markdown export."""
        monkeypatch.setenv("OBSIDIAN_TODO_PATH", str(temp_markdown_file))

        success = update_obsidian_export(sample_tasks)

        assert success is True
        assert temp_markdown_file.exists()

        content = temp_markdown_file.read_text()

        assert "# Todo List" in content
        assert "---" in content
        assert "task_count:" in content
        assert "not_completed_count:" in content
        assert "percent_complete:" in content

        assert "Implement authentication system" in content
        assert "Design user interface" in content
        assert "Plan vacation" in content
        assert "Go to gym" in content
        assert "Buy groceries" in content

        assert "### Work" in content
        assert "### Personal" in content
        assert "#### Backend" in content
        assert "#### Frontend" in content
        assert "#### Travel" in content
        assert "#### Life" in content

        assert "- [ ]" in content
        assert "- [x]" in content

    def test_update_obsidian_export_no_env_var(self, sample_tasks, monkeypatch):
        """Test export when OBSIDIAN_TODO_PATH is not set."""
        monkeypatch.delenv("OBSIDIAN_TODO_PATH", raising=False)

        success = update_obsidian_export(sample_tasks)

        assert success is False

    def test_update_obsidian_export_empty_todo_list(self, temp_markdown_file, monkeypatch):
        """Test export with empty todo list."""
        monkeypatch.setenv("OBSIDIAN_TODO_PATH", str(temp_markdown_file))

        empty_todo_list = {}
        success: bool = update_obsidian_export(empty_todo_list)

        assert success is True
        assert temp_markdown_file.exists()

        content: str = temp_markdown_file.read_text()
        assert "task_count: 0" in content
        assert "not_completed_count: 0" in content
        assert "percent_complete: 0.00" in content

    def test_hierarchical_structure(self, sample_tasks: dict[int, Task], temp_markdown_file, monkeypatch):
        """Test that hierarchical task structure is preserved in markdown."""
        monkeypatch.setenv("OBSIDIAN_TODO_PATH", str(temp_markdown_file))

        success: bool = update_obsidian_export(sample_tasks)
        assert success is True

        content: str = temp_markdown_file.read_text()
        lines = content.split("\n")

        subtask_lines = [line for line in lines if line.startswith("  - ")]
        assert len(subtask_lines) > 0, "Should have indented subtasks"

        sub_subtask_lines = [line for line in lines if line.startswith("    - ")]
        assert len(sub_subtask_lines) > 0, "Should have double-indented sub-subtasks"

    def test_completed_vs_incomplete_sections(self, sample_tasks, temp_markdown_file, monkeypatch):
        """Test that completed and incomplete tasks are in separate sections."""
        monkeypatch.setenv("OBSIDIAN_TODO_PATH", str(temp_markdown_file))

        success = update_obsidian_export(sample_tasks)
        assert success is True

        content = temp_markdown_file.read_text()

        assert "## Completed Tasks" in content

        assert "----" in content

        parts = content.split("----")
        assert len(parts) == 2

        incomplete_section = parts[0]
        completed_section = parts[1]

        assert "Go to gym" in incomplete_section
        assert "Implement authentication system" in incomplete_section

        assert "Design user interface" in completed_section
        assert "Buy groceries" in completed_section

    def test_yaml_frontmatter_calculation(self, sample_tasks, temp_markdown_file, monkeypatch):
        """Test that YAML frontmatter calculations are correct."""
        monkeypatch.setenv("OBSIDIAN_TODO_PATH", str(temp_markdown_file))

        success: bool = update_obsidian_export(sample_tasks)
        assert success is True

        content = temp_markdown_file.read_text()

        total_tasks: int = len(sample_tasks)
        completed_tasks: int = sum(1 for task in sample_tasks.values() if task.completed)
        incomplete_tasks: int = total_tasks - completed_tasks
        expected_percent: float | Literal[0] = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        assert f"task_count: {total_tasks}" in content
        assert f"not_completed_count: {incomplete_tasks}" in content
        assert f"percent_complete: {expected_percent:.2f}" in content
