from io import StringIO
from typing import cast

from rich.console import Console
from rich.tree import Tree

from ._schemas import Task


class TreeHandler:
    def __init__(self, todo_list: dict[int, Task] | None = None) -> None:
        self.todo_list: dict[int, Task] | None = todo_list
        self.tree = Tree("Todo List", highlight=False, hide_root=True)
        self.console = Console(
            file=StringIO(),
            markup=False,
            highlight=False,
            no_color=True,
        )
        self.buffer: StringIO = cast("StringIO", self.console.file)

    def get_buffer(self, tree: Tree | None = None) -> str:
        """Reset the console buffer"""
        self.console.print(self.tree if tree is None else tree)
        capture: str = self.buffer.getvalue()
        self.buffer.truncate(0)
        self.buffer.seek(0)
        return capture

    def _add_to_tree(self, task: Task, tree_node: Tree) -> None:
        """Add a task and its subtasks to the tree"""
        task_node: Tree = tree_node.add(label=task.to_string(get_id=True))
        for subtask in task.subtasks:
            self._add_to_tree(task=subtask, tree_node=task_node)

    def build_hierarchy(self, root_task: Task) -> str:
        """Build a tree for a specific root task and its subtasks"""
        temp_tree = Tree(label=root_task.to_string(get_id=True), hide_root=True)
        self._add_to_tree(task=root_task, tree_node=temp_tree)
        return self.get_buffer(tree=temp_tree)

    def build_full_tree(self) -> str:
        """Build a tree for all top-level tasks and their subtasks"""
        if self.todo_list is None:
            return "No tasks available to build tree."
        completed: list[Task] = [task for task in self.todo_list.values() if task.completed]
        incomplete: list[Task] = [task for task in self.todo_list.values() if not task.completed]
        todo_list: list[Task] = sorted(incomplete, key=lambda t: (t.category, t.subcategory, t.created_at))
        todo_list += sorted(completed, key=lambda t: (t.category, t.subcategory, t.created_at))

        for task in todo_list:
            if task.parent_task_id is None:
                self._add_to_tree(task=task, tree_node=self.tree)
        return self.get_buffer()
