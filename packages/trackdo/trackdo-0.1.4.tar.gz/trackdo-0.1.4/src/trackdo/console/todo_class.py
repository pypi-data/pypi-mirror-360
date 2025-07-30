"""Todo CLI for TrackDo."""

from __future__ import annotations

from shlex import split
import sys
from typing import TYPE_CHECKING, Any, Literal, LiteralString, NoReturn

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import confirm
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from singleton_base import SingletonBase

from trackdo.console._common_tasks import get_completed_tasks, get_incomplete_tasks, get_indent, get_invalid_ids
from trackdo.console.aliases import CommandMeta, TyperBridge
from trackdo.console.command_registry import CommandRegistry, CommandSpec, pos_arg
from trackdo.core.task_handler import TodoHandler

if TYPE_CHECKING:
    from argparse import Namespace

    from trackdo.core._schemas import Task

console = Console()

INDENT = "  "

registry = CommandRegistry()


class TodoCLI(SingletonBase):
    """Interactive Todo CLI with colorful interface using rich and prompt_toolkit."""

    def __init__(self) -> None:
        """Initialize the TodoCLI with a TodoHandler and command mappings."""
        self.todo_handler = TodoHandler()
        # do not init because cli should have initialized it, if it doesn't then we have a problem
        self.typer_bridge: TyperBridge = TyperBridge.get_instance(init=False)
        self.commands: dict[str, CommandSpec] = registry.commands
        self.command_completer = WordCompleter(words=list(self.commands.keys()))
        self.command_history = FileHistory(".todo_cli_history")

    def show_welcome(self) -> None:
        """Display welcome message"""
        welcome_panel: Panel = Panel.fit(
            renderable="[bold magenta]⚡ TrackDo Neural Interface Activated ⚡[/bold magenta]\n\n"
            "[dim cyan]>> Cybernetic task management system online <<[/dim cyan]\n"
            "Enter 'help' to access command matrix or 'quit' to jack out",
            border_style="bright_magenta",
            title="🔧 NEURAL UPLINK 🔧",
        )
        console.print(welcome_panel)

    @registry.command("help", help_text="Show available commands")
    def show_help(self, command_name: str | None = None) -> None:
        """Show available commands using Typer's registered commands

        Args:
            command_name (str | None): Specific command name to show help for. If None, shows all commands.
        """
        help_table = Table(title="🔧 Command Matrix", border_style="bright_cyan")
        help_table.add_column(header="Protocol", style="bold bright_magenta", width=15)
        help_table.add_column(header="Function", style="dim bright_green")
        commands = {}
        if command_name:
            match_command: CommandMeta | None = self.typer_bridge.get_command_info(command_name)
            if match_command is not None:
                commands: dict[str, CommandMeta] = {command_name: match_command}
        else:
            commands: dict[str, CommandMeta] = self.typer_bridge.get_all_command_info(show_hidden=False)

        for cmd_name, cmd_info in commands.items():
            help_table.add_row(cmd_name, cmd_info["help"])
        console.print(help_table)

    @registry.command("refresh", help_text="Refresh the Obsidian Todo file")
    def refresh_obsidian(self) -> None:
        """Refresh the Obsidian Todo file"""
        try:
            self.todo_handler.update_tasks()
            console.print("[bright_green]>> Data stream synchronized successfully <<[/bright_green]")
        except Exception as e:
            console.print(f"[bright_red]⚠️ Neural link error: {e}[/bright_red]")
            return

    def list_tasks(
        self,
        table_name: str = "� Active Process Queue",
        tasks_input: dict[int, Task] | None = None,
    ) -> None:
        """List all tasks in a beautiful table"""
        tasks: dict[int, Task] = tasks_input if tasks_input else self.todo_handler.get_tasks()
        if not tasks:
            console.print("[bright_yellow]⚡ No active processes detected ⚡[/bright_yellow]")
            return
        table = Table(title=table_name, border_style="bright_green")
        table.add_column(header="PID", style="bold bright_cyan", width=3)
        table.add_column(header="Process", style="bright_white", overflow="ellipsis")
        table.add_column(header="Sector", style="bright_blue")
        table.add_column(header="Sub-Sector", style="bright_magenta")
        table.add_column(header="Level", style="dim", width=2)
        for task_id, task in tasks.items():
            indent: LiteralString = get_indent(sep=INDENT, depth=task.depth)
            task_text: str = f"{indent}{task.to_string(category=False)}"
            category: str = task.category if task.category else "Uncategorized"
            subcategory: str = task.subcategory if task.subcategory else "None"
            table.add_row(str(task_id), task_text, category, subcategory, str(task.depth))
        console.print(table)

    @registry.command(
        *["l", "list"],  # l, list are aliases for this command
        help_text="List all tasks",
        args=[
            pos_arg(
                "task_choice",
                obj_type=str,
                default="all",
                nargs="?",
                choices=["incomplete", "complete", "all"],
                help_text="Choose task type to list",
            )
        ],
    )
    def list_tasks_cmd(self, task_choice: Literal["incomplete", "complete", "all"] = "all") -> None:
        """List all tasks (command-line mode)"""
        tasks: dict[int, Task] = {}
        table_name: str = "📋 All Processes"
        match task_choice:
            case "incomplete":
                tasks: dict[int, Task] = get_incomplete_tasks()
                table_name = "🔋 Incomplete Processes"
            case "complete":
                tasks = get_completed_tasks()
                table_name = "✅ Completed Processes"
            case "all":
                tasks = self.todo_handler.get_tasks()
            case _:
                console.print(f"[bright_red]Unknown task choice: {task_choice}[/bright_red]")
        if not tasks:
            console.print("[bright_yellow]⚡ No tasks found in the system ⚡[/bright_yellow]")
            return
        self.list_tasks(table_name=table_name, tasks_input=tasks)

    @registry.command("completed_today", help_text="List tasks completed today")
    def get_completed_today(self) -> None:
        """List tasks completed today"""
        completed_today: dict[int, Task] = self.todo_handler.tasks_finished_today()
        if not completed_today:
            console.print("[bright_yellow]⚡ No processes completed today ⚡[/bright_yellow]")
            return

        for task_id, task in completed_today.items():
            if task.completed_at is None:
                console.print(f"[bright_red]⚠️ Task ID {task_id} has no completion time recorded![/bright_red]")
            else:
                console.print(f" - [x] {task.text}", markup=False, style="bright_green")

    @registry.command(
        "add_task",
        "add",
        help_text="Add a new task",
        args=[
            pos_arg("task_text", obj_type=str, help_text="Task description", nargs="?"),
            pos_arg("category", obj_type=str, help_text="Task category", nargs="?"),
            pos_arg("subcategory", obj_type=str, help_text="Task subcategory", nargs="?"),
            pos_arg(
                "already_done",
                obj_type=bool,
                default=None,
                nargs="?",
                help_text="Mark task as completed immediately (default: False)",
            ),
        ],
    )
    def add_task(self, **kwargs: Any) -> None:
        """Add a new task interactively"""
        console.print("[bold bright_green]>> Initiating new process <<[/bold bright_green]")
        task_text: str = kwargs.get("task_text", "")
        category: str = kwargs.get("category", "")
        subcategory: str = kwargs.get("subcategory", "")
        task_text: str = task_text if task_text else prompt(message="Process description: ").strip()
        if not task_text:
            console.print("[bright_red]Process description required for initialization![/bright_red]")
            return
        categories: list[str] = self.todo_handler.get_categories()
        if categories:
            console.print("\n[dim bright_cyan]Available sectors:[/dim bright_cyan]")
            for cat in categories:
                console.print(f"  • {cat}")
        category: str = category if category else prompt(message="Target sector: ").strip()
        if not category:
            console.print("[bright_red]Sector designation required![/bright_red]")
            return
        subcategory: str = subcategory if subcategory else prompt(message="Sub-sector: ").strip()
        if not subcategory:
            console.print("[bright_red]Sub-sector designation required![/bright_red]")
            return
        self.add_task_cmd(
            task_text=task_text,
            category=category,
            subcategory=subcategory,
            already_done=kwargs.get("already_done", False),
        )

    def add_task_cmd(self, task_text: str, category: str, subcategory: str, already_done: bool | None = None) -> None:
        """Add a new task (command-line mode)"""
        try:
            result: str = self.todo_handler.add_task(task_text=task_text, category=category, sub_category=subcategory)
            if already_done:
                self.todo_handler.complete_task(task_id=int(result))
                console.print("[bright_green]>> Process initialized and terminated successfully! <<[/bright_green]")
                return
            console.print(f"[bright_green]>> Process initialized successfully! << ({result})[/bright_green]")
            self.todo_handler.update_tasks()
        except Exception as e:
            console.print(f"[bright_red]⚠️ Process initialization failed: {e}[/bright_red]")

    def add_subtask(self) -> None:
        """Add a subtask to an existing task"""
        console.print("[bold bright_green]Initiating sub-process[/bold bright_green]")
        self.list_tasks()
        try:
            parent_id = int(prompt(message="\nParent process PID: ").strip())
        except ValueError:
            console.print("[bright_red]Invalid process ID![/bright_red]")
            return
        tasks: dict[int, Task] = self.todo_handler.get_tasks()
        if parent_id not in tasks:
            console.print(f"[bright_red]Process {parent_id} not found in system![/bright_red]")
            return
        subtask_text: str = prompt(message="Sub-process description: ").strip()
        if not subtask_text:
            console.print("[bright_red]Sub-process description required![/bright_red]")
            return
        self.add_subtask_cmd(parent_id=str(parent_id), subtask_text=subtask_text)

    def add_subtask_cmd(self, parent_id: str, subtask_text: str) -> None:
        """Add a subtask (command-line mode)"""
        try:
            parent_id_int = int(parent_id)
            tasks: dict[int, Task] = self.todo_handler.get_tasks()
            if parent_id_int not in tasks:
                console.print(f"[bright_red]Process {parent_id_int} not found in system![/bright_red]")
                return
            parent_task: Task = tasks[parent_id_int]
            self.todo_handler.add_subtask(
                text=subtask_text,
                category=parent_task.category,
                subcategory=parent_task.subcategory,
                parent_task_id=parent_id_int,
            )
            console.print("[bright_green]>> Sub-process spawned successfully! <<[/bright_green]")
        except ValueError:
            console.print("[bright_red]Invalid parent process ID![/bright_red]")
        except Exception as e:
            console.print(f"[bright_red]⚠️ Sub-process spawn failed: {e}[/bright_red]")

    def complete_task(self) -> None:
        """Mark tasks as completed"""
        console.print("[bold bright_green]🔋 Terminating processes[/bold bright_green]")
        incomplete_tasks: dict[int, Task] = get_incomplete_tasks()

        if not incomplete_tasks:
            console.print("[bright_yellow]⚡ All processes completed! System clean! ⚡[/bright_yellow]")
            return
        self.list_tasks(table_name="🔋 Incomplete Processes", tasks_input=incomplete_tasks)
        task_ids_input: str = prompt("\nProcess IDs to terminate (comma-separated): ").strip()
        if not task_ids_input:
            console.print("[bright_red]No process IDs provided![/bright_red]")
            return
        self.complete_task_cmd(task_ids_str=task_ids_input)

    def complete_task_cmd(self, task_ids_str: str):
        """Complete tasks (command-line mode)"""
        try:
            incomplete_tasks: dict[int, Task] = get_incomplete_tasks()
            task_ids, invalid_ids = get_invalid_ids(task_ids_input=task_ids_str, tasks=incomplete_tasks)
            if invalid_ids:
                console.print(f"[bright_red]Invalid/terminated process IDs: {invalid_ids}[/bright_red]")
                return
            for task_id in task_ids:
                try:
                    self.todo_handler.complete_task(task_id)
                except Exception as e:
                    console.print(f"[bright_red]⚠️ Failed to terminate process {task_id}: {e}[/bright_red]")
                    continue
            console.print(f"[bright_green]>> {len(task_ids)} process(es) terminated successfully! <<[/bright_green]")
            self.todo_handler.update_tasks()
        except ValueError:
            console.print("[bright_red]Invalid process ID format![/bright_red]")
        except Exception as e:
            console.print(f"[bright_red]⚠️ Process termination failed: {e}[/bright_red]")

    @registry.command(
        "delete_task",
        "purge",
        help_text="Purge tasks from memory",
        args=[pos_arg("task_ids_str", obj_type=str, nargs="?", help_text="Comma-separated task IDs")],
    )
    def delete_task(self, task_ids_str: str | None = None) -> None:
        """Purge tasks from memory

        If no task IDs are provided, prompt the user to select tasks to purge.

        Args:
            task_ids_str (str | None): Comma-separated string of task IDs to purge. If None, user will be prompted.
        """
        console.print("[bold bright_red]🗑️ Purging processes from memory[/bold bright_red]")
        self.list_tasks()
        task_ids_input: str = (
            task_ids_str if task_ids_str else prompt(message="\nProcess IDs to purge (comma-separated): ").strip()
        )
        if not task_ids_input:
            console.print("[bright_red]No process IDs provided![/bright_red]")
            return
        self.delete_task_cmd(task_ids_str=task_ids_input, interactive=True)

    def delete_task_cmd(self, task_ids_str: str, interactive: bool = False) -> None:
        """Delete tasks (command-line mode)"""
        try:
            tasks: dict[int, Task] = self.todo_handler.get_tasks()
            task_ids, invalid_ids = get_invalid_ids(task_ids_input=task_ids_str, tasks=tasks)
            if invalid_ids:
                console.print(f"[bright_red]Invalid process IDs: {invalid_ids}[/bright_red]")
                return
            if interactive and not confirm(message=f"Confirm memory purge for {len(task_ids)} process(es)?"):
                console.print("[bright_yellow]Memory purge cancelled[/bright_yellow]")
                return
            for task_id in task_ids:
                try:
                    self.todo_handler.delete_task(task_id)
                except Exception as e:
                    console.print(f"[bright_red]⚠️ Failed to purge process {task_id}: {e}[/bright_red]")
                    continue
            console.print(f"[bright_green]>> {len(task_ids)} process(es) purged from memory! <<[/bright_green]")
            self.todo_handler.update_tasks()
        except ValueError:
            console.print("[bright_red]Invalid process ID format![/bright_red]")
        except Exception as e:
            console.print(f"[bright_red]⚠️ Memory purge failed: {e}[/bright_red]")

    @registry.command("categories", "list_categories", help_text="List all available categories")
    def list_categories(self) -> None:
        """List all available categories"""
        categories: list[str] = self.todo_handler.get_categories()
        if not categories:
            console.print("[bright_yellow]No sectors detected in database![/bright_yellow]")
            return
        table = Table(title="🌐 Available Sectors", border_style="bright_blue")
        table.add_column(header="Sector", style="bold bright_blue")
        for category in sorted(categories):
            table.add_row(category)
        console.print(table)

    def show_hierarchy(self) -> None:
        """Show task hierarchy for a specific task"""
        task_id: str = prompt(message="\nProcess ID for neural tree analysis (leave empty for full system): ").strip()
        self.show_hierarchy_cmd(task_id_str=task_id)

    @registry.command(
        "hierarchy",
        "show_hierarchy",
        help_text="Show task hierarchy",
        args=[pos_arg("task_id_str", obj_type=str, nargs="?", help_text="Task ID for hierarchy")],
    )
    def show_hierarchy_cmd(self, task_id_str: str | None = None) -> None:
        """Show task hierarchy (command-line mode)"""
        try:
            if task_id_str is None or task_id_str.strip() == "":
                hierarchy_str: str = self.todo_handler.get_task_tree()
            else:
                task_id = int(task_id_str)
                hierarchy_str = self.todo_handler.get_task_hierarchy(task_id=task_id)
            if hierarchy_str.startswith("Task with ID"):
                console.print(f"[bright_red]⚠️ {hierarchy_str}[/bright_red]")
            else:
                console.print("[bold bright_blue]🔍 Neural Tree Analysis:[/bold bright_blue]")
                console.print(hierarchy_str)
        except ValueError:
            console.print("[bright_red]Invalid process ID![/bright_red]")
        except Exception as e:
            console.print(f"[bright_red]⚠️ Neural tree analysis failed: {e}[/bright_red]")

    def _run_command(self, parsed: tuple[CommandSpec, Namespace]) -> None:
        """Run a command with the given arguments"""
        command_spec, namespace = parsed
        try:
            command_spec.func(**vars(namespace))
        except TypeError as e:
            console.print(f"[bright_red]⚠️ Argument error: {e}[/bright_red]")
            console.print("Enter 'help' to access command matrix")
        except Exception as e:
            console.print(f"[bright_red]Error occurred while executing command: {e}[/bright_red]")

    def run(self) -> None:
        """Main CLI loop"""
        self.show_welcome()
        while True:
            try:
                command: str = prompt(message="> ", completer=self.command_completer, history=self.command_history)
                command_parts: list[str] = split(command)
                if not command_parts:
                    continue
                if command_parts[0] in ["quit"]:
                    self.quit()
                self.typer_bridge.execute_command(command_string=command)

                # parsed: tuple[CommandSpec, Namespace] | None = registry.parse_args(command_parts)
                # if parsed is None:
                #     console.print(f"[bright_red]Unknown protocol: {command}[/bright_red]")
                #     console.print("Enter 'help' to access command matrix")
                #     continue
                # self._run_command(parsed)
            except KeyboardInterrupt:
                console.print("\n[bright_yellow]Use 'quit' or 'exit' to jack out[/bright_yellow]")
            except EOFError:
                break

    @registry.command("quit", "exit", "q", help_text="Exit the application")
    def quit(self) -> NoReturn:
        """Exit the application"""
        console.print(
            "[bold bright_magenta]⚡ Neural interface disconnected. Stay frosty, samurai. ⚡[/bold bright_magenta]"
        )
        sys.exit(0)


