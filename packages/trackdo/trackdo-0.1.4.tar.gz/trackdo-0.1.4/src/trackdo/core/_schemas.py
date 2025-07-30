from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from typing import TYPE_CHECKING, Self

from bear_epoch_time import EpochTimestamp
from bear_utils.database import DatabaseManager
from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column as m_column, relationship

if TYPE_CHECKING:
    from sqlalchemy.orm.decl_api import DeclarativeMeta

Base: DeclarativeMeta = DatabaseManager.get_base()

DONE = "✅"
TODO = "⭕"


@dataclass
class Task:
    task_id: int
    text: str
    category: str
    subcategory: str
    created_at: EpochTimestamp
    completed_at: EpochTimestamp | None = None
    completed: bool = False
    parent_task_id: int | None = None
    subtasks: list[Task] = field(default_factory=list)
    depth: int = 0

    def __repr__(self) -> str:
        return self.to_string(get_id=True, category=True)

    def to_string(self, get_id: bool = False, category: bool = True) -> str:
        """Get the task string representation with optional ID"""
        result = f"{self.icon} {self.text}"
        if category:
            result = f"{self.category_str} {result}"
        if get_id:
            result = f"{self.task_id}: {result}"
        return result

    @staticmethod
    def get_hash(string_rep: str) -> str:
        return hashlib.blake2b(string_rep.encode()).hexdigest()

    def to_attrs(self) -> str:
        """Get a string representation of the task attributes"""
        string_rep: str = ", ".join(
            [
                f"{self.task_id=}",
                f"{self.category=}",
                f"{self.subcategory=}",
                f"{self.completed_at=}",
                f"{self.created_at=}",
                f"{self.completed=}",
                f"{self.parent_task_id=}",
            ]
        ).replace("self.", "")
        hashed = str(self.get_hash(string_rep))
        return f"task_hash={hashed}, {string_rep}"

    @property
    def icon(self) -> str:
        """Get the icon based on completion status"""
        return DONE if self.completed else TODO

    @property
    def category_str(self) -> str:
        """Get the full category:subcategory string"""
        return f"{self.category}:{self.subcategory}"

    @property
    def is_subtask(self) -> bool:
        """Check if this is a subtask"""
        return self.parent_task_id is not None

    @classmethod
    def from_todo_list(cls, todo_entry: TodoList, depth: int = 0) -> Self:
        """Create a Task instance from a TodoList entry"""
        subtasks: list[Task] = [
            cls.from_todo_list(
                todo_entry=subtask,
                depth=depth + 1,
            )
            for subtask in todo_entry.subtasks
        ]
        return cls(
            task_id=todo_entry.id,
            text=todo_entry.task_text,
            completed=todo_entry.completed,
            category=todo_entry.category,
            subcategory=todo_entry.subcategory,
            created_at=EpochTimestamp(todo_entry.created_at),
            completed_at=EpochTimestamp(todo_entry.completed_at) if todo_entry.completed_at else None,
            parent_task_id=todo_entry.parent_task_id,
            subtasks=subtasks,
            depth=todo_entry.depth if todo_entry.depth is not None else depth,
        )


class Categories(Base):
    __tablename__: str = "categories"
    name: Mapped[str] = m_column(String, primary_key=True)
    todos: Mapped[list[TodoList]] = relationship(
        argument="TodoList",
        back_populates="category_ref",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"{self.name}"


class TodoList(Base):
    __tablename__: str = "todo_list"

    id: Mapped[int] = m_column(Integer, primary_key=True)
    task_text: Mapped[str] = m_column(String, nullable=False)
    completed: Mapped[bool] = m_column(Boolean, default=False, index=True)
    subcategory: Mapped[str] = m_column(String, nullable=False)
    created_at: Mapped[int] = m_column(Integer, default=EpochTimestamp.now)
    completed_at: Mapped[int | None] = m_column(Integer, nullable=True)
    parent_task_id: Mapped[int | None] = m_column(Integer, ForeignKey("todo_list.id"), nullable=True, index=True)
    category_ref: Mapped[Categories] = relationship(
        "Categories",
        back_populates="todos",
        lazy="select",
    )
    category: Mapped[str] = m_column(
        String,
        ForeignKey("categories.name"),
        nullable=False,
        index=True,
    )
    parent_task: Mapped[TodoList | None] = relationship("TodoList", remote_side=[id], back_populates="subtasks")
    subtasks: Mapped[list[TodoList]] = relationship(
        "TodoList", back_populates="parent_task", cascade="all, delete-orphan"
    )
    depth: Mapped[int] = m_column(Integer, default=0, nullable=False)

    def __repr__(self) -> str:
        return f"{self.icon} {self.category_str} {self.task_text}"

    @property
    def icon(self) -> str:
        """Get the icon based on completion status"""
        return DONE if self.completed else TODO

    @property
    def category_str(self) -> str:
        """Get the full category:subcategory string"""
        return f"{self.category}:{self.subcategory}"

    @property
    def is_top_level(self) -> bool:
        """Check if this is a top-level task (no parent)"""
        return self.parent_task_id is None

    @property
    def has_subtasks(self) -> bool:
        """Check if this task has subtasks"""
        return len(self.subtasks) > 0
