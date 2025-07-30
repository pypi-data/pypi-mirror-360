from __future__ import annotations

from logging import DEBUG
from pathlib import Path
import sys
from typing import TYPE_CHECKING, Annotated

from bear_utils.logger_manager import ConsoleLogger
from dotenv import load_dotenv
from typer import Argument, Exit, Option, Typer, echo

from trackdo._internal import debug
from trackdo.console.aliases import TyperBridge
from trackdo.console.todo_class import TodoCLI

if TYPE_CHECKING:
    from trackdo.console.todo_class import TodoCLI
    from trackdo.core._schemas import Task

console: ConsoleLogger = ConsoleLogger.get_instance(
    init=True,
    name="todo_cli",
    level=DEBUG,
    queue_handler=True,
)


PROG = "trackdo"

app = Typer(
    name=PROG,
    help="[bold bright_magenta]TrackDo Neural Interface[/bold bright_magenta] - [green]Cybernetic task management system[/green]",
    rich_markup_mode="rich",
)

cli: TyperBridge = TyperBridge.get_instance(init=True, typer_app=app, console=console)


def _get_todo_cli() -> TodoCLI:
    """Get TodoCLI instance with loaded environment."""
    from trackdo.console.todo_class import TodoCLI  # noqa: PLC0415

    return TodoCLI.get_instance(init=True)


def _debug_info_callback(value: bool) -> None:
    """Print debug information and exit."""
    if value:
        debug._print_debug_info()
        raise Exit


def _version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        echo(f"trackdo {debug._get_version()}")
        raise Exit


@app.callback()
def app_callback(
    debug_info: Annotated[
        bool,
        Option("--debug-info", callback=_debug_info_callback, help="Access system diagnostics."),
    ] = False,
    version: Annotated[
        bool,
        Option("-V", "--version", callback=_version_callback, help="Display neural interface version."),
    ] = False,
) -> None:
    """[bold bright_magenta]TrackDo Neural Interface[/bold bright_magenta] - Cybernetic task management system."""


@app.command()
def interactive() -> None:
    """Activate neural interface mode."""
    todo_cli: TodoCLI = _get_todo_cli()
    todo_cli.run()


@app.command(name="list")
def list_tasks() -> None:
    """Display active process queue."""
    todo_cli: TodoCLI = _get_todo_cli()
    todo_cli.list_tasks()


@app.command()
def add(
    text: Annotated[str, Argument(help="Process description")],
    category: Annotated[str, Argument(help="Target sector")],
    subcategory: Annotated[str, Argument(help="Sub-sector designation")],
    already_done: Annotated[bool, Option("--already-done", help="Execute and terminate immediately")] = False,
) -> None:
    """Initialize a new process."""
    todo_cli: TodoCLI = _get_todo_cli()
    todo_cli.add_task_cmd(task_text=text, category=category, subcategory=subcategory, already_done=already_done)


@app.command()
def complete(
    task_ids: Annotated[str, Argument(help="Comma-separated process IDs")],
) -> None:
    """Terminate processes."""
    todo_cli: TodoCLI = _get_todo_cli()
    todo_cli.complete_task_cmd(task_ids_str=task_ids)


@app.command()
def delete(
    task_ids: Annotated[str, Argument(help="Comma-separated process IDs")],
) -> None:
    """Purge processes from memory."""
    todo_cli: TodoCLI = _get_todo_cli()
    todo_cli.delete_task_cmd(task_ids_str=task_ids)


@app.command()
def subtask(
    parent_id: Annotated[int, Argument(help="Parent process ID")],
    text: Annotated[str, Argument(help="Sub-process description")],
) -> None:
    """Spawn sub-process from existing process."""
    todo_cli: TodoCLI = _get_todo_cli()
    todo_cli.add_subtask_cmd(parent_id=str(parent_id), subtask_text=text)


@app.command()
def refresh() -> None:
    """Synchronize data stream."""
    todo_cli: TodoCLI = _get_todo_cli()
    todo_cli.refresh_obsidian()


@app.command()
def categories() -> None:
    """List available sectors."""
    todo_cli: TodoCLI = _get_todo_cli()
    todo_cli.list_categories()


@app.command()
def hierarchy(
    task_id: Annotated[int, Argument(help="Process ID")],
) -> None:
    """Analyze neural tree structure."""
    todo_cli: TodoCLI = _get_todo_cli()
    todo_cli.show_hierarchy_cmd(task_id_str=str(task_id))


@cli.aliases("ct")
@app.command()
def completed_today() -> None:
    """List tasks completed today."""
    todo_cli: TodoCLI = _get_todo_cli()
    completed_tasks: dict[int, Task] = todo_cli.todo_handler.tasks_finished_today()
    if not completed_tasks:
        echo(message="No tasks completed today.")
    else:
        for task_id, task in completed_tasks.items():
            if task.completed_at is None:
                echo(f"Task ID: {task_id}, Description: {task.text}, Completed At: Not available")
            else:
                echo(f"Task ID: {task_id}, Description: {task.text}, Completed At: {task.completed_at.to_string()}")


@cli.aliases("h")
@app.command()
def help(command_name: str | None = Argument(None, help="Specific command to get help for")) -> None:
    """Display help information."""
    todo_cli: TodoCLI = _get_todo_cli()
    todo_cli.show_help(command_name=command_name)


@cli.aliases("q", "exit")
@app.command()
def quit() -> None:
    """Exit the neural interface."""
    todo_cli: TodoCLI = _get_todo_cli()
    todo_cli.quit()


def main(args: list[str] | None = None) -> int:
    """Entry point for the CLI application.

    This function is executed when you type `trackdo` or `python -m trackdo`.

    Parameters:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """
    load_dotenv(dotenv_path=str(Path(__file__).parent.parent.parent.parent / ".env"))

    if args is None:
        args = sys.argv[1:]

    if not args:
        todo_cli: TodoCLI = _get_todo_cli()
        todo_cli.run()
        return 0

    try:
        app(args)
        return 0
    except SystemExit as e:
        exit_code = e.code
        if isinstance(exit_code, int):
            return exit_code
        return 0 if exit_code is None else 1
    except Exception:
        return 1


if __name__ == "__main__":
    main()
