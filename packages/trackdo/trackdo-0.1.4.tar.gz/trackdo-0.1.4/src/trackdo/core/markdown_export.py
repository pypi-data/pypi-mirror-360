"""This Module exports the current todo list to a markdown file with proper checkbox formatting for Obsidian compatibility.

The export is triggered automatically on any todo list modification (add, complete, clear).

Environment Variables:
    OBSIDIAN_TODO_PATH: Path to the markdown file for export.
    If not set or empty, no export occurs.

Markdown Format:
    - Incomplete tasks: `- [ ] [category:subcategory] Task text`
    - Completed tasks: `- [x] [category:subcategory] Task text`
    - Organized hierarchically into category sections
    - Categories are displayed as "Category: Subcategory" headers
    - Both incomplete and completed tasks are grouped by category

Error Handling:
    - Gracefully handles file permission errors
    - Creates parent directories if they don't exist
    - Prints error messages to console on failure
    - Never raises exceptions to avoid breaking todo operations

Examples:
    # Set environment variable
    export OBSIDIAN_TODO_PATH="/path/to/obsidian/vault/todos.md"

    # Add tasks - automatically triggers export
    add_tasks(["Fix bug", "Write tests"], category="project:mcp")

    # Generated markdown:
    # # Todo List
    #
    # ## Incomplete Tasks
    #
    # ### Project: Mcp
    #
    # - [ ] [project:mcp] Fix bug
    # - [ ] [project:mcp] Write tests
    #
    # ### Work: Development
    #
    # - [ ] [work:development] Code review
"""

from io import StringIO
import os
from pathlib import Path
import sys
from types import SimpleNamespace
from typing import LiteralString

from bear_epoch_time import EpochTimestamp

from ._schemas import DONE, TODO, Task

MK_TODO = "- [ ]"
MK_DONE = "- [x]"
MARKDOWN_INDENT = "  "


def yaml_frontmatter(count: int, not_complete_count: int) -> str:
    """Generate YAML frontmatter for Obsidian markdown export"""
    percent_complete: float = 0.0 if count == 0 else 100 - not_complete_count / count * 100

    return f"""---
task_count: {count}
not_completed_count: {not_complete_count}
percent_complete: {percent_complete:.2f}
timestamp: {EpochTimestamp.now()}
created: {EpochTimestamp.now().to_string()}
---\n
"""


def replace_symbols(text: str) -> str:
    """Replace task symbols with markdown checkboxes for Obsidian compatibility"""
    return text.replace(TODO, MK_TODO).replace(DONE, MK_DONE)


class MarkdownExporter:
    """Export the todo list to a markdown file for Obsidian compatibility."""

    def __init__(self, todo_list: dict[int, Task], path: str) -> None:
        """Initialize the MarkdownExporter"""
        self.obsidian_path: str = path
        self.tasks = SimpleNamespace(
            completed=[task for task in todo_list.values() if task.completed and task.parent_task_id is None],
            incomplete=[task for task in todo_list.values() if not task.completed and task.parent_task_id is None],
        )
        self.tasks.completed = sorted(self.tasks.completed, key=lambda t: (t.category, t.subcategory, t.created_at))
        self.tasks.incomplete = sorted(self.tasks.incomplete, key=lambda t: (t.category, t.subcategory, t.created_at))
        self.count: int = len(todo_list)
        self.not_complete_count: int = sum(1 for task in todo_list.values() if not task.completed)
        self.md_str = StringIO()

    def _header(self) -> None:
        """Generate the header for the markdown file"""
        self.md_str.write(yaml_frontmatter(count=self.count, not_complete_count=self.not_complete_count))
        self.md_str.write("# Todo List\n")

    def _create_html_comment(self, task: Task) -> str:
        """Create an HTML comment for the task ID"""
        return f"<!-- {task.to_attrs()} -->"

    def _write_task(self, task: Task) -> str:
        """Format a single task for markdown export"""
        string_output: str = replace_symbols(task.to_string(category=False))
        string_output += self._create_html_comment(task)
        return string_output

    def _write_task_with_subtasks(self, task: Task, depth: int = 0) -> None:
        """Write a task and all its subtasks to the markdown string"""
        indent: LiteralString = MARKDOWN_INDENT * depth
        line: str = self._write_task(task)
        self.md_str.write(f"{indent}{line}\n")

        for subtask in task.subtasks:
            self._write_task_with_subtasks(subtask, depth + 1)

    def _write_incomplete_tasks(self) -> None:
        """Write incomplete tasks to the markdown string"""
        if not self.tasks.incomplete:
            return
        current_category = None
        current_subcategory = None

        for task in self.tasks.incomplete:
            if task.category != current_category:
                if current_category is not None:
                    self.md_str.write("\n")
                current_category = task.category
                current_subcategory = None
                self.md_str.write(f"\n### {task.category.title()}\n")
            if task.subcategory != current_subcategory:
                current_subcategory = task.subcategory
                self.md_str.write(f"\n#### {task.subcategory.title()}\n")

            self._write_task_with_subtasks(task)

    def _write_completed_tasks(self) -> None:
        """Write completed tasks to the markdown string"""
        if not self.tasks.completed:
            return

        self.md_str.write("## Completed Tasks\n\n")
        current_category = None
        current_subcategory = None

        for task in self.tasks.completed:
            if task.category != current_category:
                if current_category is not None:
                    self.md_str.write("\n")
                current_category = task.category
                current_subcategory = None
                self.md_str.write(f"### {task.category.title()}\n")
            if task.subcategory != current_subcategory:
                current_subcategory = task.subcategory
                self.md_str.write(f"\n#### {task.subcategory.title()}\n")

            self._write_task_with_subtasks(task)

    def write_to_file(self) -> bool:
        """Write the current todo list to the Obsidian markdown file"""
        try:
            if self.obsidian_path is None:
                return False
            obsidian_file = Path(self.obsidian_path)
            obsidian_file.parent.mkdir(parents=True, exist_ok=True)
            obsidian_file.write_text(self.md_str.getvalue(), encoding="utf-8")
            return True
        except Exception as e:
            print(f"Failed to update Obsidian export: {e}", file=sys.stderr)
            return False
        finally:
            self.md_str.close()

    def export(self) -> bool:
        """Export the todo list to markdown format"""
        if not self.obsidian_path:
            return False

        self._header()
        self._write_incomplete_tasks()
        self.md_str.write("\n----\n\n")
        self._write_completed_tasks()
        return self.write_to_file()


def update_obsidian_export(todo_list: dict[int, Task]) -> bool:
    """Update Obsidian markdown file if OBSIDIAN_TODO_PATH is set

    Args:
        todo_list (dict[int, Task]): The current todo list to export.

    Returns:
        bool: True if the export was successful, False otherwise.
    """
    path: str | None = os.getenv("OBSIDIAN_TODO_PATH", None)
    if path is None:
        print("OBSIDIAN_TODO_PATH is not set. Skipping export.", file=sys.stderr)
        return False
    markdown = MarkdownExporter(todo_list=todo_list, path=path)
    return markdown.export()
