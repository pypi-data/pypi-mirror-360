"""RichTreeCLI constants and data classes."""

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

from rich.tree import Tree

if TYPE_CHECKING:
    from rich_tree_cli.main import RichTreeCLI


@dataclass
class RunResult:
    """Data returned from :class:`RichTreeCLI.run`."""

    tree: Tree
    totals: str
    cli: "RichTreeCLI"


class OutputFormat(StrEnum):
    """Enum for output formats."""

    TEXT = "txt"
    MARKDOWN = "md"
    HTML = "html"
    JSON = "json"
    SVG = "svg"
    TOML = "toml"
    YAML = "yaml"
    XML = "xml"

    @classmethod
    def key_to_value(cls, key: str) -> str:
        """Get the value of the enum based on the key."""
        try:
            return cls[key.upper()].value
        except KeyError:
            raise ValueError(f"Invalid output format key: {key}") from None

    @staticmethod
    def choices() -> list[str]:
        """Return a list of available output format choices."""
        return [format.name.lower() for format in OutputFormat]

    @staticmethod
    def default() -> list[str]:
        """Return the default output format."""
        default = OutputFormat.TEXT

        return [default.name.lower()]
