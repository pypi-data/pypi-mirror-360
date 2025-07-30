from dataclasses import asdict, dataclass
from io import StringIO

from rich.console import Console


@dataclass
class ConsoleConfig:
    """Configuration for the console."""

    file: StringIO | None = None
    highlight: bool = True
    soft_wrap: bool = True
    width: int = 80
    emoji: bool = True
    emoji_variant: str = "emoji"
    markup: bool = True
    record: bool = False
    force_terminal: bool = True
    style: str | None = None

    def update(self, **kwargs) -> None:
        """Update the console configuration with additional keyword arguments."""
        for key, value in kwargs.items():
            setattr(self, key, value)


def get_console(disable_color: bool, **kwargs) -> Console:
    """Create the output and capture consoles with the specified configurations."""
    base_config = ConsoleConfig()
    if file := kwargs.pop("file", None):
        base_config.file = file
    if disable_color:
        base_config.highlight = False
        base_config.markup = False
        base_config.force_terminal = False
    if kwargs:  # allows an override anything that comes before this
        base_config.update(**kwargs)

    return Console(**asdict(base_config))