# class CommandRegistry:
#     def __init__(self, todo_cli: TodoCLI) -> None:
#         """Initialize the command registry with the TodoCLI instance."""
#         self.todo_cli: TodoCLI = todo_cli
#         self.commands: dict[str, Any] = self.todo_cli.commands

#     def get_args(self, command: list[str]) -> Namespace:
#         """Parse command arguments using argparse."""
#         try:
#             parser: ArgumentParser = ArgumentParser(exit_on_error=False, add_help=False)
#             subparsers: _SubParsersAction[ArgumentParser] = parser.add_subparsers(dest="command", required=True)

#             list_parser: ArgumentParser = subparsers.add_parser("list", help="List all tasks")
#             list_parser.add_argument("-c", "--completed", action="store_true", help="Show completed tasks")

#             add_parser: ArgumentParser = subparsers.add_parser("add", help="Add a new task")
#             add_parser.add_argument("task_text", type=str, help="Task description")
#             add_parser.add_argument("category", type=str, help="Task category")
#             add_parser.add_argument("subcategory", type=str, help="Task subcategory")

#             complete_parser: ArgumentParser = subparsers.add_parser("complete", help="Complete tasks")
#             complete_parser.add_argument("task_ids", type=str, nargs="*", help="Task IDs to complete")

#             delete_parser: ArgumentParser = subparsers.add_parser("delete", help="Delete tasks")
#             delete_parser.add_argument("task_ids", type=str, nargs="*", help="Task IDs to delete")

