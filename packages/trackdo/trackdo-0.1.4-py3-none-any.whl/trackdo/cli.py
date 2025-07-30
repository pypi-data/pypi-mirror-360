"""Interactive Todo CLI with colorful interface using rich and prompt_toolkit."""

from __future__ import annotations

from logging import DEBUG
import sys

from bear_utils.logger_manager import ConsoleLogger

from trackdo.console.todo_class import TodoCLI

console: ConsoleLogger = ConsoleLogger.get_instance(
    init=True,
    name="todo_cli",
    level=DEBUG,
    queue_handler=True,
)


def main() -> None:
    """Main entry point for interactive mode only."""
    try:
        cli = TodoCLI()
        cli.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye! 👋[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
