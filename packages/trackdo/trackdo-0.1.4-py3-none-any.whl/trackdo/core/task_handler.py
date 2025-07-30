"""TodoHandler Module

This module provides the TodoHandler class, which manages a todo list and tasks.
"""

from __future__ import annotations

from os import getenv
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from bear_epoch_time import EpochTimestamp
from bear_utils.database import DatabaseManager
from singleton_base import SingletonBase

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from ._schemas import Categories, Task, TodoList
from ._trees import TreeHandler
from .markdown_export import update_obsidian_export


class TodoHandler(SingletonBase):
    """Singleton class to manage the todo list and tasks"""

    def __init__(self) -> None:
        """Initialize the TodoHandler with an empty todo list and database connection"""
        self.todo_list: dict[int, Task] = {}
        self._categories_cache: list[str] | None = None
        db_path: str = getenv("DATABASE_PATH", str(Path(__file__).parent))
        db_url: str = f"sqlite:///{db_path}/{getenv('DATABASE_FILENAME', 'todo_list.db')}"
        self.db = DatabaseManager(db_url=db_url)
        self.update_tasks()

    def update_tasks(self) -> None:
        """Update the todo list from the database and refresh the export file"""
        if self.todo_list:
            self.todo_list.clear()
        session: Session = self.db.session()
        existing_tasks: list[TodoList] = session.query(TodoList).all()
        for todo_entry in existing_tasks:
            task: Task = Task.from_todo_list(todo_entry)
            self.todo_list[todo_entry.id] = task
        update_obsidian_export(todo_list=self.todo_list)

    def get_tasks(self) -> dict[int, Task]:
        """Get the current todo list as a dictionary of Task objects

        Returns:
            dict[int, Task]: Dictionary of Task objects indexed by task ID
        """
        return self.todo_list

    def get_task(self, task_id: int) -> Task | None:
        """Get a specific task by ID

        Args:
            task_id (int): The ID of the task to retrieve

        Returns:
            Task | None: The Task object if found, otherwise None
        """
        return self.todo_list.get(task_id)

    def tasks_finished_today(self) -> dict[int, Task]:
        """Get a list of tasks that were completed within the last 24 hours.

        Returns:
            list[Task]: List of Task objects that were completed within the last 24 hours.
        """
        thirty_six_hundred = 24 * 60 * 60 * 1000
        twenty_four_hours_ago = EpochTimestamp(EpochTimestamp.now() - thirty_six_hundred)
        print(f"Tasks completed since: {twenty_four_hours_ago.to_string()}")
        completed_tasks: list[Task] = [task for task in self.todo_list.values() if task.completed]

        completed_tasks = [
            t for t in completed_tasks if t.completed_at is not None and t.completed_at >= twenty_four_hours_ago
        ]
        return {t.task_id: t for t in completed_tasks}

    def _validate_category_exists(self, session: Session, category: str) -> str | None:
        """Validate that a category exists, return error message if not"""
        if not session.query(Categories).filter_by(name=category).first():
            return f"Category '{category}' does not exist. Available categories: {', '.join(self.get_categories())}"
        return None

    def _validate_parent_task(self, session: Session, parent_task_id: int) -> TodoList | str:
        """Validate parent task exists, return TodoList object or error message"""
        parent_task = session.query(TodoList).filter(TodoList.id == parent_task_id).first()
        if parent_task is None:
            return f"Parent task with ID {parent_task_id} not found"
        return parent_task

    def _calculate_depth(self, task: TodoList) -> int:
        """Calculate the depth of a task in the hierarchy"""
        depth: int = 0
        while task.parent_task_id is not None:
            parent_task: TodoList | None = self.db.session().query(TodoList).filter_by(id=task.parent_task_id).first()
            if parent_task is None:
                break
            depth += 1
            task = parent_task
        return depth

    def add_task(self, task_text: str, category: str, sub_category: str, parent_task_id: int | None = None) -> str:
        """Add a task with category:subcategory format, optionally as a subtask

        Args:
            task_text (str): The text of the task to add
            category (str): The category name
            sub_category (str): The subcategory name
            parent_task_id (int | None): The ID of the parent task, if this is a subtask
        Returns:
            str: Success or error message
        """
        if not task_text:
            return "Task text cannot be empty."
        session: Session = self.db.session()
        category_error: str | None = self._validate_category_exists(session, category)
        if category_error is not None:
            return category_error

        parent_task: TodoList | None = None
        if parent_task_id is not None:
            parent_result: TodoList | str = self._validate_parent_task(session, parent_task_id)
            if isinstance(parent_result, str):
                return parent_result
            parent_task = parent_result

        todo_entry = TodoList(
            task_text=task_text,
            completed=False,
            category=category,
            subcategory=sub_category,
            parent_task_id=parent_task_id,
            created_at=EpochTimestamp.now(),
            depth=0,
        )
        depth = self._calculate_depth(todo_entry)
        todo_entry.depth = depth
        if parent_task is not None:
            parent_task.subtasks.append(todo_entry)
            session.add(parent_task)
        session.add(todo_entry)
        session.commit()

        self.update_tasks()

        if parent_task is not None:
            return f"Subtask added successfully with ID {todo_entry.id}. Parent: '{parent_task.task_text}'"
        return f"Task added: {todo_entry.id}: {todo_entry.task_text}"

    def edit_task(self, task_id: int, new_text: str) -> str:
        """Edit an existing task's text

        Args:
            task_id (int): The ID of the task to edit
            new_text (str): The new text for the task

        Returns:
            str: Success message or error message if task not found
        """
        if task_id not in self.todo_list:
            return f"Task ID#'{task_id}' not found."
        session: Session = self.db.session()
        db_task: TodoList | None = session.query(TodoList).filter_by(id=task_id).first()
        if db_task is None:
            return f"Task ID#'{task_id}' not found in database."
        db_task.task_text = new_text
        session.commit()
        self.update_tasks()
        return f"Task updated: ID#{task_id} - {new_text}"

    def _complete(self, db_task: TodoList) -> str:
        """Complete a task in the database and update its status

        Args:
            db_task (TodoList): The task to complete

        Returns:
            str: Success message indicating task completion
        """
        task_id: int = db_task.id
        self.todo_list[task_id].completed = True
        db_task.completed = True
        db_task.completed_at = EpochTimestamp.now()
        return f"Task Completed: ID#{task_id}"

    def complete_task(self, task_id: int, complete_subtasks: bool = False) -> str:
        """Complete a task by ID, optionally completing all subtasks

        Args:
            task_id (int): The ID of the task to complete
            complete_subtasks (bool, optional): Whether to complete all subtasks of the task. Defaults to False.

        Returns:
            str: Success message or error message if task not found
        """
        if task_id not in self.todo_list:
            return f"Task ID#'{task_id}' not found."
        session: Session = self.db.session()
        db_task: TodoList | None = session.query(TodoList).filter_by(id=task_id).first()
        if db_task is None:
            return f"Task ID#'{task_id}' not found in database."
        self._complete(db_task)
        completed_count = 1
        if complete_subtasks:
            completed_count += self._complete_subtasks(db_task)
        session.commit()
        self.update_tasks()
        if completed_count > 1:
            return f"Completed {completed_count} task(s) successfully"
        return f"Task completed: ID#{task_id}"

    def undo_complete_task(self, task_id: int) -> str:
        """Undo completion of a task by ID

        Args:
            task_id (int): The ID of the task to undo completion for

        Returns:
            str: Success message or error message if task not found
        """
        if task_id not in self.todo_list:
            return f"Task ID#'{task_id}' not found."
        session: Session = self.db.session()
        db_task: TodoList | None = session.query(TodoList).filter_by(id=task_id).first()
        if db_task is None:
            return f"Task ID#'{task_id}' not found in database."
        db_task.completed = False
        db_task.completed_at = None
        session.commit()
        self.update_tasks()
        return f"Task undone: ID#{task_id}"

    def _complete_subtasks(self, parent_task: TodoList) -> int:
        """Complete all subtasks of a given parent task

        Args:
            parent_task (TodoList): The parent task whose subtasks will be completed

        Returns:
            int: Number of subtasks completed
        """
        completed_count = 0
        stack: list[TodoList] = list(parent_task.subtasks)
        while stack:
            subtask: TodoList = stack.pop()
            if not subtask.completed:
                self._complete(subtask)
                completed_count += 1
            stack.extend(subtask.subtasks)
        return completed_count

    def get_task_strings(self) -> list[str]:
        """Get the current todo list as a list of task strings

        Returns:
            list[str]: List of task strings in the format "⭕ [category:subcategory] Task text" or "✅ [category:subcategory] Task text"
        """
        return [str(task) for task in self.todo_list.values()]

    def get_tasks_by_category(self, category: str, subcategory: str | None = None) -> dict[int, Task]:
        """Get tasks filtered by category and/or subcategory

        Args:
            category: Category to filter by.
            subcategory: Subcategory to filter by. If None, returns all tasks in category.

        Returns:
            dict: Dictionary of tasks matching the filter
        """
        filtered: dict[int, Task] = {k: v for k, v in self.todo_list.items() if v.category == category}
        if subcategory is not None:
            filtered = {k: v for k, v in filtered.items() if v.subcategory == subcategory}
        return filtered

    def get_categories(self) -> list[str]:
        """Get list of available categories (cached)"""
        if self._categories_cache is None:
            session: Session = self.db.session()
            categories: list[Categories] = session.query(Categories).all()
            self._categories_cache = [cat.name for cat in categories]
        return self._categories_cache

    def add_category(self, category_name: str) -> str:
        """Add a new category"""
        session: Session = self.db.session()
        if session.query(Categories).filter_by(name=category_name).first():
            return f"Category '{category_name}' already exists."
        session.add(Categories(name=category_name))
        session.commit()
        return f"Category '{category_name}' added successfully."

    def delete_category(self, category_name: str) -> str:
        """Delete a category and all associated tasks (using cascade delete)"""
        session: Session = self.db.session()
        category: Categories | None = session.query(Categories).filter_by(name=category_name).first()
        if category is None:
            return f"Category '{category_name}' does not exist."
        session.delete(category)
        session.commit()
        self.update_tasks()
        return f"Category '{category_name}' deleted successfully."

    def delete_task(self, task_id: int) -> str:
        """Delete a single task by ID

        Args:
            task_id: The ID of the task to delete

        Returns:
            Success message with task details or error message
        """
        if task_id not in self.todo_list:
            return f"Task ID#'{task_id}' not found."
        session: Session = self.db.session()
        session.query(TodoList).filter_by(id=task_id).delete()
        session.commit()
        self.update_tasks()
        return f"Task deleted: ID#{task_id}"

    def clear_tasks(self) -> Literal["All tasks cleared."]:
        """Clear all tasks from the todo list.

        Returns:
            Literal["All tasks cleared."]: Confirmation message indicating all tasks have been cleared.
        """
        session: Session = self.db.session()
        session.query(TodoList).delete()
        session.commit()
        self.update_tasks()
        return "All tasks cleared."

    def clear_completed_tasks(self) -> Literal["All completed tasks cleared."]:
        """Clear all completed tasks from the todo list.

        Returns:
            Literal["All completed tasks cleared."]: Confirmation message indicating all completed tasks have been cleared.
        """
        session: Session = self.db.session()
        session.query(TodoList).filter_by(completed=True).delete()
        session.commit()
        self.update_tasks()
        return "All completed tasks cleared."

    def add_subtask(self, text: str, category: str, subcategory: str, parent_task_id: int) -> str:
        """Add a subtask to an existing task

        This is a convenience wrapper around add_task() with parent_task_id

        Args:
            text: The task text
            category: The category name
            subcategory: The subcategory name
            parent_task_id: The ID of the parent task

        Returns:
            str: Success or error message
        """
        return self.add_task(
            task_text=text,
            category=category,
            sub_category=subcategory,
            parent_task_id=parent_task_id,
        )

    def get_task_tree(self) -> str:
        """Get a tree representation of all top-level tasks and their subtasks

        Returns:
            str: Tree structure of tasks
        """
        return TreeHandler(todo_list=self.todo_list).build_full_tree()

    def get_task_hierarchy(self, task_id: int) -> str:
        """Get a task and all its subtasks in a hierarchical structure

        Args:
            task_id: The ID of the root task

        Returns:
            str: Task hierarchy or error message
        """
        if task_id not in self.todo_list:
            return f"Task with ID {task_id} not found"

        root_task: Task = self.todo_list[task_id]
        return TreeHandler().build_hierarchy(root_task)

    def get_top_level_tasks(self, category: str | None = None, subcategory: str | None = None) -> dict[int, Task]:
        """Get all top-level tasks (no parent) with optional category filtering

        Args:
            category: Optional category filter
            subcategory: Optional subcategory filter

        Returns:
            dict[int, Task]: Dictionary of top-level Task objects
        """
        filtered: dict[int, Task] = {k: v for k, v in self.todo_list.items() if v.parent_task_id is None}

        if category is not None:
            filtered = {k: v for k, v in filtered.items() if v.category == category}
        if subcategory is not None:
            filtered = {k: v for k, v in filtered.items() if v.subcategory == subcategory}

        return filtered

    def complete_task_with_subtasks(self, task_id: int, complete_subtasks: bool = False) -> str:
        """Complete a task and optionally its subtasks

        Args:
            task_id: The ID of the task to complete
            complete_subtasks: Whether to also complete all subtasks
        Returns:
            str: Success message or error message
        """
        return self.complete_task(task_id, complete_subtasks)

    def get_subtasks(self, parent_task_id: int) -> dict[int, Task]:
        """Get all direct subtasks of a parent task

        Args:
            parent_task_id: The ID of the parent task

        Returns:
            dict[int, Task]: Dictionary of Task objects that are direct children
        """
        return {k: v for k, v in self.todo_list.items() if v.parent_task_id == parent_task_id}


def get_todo_handler() -> TodoHandler:
    """Get the singleton TodoHandler instance"""
    return TodoHandler.get_instance(init=True)