#             subtask_parser: ArgumentParser = subparsers.add_parser("subtask", help="Add a subtask")
#             subtask_parser.add_argument("task_id", type=str, help="Parent task ID")
#             subtask_parser.add_argument("subtask_text", type=str, help="Subtask description")

#             categories_parser: ArgumentParser = subparsers.add_parser("categories", help="List all categories")
#             categories_parser.add_argument(
#                 "-a",
#                 "--all",
#                 action="store_true",
#                 help="Show all categories including inactive ones",
#             )

#             subparsers.add_parser("refresh", help="Refresh Obsidian Todo file")

#             hierarchy_parser: ArgumentParser = subparsers.add_parser("hierarchy", help="Show task hierarchy")
#             hierarchy_parser.add_argument(
#                 "task_id",
#                 type=str,
#                 nargs="?",
#                 default=None,
#                 help="Task ID to show hierarchy for (leave empty for full system)",
#             )

#             subparsers.add_parser(
#                 "completed_today",
#                 help="List tasks completed today",
#             )

#             help_parser: ArgumentParser = subparsers.add_parser("help", help="Show this help message")
#             help_parser.add_argument("command", type=str, nargs="?", help="Command to get help for")

#             quit_parser: ArgumentParser = subparsers.add_parser("quit", help="Exit the application")
#             quit_parser.add_argument(
#                 "-f",
#                 "--force",
#                 action="store_true",
#                 help="Force exit without confirmation",
#             )
#             return parser.parse_args(command)
#         except ArgumentError as e:
#             console.print(f"[bright_red]⚠️ Argument error: {e}[/bright_red]")
#             return Namespace(command="help")
