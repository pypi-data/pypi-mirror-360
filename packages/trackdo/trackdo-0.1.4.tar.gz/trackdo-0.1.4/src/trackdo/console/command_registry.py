"""# CommandRegistry class for registering and managing CLI commands."""

from argparse import ArgumentParser, Namespace
from collections.abc import Callable
from functools import wraps
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

Nargs = Literal["?", "+", "*", ""]


class ArgSpec(BaseModel):
    """Specification for a command-line argument."""

    help: str | None = Field(default=None, description="Help text for the argument")


class PosArgSpec(BaseModel):
    """Specification for a positional argument."""

    name: str = Field("", description="Name of the positional argument")
    help: str | None = Field(default=None, description="Help text for the argument")
    nargs: Nargs = Field(default="", description="Number of arguments expected")
    type_: type = Field(default=str, alias="type", description="Type of the argument")
    default: Any = Field(default=None, description="Default value for the argument")
    choices: list[Any] | None = Field(default=None, description="List of valid choices for the argument")

    model_config = {"arbitrary_types_allowed": True}

    @field_validator("type_", mode="before")
    @classmethod
    def validate_type(cls, value: type | Any) -> type:
        """Ensure that the 'type' field is a valid type."""
        if not isinstance(value, type):
            raise TypeError(f"Invalid type: {value}. Must be a valid Python type.")
        return value

    @field_validator("nargs", mode="before")
    @classmethod
    def validate_nargs(cls, value: Nargs) -> Nargs:
        """Ensure that the 'nargs' field is one of the valid Nargs values."""
        valid_nargs = {"?", "+", "*", ""}
        if value not in valid_nargs:
            raise ValueError(f"Invalid nargs value: {value}. Must be one of {valid_nargs}.")
        return value

    def to_kwargs(self) -> dict[str, Any]:
        """Convert to kwargs dict for ArgumentParser.add_argument()"""
        kwargs = {}
        if self.help:
            kwargs["help"] = self.help
        if self.type_:
            kwargs["type"] = self.type_
        if self.nargs:
            kwargs["nargs"] = self.nargs
        if self.default is not None:
            kwargs["default"] = self.default
        if hasattr(self, "choices") and self.choices:
            kwargs["choices"] = self.choices
        return kwargs


class FlagArg(ArgSpec):
    """Specification for a command-line flag argument."""

    name: list[str] = Field(default_factory=list, description="List of names for the flag")
    action: str = Field(default="store_true", description="Action to perform when the flag is set")

    model_config = {"arbitrary_types_allowed": True}

    @field_validator("action", mode="before")
    @classmethod
    def validate_action(cls, value: str) -> str:
        """Ensure that the 'action' field is a valid action."""
        valid_actions = {"store_true", "store_false", "append", "count"}
        if value not in valid_actions:
            raise ValueError(f"Invalid action: {value}. Must be one of {valid_actions}.")
        return value

    def to_kwargs(self) -> dict[str, Any]:
        """Convert the FlagArg to a dictionary of keyword arguments for argparse."""
        kwargs = {}
        if self.help:
            kwargs["help"] = self.help
        if self.action:
            kwargs["action"] = self.action
        return kwargs


class CommandSpec(BaseModel):
    """Specification for a command in the command registry."""

    name: str = Field(default="", description="Name of the command")
    help: str | None = Field(default=None, description="Help text for the command")
    func: Callable = Field(default=..., description="Function to execute for the command")
    args: list[PosArgSpec] = Field(default_factory=list, description="List of positional arguments for the command")
    flags: list[FlagArg] = Field(default_factory=list, description="List of flag arguments for the command")

    model_config = {"arbitrary_types_allowed": True}

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, value: str) -> str:
        """Ensure that the 'name' field is a non-empty string."""
        if not value:
            raise ValueError("The 'name' field must be a non-empty string.")
        return value

    @field_validator("func", mode="before")
    @classmethod
    def validate_func(cls, value: Callable | Any) -> Callable | None:
        """Ensure that the 'func' field is a callable."""
        if value is not None and not callable(value):
            raise TypeError(f"Invalid func: {value}. Must be a callable.")
        return value


class CommandRegistry:
    """A Command registry that uses decorators to register commands."""

    def __init__(self) -> None:
        """Initialize the CommandRegistry."""
        self.commands: dict[str, CommandSpec] = {}
        self.app: object | None = None

    def set_app(self, app: object) -> None:
        """Set the outside app instance for the CommandRegistry."""
        self.app = app

    def command(
        self,
        *name: str,
        help_text: str = "",
        args: list[PosArgSpec | FlagArg] | None = None,
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Decorator to register a command with all its arguments and flags"""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            """Decorator to register a command with its function, help text, and arguments."""
            for cmd_name in name:
                self.commands[cmd_name] = CommandSpec(
                    name=cmd_name,
                    func=lambda *args, **kwargs: func(self.app, *args, **kwargs) if self.app else func(*args, **kwargs),
                    help=help_text,
                    args=[arg for arg in args if isinstance(arg, PosArgSpec)] if args is not None else [],
                    flags=[flag for flag in args if isinstance(flag, FlagArg)] if args is not None else [],
                )

            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                """Wrapper function to call the registered command."""
                return func(*args, **kwargs)

            return wrapper

        return decorator

    def get_command(self, name: str) -> CommandSpec | None:
        """Get a command by its name."""
        return self.commands.get(name)

    def parse_args(self, command_parts: list[str]) -> tuple[CommandSpec, Namespace] | None:
        """Parse the arguments for a given command."""
        command_name, args = command_parts[0], command_parts[1:]
        command: CommandSpec | None = self.get_command(command_name)
        if not command:
            return None
        parser = ArgumentParser(prog=command_name, description=command.help, exit_on_error=False, add_help=False)

        for arg in command.args:
            parser.add_argument(arg.name, **arg.to_kwargs())

        for flag in command.flags:
            parser.add_argument(*flag.name, **flag.to_kwargs())

        return command, parser.parse_args(args)


def pos_arg(
    name: str,
    help_text: str = "",
    nargs: Nargs = "",
    obj_type: type = str,
    default: Any = None,
    choices: list[Any] | None = None,
) -> PosArgSpec:
    """Returns a PosArgSpec for a positional argument."""
    return PosArgSpec(
        name=name,
        help=help_text,
        nargs=nargs,
        type=obj_type,
        default=default,
        choices=choices,
    )


def flag_arg(
    *name: str,
    help_text: str = "",
    action: str = "store_true",
) -> FlagArg:
    """Returns a FlagArg for a command-line flag."""
    names = []
    for n in name:
        if not isinstance(n, str):
            raise TypeError(f"Flag name must be a string, got {type(n).__name__}")
        names.append(n)
    return FlagArg(
        name=names,
        help=help_text,
        action=action,
    )
